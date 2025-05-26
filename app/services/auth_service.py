import logging
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from passlib.context import CryptContext
import uuid
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.user import UserCreate, UserInDB, User, TokenData
from app.repositories.user_repository import user_repository
from app.services.blacklist_service import blacklist_service
from app.db.base import get_db
from app.config import settings

# Configuración de logger
logger = logging.getLogger("hydrous")

# Configuración de hashing para passwords - Corregido
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class AuthService:
    """Servicio para manejo de autenticación y autorización"""

    # Configuración de JWT
    SECRET_KEY = "temporalsecretkey123456789"  # Cambiar en producción y usar settings
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

    def __init__(self):
        """Inicializador del servicio"""
        logger.info("Inicializando servicio de autenticación")

    def get_password_hash(self, password: str) -> str:
        """Genera hash seguro de contraseña"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña coincide con el hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, user_data: UserCreate, db: Session) -> User:
        """Crea un nuevo usuario en la base de datos"""
        try:
            logger.info(f"Creando usuario: {user_data.email}")
            logger.debug(f"Datos completos: {user_data.model_dump(exclude={'password'})}")
            
            # Verificar si el correo ya existe
            db_user = user_repository.get_by_email(db, email=user_data.email)
            if db_user:
                logger.warning(
                    f"Intento de registro con email duplicado: {user_data.email}"
                )
                raise ValueError("Email ya registrado")

            # Crear usuario con hash de contraseña
            hashed_password = self.get_password_hash(user_data.password)
            logger.debug(f"Hash de contraseña generado para {user_data.email}")
            
            db_user = user_repository.create_with_hashed_password(
                db, obj_in=user_data, hashed_password=hashed_password
            )

            if not db_user:
                logger.error(f"create_with_hashed_password retornó None para {user_data.email}")
                raise ValueError("Error al crear usuario en base de datos")

            # Log para debug
            logger.info(f"Usuario creado exitosamente: {db_user.id} - {db_user.email}")

            # Devolver versión pública (sin password_hash)
            return User(
                id=str(db_user.id),
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                company_name=db_user.company_name,
                location=db_user.location,
                sector=db_user.sector,
                subsector=db_user.subsector,
                created_at=db_user.created_at,
            )
        except Exception as e:
            logger.error(f"Error creando usuario: {str(e)}")
            raise

    def authenticate_user(
        self, email: str, password: str, db: Session
    ) -> Optional[User]:
        """Autentica un usuario por email y contraseña"""
        try:
            # Buscar usuario por email
            db_user = user_repository.get_by_email(db, email=email)

            if not db_user:
                logger.warning(f"Intento de login con email no encontrado: {email}")
                return None

            # Verificar contraseña
            if not self.verify_password(password, db_user.password_hash):
                logger.warning(f"Intento de login con contraseña incorrecta: {email}")
                return None

            # Devolver versión pública (sin password_hash)
            return User(
                id=str(db_user.id),
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                company_name=db_user.company_name,
                location=db_user.location,
                sector=db_user.sector,
                subsector=db_user.subsector,
                created_at=db_user.created_at,
            )
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            return None

    def create_access_token(self, user_id: str) -> TokenData:
        """Crea un token JWT para el usuario con jti para tracking"""
        try:
            # Configurar expiración
            expires_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            expires_at = datetime.utcnow() + expires_delta

            # Añadir jti (JWT ID) para poder rastrear el token
            jti = str(uuid.uuid4())

            # Datos a codificar en el token
            to_encode = {
                "sub": user_id,
                "exp": expires_at,
                "iat": datetime.utcnow(),
                "jti": jti,
            }

            # Crear token
            encoded_jwt = jwt.encode(
                to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
            )

            # Devolver datos del token
            return TokenData(
                access_token=encoded_jwt,
                token_type="bearer",
                user_id=user_id,
                expires_at=expires_at,
            )
        except Exception as e:
            logger.error(f"Error creando token: {str(e)}")
            raise

    async def verify_token(self, token: str, db: Session) -> Optional[Dict[str, Any]]:
        """Verifica y decodifica un token JWT"""
        try:
            # Verificar si el token esta en la blacklist
            if await blacklist_service.is_blacklisted(token):
                logger.warning("Token intentado pero esta en blacklist")
                return None

            # Decodificar token
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = payload.get("sub")

            if user_id is None:
                logger.warning("Token sin id de usuario")
                return None

            # Verificar si el usuario existe
            try:
                user_uuid = UUID(user_id)
                db_user = user_repository.get(db, id=user_uuid)
                if not db_user:
                    logger.warning(f"Token con id de usuario no existente: {user_id}")
                    return None
            except ValueError:
                logger.warning(f"ID de usuario inválido en token: {user_id}")
                return None

            # Devolver datos básicos del usuario (sin incluir password_hash)
            return {
                "id": user_id,
                "email": db_user.email,
                "first_name": db_user.first_name,
                "last_name": db_user.last_name,
                "company_name": db_user.company_name,
                "location": db_user.location,
                "sector": db_user.sector,
                "subsector": db_user.subsector,
            }
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token inválido")
            return None
        except Exception as e:
            logger.error(f"Error verificando token: {str(e)}")
            return None

    async def logout(self, token: str, user_id: str) -> bool:
        """
        Realiza logout invalidando el token actual.

        Args:
            token: JWT token a invalidar
            user_id: ID del usuario
        Returns:
            bool: True si logout exitoso
        """
        try:
            # Añadir token a blacklist
            await blacklist_service.add_to_blacklist(token)

            logger.info(f"Logout exitoso para usuario {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return False

    async def logout_all_devices(self, user_id: str, current_token: str) -> bool:
        """
        Cierra sesión en todos los dispositivos del usuario.
        
        Args:
            user_id: ID del usuario
            current_token: Token actual (se excluye de la invalidación)
            
        Returns:
            bool: True si logout exitoso
        """
        try:
            # Invalidar todas las sesiones del usuario
            invalidated = await blacklist_service.invalidate_user_sessions(
                user_id, 
                exclude_session=self._get_token_jti(current_token)
            )
            
            logger.info(f"Logout masivo: {invalidated} sesiones invalidadas para usuario {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error en logout masivo: {e}")
            return False
    
    def _get_token_jti(self, token: str) -> Optional[str]:
        """Extrae el jti de un token sin verificar la firma"""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded.get("jti")
        except:
            return None

    def get_user_by_id(self, user_id: str, db: Session) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        try:
            # Validar ID
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                logger.warning(f"ID de usuario inválido: {user_id}")
                return None

            db_user = user_repository.get(db, id=user_uuid)
            if not db_user:
                return None

            # Devolver versión pública
            return User(
                id=str(db_user.id),
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                company_name=db_user.company_name,
                location=db_user.location,
                sector=db_user.sector,
                subsector=db_user.subsector,
                created_at=db_user.created_at,
            )
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID: {str(e)}")
            return None


# Instancia global
auth_service = AuthService()
