from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Crear motor de SQLAlchemy
engine = create_engine(settings.DATABASE_URL)

# Crear clase de sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Importar Base desde declarations.py
from app.db.models.declarations import Base


# Función para usar en dependencias de FastAPI
def get_db():
    """Dependencia para obtener sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para obtener sesión directa (para scripts)
def get_db_session():
    """Obtener sesión directa de base de datos para scripts."""
    return SessionLocal()
