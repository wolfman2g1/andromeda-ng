from uuid import uuid4
from datetime import datetime
from andromeda_ng.service.schema import LeadOutput, LeadSchema
from andromeda_ng.service.models import Lead

# Test data fixtures
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


create_lead = {
    "lead_first_name": "John",
    "lead_last_name": "Doe",
    "lead_email": "john.doe@example.com",
    "lead_phone": "+1-555-1234",
    "lead_message": "I'm interested in your services.",
    "lead_company": "Acme Inc.",
    "lead_website": "https://www.acme.com",
    "lead_status": "New"
}

def test_ping(test_client):
    response = test_client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "PONG!"}

def test_create_lead(test_client, test_db):

    
    # Make the API request to create a lead
    response = test_client.post("/api/v1/leads/", json=create_lead)
    print("Response status:", response.status_code)
    print("Response body:", response.json())
    
    # Check response

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["lead_first_name"] == create_lead["lead_first_name"]
  

#def test_create_lead_already_exists(test_client, test_db):
#    # First, create a lead
#    lead_data = {k: v for k, v in create_lead.items() if k != "id"}
#    existing_lead = Lead(**lead_data)
#    test_db.add(existing_lead)
#    test_db.commit()
#    
#    # Try to create the same lead again
#    response = test_client.post("/api/v1/leads/", json=lead_data)
#    
#    # Verify the response
#    assert response.status_code == 400
#    assert response.json() == {"detail": "Lead already exists"}
#    
#    # Verify only one lead exists in the database
#    lead_count = test_db.query(Lead).filter(
#        LeadSchema.lead_email == lead_data["lead_email"]
#    ).count()
#    assert lead_count == 1
#
#def test_create_lead_no_email(test_client, test_db):
#    # Create lead data without email
#    lead_data = {k: v for k, v in create_lead.items() if k != "id"}
#    lead_data["lead_email"] = None
#    
#    # Try to create lead without email
#    response = test_client.post("/api/v1/leads/", json=lead_data)
#    
#    # Verify response
#    assert response.status_code == 422
#    
#    # Verify no lead was created in the database
#    lead_count = test_db.query(Lead).count()
#    assert lead_count == 0