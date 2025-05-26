import secrets
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import redis.asyncio as redis

from app.config import settings
from app.services.auth_service import auth_service
from app.repositories.user_repository import user_repository

logger = logging.getLogger("hydrous")


class PasswordResetService:
    """
    Servicio para gestionar la recuperación de contraseñas.

    Flujo de seguridad:
    1. Usuario solicita reset con su email
    2. Sistema genera token único con expiración
    3. Se envía email con enlace seguro
    4. Usuario hace clic → valida token
    5. Permite cambiar contraseña
    6. Token se invalida inmediatamente
    """

    def __init__(self):
        # Cliente Redis para almacenar tokens temporales
        redis_url = (
            settings.REDIS_URL
            if hasattr(settings, "REDIS_URL")
            else "redis://localhost:6379"
        )
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

        # Prefijo para keys de reset
        self.RESET_TOKEN_PREFIX = "password_reset:"

        # Configuración de email
        self.smtp_server = (
            settings.SMTP_SERVER if hasattr(settings, "SMTP_SERVER") else "localhost"
        )
        self.smtp_port = settings.SMTP_PORT if hasattr(settings, "SMTP_PORT") else 587
        self.smtp_user = settings.SMTP_USER if hasattr(settings, "SMTP_USER") else ""
        self.smtp_password = (
            settings.SMTP_PASSWORD if hasattr(settings, "SMTP_PASSWORD") else ""
        )
        self.from_email = (
            settings.FROM_EMAIL
            if hasattr(settings, "FROM_EMAIL")
            else "noreply@hydrous.com"
        )

        # Configuración de tokens
        self.token_expiration_hours = 1  # Tokens expiran en 1 hora
        self.max_attempts_per_hour = 3  # Máximo 3 intentos por hora por email

    async def request_password_reset(self, email: str) -> Dict[str, any]:
        """
        Inicia el proceso de recuperación de contraseña.

        Args:
            email: Email del usuario que solicita el reset

        Returns:
            Dict con el resultado de la operación
        """
        try:
            # 1. Verificar que el usuario existe
            user = user_repository.get_by_email(self._get_db(), email)
            if not user:
                # Por seguridad, no revelamos si el email existe o no
                # pero limitamos intentos para prevenir enumeración
                await self._track_failed_attempt(email)
                return {
                    "success": True,
                    "message": "Si el email existe, recibirás un enlace de recuperación",
                }

            # 2. Verificar límite de intentos
            if not await self._check_rate_limit(email):
                logger.warning(f"Rate limit excedido para password reset: {email}")
                return {
                    "success": False,
                    "error": "Demasiados intentos. Espera 1 hora.",
                }

            # 3. Generar token seguro
            reset_token = self._generate_reset_token()

            # 4. Almacenar token con expiración
            await self._store_reset_token(
                email=email, token=reset_token, user_id=str(user.id)
            )

            # 5. Enviar email
            await self._send_reset_email(
                to_email=email, reset_token=reset_token, user_name=user.first_name
            )

            logger.info(f"Password reset solicitado para: {email}")

            return {
                "success": True,
                "message": "Si el email existe, recibirás un enlace de recuperación",
            }

        except Exception as e:
            logger.error(f"Error en request_password_reset: {e}")
            return {"success": False, "error": "Error procesando solicitud"}

    async def verify_reset_token(self, token: str) -> Dict[str, any]:
        """
        Verifica si un token de reset es válido.

        Args:
            token: Token a verificar

        Returns:
            Dict con información del token si es válido
        """
        try:
            # Buscar token en Redis
            reset_key = f"{self.RESET_TOKEN_PREFIX}{token}"
            token_data = await self.redis_client.get(reset_key)

            if not token_data:
                return {"valid": False, "error": "Token inválido o expirado"}

            # Parsear datos del token
            import json

            token_info = json.loads(token_data)

            return {
                "valid": True,
                "email": token_info["email"],
                "user_id": token_info["user_id"],
                "created_at": token_info["created_at"],
            }

        except Exception as e:
            logger.error(f"Error en verify_reset_token: {e}")
            return {"valid": False, "error": "Error verificando token"}

    async def reset_password(self, token: str, new_password: str) -> Dict[str, any]:
        """
        Completa el reset de contraseña con un token válido.

        Args:
            token: Token de reset válido
            new_password: Nueva contraseña del usuario

        Returns:
            Dict con el resultado de la operación
        """
        try:
            # 1. Verificar token
            token_info = await self.verify_reset_token(token)
            if not token_info.get("valid"):
                return {
                    "success": False,
                    "error": token_info.get("error", "Token inválido"),
                }

            # 2. Obtener usuario
            user = user_repository.get(self._get_db(), token_info["user_id"])
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}

            # 3. Validar nueva contraseña
            password_validation = self._validate_password(new_password)
            if not password_validation["valid"]:
                return {"success": False, "error": password_validation["error"]}

            # 4. Hashear nueva contraseña
            hashed_password = auth_service.get_password_hash(new_password)

            # 5. Actualizar contraseña en BD
            user.password_hash = hashed_password
            self._get_db().commit()

            # 6. Invalidar token
            reset_key = f"{self.RESET_TOKEN_PREFIX}{token}"
            await self.redis_client.delete(reset_key)

            # 7. Invalidar todas las sesiones del usuario (logout forzado)
            from app.services.blacklist_service import blacklist_service

            await blacklist_service.invalidate_user_sessions(str(user.id))

            logger.info(f"Password reset completado para usuario: {user.id}")

            return {"success": True, "message": "Contraseña actualizada exitosamente"}

        except Exception as e:
            logger.error(f"Error en reset_password: {e}")
            return {"success": False, "error": "Error procesando reset de contraseña"}

    def _generate_reset_token(self) -> str:
        """
        Genera un token seguro para reset de contraseña.

        Características:
        - 32 bytes de entropía
        - URL-safe
        - Único y aleatorio
        """
        return secrets.token_urlsafe(32)

    async def _store_reset_token(self, email: str, token: str, user_id: str):
        """
        Almacena un token de reset en Redis con expiración.
        """
        try:
            # Key para el token
            reset_key = f"{self.RESET_TOKEN_PREFIX}{token}"

            # Datos del token
            token_data = {
                "email": email,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "token": token,
            }

            # Almacenar con expiración
            expiration_seconds = self.token_expiration_hours * 3600
            await self.redis_client.setex(
                reset_key, expiration_seconds, json.dumps(token_data)
            )

            # También almacenar por email para rate limiting
            email_key = f"reset_attempts:{email}"
            await self.redis_client.incr(email_key)
            await self.redis_client.expire(email_key, 3600)  # 1 hora

        except Exception as e:
            logger.error(f"Error almacenando reset token: {e}")
            raise

    async def _send_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """
        Envía el email de recuperación de contraseña.
        """
        try:
            # Construir URL de reset
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

            # Crear mensaje
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = "Recuperación de contraseña - Hydrous"

            # Cuerpo del email
            body = f"""
            Hola {user_name},
            
            Has solicitado recuperar tu contraseña de Hydrous. 
            
            Haz clic en el siguiente enlace para crear una nueva contraseña:
            {reset_url}
            
            Este enlace expirará en {self.token_expiration_hours} hora(s).
            
            Si no solicitaste este cambio, puedes ignorar este mensaje.
            
            Saludos,
            El equipo de Hydrous
            """

            message.attach(MIMEText(body, "plain"))

            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(message)

            logger.info(f"Email de reset enviado a: {to_email}")

        except Exception as e:
            logger.error(f"Error enviando email de reset: {e}")
            raise

    async def _check_rate_limit(self, email: str) -> bool:
        """
        Verifica si el email ha excedido el límite de intentos.
        """
        try:
            email_key = f"reset_attempts:{email}"
            attempts = await self.redis_client.get(email_key)

            if attempts and int(attempts) >= self.max_attempts_per_hour:
                return False

            return True

        except Exception as e:
            logger.error(f"Error verificando rate limit: {e}")
            return False

    async def _track_failed_attempt(self, email: str):
        """
        Registra un intento fallido de reset.
        """
        try:
            email_key = f"reset_attempts:{email}"
            await self.redis_client.incr(email_key)
            await self.redis_client.expire(email_key, 3600)
        except Exception as e:
            logger.error(f"Error tracking failed attempt: {e}")

    def _validate_password(self, password: str) -> Dict[str, any]:
        """
        Valida que una contraseña cumpla con los requisitos de seguridad.
        """
        if len(password) < 8:
            return {
                "valid": False,
                "error": "La contraseña debe tener al menos 8 caracteres",
            }

        if not any(c.isupper() for c in password):
            return {
                "valid": False,
                "error": "La contraseña debe contener al menos una mayúscula",
            }

        if not any(c.islower() for c in password):
            return {
                "valid": False,
                "error": "La contraseña debe contener al menos una minúscula",
            }

        if not any(c.isdigit() for c in password):
            return {
                "valid": False,
                "error": "La contraseña debe contener al menos un número",
            }

        return {"valid": True}

    def _get_db(self):
        """Helper para obtener sesión de base de datos"""
        from app.db.base import SessionLocal

        return SessionLocal()


# Instancia global
password_reset_service = PasswordResetService()
