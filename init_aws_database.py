#!/usr/bin/env python3
"""
Script para inicializar la base de datos en AWS RDS
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
logger = logging.getLogger("db_init_aws")

# Configuración de la base de datos de AWS
RDS_USER = "hydrous"
RDS_PASSWORD = "hydrous_password"
RDS_HOST = "hydrous-db.cuj8q6augwwx.us-east-1.rds.amazonaws.com"
RDS_PORT = "5432"
RDS_DB = "hydrous_db"
DATABASE_URL = f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"

# Importar modelos y configuraciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from app.db.models.declarations import Base
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
        # Información de conexión
        logger.info(f"Conectando a: {RDS_HOST}:{RDS_PORT}/{RDS_DB} como {RDS_USER}")
        
        # Crear motor de base de datos
        logger.info(f"URL de conexión: {DATABASE_URL}")
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 20,
                "application_name": "hydrous_init_aws_script"
            }
        )
        
        # Probar conexión
        if not test_connection(engine):
            logger.error("No se pudo conectar a la base de datos RDS")
            return False
        
        # Listar los modelos que se van a crear
        logger.info("Modelos que se crearán en la base de datos:")
        for model in Base.registry.mappers:
            logger.info(f"  - {model.class_.__name__}")
        
        # Verificar si ya existen tablas
        try:
            with engine.connect() as conn:
                tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables_list = [table[0] for table in tables]
                if tables_list:
                    logger.info("Tablas existentes en la base de datos:")
                    for table in tables_list:
                        logger.info(f"  - {table}")
        except SQLAlchemyError as e:
            logger.error(f"Error al verificar tablas existentes: {type(e).__name__}: {str(e)}")
        
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
                logger.info("Tablas en la base de datos después de la inicialización:")
                for table in tables:
                    logger.info(f"  - {table[0]}")
        except SQLAlchemyError as e:
            logger.error(f"Error al verificar tablas creadas: {type(e).__name__}: {str(e)}")
        
        # Crear extensión pgvector si es necesario
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("Extensión 'vector' creada o ya existente")
        except SQLAlchemyError as e:
            logger.error(f"Error al crear extensión vector: {type(e).__name__}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Iniciando script de inicialización de base de datos en AWS RDS")
    success = init_database()
    if success:
        logger.info("Inicialización completada correctamente")
        sys.exit(0)
    else:
        logger.error("Error en la inicialización de la base de datos")
        sys.exit(1)
