# andromeda_ng/app.py
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config
from .service.database import get_db
from .service.settings import config
from .service.ping import router as ping_router

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

    app.include_router(ping_router)
    return app

# Create the app instance
app = configure_app()

# main.py
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {config.SERVICE_NAME}")
    uvicorn.run("andromeda_ng.app:app", host="0.0.0.0", reload=True, log_level="debug")