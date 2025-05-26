from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.db.base import get_db
from app.db.models.user import User

router = APIRouter()
logger = logging.getLogger("hydrous")

@router.get("/db-status")
def check_database_status(db: Session = Depends(get_db)):
    """Endpoint para verificar el estado de la base de datos"""
    try:
        # Test básico de conexión
        result = db.execute(text("SELECT 1 as test")).scalar()
        
        # Verificar tablas existentes
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = db.execute(tables_query).fetchall()
        
        # Verificar estructura de tabla users
        users_columns = []
        if any('users' in str(table[0]) for table in tables):
            columns_query = text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            columns = db.execute(columns_query).fetchall()
            users_columns = [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == "YES",
                    "default": col[3]
                } for col in columns
            ]
            
            # Contar usuarios
            user_count = db.query(User).count()
        else:
            user_count = None
        
        return {
            "status": "ok",
            "connection_test": result,
            "tables": [table[0] for table in tables],
            "users_table_exists": any('users' in str(table[0]) for table in tables),
            "users_columns": users_columns,
            "user_count": user_count
        }
        
    except Exception as e:
        logger.error(f"Error en diagnóstico de DB: {e}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.get("/user-sample")
def get_user_sample(db: Session = Depends(get_db)):
    """Obtener una muestra de usuarios para diagnóstico"""
    try:
        # Obtener primeros 5 usuarios (sin password_hash)
        users = db.query(User).limit(5).all()
        
        user_data = []
        for user in users:
            user_data.append({
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "has_password_hash": bool(user.password_hash)
            })
        
        return {
            "status": "ok",
            "total_users": db.query(User).count(),
            "sample_users": user_data
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo muestra de usuarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
