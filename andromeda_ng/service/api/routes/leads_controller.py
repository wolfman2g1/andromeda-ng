from fastapi import status, APIRouter, Depends, HTTPException
from typing import List, Optional
from loguru import logger
import uuid
from andromeda_ng.service.schema import LeadSchema, LeadOutput
from andromeda_ng.service.crud import lead_service
from andromeda_ng.service.database import get_db

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])


@router.post("/", response_model=LeadSchema, status_code=status.HTTP_201_CREATED)
async def create_lead(lead_data: LeadSchema, db=Depends(get_db)):
    if not lead_data.lead_email:
        logger.error("Please provide a valid email address")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please provide a valid email address")
    # Normalize email to lowercase for case-insensitive search
    lead_data.lead_email = lead_data.lead_email.lower()
    # Check if lead already exists
    check_lead = await lead_service.read_lead_by_email(db, lead_data.lead_email)
    if check_lead:
        logger.error(f"Lead already exists with email: {lead_data.lead_email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Lead already exists")
    lead = await lead_service.create_lead(db, lead_data)
    if not lead:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please check your input data")
    return lead


@router.get("/", response_model=List[LeadOutput],  status_code=status.HTTP_200_OK)
async def read_leads(db=Depends(get_db)):
    try:
        logger.info("Reading leads")
        leads = await lead_service.read_leads(db)
        return leads
    except HTTPException as e:
        logger.error(f"Error reading leads: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error reading leads: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


@router.get("/{lead_id}", response_model=LeadOutput, status_code=status.HTTP_200_OK)
async def read_lead_by_id(lead_id: uuid.UUID, db=Depends(get_db)):
    try:
        lead = await lead_service.read_lead_by_id(db, lead_id)

        if not lead:
            logger.error(f"Lead not found with id: {lead_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        logger.infot("Found Lead id: {lead_id}")
        return lead
    except HTTPException as e:
        logger.error(f"Error reading lead: {e}")
        raise e


@router.put("/{lead_id}", response_model=LeadOutput, status_code=status.HTTP_200_OK)
async def update_lead(lead_id: uuid.UUID, lead_data: LeadSchema, db=Depends(get_db)):
    try:
        check_lead = await lead_service.read_lead_by_id(db, lead_id)
        if not check_lead:
            logger.error(f"Lead not found with id: {lead_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        updated_lead = await lead_service.update_lead(db, lead_id, lead_data)
        if not updated_lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Please check your input data")
        logger.info(f"Lead updated: {lead_id}")
        return updated_lead
    except HTTPException as e:
        logger.error(f"Error updating lead: {e}")
        raise e


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: uuid.UUID, db=Depends(get_db)):
    try:
        check_lead = await lead_service.read_lead_by_id(db, lead_id)
        if not check_lead:
            logger.error(f"Lead not found with id: {lead_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        await lead_service.delete_lead(db, lead_id)
        logger.info(f"Lead deleted: {lead_id}")
        return
    except HTTPException as e:
        logger.error(f"Error deleting lead: {e}")
        raise e
