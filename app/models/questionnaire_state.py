# app/models/questionnaire_state.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class QuestionnaireState(BaseModel):
    """Modelo mejorado para mantener el estado del cuestionario y el contexto de la conversación"""

    # Sector y subsector seleccionados
    sector: Optional[str] = None
    subsector: Optional[str] = None

    # Índice de la pregunta actual
    current_question_index: int = 0

    # Respuestas almacenadas
    answers: Dict[str, Any] = Field(default_factory=dict)

    # Preguntas que se han presentado
    presented_questions: List[str] = Field(default_factory=list)

    # Entidades importantes extraídas
    key_entities: Dict[str, Any] = Field(default_factory=dict)

    # Si el cuestionario está completo
    is_complete: bool = False

    # Ultimo resumen presentado (indice)
    last_summary_at: int = 0

    def update_answer(self, question_id: str, answer: Any) -> None:
        """Actualiza la respuesta a una pregunta específica"""
        self.answers[question_id] = answer

        # Extraer entidades clave basadas en la pregunta
        if question_id == "nombre_empresa":
            self.key_entities["company_name"] = answer
        elif question_id == "ubicacion":
            self.key_entities["location"] = answer
        elif question_id == "cantidad_agua_consumida":
            self.key_entities["water_volume"] = answer
        elif question_id == "costo_agua":
            self.key_entities["water_cost"] = answer
        elif question_id == "presupuesto":
            self.key_entities["budget"] = answer
        # Se pueden añadir más mapeos según sea necesario

    def get_context_summary(self) -> str:
        """Genera un resumen del contexto actual para incluir en el prompt"""
        summary_parts = []

        # Añadir entidades clave
        for entity_name, value in self.key_entities.items():
            if value:
                summary_parts.append(f"{entity_name}: {value}")

        # Añadir sector/subsector si están definidos
        if self.sector:
            summary_parts.append(f"Sector: {self.sector}")
        if self.subsector:
            summary_parts.append(f"Subsector: {self.subsector}")

        # Añadir respuestas a preguntas clave
        for q_id, answer in self.answers.items():
            if (
                q_id not in ["nombre_empresa", "ubicacion"] and answer
            ):  # Evitar duplicados
                summary_parts.append(f"{q_id}: {answer}")

        return "\n".join(summary_parts)

    def should_present_summary(self) -> bool:
        """Determina si es momento de presentar un resumen"""
        # Presentar un resumen cada 3-4 preguntas
        if self.current_question_index > 0 and self.current_question_index % 3 == 0:
            # Verificar que no se haya presentado un resumen en esta posición antes
            if getattr(self, "last_summary_at", -1) != self.current_question_index:
                self.last_summary_at = self.current_question_index
                return True
        return False
