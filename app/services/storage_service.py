# app/services/storage_service.py
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.models.conversation import Conversation as PydanticConversation
from app.models.message import Message as PydanticMessage
from app.db.models.conversation import Conversation as DBConversation
from app.db.models.message import Message as DBMessage, RoleEnum
from app.db.base import get_db
from app.repositories.conversation_repository import conversation_repository
from app.repositories.message_repository import message_repository
from app.config import settings

logger = logging.getLogger("hydrous")


class StorageService:
    """
    Servicio de almacenamiento refactorizado para usar PostgreSQL
    """

    async def create_conversation(self, db: Session) -> PydanticConversation:
        """Crea y almacena una nueva conversación con metadata inicial."""
        initial_metadata = {
            "current_question_id": None,
            "collected_data": {},
            "selected_sector": None,
            "selected_subsector": None,
            "questionnaire_path": [],
            "is_complete": False,
            "has_proposal": False,
            "proposal_text": None,
            "pdf_path": None,
            "client_name": "Cliente",
            "last_error": None,
        }

        # Crear en base de datos
        db_conversation = conversation_repository.create_with_metadata(
            db,
            obj_in={
                "selected_sector": None,
                "selected_subsector": None,
                "current_question_id": None,
                "is_complete": False,
                "has_proposal": False,
                "client_name": "Cliente",
                "proposal_text": None,
                "pdf_path": None,
                "user_id": None,
            },
            metadata=initial_metadata,
        )

        if not db_conversation:
            logger.error("Error al crear conversación en base de datos")
            raise Exception("Error al crear conversación")

        # Convertir a modelo Pydantic
        conversation = PydanticConversation(
            id=str(db_conversation.id),
            created_at=db_conversation.created_at,
            messages=[],
            metadata=initial_metadata,
        )

        logger.info(
            f"DBG_SS: Conversación {conversation.id} CREADA. Metadata inicial: {initial_metadata}"
        )
        return conversation

    async def get_conversation(
        self, conversation_id: str, db: Session
    ) -> Optional[PydanticConversation]:
        """Obtiene una conversación por su ID desde la base de datos."""
        # Validar ID
        try:
            conversation_uuid = UUID(conversation_id)
        except ValueError:
            logger.warning(f"DBG_SS: ID de conversación inválido: {conversation_id}")
            return None

        # Obtener conversación y sus mensajes
        db_conversation = conversation_repository.get(db, conversation_uuid)

        if not db_conversation:
            logger.warning(f"DBG_SS: Conversación {conversation_id} NO encontrada.")
            return None

        # Obtener mensajes
        db_messages = message_repository.get_by_conversation_id(db, conversation_uuid)

        # Obtener metadata
        metadata = conversation_repository.get_metadata(
            db, conversation_id=conversation_uuid
        )

        # Si no hay metadata, usar valores predeterminados
        if not metadata:
            metadata = {
                "current_question_id": None,
                "collected_data": {},
                "selected_sector": None,
                "selected_subsector": None,
                "questionnaire_path": [],
                "is_complete": False,
                "has_proposal": False,
                "proposal_text": None,
                "pdf_path": None,
                "client_name": "Cliente",
                "last_error": None,
            }

        # Convertir a modelo Pydantic
        pydantic_messages = []
        for msg in db_messages:
            pydantic_messages.append(
                PydanticMessage(
                    id=str(msg.id),
                    role=msg.role.value,
                    content=msg.content,
                    created_at=msg.created_at,
                )
            )

        conversation = PydanticConversation(
            id=str(db_conversation.id),
            created_at=db_conversation.created_at,
            messages=pydantic_messages,
            metadata=metadata,
        )

        logger.info(
            f"DBG_SS: Conversación {conversation_id} RECUPERADA. Metadata actual: {metadata}"
        )
        return conversation

    async def add_message_to_conversation(
        self, conversation_id: str, message: PydanticMessage, db: Session
    ) -> bool:
        """Añade un mensaje a la conversación en la base de datos."""
        # Validar ID
        try:
            conversation_uuid = UUID(conversation_id)
        except ValueError:
            logger.error(f"DBG_SS: ID de conversación inválido: {conversation_id}")
            return False

        # Verificar que la conversación existe
        db_conversation = conversation_repository.get(db, conversation_uuid)
        if not db_conversation:
            logger.error(
                f"DBG_SS: Error al añadir mensaje, conversación {conversation_id} no encontrada."
            )
            return False

        # Crear mensaje según el rol
        role = getattr(message, "role", "user")
        content = getattr(message, "content", "")

        if role == "user":
            db_message = message_repository.create_user_message(
                db, conversation_id=conversation_uuid, content=content
            )
        elif role == "assistant":
            db_message = message_repository.create_assistant_message(
                db, conversation_id=conversation_uuid, content=content
            )
        elif role == "system":
            db_message = message_repository.create_system_message(
                db, conversation_id=conversation_uuid, content=content
            )
        else:
            logger.error(f"DBG_SS: Rol de mensaje inválido: {role}")
            return False

        if not db_message:
            logger.error(f"DBG_SS: Error al crear mensaje para {conversation_id}")
            return False

        logger.debug(f"DBG_SS: Mensaje '{role}' añadido a {conversation_id}.")
        return True

    async def save_conversation(
        self, conversation: PydanticConversation, db: Session
    ) -> bool:
        """Guarda/Actualiza la conversación completa en la base de datos."""
        if not isinstance(conversation, PydanticConversation):
            logger.error(
                f"DBG_SS: Intento de guardar objeto inválido: {type(conversation)}"
            )
            return False

        # Validar ID
        try:
            conversation_id = UUID(conversation.id)
        except ValueError:
            logger.error(f"DBG_SS: ID de conversación inválido: {conversation.id}")
            return False

        # Verificar que la conversación existe
        db_conversation = conversation_repository.get(db, conversation_id)
        if not db_conversation:
            logger.error(
                f"DBG_SS: Conversación {conversation.id} no encontrada para actualizar."
            )
            return False

        # Actualizar datos principales
        update_data = {
            "selected_sector": conversation.metadata.get("selected_sector"),
            "selected_subsector": conversation.metadata.get("selected_subsector"),
            "current_question_id": conversation.metadata.get("current_question_id"),
            "is_complete": conversation.metadata.get("is_complete", False),
            "has_proposal": conversation.metadata.get("has_proposal", False),
            "client_name": conversation.metadata.get("client_name", "Cliente"),
            "proposal_text": conversation.metadata.get("proposal_text"),
            "pdf_path": conversation.metadata.get("pdf_path"),
        }

        # Actualizar conversación
        updated_conversation = conversation_repository.update(
            db, db_obj=db_conversation, obj_in=update_data
        )
        if not updated_conversation:
            logger.error(f"DBG_SS: Error al actualizar conversación {conversation.id}")
            return False

        # Actualizar metadata
        for key, value in conversation.metadata.items():
            # Solo guardar en tabla metadata lo que no está en campos principales
            if key not in update_data:
                conversation_repository.update_metadata(
                    db, conversation_id=conversation_id, key=key, value=value
                )

        logger.info(
            f"DBG_SS: Conversación {conversation.id} actualizada en base de datos."
        )
        return True

    async def cleanup_old_conversations(self):
        """Elimina conversaciones más antiguas que el timeout."""
        # Obtener nueva sesión
        db = conversation_repository.get_session()
        try:
            # Obtener conversaciones antiguas
            old_conversations = conversation_repository.get_old_conversations(
                db, older_than_seconds=settings.CONVERSATION_TIMEOUT
            )

            removed_count = 0
            for conv in old_conversations:
                try:
                    # Eliminar conversación (cascada elimina mensajes y metadata)
                    conversation_repository.remove(db, id=conv.id)
                    removed_count += 1
                except Exception as e:
                    logger.error(
                        f"Error eliminando conversación antigua {conv.id}: {e}"
                    )

            if removed_count > 0:
                logger.info(
                    f"Limpieza completada. {removed_count} conversaciones antiguas eliminadas."
                )
        finally:
            db.close()


# Instancia global
storage_service = StorageService()
