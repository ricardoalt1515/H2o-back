from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Dict
import time
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("hydrous")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware que implementa rate limiting usando el algoritmo de "Token Bucket".

    ¿Cómo funciona Token Bucket?
    - Cada usuario tiene un "bucket" (cubo) con tokens
    - Cada petición consume 1 token
    - Los tokens se recargan a una tasa fija
    - Si no hay tokens, la petición se rechaza

    Ventajas:
    - Permite ráfagas cortas (burst)
    - Suaviza el tráfico a largo plazo
    - Fácil de implementar
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        per_user: bool = True,
    ):
        """
        Args:
            requests_per_minute: Peticiones permitidas por minuto
            burst_size: Máximo de peticiones en ráfaga
            per_user: Si True, límite por usuario. Si False, por IP
        """
        super().__init__(app)

        # Configuración del rate limiting
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.per_user = per_user

        # Tasa de recarga (tokens por segundo)
        self.refill_rate = requests_per_minute / 60.0

        # Almacén de buckets en memoria (en producción usar Redis)
        self.buckets: Dict[str, Dict] = {}

        # Limpieza periódica de buckets antiguos
        self._start_cleanup_task()

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Verifica y actualiza el rate limit para cada petición.
        """

        # 1. Determinar el identificador (usuario o IP)
        identifier = await self._get_identifier(request)

        # 2. Verificar rate limit
        allowed, retry_after = await self._check_rate_limit(identifier)

        if not allowed:
            # 3. Si se excedió el límite, devolver error 429
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit excedido. Espera {retry_after} segundos.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": retry_after,
                },
            )

        # 4. Petición permitida, continuar
        response = await call_next(request)

        # 5. Añadir headers informativos sobre rate limit
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            int(self.buckets[identifier]["tokens"])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(self.buckets[identifier]["next_refill"])
        )

        return response

    async def _get_identifier(self, request: Request) -> str:
        """
        Obtiene el identificador para rate limiting.

        Returns:
            - ID del usuario si está autenticado y per_user=True
            - IP del cliente en caso contrario
        """
        if self.per_user and hasattr(request.state, "user") and request.state.user:
            # Rate limit por usuario autenticado
            return f"user:{request.state.user['id']}"
        else:
            # Rate limit por IP
            client_host = request.client.host if request.client else "unknown"
            return f"ip:{client_host}"

    async def _check_rate_limit(self, identifier: str) -> tuple[bool, float]:
        """
        Implementa el algoritmo Token Bucket.

        Returns:
            tuple: (allowed: bool, retry_after: float)
        """
        current_time = time.time()

        # Inicializar bucket si no existe
        if identifier not in self.buckets:
            self.buckets[identifier] = {
                "tokens": self.burst_size,
                "last_refill": current_time,
                "next_refill": current_time + 1.0 / self.refill_rate,
            }

        bucket = self.buckets[identifier]

        # Calcular cuántos tokens añadir desde la última recarga
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * self.refill_rate

        # Añadir tokens (sin exceder el burst_size)
        bucket["tokens"] = min(self.burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Verificar si hay tokens disponibles
        if bucket["tokens"] >= 1:
            # Consumir un token
            bucket["tokens"] -= 1

            # Actualizar tiempo de siguiente recarga completa
            if bucket["tokens"] == 0:
                bucket["next_refill"] = current_time + 1.0 / self.refill_rate

            return True, 0
        else:
            # No hay tokens, calcular tiempo de espera
            tokens_needed = 1 - bucket["tokens"]
            retry_after = tokens_needed / self.refill_rate

            logger.warning(
                f"Rate limit excedido para {identifier}. "
                f"Retry after: {retry_after:.2f} segundos"
            )

            return False, retry_after

    def _start_cleanup_task(self):
        """
        Inicia tarea de limpieza de buckets antiguos para evitar memory leaks.
        """

        async def cleanup():
            while True:
                await asyncio.sleep(300)  # Limpiar cada 5 minutos
                current_time = time.time()

                # Remover buckets inactivos por más de 1 hora
                expired_identifiers = [
                    identifier
                    for identifier, bucket in self.buckets.items()
                    if current_time - bucket["last_refill"] > 3600
                ]

                for identifier in expired_identifiers:
                    del self.buckets[identifier]

                logger.debug(
                    f"Rate limit cleanup: {len(expired_identifiers)} buckets removidos"
                )

        # Ejecutar tarea de limpieza en background
        asyncio.create_task(cleanup())
