from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.db.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.database_schemas import UserCreate, UserUpdate

logger = logging.getLogger("hydrous")


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtener un usuario por su email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error en get_by_email: {e}")
            return None

    def create_with_hashed_password(
        self, db: Session, *, obj_in: UserCreate, hashed_password: str
    ) -> Optional[User]:
        """Crear un usuario con contraseña hasheada"""
        try:
            logger.info(f"[USER_REPOSITORY] Iniciando creación de usuario: {obj_in.email}")
            
            # Crear diccionario con los datos
            user_data = {}
            if hasattr(obj_in, "model_dump"):
                # Si es un objeto Pydantic v2
                user_dict = obj_in.model_dump(exclude={"password"})
                logger.debug(f"[USER_REPOSITORY] Datos del modelo Pydantic v2: {user_dict}")
                for key, value in user_dict.items():
                    user_data[key] = value
            elif hasattr(obj_in, "dict"):
                # Si es un objeto Pydantic v1 (fallback)
                user_dict = obj_in.dict(exclude={"password"})
                logger.debug(f"[USER_REPOSITORY] Datos del modelo Pydantic v1: {user_dict}")
                for key, value in user_dict.items():
                    user_data[key] = value
            else:
                # Si es un diccionario
                logger.debug(f"[USER_REPOSITORY] Procesando como diccionario")
                for key, value in obj_in.items():
                    if key != "password":
                        user_data[key] = value

            # Añadir la contraseña hasheada
            user_data["password_hash"] = hashed_password
            
            logger.debug(f"[USER_REPOSITORY] Datos finales para crear usuario: {user_data}")
            logger.info(f"[USER_REPOSITORY] Intentando crear instancia de User con campos: {list(user_data.keys())}")

            db_obj = User(**user_data)
            db.add(db_obj)
            logger.info(f"[USER_REPOSITORY] Usuario añadido a la sesión, ejecutando commit...")
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"[USER_REPOSITORY] Usuario creado exitosamente con ID: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"[USER_REPOSITORY] Error SQLAlchemy en create_with_hashed_password: {e}")
            logger.error(f"[USER_REPOSITORY] Tipo de error: {type(e).__name__}")
            db.rollback()
            return None
        except Exception as e:
            logger.error(f"[USER_REPOSITORY] Error general en create_with_hashed_password: {e}")
            logger.error(f"[USER_REPOSITORY] Tipo de error: {type(e).__name__}")
            db.rollback()
            return None


# Instanciar repositorio
user_repository = UserRepository(User)
