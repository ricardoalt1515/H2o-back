from pydantic_settings import BaseSettings
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Configuración general
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "hydrous-backend"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    # URL del backend para enlaces absolutos
    BACKEND_URL: str = os.getenv(
        "BACKEND_URL", "https://api.h2oassistant.com"
    )

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Para desarrollo local
        "https://h2oassistant.com",
        "https://www.h2oassistant.com",  # Dominio principal de producción
        "https://hydrous-chat.vercel.app",  # Vercel deployment backup
        "*" if os.getenv("DEBUG", "False").lower() in ("true", "1", "t") else "",
    ]

    # Configuración IA - Añadimos compatibilidad con los nombres antiguos y nuevos
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    API_KEY: str = os.getenv(
        "OPENAI_API_KEY", os.getenv("GROQ_API_KEY", "")
    )  # Para compatibilidad

    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "gemma2-9b-it")
    MODEL: str = os.getenv(
        "MODEL", os.getenv("OPENAI_MODEL", os.getenv("GROQ_MODEL", "gpt-4o-mini"))
    )

    # Determinar URL de API basado en lo que esté disponible
    API_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # "openai" o "groq"

    @property
    def API_URL(self):
        if self.API_PROVIDER == "groq":
            return "https://api.groq.com/openai/v1/chat/completions"
        else:
            return "https://api.openai.com/v1/chat/completions"

    # Almacenamiento
    CONVERSATION_TIMEOUT: int = 60 * 60 * 24  # 24 horas
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    # PostgreSQL
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "hydrous")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "hydrous_password")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "hydrous_db")

    # URL de conexión SQLAlchemy
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://:redis_password@localhost:6379/0")

    # Seguridad
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "temporalsecretkey123456789")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")


# Crear instancia de configuración
settings = Settings()

# Asegurar que exista el directorio de uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
# Asegurar que exista el directorio de logs
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
