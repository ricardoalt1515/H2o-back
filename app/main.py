# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routes import chat, documents, feedback, auth, diagnostic
from app.config import settings
from app.db.models.declarations import Base
from app.db.base import engine

# Inicializar la base de datos (crear tablas si no existen)
logger = logging.getLogger("hydrous")
logger.info("Verificando e inicializando tablas de la base de datos...")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("¡Tablas inicializadas correctamente!")
except Exception as e:
    logger.error(f"Error al inicializar tablas: {e}")

# Importar middlewares
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware

# Configuración de logging
from app.core.logging_config import get_logger

# Configurar logging (ya inicializado arriba)
logger = get_logger("hydrous")

# Asegurarse de que el directorio de uploads existe
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Inicializar aplicación
app = FastAPI(
    title="Hydrous AI Chatbot API",
    description="Backend para el chatbot de soluciones de agua Hydrous",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    allow_origin_regex=r"https://.*\.hostingersite\.com$|https://ricardoalt1515\.github\.io$|http://localhost:.*$|https://(www\.)?h2oassistant\.com$",
)

# Middleware de autenticación
app.add_middleware(AuthMiddleware)

# Rate limiting
app.add_middleware(
    RateLimitMiddleware, requests_per_minute=60, burst_size=10, per_user=True
)

# Incluir rutas
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(
    documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"]
)
app.include_router(
    feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"]
)
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(diagnostic.router, prefix=f"{settings.API_V1_STR}/diagnostic", tags=["diagnostic"])


@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {"status": "ok", "version": app.version}

@app.get("/alb-health")
async def alb_health_check():
    """Endpoint de salud específico para el ALB (sin /api prefix)"""
    return "OK"


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
