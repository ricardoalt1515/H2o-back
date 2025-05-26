# app/routes/feedback.py
from fastapi import APIRouter, HTTPException
import logging
import os
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
logger = logging.getLogger("hydrous")


class FeedbackModel(BaseModel):
    """Modelo simple para retroalimentación"""

    conversation_id: str
    message_id: Optional[str] = None
    rating: int  # 1-5 donde 5 es excelente
    comment: Optional[str] = None


# Directorio para almacenar retroalimentación
FEEDBACK_DIR = os.path.join("uploads", "feedback")
os.makedirs(FEEDBACK_DIR, exist_ok=True)


@router.post("/submit")
async def submit_feedback(feedback: FeedbackModel):
    """Envía retroalimentación sobre una respuesta"""
    try:
        # Crear un ID único para la retroalimentación
        feedback_id = (
            f"{feedback.conversation_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        # Preparar datos para guardar
        feedback_data = {
            "id": feedback_id,
            "conversation_id": feedback.conversation_id,
            "message_id": feedback.message_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "timestamp": datetime.now().isoformat(),
        }

        # Guardar en archivo JSON
        feedback_file = os.path.join(FEEDBACK_DIR, f"{feedback_id}.json")
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "Retroalimentación recibida correctamente",
        }

    except Exception as e:
        logger.error(f"Error al procesar retroalimentación: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al procesar la retroalimentación"
        )
