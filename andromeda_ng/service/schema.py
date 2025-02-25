from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


# 1️⃣ ENUM DEFINITION
class Status(str, Enum):
    New = "New"
    Qualified = "Qualified"
    Archived = "Archived"


class CustomerBasic(BaseModel):
    id: UUID
    customer_name: str

    class Config:
        from_attributes = True


# 2️⃣ INPUT MODELS (Schemas)
class LeadSchema(BaseModel):
    lead_first_name: str
    lead_last_name: str
    lead_email: EmailStr
    lead_phone: str
    lead_message: Optional[str] = None
    lead_company: str
    lead_website: Optional[str] = None
    lead_converted: Optional[bool] = False

    class Config:
        from_attributes = True


class ContactSchema(BaseModel):
    contact_first_name: str
    contact_last_name: str
    contact_email: EmailStr
    customer_id: UUID

    class Config:
        from_attributes = True


class CustomerSchema(BaseModel):
    customer_name: str
    customer_phone: str
    customer_street: str
    customer_city: str
    customer_state: str
    customer_postal: str
    customer_website: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


class CustomerOutput(BaseModel):
    id: UUID
    customer_name: str
    customer_phone: str
    customer_street: str
    customer_city: str
    customer_state: str
    customer_postal: str
    customer_website: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    children: Optional[List["ContactOutput"]] = None

    class Config:
        from_attributes = True


class ContactOutput(BaseModel):
    id: UUID
    contact_first_name: str
    contact_last_name: str
    contact_email: EmailStr
    customer_id: UUID
    customer: Optional[CustomerBasic] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadOutput(BaseModel):
    id: UUID
    lead_first_name: str
    lead_last_name: str
    lead_email: EmailStr
    lead_phone: str
    lead_message: Optional[str] = None
    lead_company: str
    lead_website: Optional[str] = None
    lead_status: str
    lead_converted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


CustomerOutput.model_rebuild()
ContactOutput.model_rebuild()
CustomerBasic.model_rebuild()
