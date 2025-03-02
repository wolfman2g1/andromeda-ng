from sqlalchemy import Column, UUID, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from andromeda_ng.service.base import Base
import uuid


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid4)
    customer_name = Column(String, nullable=False, index=True)
    customer_phone = Column(String, nullable=False, index=True)
    customer_street = Column(String, nullable=False)
    customer_city = Column(String, nullable=False)
    customer_state = Column(String, nullable=False)
    customer_postal = Column(String, nullable=False)
    customer_website = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    children = relationship("Contact", back_populates="customer")
    notes = relationship("Note", back_populates="customer")
    zammad_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid4)
    contact_first_name = Column(String, nullable=False)
    contact_last_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="children")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def customer_name(self):
        return self.customer.customer_name if self.customer else None
