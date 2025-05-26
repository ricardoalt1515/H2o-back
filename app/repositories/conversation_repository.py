from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import json

from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.conversation_metadata import ConversationMetadata
from app.repositories.base import BaseRepository
from app.schemas.database_schemas import ConversationCreate, ConversationUpdate

logger = logging.getLogger("hydrous")


class ConversationRepository(
    BaseRepository[Conversation, ConversationCreate, ConversationUpdate]
):
    def get_with_messages(self, db: Session, id: UUID) -> Optional[Conversation]:
        """Obtener una conversación con sus mensajes"""
        try:
            return db.query(Conversation).filter(Conversation.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error en get_with_messages: {e}")
            return None

    def get_by_user_id(
        self, db: Session, user_id: UUID, *, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """Obtener conversaciones de un usuario"""
        try:
            return (
                db.query(Conversation)
                .filter(Conversation.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error en get_by_user_id: {e}")
            return []

    def create_with_metadata(
        self, db: Session, *, obj_in: Dict[str, Any], metadata: Dict[str, Any] = None
    ) -> Optional[Conversation]:
        """Crear una conversación con metadatos iniciales"""
        try:
            # Crear conversación
            db_conversation = Conversation(**obj_in)
            db.add(db_conversation)
            db.flush()  # Para obtener el ID sin hacer commit todavía

            # Añadir metadatos si existen
            if metadata:
                for key, value in metadata.items():
                    # Solo metadatos que no estén en los campos principales
                    if key not in obj_in or obj_in.get(key) is None:
                        metadata_item = ConversationMetadata(
                            conversation_id=db_conversation.id,
                            key=key,
                            value=value,  # PostgreSQL maneja JSONB directamente
                        )
                        db.add(metadata_item)

            db.commit()
            db.refresh(db_conversation)
            return db_conversation
        except SQLAlchemyError as e:
            logger.error(f"Error en create_with_metadata: {e}")
            db.rollback()
            return None

    def update_metadata(
        self, db: Session, *, conversation_id: UUID, key: str, value: Any
    ) -> bool:
        """Actualizar o crear un ítem de metadatos"""
        try:
            # Buscar si existe
            metadata_item = (
                db.query(ConversationMetadata)
                .filter(
                    ConversationMetadata.conversation_id == conversation_id,
                    ConversationMetadata.key == key,
                )
                .first()
            )

            if metadata_item:
                # Actualizar existente
                metadata_item.value = value
            else:
                # Crear nuevo
                metadata_item = ConversationMetadata(
                    conversation_id=conversation_id, key=key, value=value
                )
                db.add(metadata_item)

            db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error en update_metadata: {e}")
            db.rollback()
            return False

    def get_metadata(self, db: Session, *, conversation_id: UUID) -> Dict[str, Any]:
        """Obtener todos los metadatos de una conversación"""
        try:
            metadata_items = (
                db.query(ConversationMetadata)
                .filter(ConversationMetadata.conversation_id == conversation_id)
                .all()
            )

            # Convertir a diccionario
            metadata_dict = {}
            for item in metadata_items:
                metadata_dict[item.key] = item.value

            return metadata_dict
        except SQLAlchemyError as e:
            logger.error(f"Error en get_metadata: {e}")
            return {}

    def get_old_conversations(
        self, db: Session, *, older_than_seconds: int
    ) -> List[Conversation]:
        """Obtener conversaciones antiguas para limpieza"""
        from datetime import datetime, timedelta

        try:
            cutoff_date = datetime.utcnow() - timedelta(seconds=older_than_seconds)
            return (
                db.query(Conversation)
                .filter(Conversation.created_at < cutoff_date)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error en get_old_conversations: {e}")
            return []


# Instanciar repositorio - CORREGIDO
conversation_repository = ConversationRepository(Conversation)
