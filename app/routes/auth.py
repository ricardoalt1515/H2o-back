from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
import logging
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr  # AÑADIDO: EmailStr
from sqlalchemy import text  # AÑADIDO: Para test de DB

from app.models.user import UserCreate, User, LoginRequest
from app.services.auth_service import auth_service
from app.services.password_reset_service import password_reset_service  # AÑADIDO
from app.db.base import get_db

# Configuración del logger
logger = logging.getLogger("hydrous")

# Crear router
router = APIRouter()

# MODELOS PARA RECUPERACIÓN DE CONTRASEÑA
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    try:
        # Log detallado de los datos recibidos (sin contraseña)
        logger.info(f"Iniciando registro para: {user_data.email}")
        logger.debug(f"Datos de registro recibidos: {user_data.model_dump(exclude={'password'})}")
        
        # Crear usuario
        user = auth_service.create_user(user_data, db)

        # Generar token
        token_data = auth_service.create_access_token(user.id)

        # Devolver datos de usuario y token
        return {
            "status": "success",
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company_name": user.company_name,
                "location": user.location,
                "sector": user.sector,
                "subsector": user.subsector,
            },
            "token": token_data.access_token,
            "token_type": token_data.token_type,
            "expires_at": token_data.expires_at.isoformat(),
        }
    except ValueError as ve:
        # Errores de validación (ej: email duplicado)
        logger.warning(f"Error de validación en registro: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Otros errores
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en el registro")


@router.post("/login", response_model=dict)
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión de usuario"""
    try:
        # Autenticar usuario
        user = auth_service.authenticate_user(login_data.email, login_data.password, db)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generar token
        token_data = auth_service.create_access_token(user.id)

        # Devolver datos de usuario y token
        return {
            "status": "success",
            "message": "Inicio de sesión exitoso",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company_name": user.company_name,
                "location": user.location,
                "sector": user.sector,
                "subsector": user.subsector,
            },
            "token": token_data.access_token,
            "token_type": token_data.token_type,
            "expires_at": token_data.expires_at.isoformat(),
        }
    except HTTPException:
        # Re-lanzar HTTPExceptions
        raise
    except Exception as e:
        # Otros errores
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en el inicio de sesión")


@router.get("/verify", response_model=dict)
async def verify_token(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Verifica si un token es válido"""
    try:
        # Verificar que hay un token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Token no proporcionado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extraer token
        token = authorization.replace("Bearer ", "")

        # Verificar token
        user_data = await auth_service.verify_token(token, db)

        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Devolver datos del usuario
        return {"status": "success", "message": "Token válido", "user": user_data}
    except HTTPException:
        # Re-lanzar HTTPExceptions
        raise
    except Exception as e:
        # Otros errores
        logger.error(f"Error en verificación de token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error verificando token")


@router.get("/me", response_model=dict)
async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Obtiene información del usuario actual"""
    try:
        # Verificar que hay un token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Token no proporcionado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extraer token
        token = authorization.replace("Bearer ", "")

        # Verificar token
        user_data = await auth_service.verify_token(token, db)

        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Obtener usuario completo
        user = auth_service.get_user_by_id(user_data["id"], db)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado",
            )

        # Devolver datos del usuario
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company_name": user.company_name,
                "location": user.location,
                "sector": user.sector,
                "subsector": user.subsector,
                "created_at": user.created_at.isoformat(),
            },
        }
    except HTTPException:
        # Re-lanzar HTTPExceptions
        raise
    except Exception as e:
        # Otros errores
        logger.error(f"Error obteniendo usuario actual: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo usuario")

# NUEVOS ENDPOINTS DE LOGOUT
@router.post("/logout", response_model=dict)
async def logout(request: Request, db: Session = Depends(get_db)):
    """Cierra sesión invalidando el token actual"""
    try:
        # Obtener el token del request
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Token no proporcionado"
            )
        
        token = authorization.replace("Bearer ", "")
        
        # Obtener usuario actual
        user_data = await auth_service.verify_token(token, db)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )
        
        # Realizar logout
        success = await auth_service.logout(token, user_data["id"])
        
        if success:
            return {
                "status": "success",
                "message": "Logout exitoso"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error durante logout"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        raise HTTPException(status_code=500, detail="Error en logout")

@router.post("/logout-all", response_model=dict)
async def logout_all_devices(request: Request, db: Session = Depends(get_db)):
    """Cierra sesión en todos los dispositivos del usuario"""
    try:
        # Obtener el token del request
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Token no proporcionado"
            )
        
        token = authorization.replace("Bearer ", "")
        
        # Obtener usuario actual
        user_data = await auth_service.verify_token(token, db)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )
        
        # Realizar logout masivo
        success = await auth_service.logout_all_devices(user_data["id"], token)
        
        if success:
            return {
                "status": "success",
                "message": "Sesión cerrada en todos los dispositivos"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error durante logout masivo"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en logout masivo: {e}")
        raise HTTPException(status_code=500, detail="Error en logout masivo")

# ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA
@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: PasswordResetRequest):
    """Solicita un enlace de recuperación de contraseña"""
    try:
        result = await password_reset_service.request_password_reset(request.email)
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=429 if "Demasiados" in result.get("error", "") else 400,
                detail=result["error"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en forgot_password: {e}")
        raise HTTPException(status_code=500, detail="Error procesando solicitud")

@router.get("/verify-reset-token/{token}", response_model=dict)
async def verify_reset_token(token: str):
    """Verifica si un token de reset es válido"""
    try:
        result = await password_reset_service.verify_reset_token(token)
        
        if result["valid"]:
            return {
                "status": "success",
                "valid": True,
                "message": "Token válido"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en verify_reset_token: {e}")
        raise HTTPException(status_code=500, detail="Error verificando token")

@router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordResetConfirm):
    """Completa el proceso de recuperación de contraseña"""
    try:
        result = await password_reset_service.reset_password(
            token=request.token,
            new_password=request.new_password
        )
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset_password: {e}")
        raise HTTPException(status_code=500, detail="Error reseteando contraseña")

# ENDPOINT DE DIAGNÓSTICO TEMPORAL
@router.get("/db-test")
async def test_database_connection(db: Session = Depends(get_db)):
    """Endpoint temporal para probar la conectividad a la base de datos"""
    try:
        # Probar conexión básica
        result = db.execute(text("SELECT 1 as test"))
        db_result = result.scalar()
        
        # Probar consulta a tabla de usuarios
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        
        return {
            "status": "success",
            "db_connection": "OK",
            "test_query": db_result,
            "user_count": user_count,
            "message": "Database connection is working"
        }
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")