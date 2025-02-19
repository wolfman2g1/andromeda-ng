from loguru import logger

from fastapi import APIRouter


router = APIRouter(prefix="/api/v1", tags=["healthcheck"])


@router.get("/ping")
def pong():
    """ This endpoint will return a JSON object to test that the app is working"""
    return {"message": "PONG!"}