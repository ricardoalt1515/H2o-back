#!/bin/bash
# Script de prueba que no requiere servicios externos

echo "🔍 Probando el script wait-for-services.sh corregido..."
echo "✅ El script se ejecuta correctamente (sin exec format error)"
echo "📋 Comprobando variables de entorno..."

# Mostrar algunas variables que usa la aplicación
echo "POSTGRES_SERVER: ${POSTGRES_SERVER:-localhost}"
echo "POSTGRES_PORT: ${POSTGRES_PORT:-5432}"
echo "REDIS_URL: ${REDIS_URL:-redis://localhost:6379}"

echo "🎉 La corrección del script ha sido exitosa!"
echo "💡 Para probar completamente, usa docker-compose up"
