from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    SERVICE_NAME: str
    ENV: str
    DB_HOST: str
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str
    DB_PORT: Optional[str] = 5432
    
    
    class Config:
        env_file = ".env"
@lru_cache
def get_config():
    return Settings()

config = get_config()