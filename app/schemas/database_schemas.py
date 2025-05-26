from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Esquemas para User
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserDB(UserBase):
    id: UUID
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


# Esquemas para Conversation
class ConversationBase(BaseModel):
    selected_sector: Optional[str] = None
    selected_subsector: Optional[str] = None
    current_question_id: Optional[str] = None
    is_complete: bool = False
    has_proposal: bool = False
    client_name: str = "Cliente"
    proposal_text: Optional[str] = None
    pdf_path: Optional[str] = None


class ConversationCreate(ConversationBase):
    user_id: Optional[UUID] = None


class ConversationUpdate(ConversationBase):
    pass


class ConversationDB(ConversationBase):
    id: UUID
    created_at: datetime
    user_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# Esquemas para Message
class MessageBase(BaseModel):
    role: str
    content: str


class MessageCreate(MessageBase):
    conversation_id: UUID


class MessageUpdate(MessageBase):
    pass


class MessageDB(MessageBase):
    id: UUID
    created_at: datetime
    conversation_id: UUID

    class Config:
        from_attributes = True


# Esquemas para ConversationMetadata
class MetadataBase(BaseModel):
    key: str
    value: Dict[str, Any]


class MetadataCreate(MetadataBase):
    conversation_id: UUID


class MetadataUpdate(MetadataBase):
    pass


class MetadataDB(MetadataBase):
    id: UUID
    created_at: datetime
    conversation_id: UUID

    class Config:
        from_attributes = True


# Esquemas para Document
class DocumentBase(BaseModel):
    filename: str
    file_path: str
    content_type: Optional[str] = None
    processed_text: Optional[str] = None


class DocumentCreate(DocumentBase):
    conversation_id: UUID


class DocumentUpdate(DocumentBase):
    pass


class DocumentDB(DocumentBase):
    id: UUID
    created_at: datetime
    conversation_id: UUID

    class Config:
        from_attributes = True
