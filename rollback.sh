#!/bin/bash
set -e

# Colores para la salida
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración para Hydrous App en AWS
AWS_REGION="us-east-1"
ECS_CLUSTER_NAME="hydrous-cluster"
ECS_SERVICE_NAME="hydrous-backend-service"
DEPLOY_LOG_DIR="deploy-logs"

# Función para imprimir mensajes
print_step() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Verificar si se proporcionó una versión específica
VERSION=$1
if [ -z "$VERSION" ]; then
    # Si no se proporciona versión, usar la última registrada
    LATEST_LOG=$(ls -t $DEPLOY_LOG_DIR/last-working-task-*.txt 2>/dev/null | head -n 1)
    
    if [ -z "$LATEST_LOG" ]; then
        print_error "No se encontró registro de despliegues anteriores. Ejecuta primero deploy-with-rollback.sh"
    fi
    
    VERSION=$(echo $LATEST_LOG | sed "s|$DEPLOY_LOG_DIR/last-working-task-\(.*\).txt|\1|")
    echo "Usando la última versión registrada: $VERSION"
fi

# Archivo de rollback para esta versión
ROLLBACK_FILE="$DEPLOY_LOG_DIR/last-working-task-$VERSION.txt"

# Verificar si existe el archivo
if [ ! -f "$ROLLBACK_FILE" ]; then
    print_error "No se encontró información de rollback para la versión $VERSION"
fi

# Obtener la definición de tarea anterior
LAST_WORKING_TASK=$(cat $ROLLBACK_FILE)
if [ -z "$LAST_WORKING_TASK" ]; then
    print_error "El archivo de rollback está vacío o no contiene una definición de tarea válida"
fi

print_step "Iniciando rollback a la versión anterior"
echo "Definición de tarea para rollback: $LAST_WORKING_TASK"
echo "Cluster: $ECS_CLUSTER_NAME"
echo "Servicio: $ECS_SERVICE_NAME"
echo ""

# Confirmar antes de proceder
read -p "¿Estás seguro de que quieres hacer rollback? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operación cancelada"
    exit 0
fi

# Realizar el rollback
print_step "Actualizando servicio ECS a la versión anterior"
aws ecs update-service \
    --cluster $ECS_CLUSTER_NAME \
    --service $ECS_SERVICE_NAME \
    --task-definition $LAST_WORKING_TASK \
    --force-new-deployment \
    --region $AWS_REGION || print_error "Error al actualizar el servicio ECS"

print_success "¡Rollback iniciado correctamente!"
echo "La aplicación volverá a la versión anterior en unos minutos."
echo "Para monitorear el progreso, ejecuta:"
echo "  aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --query 'services[0].deployments'"
