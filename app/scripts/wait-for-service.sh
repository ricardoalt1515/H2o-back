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
wait_for postgres 5432

# Esperar a que Redis esté disponible
wait_for redis 6379

# Ejecutar el comando pasado a este script
exec "$@"
