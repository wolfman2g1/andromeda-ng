# andromeda_ng/app.py
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config
from .service.database import get_db, engine
from .service.settings import config
from .service.ping import router as ping_router
from andromeda_ng.service.api.routes import leads_controller, customers_controller, contact_controller, notes_controller, users_controller, auth_controller
from andromeda_ng.service.utils.telemetry import configure_telemetry


def configure_app():
    logger.info(f"Using Config {config.ENV}")
    app = FastAPI(docs_url="/api/v1/docs")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Configure OpenTelemetry if enabled
    telemetry = configure_telemetry(app=app, db_engine=engine)
    app.state.telemetry = telemetry

    if telemetry.get("enabled", False):
        logger.info(
            f"OpenTelemetry is enabled. Exporting to Tempo: {config.TEMPO_ENDPOINT}, Loki: {config.LOKI_ENDPOINT}")
    else:
        logger.info(
            "OpenTelemetry is disabled. Set TELEMETRY_ENABLED=True to enable.")

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting application...")
        try:
            # Run Migrations First
            logger.info("Running database migrations...")
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations complete.")
            # Establish Database Connection
            logger.info("Connecting to database...")
            db_gen = get_db()
            db = next(db_gen)
            logger.info("Database connection established.")
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
        finally:
            try:
                db.close()
                logger.info("Database session closed")
            except Exception as e:
                logger.error(f"Error closing session: {e}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application...")
        # Force flush any pending telemetry data
        if hasattr(app.state, "telemetry"):
            try:
                trace_provider = app.state.telemetry.get("trace_provider")
                if trace_provider:
                    trace_provider.shutdown()

                logger_provider = app.state.telemetry.get("logger_provider")
                if logger_provider:
                    logger_provider.shutdown()

                logger.info("Telemetry shutdown complete")
            except Exception as e:
                logger.error(f"Error during telemetry shutdown: {e}")

    app.include_router(ping_router)
    app.include_router(leads_controller.router)
    app.include_router(customers_controller.router)
    app.include_router(contact_controller.router)
    app.include_router(notes_controller.router)
    app.include_router(users_controller.router)
    app.include_router(auth_controller.router)
    return app


# Create the app instance
app = configure_app()

# main.py
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {config.SERVICE_NAME}")
    uvicorn.run("andromeda_ng.app:app", host="0.0.0.0",
                reload=True, log_level="debug")
