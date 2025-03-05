import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
# Import our custom LoguruInstrumentor
from andromeda_ng.service.utils.opentelemetry_instrumentation_loguru import LoguruInstrumentor
import logging
from loguru import logger
import sys
from andromeda_ng.service.settings import config


def configure_telemetry(app=None, db_engine=None):
    """Configure OpenTelemetry for the application"""

    # If telemetry is not enabled, return empty providers
    if not config.TELEMETRY_ENABLED:
        logger.info("Telemetry is disabled. Skipping OpenTelemetry setup.")
        return {
            "trace_provider": None,
            "logger_provider": None,
            "enabled": False
        }

    logger.info("Configuring OpenTelemetry...")

    # Create a resource with service information
    resource = Resource.create({
        "service.name": config.SERVICE_NAME,
        "service.version": "0.1.0",  # Replace with your version
        "deployment.environment": config.ENV
    })

    # Configure tracing
    trace_provider = TracerProvider(resource=resource)

    # Configure the OTLP exporter for Tempo
    tempo_endpoint = os.getenv("TEMPO_ENDPOINT", "tempo:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=tempo_endpoint, insecure=True)
    trace_processor = BatchSpanProcessor(otlp_exporter)
    trace_provider.add_span_processor(trace_processor)

    # Set the global trace provider
    trace.set_tracer_provider(trace_provider)

    # Configure logging for OpenTelemetry
    # Create a LoggerProvider
    logger_provider = LoggerProvider(resource=resource)

    # Configure Loki exporter
    loki_endpoint = os.getenv("LOKI_ENDPOINT", "loki:4317")
    log_exporter = OTLPLogExporter(endpoint=loki_endpoint, insecure=True)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter)
    )

    # Create a handler for logging
    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider,
    )

    # Configure loguru with OpenTelemetry
    # Remove default handler
    logger.remove()
    # Add OpenTelemetry-compatible handler
    logger.configure(handlers=[{
        "sink": sys.stderr,
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra}"
    }])

    # Instrument loguru
    LoguruInstrumentor().instrument(logger_provider=logger_provider)

    # Instrument the Python logging
    LoggingInstrumentor().instrument(logger_provider=logger_provider)

    # Instrument the application if provided
    if app:
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=trace_provider,
        )

    # Instrument the database if provided
    if db_engine:
        SQLAlchemyInstrumentor().instrument(
            engine=db_engine,
            tracer_provider=trace_provider,
        )

    # Instrument HTTP libraries
    HTTPXClientInstrumentor().instrument(tracer_provider=trace_provider)
    RequestsInstrumentor().instrument(tracer_provider=trace_provider)

    return {
        "trace_provider": trace_provider,
        "logger_provider": logger_provider,
        "enabled": True
    }
