import uvicorn
import sys
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from service.settings import config

def configure_app():
    logger.info(f"Using Config ${config.ENV}")
    app = FastAPI(docs_url="/api/v1/docs")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    return app

if __name__ == "__main__":
    logger.info(f"Starting {config.SERVICE_NAME}")
    app = configure_app()
    uvicorn.run("app:configure_app", host="0.0.0.0", reload=True,
                log_level="debug", factory=True)