# andromeda_ng/service/utils/opentelemetry_instrumentation_loguru.py
import sys
from typing import Collection, Optional
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LogRecord
from opentelemetry.sdk._logs.export import LogExporter, BatchLogRecordProcessor
from opentelemetry.trace import format_trace_id, format_span_id
from opentelemetry.util.types import AttributeValue
import time
from loguru import logger


class LoguruInstrumentor(BaseInstrumentor):
    """An instrumentor for Loguru"""

    def _instrument(self, **kwargs):
        """Instrument Loguru"""
        tracer_provider = kwargs.get("tracer_provider")
        logger_provider = kwargs.get("logger_provider")

        if not logger_provider:
            return

        # Create a new loguru handler that forwards logs to OpenTelemetry
        def otel_sink(message):
            # Extract log record attributes
            record = message.record

            # Get the current span context
            span_context = trace.get_current_span().get_span_context()
            trace_id = format_trace_id(
                span_context.trace_id) if span_context.is_valid else None
            span_id = format_span_id(
                span_context.span_id) if span_context.is_valid else None

            # Create attributes dictionary
            attributes = {
                "log.severity": record["level"].name,
                "log.message": record["message"],
                "log.logger_name": record["name"],
                "thread.id": record["thread"].id,
                "thread.name": record["thread"].name,
                "code.function": record["function"],
                "code.filename": record["file"].name,
                "code.lineno": record["line"],
            }

            # Add trace context if available
            if trace_id:
                attributes["trace_id"] = trace_id
            if span_id:
                attributes["span_id"] = span_id

            # Add any extra attributes from the log record
            if record["extra"]:
                for key, value in record["extra"].items():
                    # Ensure value is a valid attribute value type
                    if isinstance(value, (str, bool, int, float)) or (
                        isinstance(value, Collection) and
                        not isinstance(value, (str, bytes, bytearray)) and
                        all(isinstance(x, (str, bool, int, float))
                            for x in value)
                    ):
                        attributes[key] = value

            # Create and emit the log record
            log_record = LogRecord(
                timestamp=int(time.time() * 1_000_000_000),  # nanoseconds
                trace_id=span_context.trace_id if span_context.is_valid else None,
                span_id=span_context.span_id if span_context.is_valid else None,
                trace_flags=span_context.trace_flags if span_context.is_valid else None,
                severity_text=record["level"].name,
                severity_number=_get_severity_number(record["level"].name),
                body=record["message"],
                attributes=attributes,
                resource=logger_provider.resource,
            )

            # Get the logger from the provider
            otel_logger = logger_provider.get_logger(
                record["name"],
                "1.0.0",  # version
                "python.loguru",  # schema_url
            )

            # Emit the log record
            otel_logger.emit(log_record)

            # Return the original message to allow further processing
            return message

        # Replace the existing Loguru handler with our instrumented one
        logger.configure(handlers=[
            # Format is minimal as we extract info elsewhere
            {"sink": otel_sink, "format": "{message}"},
            {"sink": sys.stderr, "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra}"}
        ])

        # Store the original configurations
        self._original_handlers = logger._core.handlers

    def _uninstrument(self, **kwargs):
        """Uninstrument Loguru"""
        # Restore original handlers if available
        if hasattr(self, "_original_handlers"):
            logger._core.handlers = self._original_handlers


def _get_severity_number(severity_text: str) -> Optional[int]:
    """Convert Loguru severity text to OpenTelemetry severity number"""
    severity_map = {
        "TRACE": 1,
        "DEBUG": 5,
        "INFO": 9,
        "SUCCESS": 9,
        "WARNING": 13,
        "ERROR": 17,
        "CRITICAL": 21,
    }
    return severity_map.get(severity_text.upper())
