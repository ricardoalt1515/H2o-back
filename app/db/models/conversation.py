from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.declarations import Base, BaseModel


class Conversation(Base, BaseModel):
    """Modelo SQLAlchemy para conversaciones"""

    __tablename__ = "conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    selected_sector = Column(String(100), nullable=True)
    selected_subsector = Column(String(100), nullable=True)
    current_question_id = Column(String(100), nullable=True)
    is_complete = Column(Boolean, default=False)
    has_proposal = Column(Boolean, default=False)
    client_name = Column(String(255), default="Cliente")
    proposal_text = Column(Text, nullable=True)
    pdf_path = Column(String(255), nullable=True)

    # Relaciones - usar strings para evitar referencias circulares
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    metadata_items = relationship(
        "ConversationMetadata",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    documents = relationship(
        "Document", back_populates="conversation", cascade="all, delete-orphan"
    )
