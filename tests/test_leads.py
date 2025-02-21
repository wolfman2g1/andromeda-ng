from unittest.mock import MagicMock
from uuid import uuid4
from andromeda_ng.service.schema import LeadOutput,LeadSchema
from datetime import datetime


lead = {
    "id": str(uuid4()),
    "lead_first_name": "Emily",
    "lead_last_name": "Davis",
    "lead_email": "emily.6davis@example.com",
    "lead_phone": "+1-555-4321",
    "lead_message": "Looking for pricing details.",
    "lead_company": "Delta LLC",
    "lead_website": "https://www.deltallc.com",
    "lead_status": "Qualified",
    "lead_converted": False,
    "created_at": datetime(2021, 7, 1, 12, 0, 0).isoformat(),
    "updated_at": None
}
create_lead =  {
    "id": str(uuid4()),
    "lead_first_name": "Emily",
    "lead_last_name": "Davis",
    "lead_email": "emily.6davis@example.com",
    "lead_phone": "+1-555-4321",
    "lead_message": "Looking for pricing details.",
    "lead_company": "Delta LLC",
    "lead_website": "https://www.deltallc.com",
    "lead_status": "Qualified",
    "lead_converted": False,
}



def test_ping(test_client):
    response = test_client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "PONG!"}

def test_create_lead(test_client, mock_db_session):
    lead_data = {k: v for k, v in create_lead.items() if k != "id"}

     #configure the mock add method to return the mock Lead
    mock_db_session.add.return_value = LeadSchema(**lead_data)
    # configure the mock commit method
    mock_db_session.commit.return_value = None
    # configure the mock refresh method
    mock_db_session.refresh.return_value = LeadSchema(**lead_data)
    response = test_client.post("/api/v1/leads/", json=lead_data)
    assert response.status_code == 201
    assert response.json() == lead_data
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

#def test_get_leads(test_client, mock_db_session):
#    # Create a mock Lead object that matches your model
#    mock_lead = LeadOutput(**lead)
#    for key, value in lead.items():
#        setattr(mock_lead, key, value)
#    # Configure the mock query to return the mock Lead
#    mock_query = MagicMock()
#    mock_query.all.return_value = [mock_lead]
#    mock_db_session.query.return_value = mock_query
#
#
#    response = test_client.get("/api/v1/leads/")
#    assert response.status_code == 200
#    response_data = response.json()
#    assert len(response_data) == 1
#    response_lead = response_data[0]
#    #assert response_lead["lead_first_name"] == lead["lead_first_name"]
#    #assert response_lead["lead_last_name"] == lead["lead_last_name"]
#    #assert response_lead["lead_email"] == lead["lead_email"]
#    #assert response_lead["lead_phone"] == lead["lead_phone"]
#    #assert response_lead["lead_message"] == lead["lead_message"]
#    #assert response_lead["lead_company"] == lead["lead_company"]
#    #assert response_lead["lead_website"] == lead["lead_website"]
#    #assert response_lead["lead_status"] == lead["lead_status"]
#    #assert response_lead["lead_converted"] == lead["lead_converted"]
#    #response_lead["created_at"] = datetime.fromisoformat(response_lead["created_at"].replace("Z", "+00:00"))
#    mock_db_session.query.assert_called_once()