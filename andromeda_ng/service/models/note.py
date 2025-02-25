from sqlalchemy import Column, UUID, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from andromeda_ng.service.base import Base
import uuid


class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid4)
    note_title = Column(String, nullable=False)
    note_content = Column(String, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="notes")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def customer_name(self):
        return self.customer.customer_name if self.customer else None
