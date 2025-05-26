# app/models/conversation.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from app.models.message import Message

# Quitar: from app.models.conversation_state import ConversationState


class Conversation(BaseModel):
    """Representa una conversación completa."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "current_question_id": None,
            "collected_data": {},
            "selected_sector": None,
            "selected_subsector": None,
            "questionnaire_path": [],  # Podemos seguir usando esto para referencia
            "is_complete": False,
            "has_proposal": False,
            "proposal_text": None,
            "pdf_path": None,
            "client_name": "Cliente",
            "last_error": None,
            "user_location": None,
        }
    )
    # --------------------------------------

    def add_message(self, message: Message):
        """Añade un mensaje a la conversación."""
        self.messages.append(message)
        # Limitar historial si es necesario? (Opcional)
        # MAX_HISTORY = 20
        # if len(self.messages) > MAX_HISTORY:
        #     self.messages = self.messages[-MAX_HISTORY:]

    class Config:
        pass


# Modelo para la respuesta al iniciar o cargar una conversación
class ConversationResponse(BaseModel):
    id: str
    created_at: datetime
    messages: List[Message]
    # Quitar state: Optional[ConversationState] = None
    metadata: Optional[Dict[str, Any]] = None  # Mantener metadata
