from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.sql import func
from andromeda_ng.service.base import Base
import uuid

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    lead_first_name = Column(String, nullable=False, index=True)
    lead_last_name = Column(String, nullable=False, index=True)
    lead_email = Column(String, nullable=False, index=True)
    lead_phone = Column(String, nullable=False, index=True)
    lead_message = Column(String)
    lead_company = Column(String, nullable=False, index=True)
    lead_website = Column(String, index=True)
    lead_status = Column(String, index=True)
    lead_converted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    