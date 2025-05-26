# app/routes/documents.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import logging
from typing import Optional

from app.models.message import Message
from app.services.document_service import document_service
from app.services.storage_service import storage_service
from app.services.ai_service import ai_service

router = APIRouter()

from fastapi import Path

@router.get("/{document_id}")
async def get_document(document_id: str = Path(...)):
    """Obtiene información de un documento, incluyendo la URL de descarga segura"""
    doc = await document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return doc


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    message: Optional[str] = Form(None),
):
    """Sube un documento y lo procesa"""
    try:
        # Verificar que la conversación existe
        conversation = await storage_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        # Procesar el documento
        doc_info = await document_service.process_document(file, conversation_id)

        # Crear mensaje del usuario con referencia al documento
        user_message_content = message or f"[He subido un documento: {file.filename}]"
        user_message = Message.user(user_message_content)
        await storage_service.add_message_to_conversation(conversation_id, user_message)

        # Generar respuesta basada en el documento
        doc_summary = document_service.format_document_info_for_prompt(doc_info)
        system_message = Message.system(
            f"El usuario ha subido un documento. Aquí está la información extraída:\n{doc_summary}\n"
            "Por favor, reconoce el documento subido y continúa con el cuestionario."
        )
        await storage_service.add_message_to_conversation(
            conversation_id, system_message
        )

        # Obtener respuesta del LLM
        ai_response = await ai_service.handle_conversation(
            conversation, f"He subido un documento: {file.filename}. {message or ''}"
        )

        # Añadir respuesta del asistente
        assistant_message = Message.assistant(ai_response)
        await storage_service.add_message_to_conversation(
            conversation_id, assistant_message
        )

        return {
            "id": assistant_message.id,
            "conversation_id": conversation_id,
            "message": ai_response,
            "document_id": doc_info["id"],
            "created_at": assistant_message.created_at,
        }
    except Exception as e:
        logging.error(f"Error al subir documento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar el documento")
