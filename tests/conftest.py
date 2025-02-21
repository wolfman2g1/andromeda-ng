# conftest.py
from unittest.mock import MagicMock, create_autospec
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from andromeda_ng.app import configure_app
from andromeda_ng.service.database import get_db
from sqlalchemy.orm.query import Query 
@pytest.fixture
def mock_db_session():
    # Create a more detailed mock session
    session = create_autospec(Session)
    mock_query = create_autospec(Query)
    session.query.return_value = mock_query
    
    # Configure the mock to track calls and return values
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()

    
    return session

@pytest.fixture
def test_app(mock_db_session):
    app = configure_app()
    
    # Override the database dependency
    def override_get_db():
        yield mock_db_session
        
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture
def test_client(test_app):
    return TestClient(test_app)