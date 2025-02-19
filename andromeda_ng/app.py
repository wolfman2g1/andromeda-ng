import uvicorn
import sys
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from service.settings import config
from alembic import command
from alembic.config import Config
from andromeda_ng.service.database import get_db


## Routes
from andromeda_ng.service.ping import router as ping_router

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
    @app.on_event("startup")
    async def startup_event():  # Combined startup event
        logger.info("Starting application...")

        try:
            # 1. Run Migrations First
            logger.info("Running database migrations...")
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations complete.")

            # 2. Then, Establish Database Connection
            logger.info("Connecting to database...")
            db_gen = get_db()
            db = next(db_gen)  # Get the session
            # Optional: Test the connection
            # await db.execute("SELECT 1")
            logger.info("Database connection established.")


        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise  # Re-raise to prevent app startup

        finally: # Important to close the session in finally block
            try:
                db.close()
                logger.info("Database session closed")
            except Exception as e:
                logger.error(f"Error closing session: {e}")
    app.include_router(ping_router)
    return app

if __name__ == "__main__":
    logger.info(f"Starting {config.SERVICE_NAME}")
    app = configure_app()
    uvicorn.run("app:configure_app", host="0.0.0.0", reload=True,
                log_level="debug", factory=True)