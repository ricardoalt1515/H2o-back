# Importaciones ordenadas para evitar referencias circulares
from app.db.models.declarations import Base, RoleEnum
from app.db.models.user import User
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.conversation_metadata import ConversationMetadata
from app.db.models.document import Document

# Para facilitar importaciones y asegurar que Alembic detecte los modelos
__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "RoleEnum",
    "ConversationMetadata",
    "Document",
]
