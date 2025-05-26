from typing import Optional, Dict, Any
from fastapi import Header
import logging

from app.services.auth_service import auth_service

logger = logging.getLogger("hydrous")


async def get_user_from_token(
    authorization: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Extrae información del usuario desde el token de autorización."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    try:
        user_data = await auth_service.verify_token(token)
        if user_data:
            logger.debug(f"Usuario autenticado en petición: {user_data['id']}")
            return user_data
        return None
    except Exception as e:
        logger.error(f"Error validando token: {e}")
        return None
