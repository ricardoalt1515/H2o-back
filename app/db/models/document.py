from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.declarations import Base, BaseModel


class Document(Base, BaseModel):
    """Modelo SQLAlchemy para documentos subidos"""

    __tablename__ = "documents"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    processed_text = Column(Text, nullable=True)

    # Relaciones
    conversation = relationship("Conversation", back_populates="documents")
