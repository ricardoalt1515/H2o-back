import os
import uuid
import logging
from typing import Dict, Any, Optional, List
from fastapi import UploadFile

from app.config import settings
from app.repositories import document_repository, unit_of_work
from app.db.models.document import Document as DBDocument
from app.models.document import Document
from app.repositories.unit_of_work import unit_of_work
from app.services.s3_service import upload_file_to_s3, get_presigned_url

logger = logging.getLogger("hydrous")


class DocumentService:
    """Servicio para manejo de documentos subidos"""

    async def process_document(
        self, file: UploadFile, conversation_id: str
    ) -> Dict[str, Any]:
        """Procesa un documento subido y lo almacena en S3"""
        try:
            # Generar nombre único para S3
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"

            # Subir archivo a S3
            await file.seek(0)
            await upload_file_to_s3(file.file, unique_filename, file.content_type)

            # Extraer texto o información básica (puedes mejorar esto si procesas el PDF)
            processed_text = f"Documento {file.filename} subido correctamente a S3"

            # Guardar información en la base de datos
            with unit_of_work() as db:
                db_document = DBDocument(
                    conversation_id=uuid.UUID(conversation_id),
                    filename=file.filename,
                    file_path=unique_filename,  # Guardamos la key de S3
                    content_type=file.content_type,
                    processed_text=processed_text,
                )

                db.add(db_document)
                db.commit()
                db.refresh(db_document)

                # Convertir a diccionario
                document_info = {
                    "id": str(db_document.id),
                    "conversation_id": conversation_id,
                    "filename": db_document.filename,
                    "file_path": db_document.file_path,  # Key de S3
                    "content_type": db_document.content_type,
                    "processed_text": db_document.processed_text,
                    "created_at": db_document.created_at.isoformat(),
                }

            logger.info(f"Documento procesado y guardado en S3: {file.filename}")
            return document_info

        except Exception as e:
            logger.error(f"Error procesando documento: {e}", exc_info=True)
            raise ValueError(f"Error procesando documento: {str(e)}")

    async def get_document(self, document_id: str) -> Optional[dict]:
        """Obtiene información de un documento por ID, incluyendo la URL firmada de descarga desde S3"""
        try:
            with unit_of_work() as db:
                db_document = document_repository.get(db, uuid.UUID(document_id))

                if not db_document:
                    return None

                # Generar URL firmada para descarga
                download_url = await get_presigned_url(db_document.file_path)

                return {
                    "id": str(db_document.id),
                    "conversation_id": str(db_document.conversation_id),
                    "filename": db_document.filename,
                    "file_path": db_document.file_path,
                    "content_type": db_document.content_type,
                    "processed_text": db_document.processed_text,
                    "created_at": db_document.created_at,
                    "download_url": download_url,
                }
        except Exception as e:
            logger.error(f"Error obteniendo documento: {e}", exc_info=True)
            return None

    def get_conversation_documents(self, conversation_id: str) -> List[Document]:
        """Obtiene todos los documentos de una conversación"""
        try:
            with unit_of_work() as db:
                db_documents = document_repository.get_by_conversation(
                    db, uuid.UUID(conversation_id)
                )

                return [
                    Document(
                        id=str(doc.id),
                        conversation_id=str(doc.conversation_id),
                        filename=doc.filename,
                        file_path=doc.file_path,
                        content_type=doc.content_type,
                        processed_text=doc.processed_text,
                        created_at=doc.created_at,
                    )
                    for doc in db_documents
                ]
        except Exception as e:
            logger.error(
                f"Error obteniendo documentos de conversación: {e}", exc_info=True
            )
            return []

    def format_document_info_for_prompt(self, doc_info: Dict[str, Any]) -> str:
        """Formatea la información del documento para incluir en el prompt"""
        return f"""
Documento: {doc_info.get('filename')}
Tipo: {doc_info.get('content_type', 'Desconocido')}
Contenido: {doc_info.get('processed_text', 'Sin procesar')}
        """.strip()


# Instancia global
document_service = DocumentService()
