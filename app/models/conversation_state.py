from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class ConversationState(BaseModel):
    """
    Mantiene el estado actual del proceso del cuestionario para una conversación.
    """

    current_question_id: Optional[str] = None
    # Almacena las respuestas del usuario, clave: question_id, valor: respuesta procesada
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    selected_sector: Optional[str] = None
    selected_subsector: Optional[str] = None
    # La secuencia específica de IDs de preguntas para este usuario
    questionnaire_path: List[str] = Field(default_factory=list)
    # Para almacenar entidades clave extraídas (opcional pero útil)
    key_entities: Dict[str, Any] = Field(default_factory=dict)
    # Para indicar si el cuestionario se ha completado
    is_complete: bool = False

    def update_collected_data(self, question_id: str, answer: Any):
        """Actualiza los datos recolectados con una nueva respuesta."""
        self.collected_data[question_id] = answer
        # Opcional: Actualizar key_entities si la pregunta es relevante
        if question_id == "INIT_0":  # Asumiendo ID para nombre empresa
            self.key_entities["company_name"] = answer
        elif question_id == "INIT_1":  # Asumiendo ID para sector
            self.selected_sector = str(answer)
        elif question_id == "INIT_2":  # Asumiendo ID para subsector
            self.selected_subsector = str(answer)
        elif question_id == "DATA_1":  # Asumiendo ID para ubicación
            self.key_entities["location"] = answer
        # Añadir más lógica de extracción de entidades si es necesario

    def get_next_question_in_path(self) -> Optional[str]:
        """Obtiene el ID de la siguiente pregunta en la ruta definida."""
        if not self.questionnaire_path:
            return None
        if self.current_question_id is None:
            # Si no hay pregunta actual, devolver la primera de la ruta
            return self.questionnaire_path[0] if self.questionnaire_path else None

        try:
            current_index = self.questionnaire_path.index(self.current_question_id)
            if current_index + 1 < len(self.questionnaire_path):
                return self.questionnaire_path[current_index + 1]
            else:
                # Se llegó al final de la ruta
                self.is_complete = True
                return None
        except ValueError:
            # El ID actual no estaba en la ruta (esto no debería pasar)
            # Devolver el primero como fallback o manejar el error
            return self.questionnaire_path[0] if self.questionnaire_path else None
