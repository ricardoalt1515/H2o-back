# app/models/message.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional  # Asegúrate que Optional esté importado
import uuid


class Message(BaseModel):
    """Representa un único mensaje dentro de una conversación."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Quitar conversation_id de aquí si no lo usas o mantenerlo si lo necesitas
    # conversation_id: Optional[str] = None
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Otros campos opcionales como 'metadata', 'token_count', etc. podrían ir aquí

    @classmethod
    def user(cls, content: str):
        """Método de fábrica para crear un mensaje de usuario."""
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str):
        """Método de fábrica para crear un mensaje de asistente."""
        return cls(role="assistant", content=content)

    class Config:
        pass  # Permite modificar el objeto después de crearlo


# --- AÑADIR ESTA CLASE AQUÍ ---
class MessageCreate(BaseModel):
    """
    Modelo Pydantic para validar el cuerpo de la solicitud
    cuando un usuario envía un nuevo mensaje.
    """

    conversation_id: str
    message: str
    # Puedes añadir otros campos si tu frontend los envía,
    # por ejemplo: user_id, session_id, etc.


# -----------------------------
