# app/routes/conversations.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.db.base import get_db
from app.repositories.conversation_repository import conversation_repository
from app.routes.chat import get_current_user

router = APIRouter()

class ConversationListItem(BaseModel):
    id: str
    created_at: datetime
    title: Optional[str] = "Nueva conversación"
    last_message: Optional[str] = None
    is_complete: bool = False
    has_proposal: bool = False

@router.get("/list")
async def list_conversations(
    request: Request,
    skip: int = 0, 
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lista todas las conversaciones del usuario autenticado."""
    # Obtener usuario autenticado
    current_user = get_current_user(request)
    
    # Obtener conversaciones
    conversations = conversation_repository.get_by_user_id(
        db, 
        user_id=UUID(current_user["id"]),
        skip=skip,
        limit=limit
    )
    
    # Formatear resultados
    result = []
    for conv in conversations:
        # Obtener último mensaje si existe
        last_message_text = None
        if conv.messages:
            last_msg = sorted(conv.messages, key=lambda m: m.created_at, reverse=True)[0]
            last_message_text = last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content
        
        # Crear título si no existe
        title = "Nueva conversación"
        if conv.selected_sector:
            title = f"Consulta: {conv.selected_sector}"
            if conv.selected_subsector:
                title += f" - {conv.selected_subsector}"
        
        result.append(
            ConversationListItem(
                id=str(conv.id),
                created_at=conv.created_at,
                title=title,
                last_message=last_message_text,
                is_complete=conv.is_complete,
                has_proposal=conv.has_proposal
            )
        )
    
    return result

@router.delete("/{conversation_id}")
async def delete_conversation(
    request: Request,
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Elimina una conversación del usuario."""
    # Obtener usuario autenticado
    current_user = get_current_user(request)
    
    # Verificar propiedad
    db_conversation = conversation_repository.get(db, UUID(conversation_id))
    if not db_conversation or str(db_conversation.user_id) != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar esta conversación"
        )
    
    # Eliminar conversación
    conversation_repository.remove(db, id=UUID(conversation_id))
    return {"status": "success"}