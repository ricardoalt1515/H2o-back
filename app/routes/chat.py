# app/routes/chat.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Header, Request
from fastapi.responses import FileResponse
import logging
import os
import uuid
import re
from datetime import datetime
from typing import Any, Optional, Dict, List
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.orm import Session

# Modelos
from app.models.conversation import ConversationResponse, Conversation
from app.models.message import Message, MessageCreate

# Servicios
from app.services.storage_service import storage_service
from app.services.ai_service import ai_service
from app.services.pdf_service import pdf_service
from app.services.proposal_service import proposal_service
from app.services.questionnaire_service import questionnaire_service
from app.services.auth_service import auth_service
from app.config import settings
from app.db.base import get_db

# Importar repositorios
from app.repositories.conversation_repository import conversation_repository

router = APIRouter()
logger = logging.getLogger("hydrous")

# --- Funciones Auxiliares ---


# FUNCIÓN HELPER para obtener usuario actual
def get_current_user(request: Request):
    """
    Extrae los datos del usuario autenticado del middleware.

    El middleware ya verificó el token y almacenó los datos en request.state.user
    """
    if not hasattr(request.state, "user") or not request.state.user:
        raise HTTPException(
            status_code=401, detail="No se encontraron datos de usuario autenticado"
        )
    return request.state.user


def _get_full_questionnaire_path(metadata: Dict[str, Any]) -> List[str]:
    """Intenta construir la ruta completa del cuestionario."""
    path = [
        q["id"]
        for q in questionnaire_service.structure.get("initial_questions", [])
        if "id" in q
    ]
    sector = metadata.get("selected_sector")
    subsector = metadata.get("selected_subsector")
    if sector and subsector:
        try:
            sector_data = questionnaire_service.structure.get(
                "sector_questionnaires", {}
            ).get(sector, {})
            subsector_questions = sector_data.get(subsector, [])
            if not isinstance(subsector_questions, list):
                subsector_questions = sector_data.get("Otro", [])
            path.extend([q["id"] for q in subsector_questions if "id" in q])
        except Exception as e:
            logger.error(f"Error construyendo ruta en _get_full_path: {e}")
            path = [
                q["id"]
                for q in questionnaire_service.structure.get("initial_questions", [])
                if "id" in q
            ]
    return path


def _is_last_question(
    current_question_id: Optional[str], metadata: Dict[str, Any]
) -> bool:
    """Verifica si la pregunta actual es la última de la ruta completa."""
    if not current_question_id:
        logger.debug("_is_last_question: No hay pregunta actual, retornando False")
        return False

    # Obtener la ruta completa del cuestionario
    path = metadata.get("questionnaire_path", [])
    if not path:
        # Si no existe, construirla
        logger.debug(f"_is_last_question: Construyendo ruta para {current_question_id}")
        path = _get_full_questionnaire_path(metadata)
        metadata["questionnaire_path"] = path
        logger.debug(
            f"_is_last_question: Ruta construida: {path} (total: {len(path)} preguntas)"
        )

    if not path:
        logger.warning(
            "_is_last_question: No se pudo obtener ruta de preguntas, retornando False"
        )
        return False

    try:
        # Verificar posición en la ruta
        current_index = path.index(current_question_id)
        total_questions = len(path)
        is_last = current_index == total_questions - 1

        logger.debug(
            f"_is_last_question: Pregunta {current_question_id} es la #{current_index+1} de {total_questions}"
        )

        if is_last:
            logger.info(
                f"¡ÚLTIMA PREGUNTA DETECTADA! ({current_question_id}) - Posición {current_index+1} de {total_questions}"
            )
        return is_last
    except ValueError:
        logger.warning(
            f"_is_last_question: ID '{current_question_id}' no encontrado en ruta {path}"
        )
        # Si la pregunta no está en la ruta, podríamos estar ante un caso especial
        # Verificar si es una pregunta final según alguna otra lógica
        if current_question_id and current_question_id.startswith("FINAL_"):
            logger.info(
                f"Detectada pregunta especial de finalización: {current_question_id}"
            )
            return True
        return False


def _is_pdf_request(message_content: str) -> bool:
    """Determina si el mensaje del usuario es una solicitud de descarga del PDF."""
    normalized = message_content.lower().strip()
    pdf_requests = [
        "descargar pdf",
        "download pdf",
        "obtener pdf",
        "get pdf",
        "pdf",
        "descargar",
        "download",
        "quiero el pdf",
        "quiero mi pdf",
        "dame el pdf",
        "dame mi pdf",
    ]
    return any(request in normalized for request in pdf_requests)


# --- Endpoints ---
class ConversationStartRequest(BaseModel):
    customContext: Optional[Dict[str, Any]] = None


@router.post("/start", response_model=ConversationResponse)
async def start_conversation(
    request: Request,  # Para acceder a datos del usuario
    request_data: Optional[ConversationStartRequest] = None,
    db: Session = Depends(get_db),
):
    """Inicia conversación. Ahora requiere autenticación obligatoria."""
    try:
        # Obtener usuario autenticado del middleware
        current_user = get_current_user(request)

        # Extraer y formatear datos del usuario
        client_name = f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
        user_location = current_user.get("location")
        selected_sector = current_user.get("sector")
        selected_subsector = current_user.get("subsector")
        company_name = current_user.get("company_name")

        # Log de depuración para verificar datos del usuario
        logger.info(
            f"Datos del usuario al iniciar conversación: "
            f"nombre={client_name}, empresa={company_name}, "
            f"sector={selected_sector}, subsector={selected_subsector}, "
            f"ubicación={user_location}, email={current_user.get('email')}"
        )

        # Crear metadatos iniciales con información del usuario
        initial_metadata = {
            "client_name": client_name,
            "user_name": client_name,  # Duplicar para compatibilidad con el prompt
            "user_location": user_location,
            "selected_sector": selected_sector if selected_sector else None,
            "selected_subsector": selected_subsector if selected_subsector else None,
            "sector": (
                selected_sector if selected_sector else None
            ),  # Alias para compatibilidad
            "subsector": (
                selected_subsector if selected_subsector else None
            ),  # Alias para compatibilidad
            "company_name": company_name,
            "user_email": current_user.get("email"),
            "is_new_conversation": True,  # Indicador de nueva conversación
            "first_interaction": True,  # Para mensaje inicial personalizado
        }

        # Log de depuración para verificar metadata
        logger.info(f"Metadata inicial de la conversación: {initial_metadata}")

        # Crear conversación en base de datos
        new_conversation = conversation_repository.create_with_metadata(
            db,
            obj_in={
                "user_id": UUID(current_user["id"]),
                "selected_sector": selected_sector,
                "selected_subsector": selected_subsector,
                "client_name": client_name,
            },
            metadata=initial_metadata,
        )

        if not new_conversation:
            raise HTTPException(status_code=500, detail="Error al crear conversación")

        # Crear objeto Conversation para la respuesta
        conversation = Conversation(
            id=str(new_conversation.id),
            created_at=new_conversation.created_at,
            user_id=str(new_conversation.user_id),
            messages=[],
            metadata=initial_metadata,
        )

        # Construir mensaje de bienvenida personalizado con información del usuario
        welcome_parts = [
            "Hello! I'm H₂O Allegiant, your specialized assistant in water treatment engineering.\n\n"
        ]

        # Añadir información del usuario que tenemos
        if client_name:
            welcome_parts.append(f"Welcome {client_name}. ")

        # Lista para recopilar los datos que ya tenemos
        user_data_parts = []
        if company_name:
            user_data_parts.append(f"Your company is {company_name}")
        if user_location:
            user_data_parts.append(f"You are located in {user_location}")
        if selected_sector:
            sector_part = f"You are in the sector {selected_sector}"
            if selected_subsector:
                sector_part += f", Specifically in {selected_subsector}"
            user_data_parts.append(sector_part)

        # Añadir resumen de datos del usuario si tenemos alguno
        if user_data_parts:
            welcome_parts.append("According to the information I have, ")
            if len(user_data_parts) == 1:
                welcome_parts.append(f"{user_data_parts[0]}. ")
            elif len(user_data_parts) == 2:
                welcome_parts.append(f"{user_data_parts[0]} y {user_data_parts[1]}. ")
            else:
                welcome_parts.append(
                    ", ".join(user_data_parts[:-1]) + f" y {user_data_parts[-1]}. "
                )
            welcome_parts.append("Is this information correct? ")

        # Crear mensaje de bienvenida
        welcome_message = Message.assistant("".join(welcome_parts))
        conversation.add_message(welcome_message)

        # Guardar conversación con mensaje inicial
        await storage_service.save_conversation(conversation, db)

        # Retornar datos de la conversación
        return ConversationResponse(
            id=conversation.id,
            created_at=conversation.created_at,
            messages=conversation.messages,
            metadata=conversation.metadata,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error crítico al iniciar conversación: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="No se pudo iniciar la conversación."
        )


@router.post("/message")
async def send_message(
    request: Request,
    data: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Process user message."""
    # Extraer datos del mensaje
    conversation_id = (
        data.conversation_id if hasattr(data, "conversation_id") else "unknown"
    )
    user_input = data.message if hasattr(data, "message") else ""

    # Verificar si es un mensaje de verificación silenciosa (para cargar mensajes)
    is_verification_message = user_input == "VERIFICACIÓN_SILENCIOSA"

    if is_verification_message:
        # Cargar conversación
        conversation = await storage_service.get_conversation(conversation_id, db)
        if not conversation:
            logger.error(f"Conversation not found: {conversation_id}")
            return {
                "id": "error-conv-not-found",
                "message": "Error: Conversation not found. Please restart.",
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow(),
            }

        # Retornar mensajes actuales sin procesar el mensaje de verificación
        return {
            "id": conversation.id,
            "messages": conversation.messages,
            "conversation_id": conversation_id,
            "created_at": conversation.created_at,
        }
    assistant_response_data = None

    try:
        # Get authenticated user
        current_user = get_current_user(request)

        # 1. Load conversation
        logger.debug(f"Received /message request for conv: {conversation_id}")
        conversation = await storage_service.get_conversation(conversation_id, db)
        if not conversation:
            logger.error(f"Conversation not found: {conversation_id}")
            return {
                "id": "error-conv-not-found",
                "message": "Error: Conversation not found. Please restart.",
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow(),
            }

        # 2. Create user message object
        user_message_obj = Message.user(user_input)

        # Verify ownership
        db_conversation = conversation_repository.get(db, UUID(conversation_id))
        if not db_conversation or str(db_conversation.user_id) != current_user["id"]:
            logger.warning(
                f"User {current_user['id']} tried to access unauthorized conversation {conversation_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this conversation",
            )

        # 3. Check if PDF request
        is_pdf_req = _is_pdf_request(user_input)
        proposal_ready = conversation.metadata.get("has_proposal", False)
        is_complete = conversation.metadata.get("is_complete", False)
        ready_for_proposal = conversation.metadata.get("ready_for_proposal", False)
        pdf_path = conversation.metadata.get("pdf_path")

        logger.info(
            f"PDF_CHECK: ConvID={conversation_id}, Input='{user_input}', is_pdf_req={is_pdf_req}, "
            f"proposal_ready={proposal_ready}, is_complete={is_complete}, pdf_path={pdf_path}, ready_for_proposal={ready_for_proposal}"
        )

        if is_pdf_req:
            # Añadir mensaje del usuario al historial
            await storage_service.add_message_to_conversation(
                conversation.id, user_message_obj, db
            )

            # Inteligencia para manejar diferentes estados de la propuesta

            # CASO 1: Si la propuesta está lista pero metadatos inconsistentes, arreglar
            if pdf_path and os.path.exists(pdf_path) and not proposal_ready:
                logger.info(
                    f"PDF existe pero metadatos inconsistentes. Corrigiendo para {conversation_id}..."
                )
                conversation.metadata["has_proposal"] = True
                conversation.metadata["is_complete"] = True
                await storage_service.save_conversation(conversation, db)
                db.commit()
                proposal_ready = True

            # CASO 2: Si tiene señal de "ready_for_proposal" pero no tiene PDF, generar
            elif (ready_for_proposal and not pdf_path) or (
                ready_for_proposal and pdf_path and not os.path.exists(pdf_path)
            ):
                logger.info(
                    f"Marcado como listo para propuesta. Generando PDF para {conversation_id}..."
                )
                from app.services.direct_proposal_generator import (
                    direct_proposal_generator,
                )

                pdf_path = await direct_proposal_generator.generate_complete_proposal(
                    conversation
                )
                if pdf_path and os.path.exists(pdf_path):
                    logger.info(f"PDF generado exitosamente: {pdf_path}")
                    conversation.metadata["pdf_path"] = pdf_path
                    conversation.metadata["is_complete"] = True
                    conversation.metadata["has_proposal"] = True
                    await storage_service.save_conversation(conversation, db)
                    db.commit()
                    proposal_ready = True

                    # Recargar conversación para verificar
                    conversation = await storage_service.get_conversation(
                        conversation_id, db
                    )
                    logger.info(
                        f"Metadatos después de generar: {conversation.metadata}"
                    )

            # CASO 3: Si está marcado como completo pero sin PDF, intentar regenerar
            elif (
                (is_complete and not proposal_ready)
                or (is_complete and not pdf_path)
                or (is_complete and pdf_path and not os.path.exists(pdf_path))
            ):
                logger.info(
                    f"Necesita generar o regenerar PDF para {conversation_id}. Estado: is_complete={is_complete}, proposal_ready={proposal_ready}, pdf_path={pdf_path}"
                )
                from app.services.direct_proposal_generator import (
                    direct_proposal_generator,
                )

                # Regenerar PDF
                pdf_path = await direct_proposal_generator.generate_complete_proposal(
                    conversation
                )

                if pdf_path and os.path.exists(pdf_path):
                    logger.info(f"PDF generado exitosamente: {pdf_path}")
                    # Actualizar metadata explícitamente
                    conversation.metadata["pdf_path"] = pdf_path
                    conversation.metadata["is_complete"] = True
                    conversation.metadata["has_proposal"] = True
                    await storage_service.save_conversation(conversation, db)
                    db.commit()
                    proposal_ready = True

                    # Recargar conversación para verificar
                    conversation = await storage_service.get_conversation(
                        conversation_id, db
                    )
                    logger.info(
                        f"Metadatos después de regenerar: {conversation.metadata}"
                    )
                else:
                    logger.error(f"Falló la generación del PDF para {conversation_id}")

            # Verificar nuevamente si tenemos propuesta lista
            if proposal_ready or (pdf_path and os.path.exists(pdf_path)):
                # Asegurar que todos los metadatos estén consistentes
                if pdf_path and os.path.exists(pdf_path) and not proposal_ready:
                    conversation.metadata["has_proposal"] = True
                    conversation.metadata["is_complete"] = True
                    await storage_service.save_conversation(conversation, db)
                    db.commit()

                # Construir respuesta con URL de descarga
                download_url = f"{settings.BACKEND_URL}{settings.API_V1_STR}/chat/{conversation.id}/download-pdf"

                response_text = f"¡Aquí está tu propuesta! Haz clic para descargar o espera mientras se descarga automáticamente."
                assistant_message = Message.assistant(response_text)

                await storage_service.add_message_to_conversation(
                    conversation.id, assistant_message, db
                )

                assistant_response_data = {
                    "id": assistant_message.id,
                    "message": assistant_message.content,
                    "conversation_id": conversation_id,
                    "created_at": assistant_message.created_at,
                    "action": "download_proposal_pdf",
                    "download_url": download_url,
                }

                return assistant_response_data
            else:
                # No hay propuesta disponible
                response_text = "Todavía no tengo lista tu propuesta. Por favor completa el cuestionario primero."
                assistant_message = Message.assistant(response_text)

                await storage_service.add_message_to_conversation(
                    conversation.id, assistant_message, db
                )

                assistant_response_data = {
                    "id": assistant_message.id,
                    "message": assistant_message.content,
                    "conversation_id": conversation_id,
                    "created_at": assistant_message.created_at,
                }

                return assistant_response_data

        else:
            # --- Normal Flow: Continue with questionnaire ---
            logger.info(f"Normal flow for conversation {conversation_id}")

            # Add user message to history
            await storage_service.add_message_to_conversation(
                conversation_id, user_message_obj, db
            )

            # Verificar si es la primera interacción y actualizar metadata
            if conversation.metadata.get("first_interaction", False):
                logger.info(
                    f"Primera interacción detectada para conversación {conversation_id}. Actualizando metadata."
                )
                conversation.metadata["first_interaction"] = False
                # Mantenemos is_new_conversation=True para que el asistente sepa que
                # sigue siendo una conversación nueva aunque ya no sea la primera interacción

            # Save user response immediately
            current_question_id = conversation.metadata.get("current_question_id")

            if current_question_id:
                # Update metadata with the response
                if "collected_data" not in conversation.metadata:
                    conversation.metadata["collected_data"] = {}

                conversation.metadata["collected_data"][
                    current_question_id
                ] = user_input.strip()

                # Save response summary
                if "response_summaries" not in conversation.metadata:
                    conversation.metadata["response_summaries"] = {}

                conversation.metadata["response_summaries"][current_question_id] = {
                    "question": conversation.metadata.get(
                        "current_question_asked_summary", ""
                    ),
                    "answer": user_input.strip(),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Mark question as answered
                conversation.metadata["last_answered_question_id"] = current_question_id

                # CRITICAL: Save immediately before calling AI
                await storage_service.save_conversation(conversation, db)
                db.commit()  # Force immediate commit

                logger.info(
                    f"Response saved for {current_question_id}: '{user_input.strip()}'"
                )

            # Reload conversation to ensure latest state
            conversation = await storage_service.get_conversation(conversation_id, db)

            # Check if final answer
            is_final_answer = _is_last_question(
                current_question_id, conversation.metadata
            )

            if is_final_answer:
                # Generate proposal
                logger.info(f"Generando proposal para {conversation_id}")
                from app.services.direct_proposal_generator import (
                    direct_proposal_generator,
                )

                # Intentar generar la propuesta
                pdf_path = await direct_proposal_generator.generate_complete_proposal(
                    conversation
                )

                # Actualizar metadata de la conversación
                conversation.metadata["is_complete"] = True
                conversation.metadata["current_question_id"] = None
                conversation.metadata["current_question_asked_summary"] = (
                    "Questionnaire Completed"
                )

                # Verificar que el PDF se generó correctamente
                if pdf_path and os.path.exists(pdf_path):
                    logger.info(f"Propuesta generada exitosamente: {pdf_path}")
                    # Establecer explícitamente que hay una propuesta disponible
                    conversation.metadata["pdf_path"] = pdf_path
                    conversation.metadata["has_proposal"] = True
                    # Guardar inmediatamente para persistir estos cambios
                    await storage_service.save_conversation(conversation, db)
                    db.commit()

                    # Generar URL de descarga y respuesta
                    download_url = f"{settings.BACKEND_URL}{settings.API_V1_STR}/chat/{conversation.id}/download-pdf"
                    assistant_response_data = {
                        "id": "proposal-complete-" + str(uuid.uuid4())[:8],
                        "message": "✅ ¡Propuesta Lista! Escribe 'descargar pdf' para obtener tu documento.",
                        "conversation_id": conversation_id,
                        "created_at": datetime.utcnow(),
                        "action": "proposal_complete",
                        "download_url": download_url,
                    }

                    # Añadir mensaje al historial
                    msg_to_add = Message.assistant(assistant_response_data["message"])
                    await storage_service.add_message_to_conversation(
                        conversation.id, msg_to_add, db
                    )
                else:
                    # Manejo de error si no se pudo generar el PDF
                    logger.error(
                        f"Error generando PDF para {conversation_id}. Path: {pdf_path}"
                    )
                    error_message = "Lo siento, hubo un problema generando la propuesta. Por favor intenta de nuevo."
                    error_msg = Message.assistant(error_message)
                    await storage_service.add_message_to_conversation(
                        conversation.id, error_msg, db
                    )
                    assistant_response_data = {
                        "id": error_msg.id,
                        "message": error_message,
                        "conversation_id": conversation_id,
                        "created_at": error_msg.created_at,
                    }
            else:
                # Continue with questionnaire
                ai_response_content = await ai_service.handle_conversation(conversation)

                # Detectar si es una propuesta completa que necesita generación de PDF
                if "[HYDROUS_INTERNAL_MARKER:GENERATE_PROPOSAL]" in ai_response_content:
                    logger.info(
                        f"Detectada propuesta completa que requiere generación de PDF para {conversation_id}"
                    )
                    # Extraer el texto de la propuesta (ya guardado en metadata)
                    proposal_text = conversation.metadata.get("proposal_text")
                    if not proposal_text and len(ai_response_content) > 40:
                        # Si no está en metadata, extraerlo del marcador
                        proposal_text = ai_response_content.replace(
                            "[HYDROUS_INTERNAL_MARKER:GENERATE_PROPOSAL]", ""
                        )
                        conversation.metadata["proposal_text"] = proposal_text

                    # Debugging: registrar estado de metadata antes de cambios
                    logger.info(
                        f"METADATA ANTES DE GENERAR PDF: is_complete={conversation.metadata.get('is_complete')}, has_proposal={conversation.metadata.get('has_proposal')}, pdf_path={conversation.metadata.get('pdf_path')}"
                    )

                    # Guardar los cambios iniciales a la metadata
                    await storage_service.save_conversation(conversation, db)
                    db.commit()

                    # Generar el PDF
                    from app.services.direct_proposal_generator import (
                        direct_proposal_generator,
                    )

                    logger.info(
                        f"Generando PDF para propuesta de conversación {conversation_id}..."
                    )

                    pdf_path = (
                        await direct_proposal_generator.generate_complete_proposal(
                            conversation
                        )
                    )

                    if pdf_path and os.path.exists(pdf_path):
                        logger.info(f"PDF generado exitosamente en: {pdf_path}")
                        # Actualizar metadata explícitamente
                        conversation.metadata["pdf_path"] = pdf_path
                        conversation.metadata["is_complete"] = True
                        conversation.metadata["has_proposal"] = True

                        # Verificar permisos del archivo
                        try:
                            os.chmod(pdf_path, 0o644)  # rw-r--r--
                            logger.info(f"Permisos del PDF establecidos correctamente")
                        except Exception as perm_err:
                            logger.warning(
                                f"No se pudieron establecer permisos en {pdf_path}: {perm_err}"
                            )

                        # Guardar inmediatamente los cambios
                        await storage_service.save_conversation(conversation, db)
                        db.commit()

                        # Volver a cargar la conversación para asegurar que los cambios se guardaron
                        conversation = await storage_service.get_conversation(
                            conversation_id, db
                        )

                        # Verificar que los cambios se guardaron correctamente
                        logger.info(
                            f"METADATA DESPUÉS DE GENERAR PDF: is_complete={conversation.metadata.get('is_complete')}, has_proposal={conversation.metadata.get('has_proposal')}, pdf_path={conversation.metadata.get('pdf_path')}"
                        )

                        # Preparar respuesta para el usuario
                        download_url = f"{settings.BACKEND_URL}{settings.API_V1_STR}/chat/{conversation.id}/download-pdf"
                        ai_response_content = "✅ ¡Propuesta Lista! Escribe 'descargar pdf' para obtener tu documento."

                        # Log detallado para seguimiento
                        logger.info(
                            f"Propuesta lista para {conversation_id}. URL de descarga: {download_url}"
                        )
                    else:
                        logger.error(
                            f"❌ Error generando PDF para {conversation_id}. Ruta: {pdf_path}"
                        )
                        logger.error(
                            f"Detalles: proposal_text existe: {bool(proposal_text)}, longitud: {len(proposal_text) if proposal_text else 0}"
                        )
                        ai_response_content = "Lo siento, hubo un problema generando la propuesta. Por favor intenta de nuevo."

                # Anti-repetition check
                new_question_id = None
                lines = ai_response_content.split("\n")
                for i, line in enumerate(lines):
                    if "**QUESTION:**" in line or "**PREGUNTA:**" in line:
                        new_question_id = f"q_{i}"
                        break

                # Check if AI is repeating a question
                if new_question_id and new_question_id in conversation.metadata.get(
                    "collected_data", {}
                ):
                    logger.warning(
                        f"AI attempted to repeat answered question: {new_question_id}"
                    )
                    ai_response_content = (
                        "I already have your answer to that question. Let me continue with the next one:\n\n"
                        "**QUESTION:** [Next relevant question from questionnaire]"
                    )

                # Update current question ID if new
                if new_question_id and new_question_id != current_question_id:
                    conversation.metadata["current_question_id"] = new_question_id

                assistant_message = Message.assistant(ai_response_content)
                await storage_service.add_message_to_conversation(
                    conversation.id, assistant_message, db
                )

                assistant_response_data = {
                    "id": assistant_message.id,
                    "message": assistant_message.content,
                    "conversation_id": conversation_id,
                    "created_at": assistant_message.created_at,
                }

        # Save final state
        await storage_service.save_conversation(conversation, db)
        db.commit()
        background_tasks.add_task(storage_service.cleanup_old_conversations)

        return assistant_response_data

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(
            f"Fatal error in send_message for {conversation_id}: {str(e)}",
            exc_info=True,
        )
        error_response = {
            "id": "error-fatal-" + str(uuid.uuid4())[:8],
            "message": "Sorry, an unexpected server error occurred.",
            "conversation_id": conversation_id,
            "created_at": datetime.utcnow(),
        }
        try:
            if "conversation" in locals() and isinstance(conversation, Conversation):
                conversation.metadata["last_error"] = f"Fatal: {str(e)[:200]}"
                await storage_service.save_conversation(conversation, db)
        except Exception as save_err:
            logger.error(f"Additional error saving error: {save_err}")

        return error_response


# Endpoint /download-pdf (SIN CAMBIOS)
@router.get("/{conversation_id}/download-pdf")
async def download_pdf(
    request: Request,  # Para acceder a datos del usuario
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """Descarga PDF. Solo el dueño de la conversación puede descargar."""
    try:
        # Obtener usuario autenticado
        current_user = get_current_user(request)
        logger.info(
            f"Intento de descarga PDF para conversación {conversation_id} por usuario {current_user.get('email', 'desconocido')}"
        )

        # Cargar conversación
        conversation = await storage_service.get_conversation(conversation_id, db)
        if not conversation:
            logger.error(f"Conversación no encontrada: {conversation_id}")
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        # Verificar que hay un usuario válido y tiene permisos
        if not current_user:
            logger.warning(
                f"Intento de descarga sin autenticación para {conversation_id}"
            )
            # En un entorno Docker, podemos ser más permisivos temporalmente para debug
            if os.environ.get("DOCKER_ENV") == "true" or settings.DEBUG:
                logger.warning("Permitiendo descarga sin auth en entorno DEBUG/Docker")
            else:
                raise HTTPException(
                    status_code=401, detail="No autenticado para descargar"
                )
        else:
            # VERIFICAR PROPIEDAD
            db_conversation = conversation_repository.get(db, UUID(conversation_id))
            if (
                not db_conversation
                or str(db_conversation.user_id) != current_user["id"]
            ):
                logger.warning(
                    f"Usuario {current_user['id']} intentó descargar conversación {conversation_id} no autorizada"
                )
                if not settings.DEBUG:
                    raise HTTPException(
                        status_code=403,
                        detail="No tienes permisos para descargar esta propuesta",
                    )
                else:
                    logger.warning(
                        "Permitiendo descarga sin verificación de propiedad en modo DEBUG"
                    )

        # Verificar estado de metadata
        has_proposal = conversation.metadata.get("has_proposal", False)
        is_complete = conversation.metadata.get("is_complete", False)
        ready_for_proposal = conversation.metadata.get("ready_for_proposal", False)
        pdf_path = conversation.metadata.get("pdf_path")
        proposal_text = conversation.metadata.get("proposal_text")

        logger.info(
            f"Estado PDF para descarga: has_proposal={has_proposal}, is_complete={is_complete}, ready_for_proposal={ready_for_proposal}, pdf_path={pdf_path}, proposal_text_len={len(proposal_text) if proposal_text else 0}"
        )

        # Si no existe o metadata inconsistente, intentar regenerarlo
        if not pdf_path or not os.path.exists(pdf_path) or not has_proposal:
            logger.info(
                f"PDF no existe o metadata inconsistente, regenerando para descarga directa"
            )
            from app.services.direct_proposal_generator import direct_proposal_generator

            # Si ya tenemos texto de propuesta, mejor asegurarnos que esté en la metadata
            if not proposal_text and is_complete:
                logger.info(
                    f"Sin texto de propuesta, pero is_complete=True. Generando PDF de emergencia..."
                )
                # Usar texto de emergencia o generar
                conversation.metadata["proposal_text"] = (
                    "# Propuesta de Tratamiento de Agua para Cliente\n\nGenerado automáticamente para descarga directa."
                )
                await storage_service.save_conversation(conversation, db)
                db.commit()

            logger.info(f"Regenerando PDF bajo demanda para descarga directa...")
            pdf_path = await direct_proposal_generator.generate_complete_proposal(
                conversation
            )

            if pdf_path and os.path.exists(pdf_path):
                logger.info(f"PDF regenerado exitosamente para descarga: {pdf_path}")
                # Asegurar permisos de archivo correctos
                try:
                    os.chmod(pdf_path, 0o644)  # rw-r--r--
                    logger.info(
                        f"Permisos del PDF establecidos: {oct(os.stat(pdf_path).st_mode)[-3:]}"
                    )
                except Exception as e:
                    logger.warning(
                        f"No se pudieron establecer permisos en {pdf_path}: {e}"
                    )

                # Actualizar la metadata de la conversación con la nueva ruta
                conversation.metadata["pdf_path"] = pdf_path
                conversation.metadata["has_proposal"] = True
                conversation.metadata["is_complete"] = True
                await storage_service.save_conversation(conversation, db)
                db.commit()

                # Verificar que se actualizó correctamente
                updated_conv = await storage_service.get_conversation(
                    conversation_id, db
                )
                logger.info(
                    f"Metadatos actualizados después de regenerar PDF: has_proposal={updated_conv.metadata.get('has_proposal')}, pdf_path={updated_conv.metadata.get('pdf_path')}"
                )
            else:
                logger.error(
                    f"Regeneración de PDF falló para descarga directa de {conversation_id}"
                )
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo generar el PDF. Intente nuevamente.",
                )

        # Verificar si el archivo existe después de todo
        if not os.path.exists(pdf_path):
            logger.error(f"PDF no encontrado en el sistema de archivos: {pdf_path}")
            raise HTTPException(
                status_code=404,
                detail="El archivo PDF no fue encontrado en el servidor",
            )

        # Verificar permisos de lectura
        if not os.access(pdf_path, os.R_OK):
            logger.error(f"Permisos insuficientes para leer el PDF: {pdf_path}")
            try:
                logger.warning(f"Intentando corregir permisos de archivo para lectura")
                os.chmod(pdf_path, 0o644)  # rw-r--r--
            except Exception as e:
                logger.error(f"No se pudieron corregir permisos: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Error de permisos al acceder al archivo PDF",
                )

        # Preparar nombre personalizado
        client_name = conversation.metadata.get("client_name", "Cliente")
        if client_name == "Cliente" and "[" not in client_name:
            client_name = "Industrias_Agua_Pura"

        # Limpiar el nombre para asegurar que sea válido como nombre de archivo
        client_name = "".join(
            c if c.isalnum() or c in "_- " else "_" for c in client_name
        ).replace(" ", "_")

        # Generar nombre de archivo
        filename = f"Propuesta_Hydrous_{client_name}_{conversation_id[:8]}.pdf"
        logger.info(f"Enviando archivo PDF: {filename} desde {pdf_path}")

        # Verificar tamaño del archivo antes de enviarlo
        try:
            file_size = os.path.getsize(pdf_path)
            logger.info(f"Tamaño del archivo PDF: {file_size} bytes")
            if file_size == 0:
                logger.error(f"PDF tiene tamaño cero: {pdf_path}")
                raise HTTPException(status_code=500, detail="El archivo PDF está vacío")
        except OSError as e:
            logger.error(f"Error al obtener tamaño del archivo: {e}")

        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException as http_exc:
        logger.error(f"Error HTTP en descarga PDF: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error en descarga de PDF para {conversation_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Error procesando descarga: {str(e)[:100]}"
        )


# Endpoint para diagnóstico y reparación de conversación
@router.post("/{conversation_id}/diagnose")
async def diagnose_conversation(
    request: Request,
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """Diagnostica y repara una conversación con posibles problemas."""
    try:
        # Autenticación
        current_user = get_current_user(request)
        logger.info(
            f"Diagnóstico de conversación {conversation_id} solicitado por {current_user.get('email', 'desconocido')}"
        )

        # Cargar conversación
        conversation = await storage_service.get_conversation(conversation_id, db)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        # Verificar propiedad
        db_conversation = conversation_repository.get(db, UUID(conversation_id))
        if not db_conversation or str(db_conversation.user_id) != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para diagnosticar esta conversación",
            )

        # Recolectar información de diagnóstico
        diagnostico = {
            "id": conversation.id,
            "estado_original": {
                "is_complete": conversation.metadata.get("is_complete", False),
                "has_proposal": conversation.metadata.get("has_proposal", False),
                "pdf_path": conversation.metadata.get("pdf_path"),
                "proposal_text": bool(conversation.metadata.get("proposal_text")),
                "current_question_id": conversation.metadata.get("current_question_id"),
            },
            "mensajes_count": (
                len(conversation.messages) if conversation.messages else 0
            ),
            "datos_recolectados": bool(conversation.metadata.get("collected_data")),
        }

        # Intentar reparar inconsistencias
        reparaciones = []

        # Si está marcada como completa pero no tiene propuesta
        if conversation.metadata.get(
            "is_complete", False
        ) and not conversation.metadata.get("has_proposal", False):
            reparaciones.append(
                "Conversación marcada como completa sin propuesta generada"
            )

            # Intentar generar propuesta
            from app.services.direct_proposal_generator import direct_proposal_generator

            pdf_path = await direct_proposal_generator.generate_complete_proposal(
                conversation
            )

            if pdf_path and os.path.exists(pdf_path):
                conversation.metadata["pdf_path"] = pdf_path
                conversation.metadata["has_proposal"] = True
                reparaciones.append(f"Propuesta generada correctamente en {pdf_path}")
            else:
                reparaciones.append("No se pudo generar la propuesta automáticamente")

        # Si tiene ruta de PDF pero no está marcada como lista
        elif conversation.metadata.get("pdf_path") and not conversation.metadata.get(
            "has_proposal", False
        ):
            pdf_path = conversation.metadata.get("pdf_path")
            if os.path.exists(pdf_path):
                conversation.metadata["has_proposal"] = True
                reparaciones.append(
                    "Conversación reparada: marcada con propuesta disponible"
                )
            else:
                reparaciones.append(
                    f"Ruta de PDF existe pero archivo no encontrado: {pdf_path}"
                )

        # Guardar cambios
        if reparaciones:
            await storage_service.save_conversation(conversation, db)
            db.commit()

        # Recopilar estado final
        estado_final = {
            "is_complete": conversation.metadata.get("is_complete", False),
            "has_proposal": conversation.metadata.get("has_proposal", False),
            "pdf_path": conversation.metadata.get("pdf_path"),
            "existe_archivo": (
                os.path.exists(conversation.metadata.get("pdf_path", ""))
                if conversation.metadata.get("pdf_path")
                else False
            ),
        }

        # Devolver diagnóstico
        return {
            "diagnóstico": diagnostico,
            "reparaciones_realizadas": reparaciones,
            "estado_final": estado_final,
            "mensaje": (
                "Diagnóstico completado"
                if reparaciones
                else "No se requieren reparaciones"
            ),
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error en diagnóstico para {conversation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error en diagnóstico: {str(e)[:100]}"
        )
