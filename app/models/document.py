# app/models/document.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class Document(BaseModel):
    """Modelo que representa un documento subido"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    filename: str
    file_path: str
    content_type: Optional[str] = None
    processed_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
