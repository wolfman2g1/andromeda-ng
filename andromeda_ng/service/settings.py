from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):

    # production settings
    SERVICE_NAME: str
    ENV: str
    DB_HOST: str
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str
    DB_PORT: Optional[str] = 5432
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_SECRET_KEY: SecretStr

    # testing settings
    TEST_DB_HOST: Optional[str]
    TEST_DB_USER: Optional[str]
    TEST_DB_PASS: Optional[SecretStr]
    TEST_DB_NAME: Optional[str]
    TEST_DB_PORT: Optional[str] = 5432

    class Config:
        env_file = ".env"


@lru_cache
def get_config():
    return Settings()


config = get_config()
