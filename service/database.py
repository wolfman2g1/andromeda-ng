from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from service.settings import config


SQLALCHEMY_DATABASE_URL = f"postgresql://{config.DB_USER}:{config.DB_PASS.get_secret_value()}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, future=True, echo=True
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()