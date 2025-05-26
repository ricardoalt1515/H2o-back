from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.declarations import Base, BaseModel, RoleEnum


class Message(Base, BaseModel):
    """Modelo SQLAlchemy para mensajes"""

    __tablename__ = "messages"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    role = Column(Enum(RoleEnum, name="role_enum_type"), nullable=False)
    content = Column(Text, nullable=False)

    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")
