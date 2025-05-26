from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.models.declarations import Base, BaseModel


class ConversationMetadata(Base, BaseModel):
    """Modelo SQLAlchemy para metadatos de conversación"""

    __tablename__ = "conversation_metadata"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    key = Column(String(255), nullable=False)
    value = Column(JSONB, nullable=True)

    # Relaciones
    conversation = relationship("Conversation", back_populates="metadata_items")

    # Índice compuesto para optimizar la búsqueda
    __table_args__ = ({"sqlite_autoincrement": True},)
