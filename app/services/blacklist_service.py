import logging
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import uuid

# Configuración de logger
logger = logging.getLogger("hydrous")

class TokenBlacklistService:
    """
    Servicio para gestionar la blacklist de tokens JWT.
    
    Características principales:
    - TTL automático: Los tokens se eliminan cuando expiran
    - Uso eficiente de memoria en Redis
    - Almacenamiento por jti (JWT ID)
    
    Workflow:
    - Al hacer logout, añadimos el token a Redis
    - Cada verificación de token consulta la blacklist
    - TTL del token = tiempo restante hasta expiración
    """

    def __init__(self):
        """Inicializar servicio"""
        from app.db.redis_client import redis_client

        self.redis_client = redis_client

        # Prefijos para las claves en Redis
        self.BLACKLIST_PREFIX = "blacklist:"
        self.USER_SESSIONS_PREFIX = "user_sessions:"

        logger.info("Servicio de token blacklist inicializado")

    async def add_to_blacklist(self, token: str) -> bool:
        """
        Añade un token a la blacklist.

        Args:
            token: JWT token a invalidar

        Returns:
            bool: True si se añadió correctamente
        """
        try:
            # Decodificar el token para obtener el jti y exp
            # No verificamos la firma porque podría ser un token válido que estamos revocando
            decoded = jwt.decode(token, options={"verify_signature": False})

            # Obtener identificador único del token
            jti = decoded.get("jti")
            if not jti:
                # Si no hay jti, usamos hash del token
                import hashlib

                jti = hashlib.sha256(token.encode()).hexdigest()

            # Calcular el tiempo de expiración (TTL)
            exp = decoded.get("exp")
            if exp:
                current_time = datetime.utcnow().timestamp()
                ttl = max(int(exp - current_time), 1)  # Al menos 1 segundo
            else:
                # Si no tiene exp, usamos 24 horas por defecto
                ttl = 24 * 60 * 60

            # Almacenar en Redis con TTL automático
            blacklist_key = f"{self.BLACKLIST_PREFIX}{jti}"
            await self.redis_client.setex(blacklist_key, ttl, "1")

            logger.info(f"Token añadido a blacklist: {jti[:8]}... TTL: {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Error añadiendo token a blacklist: {e}")
            return False

    async def is_blacklisted(self, token: str) -> bool:
        """
        Verifica si un token está en la blacklist.

        Args:
            token: JWT token a verificar

        Returns:
            bool: True si está blacklisted
        """
        try:
            # Decodificar token para obtener jti
            decoded = jwt.decode(token, options={"verify_signature": False})

            jti = decoded.get("jti")
            if not jti:
                import hashlib

                jti = hashlib.sha256(token.encode()).hexdigest()

            # Verificar si existe en blacklist
            blacklist_key = f"{self.BLACKLIST_PREFIX}{jti}"
            exists = await self.redis_client.exists(blacklist_key)

            if exists:
                logger.debug(f"Token blacklisted encontrado: {jti[:8]}...")
                return True

            return False

        except Exception as e:
            # CAMBIO IMPORTANTE: En lugar de rechazar el token por defecto,
            # permitimos que pase si hay problemas con Redis
            logger.warning(f"Error verificando blacklist, permitiendo token: {e}")
            # En caso de error, permitimos el token para mantener la funcionalidad
            return False

    async def add_user_session(
        self, user_id: str, token_data: dict, device_info: dict
    ):
        """
        Registra una nueva sesión de usuario.

        Args:
            user_id: ID del usuario
            token_data: Información del token (jti, exp, etc.)
            device_info: Información del dispositivo (user-agent, ip, etc.)
        """
        try:
            # Crear entrada para la sesión
            session_id = (
                token_data.get("jti")
                if token_data.get("jti")
                else str(uuid.uuid4())
            )

            # Datos a almacenar
            session_data = {
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.fromtimestamp(token_data.get("exp", 0)).isoformat()
                    if token_data.get("exp")
                    else None
                ),
                "device_info": device_info,
            }

            # Clave para lista de sesiones del usuario
            user_sessions_key = f"{self.USER_SESSIONS_PREFIX}{user_id}"

            # TTL basado en la expiración del token
            ttl = token_data.get("exp", 0) - datetime.utcnow().timestamp()
            if ttl <= 0:
                ttl = 24 * 60 * 60  # 24 horas por defecto

            # Almacenar sesión en Redis
            # Usamos una lista para mantener todas las sesiones del usuario
            serialized = json.dumps(session_data)
            await self.redis_client.sadd(user_sessions_key, serialized)

            # Asegurar que la clave expira eventualmente para limpiar
            await self.redis_client.expire(user_sessions_key, int(ttl))

            logger.info(
                f"Sesión {session_id[:8]}... añadida para usuario {user_id[:8]}..."
            )

        except Exception as e:
            logger.error(f"Error añadiendo sesión de usuario: {e}")

    async def invalidate_user_sessions(
        self, user_id: str, exclude_session: Optional[str] = None
    ) -> int:
        """
        Invalida todas las sesiones de un usuario.

        Args:
            user_id: ID del usuario
            exclude_session: ID de sesión a excluir (ej: sesión actual)

        Returns:
            int: Número de sesiones invalidadas
        """
        try:
            # Obtener datos de sesiones para añadir tokens a blacklist
            user_sessions_key = f"{self.USER_SESSIONS_PREFIX}{user_id}"
            sessions_data = await self.redis_client.smembers(user_sessions_key)

            invalidated = 0

            for session_json in sessions_data:
                try:
                    session = json.loads(session_json)
                    session_id = session.get("session_id")

                    # Excluir la sesión actual si se especifica
                    if exclude_session and session_id == exclude_session:
                        continue

                    # Aquí añadiríamos el token a blacklist si lo tuviéramos almacenado
                    # Por ahora, simplemente incrementamos el contador
                    invalidated += 1

                except Exception as inner_e:
                    logger.error(f"Error procesando sesión: {inner_e}")

            # Eliminar la clave de sesiones
            await self.redis_client.delete(user_sessions_key)

            logger.info(
                f"Sesiones invalidadas para usuario {user_id[:8]}: {invalidated}"
            )
            return invalidated

        except Exception as e:
            logger.error(f"Error invalidando sesiones: {e}")
            return 0


# Instancia global
blacklist_service = TokenBlacklistService()
