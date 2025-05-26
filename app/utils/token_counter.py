# Añadir en app/utils/token_counter.py

import tiktoken
from typing import List, Dict, Union, Any, Optional


def count_tokens(messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> int:
    """
    Cuenta de forma precisa el número de tokens en una lista de mensajes para un modelo específico

    Args:
        messages: Lista de mensajes en formato {"role": "...", "content": "..."}
        model: Nombre del modelo para el que contar tokens

    Returns:
        int: Número de tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Para modelos no reconocidos, usar cl100k_base (encodificación general para GPT-3.5/4)
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0

    # Constantes para diferentes modelos
    if model.startswith(("gpt-3.5", "gpt-4")):
        # Cada mensaje tiene un overhead de tokens
        tokens_per_message = (
            4  # Cada mensaje sigue <im_start>{role/name}\n{content}<im_end>\n
        )
        tokens_per_name = 1  # Si hay un nombre, se añade 1 token

        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name

        # Cada respuesta tiene un overhead de tokens
        num_tokens += 3  # Cada respuesta es precedida por <im_start>assistant

    else:
        # Para otros modelos, simplemente sumamos los tokens de cada mensaje
        for message in messages:
            for key, value in message.items():
                if key == "content":
                    num_tokens += len(encoding.encode(value))

    return num_tokens


def estimate_cost(tokens: int, model: str = "gpt-3.5-turbo") -> float:
    """
    Estima el costo en USD para un número dado de tokens y modelo

    Args:
        tokens: Número de tokens
        model: Nombre del modelo

    Returns:
        float: Costo estimado en USD
    """
    # Precios aproximados por 1000 tokens (pueden cambiar)
    pricing = {
        "gpt-3.5-turbo": 0.002,
        "gpt-4": 0.06,
        "gpt-4-turbo": 0.03,
        "llama-3.1-8b-instant": 0.0003,
        "llama-3.1-70b": 0.0009,
        "gemini-pro": 0.0025,
    }

    # Usar el precio del modelo especificado o un precio por defecto
    price_per_1k = pricing.get(model, 0.005)

    # Calcular y devolver el costo
    return (tokens / 1000) * price_per_1k
