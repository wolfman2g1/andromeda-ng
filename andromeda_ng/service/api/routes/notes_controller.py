from fastapi import status, APIRouter, Depends, HTTPException
from typing import List, Optional
from loguru import logger
import uuid
from andromeda_ng.service.schema import NoteOutput, NoteSchema
from andromeda_ng.service.crud import note_service, customer_service
from andromeda_ng.service.database import get_db

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.post("/", response_model=NoteOutput, status_code=status.HTTP_201_CREATED)
async def create_note(note_data: NoteSchema, db=Depends(get_db)):
    try:
        # check if customer exists
        check_company = await customer_service.read_customer_by_id(db, note_data.customer_id)
        if not check_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        if not note_data.customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a valid customer id")
        note = await note_service.create_note(db, note_data)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Please check your input data")
        logger.info(f"Note created: {note.id}")
        return note
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/", response_model=List[NoteOutput], status_code=status.HTTP_200_OK)
async def read_notes(db=Depends(get_db)):
    try:
        notes = await note_service.read_notes(db)
        notes = [NoteOutput.model_validate(
            note) for note in notes]
        return notes
    except Exception as e:
        logger.error(f"Error reading notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/{note_id}", response_model=NoteOutput, status_code=status.HTTP_200_OK)
async def read_note_by_id(note_id: uuid.UUID, db=Depends(get_db)):
    try:
        note = await note_service.read_note_by_id(db, note_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note
    except Exception as e:
        logger.error(f"Error reading note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.put("/{note_id}", response_model=NoteOutput, status_code=status.HTTP_200_OK)
async def update_note(note_id: uuid.UUID, note_data: NoteSchema, db=Depends(get_db)):
    """Update a note by ID."""
    try:
        note = await note_service.update_note(db, note_id, note_data)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note
    except Exception as e:
        logger.error(f"Error updating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")
