from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Union
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.config import settings

# Configurar logger
logger = logging.getLogger("hydrous")

# Crear engine para usar en repositorios
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Definir tipos genéricos
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repositorio base con operaciones CRUD básicas
    """

    def __init__(self, model: Type[ModelType]):
        """Inicializa con el modelo SQLAlchemy"""
        self.model = model
        self.engine = engine  # Cambiado: guardamos directamente el engine

    def get_session(self):
        """Obtener una nueva sesión de base de datos"""
        return SessionLocal()

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """Obtener un registro por ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error en get: {e}")
            db.rollback()
            return None

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Obtener múltiples registros con paginación"""
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error en get_multi: {e}")
            db.rollback()
            return []

    def create(
        self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """Crear un nuevo registro"""
        try:
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.dict(exclude_unset=True)

            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error en create: {e}")
            db.rollback()
            return None

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        """Actualizar un registro existente"""
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)

            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error en update: {e}")
            db.rollback()
            return None

    def remove(self, db: Session, *, id: UUID) -> Optional[ModelType]:
        """Eliminar un registro"""
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except SQLAlchemyError as e:
            logger.error(f"Error en remove: {e}")
            db.rollback()
            return None
