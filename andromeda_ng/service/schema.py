from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
class LeadSchema(BaseModel):
    lead_first_name: str
    lead_last_name: str
    lead_email: EmailStr
    lead_phone: str
    lead_message: Optional[str] = None
    lead_company: str
    lead_website: Optional[str] = None
    lead_status: Optional[str] = None
class LeadOutput(BaseModel):
    id: UUID
    lead_first_name: str
    lead_last_name: str
    lead_email: EmailStr
    lead_phone: str
    lead_message: str
    lead_company: str
    lead_website: str
    lead_status: str
    lead_converted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:  # Important for handling SQLAlchemy objects
        orm_mode = True  # Tell Pydantic to read data from ORM objects

