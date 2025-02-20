import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from andromeda_ng.service.crud.lead_crud import delete_lead
from andromeda_ng.service.models import Lead  # Make sure this imports your actual Lead model
import uuid
from andromeda_ng.service.settings import config


# Load environment variables from .env file

TEST_DB_USER = config.TEST_DB_USER
TEST_DB_PASS = config.TEST_DB_PASS.get_secret_value()
TEST_DB_HOST = config.TEST_DB_HOST
TEST_DB_PORT = config.TEST_DB_PORT
TEST_DB_NAME = config.TEST_DB_NAME
# Define a base for declarative models (if you haven't already)
Base = declarative_base()  # Or use your existing Base if you have one


# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

@pytest.fixture(scope="function")  # Scope is important!
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, echo=True)  # echo=False for cleaner output
    Base.metadata.create_all(engine)  # Create tables
    yield engine
    Base.metadata.drop_all(engine) # Drop all tables after the test
    engine.dispose() # Dispose of the engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin() # Start a transaction
    session = Session(bind=connection)
    yield session
    session.close() # Close the session
    transaction.rollback() # Rollback the transaction
    connection.close() # Close the connection


@pytest.fixture
def test_lead(db_session): # Inject the db_session
    lead = Lead(
        lead_email="test@example.com",
        lead_first_name="Test", # Add other required fields
        lead_last_name = "Lead",
        lead_company = "Test Company",
        lead_phone = "123-456-7890",
        lead_converted=False # add other required fields
    )
    db_session.add(lead)
    db_session.commit()
    return lead

@pytest.mark.asyncio
async def test_delete_lead_success(db_session, test_lead):
    response = await delete_lead(db_session, test_lead.id)

    assert response == {"message": "Lead deleted successfully"}
    assert db_session.query(Lead).filter(Lead.id == test_lead.id).first() is None

@pytest.mark.asyncio
async def test_delete_lead_not_found(db_session):
    non_existent_id = uuid.uuid4()

    response = await delete_lead(db_session, non_existent_id)

    assert response == {"error": "Lead not found"}

#Remove the Exception test. It's better to test database exceptions by making them occur
# in realistic conditions rather than mocking the query method.