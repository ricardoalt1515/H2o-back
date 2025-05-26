from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.db.models.document import Document
from app.repositories.base import BaseRepository
from app.schemas.database_schemas import DocumentCreate, DocumentUpdate

logger = logging.getLogger("hydrous")


class DocumentRepository(BaseRepository[Document, DocumentCreate, DocumentUpdate]):
    def get_by_conversation_id(
        self, db: Session, conversation_id: UUID
    ) -> List[Document]:
        """Obtener todos los documentos de una conversación"""
        try:
            return (
                db.query(Document)
                .filter(Document.conversation_id == conversation_id)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error en get_by_conversation_id: {e}")
            return []

    def update_processed_text(
        self, db: Session, *, document_id: UUID, processed_text: str
    ) -> Optional[Document]:
        """Actualizar el texto procesado de un documento"""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.processed_text = processed_text
                db.commit()
                db.refresh(document)
            return document
        except SQLAlchemyError as e:
            logger.error(f"Error en update_processed_text: {e}")
            db.rollback()
            return None


# Instanciar repositorio
document_repository = DocumentRepository(Document)
