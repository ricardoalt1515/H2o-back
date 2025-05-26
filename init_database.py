#!/usr/bin/env python3
"""
Script para inicializar la base de datos del proyecto Hydrous
Este script crea todas las tablas necesarias en la base de datos
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_init")

# Importar modelos y configuraciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from app.db.models.declarations import Base
    from app.config import settings
    from app.db.models.user import User
    from app.db.models.conversation import Conversation, Message, ConversationMetadata
    from app.db.models.document import Document
    logger.info("Modelos importados correctamente")
except ImportError as e:
    logger.error(f"Error importando modelos: {e}")
    sys.exit(1)

def test_connection(engine):
    """Prueba la conexión a la base de datos"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Conexión a la base de datos exitosa: {result.scalar()}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return False

def init_database():
    """Inicializa la base de datos creando todas las tablas"""
    try:
        # Mostrar información sobre las variables de entorno relacionadas con la base de datos
        logger.info(f"POSTGRES_USER: {settings.POSTGRES_USER}")
        logger.info(f"POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
        logger.info(f"POSTGRES_PORT: {settings.POSTGRES_PORT}")
        logger.info(f"POSTGRES_DB: {settings.POSTGRES_DB}")
        
        # Crear motor de base de datos
        logger.info(f"Conectando a la base de datos: {settings.DATABASE_URL}")
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "application_name": "hydrous_init_script"
            }
        )
        
        # Probar conexión
        if not test_connection(engine):
            logger.error("No se pudo conectar a la base de datos")
            return False
        
        # Listar los modelos que se van a crear
        logger.info("Modelos que se crearán en la base de datos:")
        for model in Base.registry.mappers:
            logger.info(f"  - {model.class_.__name__}")
        
        # Crear todas las tablas
        logger.info("Creando todas las tablas...")
        try:
            Base.metadata.create_all(engine)
            logger.info("¡Tablas creadas exitosamente!")
        except SQLAlchemyError as e:
            logger.error(f"Error SQL al crear tablas: {type(e).__name__}: {str(e)}")
            return False
        
        # Verificar tablas creadas
        try:
            with engine.connect() as conn:
                tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                logger.info("Tablas en la base de datos:")
                for table in tables:
                    logger.info(f"  - {table[0]}")
        except SQLAlchemyError as e:
            logger.error(f"Error al verificar tablas creadas: {type(e).__name__}: {str(e)}")
            # No retornamos False aquí porque las tablas podrían haberse creado correctamente
        
        return True
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Iniciando script de inicialización de base de datos")
    success = init_database()
    if success:
        logger.info("Inicialización completada correctamente")
        sys.exit(0)
    else:
        logger.error("Error en la inicialización de la base de datos")
        sys.exit(1)
