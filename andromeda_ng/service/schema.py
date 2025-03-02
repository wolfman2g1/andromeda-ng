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
    notes: Optional[List["NoteOutput"]] = None
    customer_tickets: Optional[dict] = None
    ticket_count: Optional[int] = None
    open_tickets: Optional[int] = None
    ticket_url: Optional[str] = None

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


class NoteSchema(BaseModel):
    note_title: str
    note_content: str
    customer_id: UUID

    class Config:
        from_attributes = True


class NoteOutput(BaseModel):
    id: UUID
    note_title: str
    note_content: str
    customer_id: UUID
    created_at: datetime


### User Schema ###
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str  # NOT HASHED IN SCHEMA STILL PLAIN TEXT
    admin: bool
    is_active: bool = False

    class Config:
        from_attributes = True


class UserOutput(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str
    id: UUID
    admin: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    username: str
    admin: bool


class Login(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    token: str
    new_password: str


class ZammadCompany(BaseModel):
    name: str
    shared: bool = False
    domain: Optional[str] = None
    domain_assignment: Optional[str] = True
    note: Optional[str] = None
    vip: bool = False


CustomerOutput.model_rebuild()
ContactOutput.model_rebuild()
CustomerBasic.model_rebuild()
