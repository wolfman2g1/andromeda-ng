from loguru import logger
from andromeda_ng.service.models import Lead, Customer, Contact
from andromeda_ng.service.database import get_db
from sqlalchemy.orm import Session
from andromeda_ng.service.schema import LeadSchema
from andromeda_ng.service.libs import zammad
import uuid


async def create_lead(db: Session, lead_data: LeadSchema):
    check_lead = db.query(Lead).filter(
        Lead.lead_email == lead_data.lead_email).first()
    if check_lead:
        logger.error("Lead already exists")
        return {"error": "Lead already exists"}
    try:
        new_lead = Lead(**lead_data.dict())
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        return new_lead
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        db.rollback()
        return {"error": "Error creating lead"}


async def read_leads(db: Session):
    try:
        leads = db.query(Lead).all()
        return leads
    except Exception as e:
        logger.error(f"Error reading leads: {e}")
        return {"error": "Error reading leads"}


async def read_lead_by_id(db: Session, lead_id: uuid.UUID):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        return lead
    except Exception as e:
        logger.error(f"Error reading lead: {e}")
        return {"error": "Error reading lead"}


async def read_lead_by_email(db: Session, lead_email: str):
    try:
        lead = db.query(Lead).filter(Lead.lead_email == lead_email).first()
        return lead
    except Exception as e:
        logger.error(f"Error reading lead: {e}")
        return {"error": "Error reading lead"}


async def update_lead(db: Session, lead_id: uuid.UUID, lead_data: LeadSchema):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"error": "Lead not found"}
        update_lead = lead.update(lead_data.dict())
        db.commit()
        db.refresh(update_lead)
        if not update_lead:
            return {"error": "Error updating lead"}
        logger.info(f"Lead updated: {lead_id}")
        return update_lead
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        db.rollback()
        return {"error": "Error updating lead"}


async def delete_lead(db: Session, lead_id: uuid.UUID):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"error": "Lead not found"}
        db.delete(lead)
        db.commit()
        logger.info(f"Lead deleted: {lead_id}")
        return {"message": "Lead deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting lead: {e}")
        db.rollback()
        return {"error": "Error deleting lead"}

# take the lead id then convert the lead to a customerin zammad


async def convert_lead_to_customer(db: Session, lead_id: uuid.UUID):
    try:
        # Get lead from database
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"error": "Lead not found"}

        # Create organization in Zammad using zammad-py client
        zammad_org = {
            "name": lead.lead_company,
            "phones": lead.lead_phone,
            "web": lead.lead_website,
            "active": True
        }

        # Create organization using zammad client
        customer = await zammad.create_organization(zammad_org)
        if not customer:
            return {"error": "Error creating organization in Zammad"}
        # zammad user creation
        user = {
            "login": lead.lead_email,
            "firstname": lead.lead_first_name,
            "lastname": lead.lead_last_name,
            "email": lead.lead_email,
            "phone": lead.lead_phone,
            "organization_id": customer["id"],
            "roles": ["Customer"],
            "active": True
        }
        zammad_user = await zammad.create_user(user, customer["id"])
        if not zammad_user:
            return {"error": "Error creating user in Zammad"}
        # Update lead status
        lead.lead_converted = True
        db.commit()
        db.refresh(lead)

        # Create local customer record
        new_customer = {
            "customer_name": lead.lead_company,
            "customer_phone": lead.lead_phone,
            "customer_street": "",
            "customer_city": "",
            "customer_state": "",
            "customer_postal": "",
            "customer_website": lead.lead_website,
            "is_active": True,
            "zammad_id": customer["id"]  # Get ID from Zammad response
        }
        create_customer = Customer(**new_customer)
        db.add(create_customer)
        db.commit()
        db.refresh(create_customer)

        # Create contact record
        new_contact = {
            "contact_first_name": lead.lead_first_name,
            "contact_last_name": lead.lead_last_name,
            "contact_email": lead.lead_email,
            "customer_id": create_customer.id
        }
        create_contact = Contact(**new_contact)
        db.add(create_contact)
        db.commit()
        db.refresh(create_contact)

        logger.info(
            f"Converted Lead Contact {lead.lead_first_name} "
            f"{lead.lead_last_name} to Contact for Customer: "
            f"{create_customer.customer_name}"
        )
        return {"message": "Lead converted to customer successfully"}

    except Exception as e:
        logger.error(f"Error converting lead to customer: {e}")
        db.rollback()
        return {"error": f"Error converting lead to customer: {str(e)}"}
