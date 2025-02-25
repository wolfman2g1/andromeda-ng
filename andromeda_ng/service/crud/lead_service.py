from loguru import logger
from andromeda_ng.service.models import Lead
from andromeda_ng.service.database import get_db
from sqlalchemy.orm import Session
from andromeda_ng.service.schema import LeadSchema
import uuid

async def create_lead(db: Session, lead_data: LeadSchema):
    check_lead = db.query(Lead).filter(Lead.lead_email == lead_data.lead_email).first()
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
        update_lead  = lead.update(lead_data.dict())
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