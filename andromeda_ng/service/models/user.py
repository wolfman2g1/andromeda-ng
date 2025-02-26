from sqlalchemy import Column, UUID, String, DateTime,  Boolean
from sqlalchemy.sql import func
from andromeda_ng.service.base import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    admin = Column(Boolean, default=False)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())
