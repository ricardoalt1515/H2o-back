from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session

from app.db.base import SessionLocal


@contextmanager
def unit_of_work() -> Generator[Session, None, None]:
    """Proporciona un contexto de transacción de base de datos"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
