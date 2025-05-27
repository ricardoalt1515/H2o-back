#!/bin/bash
# dev.sh - Herramienta para gestionar el entorno de desarrollo local

# Colores para mejor legibilidad
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si Docker está ejecutándose
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker no está ejecutándose. Por favor inicia Docker Desktop.${NC}"
  exit 1
fi

case "$1" in
  start)
    echo -e "${BLUE}Iniciando entorno de desarrollo...${NC}"
    docker compose -f docker-compose.dev.yml up -d
    echo -e "${GREEN}✅ Entorno de desarrollo iniciado${NC}"
    echo -e "📊 API disponible en: ${BLUE}http://localhost:8000/docs${NC}"
    ;;
    
  stop)
    echo -e "${BLUE}Deteniendo entorno de desarrollo...${NC}"
    docker compose -f docker-compose.dev.yml down
    echo -e "${GREEN}✅ Entorno de desarrollo detenido${NC}"
    ;;
    
  logs)
    echo -e "${BLUE}Mostrando logs en tiempo real (Ctrl+C para salir)...${NC}"
    docker compose -f docker-compose.dev.yml logs -f
    ;;
    
  restart)
    echo -e "${BLUE}Reiniciando servicios...${NC}"
    docker compose -f docker-compose.dev.yml restart
    echo -e "${GREEN}✅ Servicios reiniciados${NC}"
    ;;
    
  reset-db)
    echo -e "${YELLOW}⚠️ Reiniciando base de datos (se perderán todos los datos)...${NC}"
    read -p "¿Estás seguro? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
      echo -e "${BLUE}Operación cancelada${NC}"
      exit 0
    fi
    docker compose -f docker-compose.dev.yml down -v
    docker compose -f docker-compose.dev.yml up -d postgres
    echo -e "${GREEN}✅ Base de datos reiniciada${NC}"
    ;;
    
  shell)
    echo -e "${BLUE}Abriendo shell en el contenedor de la aplicación...${NC}"
    docker compose -f docker-compose.dev.yml exec app bash
    ;;
    
  *)
    echo -e "${BLUE}Herramienta de desarrollo Hydrous${NC}"
    echo -e "Uso: ./dev.sh {start|stop|logs|restart|reset-db|shell}"
    echo -e "  ${YELLOW}start${NC}     : Inicia todos los servicios"
    echo -e "  ${YELLOW}stop${NC}      : Detiene todos los servicios"
    echo -e "  ${YELLOW}logs${NC}      : Muestra logs en tiempo real"
    echo -e "  ${YELLOW}restart${NC}   : Reinicia todos los servicios"
    echo -e "  ${YELLOW}reset-db${NC}  : Reinicia la base de datos (borra todos los datos)"
    echo -e "  ${YELLOW}shell${NC}     : Abre una terminal en el contenedor principal"
    ;;
esac
