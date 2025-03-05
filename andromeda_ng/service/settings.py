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
    DB_PORT: Optional[int] = 5432
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_SECRET_KEY: SecretStr

    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[SecretStr] = None
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = 587
    MAIL_USE_TLS: bool = True
    MAIL_FROM: Optional[str] = None
    MAIL_CREDENTIALS: Optional[bool] = True
    FRONTEND_URL: Optional[str] = None

    # Zammad settings
    ZAMMAD_URL: Optional[str] = None
    ZAMMAD_TOKEN: Optional[SecretStr] = None

    # telemetry settings
    TEMPO_ENDPOINT: Optional[str]
    LOKI_ENDPOINT: Optional[str]
    TELEMETRY_ENABLED: bool = False

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
