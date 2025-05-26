#!/bin/bash
set -e

# Función para esperar a que un servicio esté disponible
wait_for() {
	echo "Esperando a que $1:$2 esté disponible..."
	until nc -z -v -w30 "$1" "$2"; do
		echo "Esperando a que $1:$2 esté disponible..."
		sleep 1
	done
	echo "$1:$2 ¡Disponible!"
}

# Esperar a que PostgreSQL esté disponible
wait_for "${POSTGRES_SERVER:-postgres}" "${POSTGRES_PORT:-5432}"

# Esperar a que Redis esté disponible (solo si REDIS_URL está configurado)
if [ -n "$REDIS_URL" ]; then
    # Extraer hostname y puerto de REDIS_URL
    REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        wait_for "$REDIS_HOST" "$REDIS_PORT"
    fi
fi

# Ejecutar el comando pasado a este script
exec "$@"
