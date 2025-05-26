from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.models.user import UserCreate, UserInDB
from app.repositories.base_repository import BaseRepository


class IUserRepository(BaseRepository[User, UserCreate, UserInDB], ABC):
    """Interfaz para repositorio de usuarios"""

    @abstractmethod
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        pass

    @abstractmethod
    def create_with_password(
        self, db: Session, *, obj_in: UserCreate, password_hash: str
    ) -> User:
        """Crear usuario con password hash"""
        pass
