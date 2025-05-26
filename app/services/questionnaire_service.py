# app/services/questionnaire_service.py
import logging
from typing import Optional, List, Dict, Any

# Quitar: from app.models.conversation_state import ConversationState
from app.services.questionnaire_data import QUESTIONNAIRE_STRUCTURE

# Quitar: import copy

logger = logging.getLogger("hydrous")


class QuestionnaireService:
    """Servicio simplificado para acceder a la estructura del cuestionario."""

    def __init__(self):
        self.structure = QUESTIONNAIRE_STRUCTURE
        self.all_questions_base: Dict[str, Dict[str, Any]] = self._flatten_questions()
        logger.info(
            f"Servicio de Cuestionario (Simplificado) inicializado con {len(self.all_questions_base)} preguntas base."
        )

    def _flatten_questions(self) -> Dict[str, Dict[str, Any]]:
        """Crea un diccionario plano de todas las preguntas por ID (sin cambios)."""
        # ... (La lógica de _flatten_questions se mantiene igual que antes) ...
        flat_questions = {}
        # Añadir preguntas iniciales
        for q in self.structure.get("initial_questions", []):
            if "id" in q:
                flat_questions[q["id"]] = q
            else:
                logger.error(
                    f"Pregunta inicial sin ID encontrada: {q.get('text', 'N/A')}"
                )

        # Añadir preguntas de sector/subsector
        for sector, subsectors in self.structure.get(
            "sector_questionnaires", {}
        ).items():
            for subsector, questions in subsectors.items():
                if not isinstance(questions, list):
                    logger.error(
                        f"Estructura inválida para {sector}/{subsector}. Se esperaba lista, se encontró {type(questions)}"
                    )
                    continue
                for q in questions:
                    if "id" in q:
                        flat_questions[q["id"]] = q
                    else:
                        logger.error(
                            f"Pregunta sin ID en {sector}/{subsector}: {q.get('text', 'N/A')}"
                        )
        return flat_questions

    def get_initial_greeting(self) -> str:
        """Devuelve el saludo inicial (sin cambios)."""
        return self.structure.get("initial_greeting", "¡Bienvenido!")

    def get_initial_question_id(self) -> Optional[str]:
        """Devuelve el ID de la primera pregunta inicial (sin cambios)."""
        initial_questions = self.structure.get("initial_questions", [])
        return (
            initial_questions[0]["id"]
            if initial_questions and "id" in initial_questions[0]
            else None
        )

    def get_question_details(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles BASE de una pregunta por su ID.
        NO resuelve condicionales ni formato aquí. Devuelve una copia.
        """
        question_base = self.all_questions_base.get(question_id)
        if not question_base:
            logger.error(
                f"get_question_details: No se encontró pregunta con ID: {question_id}"
            )
            return None
        # Devolver una copia para evitar modificaciones accidentales
        import copy

        return copy.deepcopy(question_base)

    # --- ELIMINAR LAS SIGUIENTES FUNCIONES ---
    # def get_question(...) # La que resolvía condicionales
    # def _determine_questionnaire_path(...)
    # def get_next_question_id(...)
    # def process_answer(...) # La lógica de procesamiento se hará en AI Service o chat.py
    # def format_question_for_display(...) # El LLM formateará
    # ----------------------------------------


# Instancia global simplificada
questionnaire_service = QuestionnaireService()
