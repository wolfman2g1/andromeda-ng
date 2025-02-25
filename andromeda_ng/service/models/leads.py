from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLAlchemyEnum
from andromeda_ng.service.base import Base
import uuid
#from enum import Enum
#class Status(str, Enum):
#    NEW = "New"
#    CONTACTED = "Contacted"
#    QUALIFIED = "Qualified"
#    PROPOSAL = "Proposal"
#    NEGOTIATION = "Negotiation"
#    CLOSED_WON = "Closed Won"
#    CLOSED_LOST = "Closed Lost"

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
    lead_status = Column(String, default="New", index=True)
    lead_converted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    