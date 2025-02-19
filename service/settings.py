from functools import lru_cache

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str
    MONGO_URI: str
    
    @lru_cache
    class Config:
        env_file = ".env"
def get_config()
    return Settings()


config = get_config()