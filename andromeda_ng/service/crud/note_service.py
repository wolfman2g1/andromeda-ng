from loguru import logger
from andromeda_ng.service.models import Note
from andromeda_ng.service.database import get_db
from sqlalchemy.orm import Session
from andromeda_ng.service.schema import NoteOutput, NoteSchema
import uuid


async def create_note(db: Session, note_data: NoteSchema):
    try:
        new_note = Note(**note_data.dict())
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        logger.info(f"Note created: {new_note.id}")
        return new_note
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        db.rollback()
        return {"error": "Error creating note"}


async def read_notes(db: Session):
    try:
        notes = db.query(Note).all()
        return notes
    except Exception as e:
        logger.error(f"Error reading notes: {e}")
        return {"error": "Error reading notes"}


async def read_note_by_id(db: Session, note_id: uuid.UUID):
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        return note
    except Exception as e:
        logger.error(f"Error reading note: {e}")
        return {"error": "Error reading note"}


async def update_note(db: Session, note_id: uuid.UUID, note_data: NoteSchema):
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            logger.error(f"Note not found with id: {note_id}")
            return {"error": "Note not found"}
        note.update(note_data.dict(exclude_unset=True))
        db.commit()
        logger.info(f"Note updated: {note_id}")
        return note
    except Exception as e:
        logger.error(f"Error updating note: {e}")
        return {"error": "Error updating note"}
