from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()


class BaseModel:
    """Modelo base con ID UUID y timestamp de creación"""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RoleEnum(enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
