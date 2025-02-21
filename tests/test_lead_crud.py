import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from andromeda_ng.service.crud.lead_crud import delete_lead
from andromeda_ng.service.models import Lead
import uuid
from andromeda_ng.service.settings import config

# Load environment variables from .env file
TEST_DB_USER = config.TEST_DB_USER
TEST_DB_PASS = config.TEST_DB_PASS.get_secret_value()
TEST_DB_HOST = config.TEST_DB_HOST
TEST_DB_PORT = config.TEST_DB_PORT
TEST_DB_NAME = config.TEST_DB_NAME

Base = declarative_base()

# Use asyncpg for async PostgreSQL operations
TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        async with session.begin():
            yield session

@pytest_asyncio.fixture
async def test_lead(db_session):
    lead = Lead(
        lead_email="test@example.com",
        lead_first_name="Test",
        lead_last_name="Lead",
        lead_company="Test Company",
        lead_phone="123-456-7890",
        lead_converted=False
    )
    db_session.add(lead)
    await db_session.commit()
    return lead