from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from andromeda_ng.service.base import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    lead_first_name = Column(String, index=True)
    lead_last_name = Column(String, index=True)
    lead_email = Column(String, index=True)
    lead_phone = Column(String, index=True)
    lead_message = Column(String, index=True)
    lead_company = Column(String, index=True)
    lead_website = Column(String, index=True)
    lead_status = Column(String, index=True)
    lead_converted = Column(Boolean,default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
    