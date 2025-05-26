from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.user import User
from app.models.user import UserCreate, UserInDB
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository
from app.repositories.interfaces.user_repository import IUserRepository


class UserRepositoryImpl(
    SQLAlchemyRepository[User, UserCreate, UserInDB], IUserRepository
):
    """Implementación del repositorio de usuarios"""

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()

    def get_by_email_or_id(
        self, db: Session, email: str = None, user_id: UUID = None
    ) -> Optional[User]:
        """Obtener usuario por email o ID"""
        if not email and not user_id:
            return None

        query = db.query(User)
        if email and user_id:
            return query.filter(or_(User.email == email, User.id == user_id)).first()
        elif email:
            return query.filter(User.email == email).first()
        else:
            return query.filter(User.id == user_id).first()

    def create_with_password(
        self, db: Session, *, obj_in: UserCreate, password_hash: str
    ) -> User:
        """Crear usuario con password hash"""
        db_obj = User(
            email=obj_in.email,
            password_hash=password_hash,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            company_name=obj_in.company_name,
            location=obj_in.location,
            sector=obj_in.sector,
            subsector=obj_in.subsector,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
