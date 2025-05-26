from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from pydantic import BaseModel

from app.db.base import Base
from app.repositories.base_repository import (
    BaseRepository,
    ModelType,
    CreateSchemaType,
    UpdateSchemaType,
)

# Configurar logger
logger = logging.getLogger("hydrous")


class SQLAlchemyRepository(
    BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    """
    Implementación SQLAlchemy del repositorio base
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

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
            raise

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
            raise

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
            raise
