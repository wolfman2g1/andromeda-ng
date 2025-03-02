from loguru import logger
from andromeda_ng.service.models import Contact, Customer
from andromeda_ng.service.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from andromeda_ng.service.schema import ContactSchema, ContactOutput
import uuid


async def create_contact(db: Session, contact_data: ContactSchema):
    try:
        contact_data.contact_email = contact_data.contact_email.lower()
        check_contact = db.query(Contact).filter(
            Contact.contact_email == contact_data.contact_email).first()
        if check_contact:
            logger.error("Contact already exists")
            return {"error": "Contact already exists"}
        new_contact = Contact(**contact_data.dict())
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        db.rollback()
        return {"error": "Error creating contact"}


async def read_contacts(db: Session):
    try:
        contacts = db.query(Contact).options(
            joinedload(Contact.customer)).all()
        logger.info(f"Returning all contacts: {len(contacts)}")
        return contacts
    except Exception as e:  # pragma: no cover
        logger.error(f"Error reading contacts: {e}")
        return {"error": "Error reading contacts"}


async def read_contact_by_id(db: Session, contact_id: uuid.UUID):
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        return contact
    except Exception as e:
        logger.error(f"Error reading contact: {e}")
        return {"error": "Error reading contact"}


async def update_contact(db: Session, contact_id: uuid.UUID, contact_data: ContactSchema):
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            logger.error(f"Contact not found with id: {contact_id}")
            return {"error": "Contact not found"}
        contact.update(contact_data.dict(exclude_unset=True))
        db.commit()
        logger.info(f"Contact updated: {contact_id}")
        return contact
    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        db.rollback()
        return {"error": "Error updating contact"}


async def delete_contact(db: Session, contact_id: uuid.UUID):
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            logger.error(f"Contact not found with id: {contact_id}")
            return {"error": "Contact not found"}
        db.delete(contact)
        db.commit()
        logger.info(f"Contact deleted: {contact_id}")
        return contact
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        db.rollback()
        return {"error": "Error deleting contact"}


async def read_contact_by_email(db: Session, contact_email: str):
    try:
        contact_email = contact_email.lower()
        contact = db.query(Contact).filter(
            Contact.contact_email == contact_email).first()
        if not contact:
            logger.error(f"Contact not found with email: {contact_email}")
            return False
        logger.info(
            f"Found contact by email: {contact_email} - {contact.id} ({contact.contact_name})")
        return contact
    except Exception as e:
        logger.error(f"Error reading contact: {e}")
        return {"error": "Error reading contact"}
