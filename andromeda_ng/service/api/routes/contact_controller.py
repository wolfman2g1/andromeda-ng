from fastapi import status, APIRouter, Depends, HTTPException
from typing import List, Optional
from loguru import logger
import uuid
from andromeda_ng.service.schema import ContactSchema, ContactOutput
from andromeda_ng.service.crud import contact_service, customer_service
from andromeda_ng.service.database import get_db

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])


@router.post("/", response_model=ContactOutput, status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactSchema, db=Depends(get_db)):
    try:

        # check if customer exists
        check_customer = customer_service.read_customer_by_id(
            db, contact_data.customer_id)
        if not check_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        if not contact_data.customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a valid customer id")
        contact_data.contact_email = contact_data.contact_email.lower()
        check_contact = await contact_service.read_contact_by_email(db, contact_data.contact_email)
        if check_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Contact already exists")
        contact = await contact_service.create_contact(db, contact_data)

        logger.info(f"Contact created: {contact.id}")
        return contact
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/", response_model=List[ContactOutput], status_code=status.HTTP_200_OK)
async def read_contacts(db=Depends(get_db)):
    try:
        contacts = await contact_service.read_contacts(db)
        contacts = [ContactOutput.model_validate(
            contact) for contact in contacts]
        return contacts
    except Exception as e:
        logger.error(f"Error reading contacts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/{contact_id}", response_model=ContactOutput, status_code=status.HTTP_200_OK)
async def read_contact_by_id(contact_id: uuid.UUID, db=Depends(get_db)):
    try:
        contact = await contact_service.read_contact_by_id(db, contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
        return contact
    except Exception as e:
        logger.error(f"Error reading contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.put("/{contact_id}", response_model=ContactOutput, status_code=status.HTTP_200_OK)
async def update_contact(contact_id: uuid.UUID, contact_data: ContactSchema, db=Depends(get_db)):
    try:
        check_contact = await contact_service.read_contact_by_id(db, contact_id)
        if not check_contact:
            logger.error(f"Contact not found with id: {contact_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
        updated_contact = await contact_service.update_contact(db, contact_id, contact_data)
        return updated_contact
    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: uuid.UUID, db=Depends(get_db)):
    try:
        check_contact = await contact_service.read_contact_by_id(db, contact_id)
        if not check_contact:
            logger.error(f"Contact not found with id: {contact_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
        await contact_service.delete_contact(db, contact_id)
        return
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")
