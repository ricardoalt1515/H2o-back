from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.db.models.message import Message, RoleEnum
from app.repositories.base import BaseRepository
from app.schemas.database_schemas import MessageCreate, MessageUpdate

logger = logging.getLogger("hydrous")


class MessageRepository(BaseRepository[Message, MessageCreate, MessageUpdate]):
    def get_by_conversation_id(
        self, db: Session, conversation_id: UUID
    ) -> List[Message]:
        """Obtener todos los mensajes de una conversación ordenados por fecha"""
        try:
            return (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error en get_by_conversation_id: {e}")
            return []

    def create_user_message(
        self, db: Session, *, conversation_id: UUID, content: str
    ) -> Optional[Message]:
        """Crear un mensaje de usuario"""
        try:
            message = Message(
                conversation_id=conversation_id, role=RoleEnum.user, content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error en create_user_message: {e}")
            db.rollback()
            return None

    def create_assistant_message(
        self, db: Session, *, conversation_id: UUID, content: str
    ) -> Optional[Message]:
        """Crear un mensaje del asistente"""
        try:
            message = Message(
                conversation_id=conversation_id,
                role=RoleEnum.assistant,
                content=content,
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error en create_assistant_message: {e}")
            db.rollback()
            return None

    def create_system_message(
        self, db: Session, *, conversation_id: UUID, content: str
    ) -> Optional[Message]:
        """Crear un mensaje del sistema"""
        try:
            message = Message(
                conversation_id=conversation_id, role=RoleEnum.system, content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error en create_system_message: {e}")
            db.rollback()
            return None


# Instanciar repositorio
message_repository = MessageRepository(Message)
