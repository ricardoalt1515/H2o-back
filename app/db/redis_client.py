import os
import logging
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger("hydrous")

# Configuración de Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
IGNORE_REDIS_ERRORS = os.getenv("IGNORE_REDIS_ERRORS", "True").lower() == "true"

# Inicializar el cliente de Redis
try:
    redis_client = redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    logger.info(f"Cliente Redis inicializado en {REDIS_URL}")
except Exception as e:
    logger.error(f"Error al inicializar Redis: {e}")
    if not IGNORE_REDIS_ERRORS:
        raise
    # Si IGNORE_REDIS_ERRORS es True, creamos un cliente simulado
    class MockRedis:
        """Clase simulada de Redis para cuando hay errores y se permite ignorarlos"""
        async def get(self, *args, **kwargs):
            return None
        
        async def setex(self, *args, **kwargs):
            return True
            
        async def exists(self, *args, **kwargs):
            return 0
            
        async def delete(self, *args, **kwargs):
            return 0
            
        async def smembers(self, *args, **kwargs):
            return set()
            
        async def sadd(self, *args, **kwargs):
            return 0
            
        async def expire(self, *args, **kwargs):
            return True
            
        async def incr(self, *args, **kwargs):
            return 1
            
        async def get(self, *args, **kwargs):
            return None
    
    redis_client = MockRedis()
    logger.warning("Usando cliente Redis simulado debido a un error de conexión")
