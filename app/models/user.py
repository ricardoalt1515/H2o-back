from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
import uuid


class UserBase(BaseModel):
    """Campos base para el usuario"""

    email: EmailStr
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None


class UserCreate(UserBase):
    """Modelo para crear un usuario (incluye contraseña)"""

    password: str


class UserInDB(UserBase):
    """Modelo para almacenar usuario (incluye id, hash y creación)"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase):
    """Modelo público de usuario (sin datos sensibles)"""

    id: str
    created_at: datetime


class TokenData(BaseModel):
    """Datos para generar y validar tokens"""

    access_token: str
    token_type: str
    user_id: str
    expires_at: datetime


class LoginRequest(BaseModel):
    """Datos para inicio de sesión"""

    email: EmailStr
    password: str
