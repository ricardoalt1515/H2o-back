from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.db.models.declarations import Base, BaseModel


class User(Base, BaseModel):
    """Modelo SQLAlchemy para usuarios"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    subsector = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relaciones - usar strings para evitar referencias circulares
    conversations = relationship("Conversation", back_populates="user", lazy="dynamic")
