import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.config import settings


def setup_logging():
    """Configura el sistema de logging para la aplicación."""
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Nivel de log basado en configuración
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configurar el logger raíz
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Eliminar manejadores existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formato de los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Manejador para archivo de log
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Manejador para consola (solo en desarrollo)
    if settings.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Configurar nivel de log para bibliotecas de terceros
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    
    logger.info("Configuración de logging inicializada")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtiene un logger configurado.
    
    Args:
        name: Nombre del logger. Si es None, devuelve el logger raíz.
    """
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
