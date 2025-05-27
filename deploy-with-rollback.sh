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
ECR_REPOSITORY_NAME="hydrous-backend"
ECS_CLUSTER_NAME="hydrous-cluster"
ECS_SERVICE_NAME="hydrous-backend-service"
TASK_FAMILY="hydrous-backend-task"

# Crear versión con timestamp para la imagen
VERSION=$(date +%Y%m%d%H%M)
DEPLOY_LOG_DIR="deploy-logs"
mkdir -p $DEPLOY_LOG_DIR

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

# Inicio del despliegue
print_step "Iniciando despliegue v$VERSION"
echo "Región AWS: $AWS_REGION"
echo "Repositorio ECR: $ECR_REPOSITORY_NAME"
echo "Cluster ECS: $ECS_CLUSTER_NAME"
echo "Servicio ECS: $ECS_SERVICE_NAME"
echo ""

# Paso 0: Guardar información de la versión actual para posible rollback
print_step "Guardando información para rollback"
CURRENT_TASK_DEF=$(aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --query 'services[0].taskDefinition' --output text)
echo "Definición de tarea actual: $CURRENT_TASK_DEF"
echo $CURRENT_TASK_DEF > $DEPLOY_LOG_DIR/last-working-task-$VERSION.txt
print_success "Información de rollback guardada en $DEPLOY_LOG_DIR/last-working-task-$VERSION.txt"

# Paso 1: Construir la imagen Docker
print_step "Construyendo imagen Docker"
docker build -t $ECR_REPOSITORY_NAME:$VERSION . || print_error "Error al construir la imagen Docker"
docker tag $ECR_REPOSITORY_NAME:$VERSION $ECR_REPOSITORY_NAME:latest
print_success "Imagen Docker construida correctamente: $ECR_REPOSITORY_NAME:$VERSION"

# Paso 2: Obtener login para ECR
print_step "Autenticando con AWS ECR"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com || print_error "Error al autenticar con ECR"
print_success "Autenticación con ECR exitosa"

# Paso 3: Verificar si el repositorio existe, si no, crearlo
print_step "Verificando repositorio ECR"
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION > /dev/null 2>&1 || aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION || print_error "Error al verificar/crear repositorio ECR"
print_success "Repositorio ECR verificado/creado"

# Paso 4: Etiquetar y subir la imagen
print_step "Subiendo imagen a ECR"
ECR_REPOSITORY_URI=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text)
docker tag $ECR_REPOSITORY_NAME:$VERSION $ECR_REPOSITORY_URI:$VERSION || print_error "Error al etiquetar la imagen con versión"
docker tag $ECR_REPOSITORY_NAME:$VERSION $ECR_REPOSITORY_URI:latest || print_error "Error al etiquetar la imagen como latest"

docker push $ECR_REPOSITORY_URI:$VERSION || print_error "Error al subir la imagen con versión a ECR"
docker push $ECR_REPOSITORY_URI:latest || print_error "Error al subir la imagen latest a ECR"
print_success "Imagen subida a ECR correctamente como $ECR_REPOSITORY_URI:$VERSION y $ECR_REPOSITORY_URI:latest"

# Paso 5: Registrar la información de versión para futura referencia
echo "$(date +"%Y-%m-%d %H:%M:%S") - Versión $VERSION desplegada - Task: $CURRENT_TASK_DEF" >> $DEPLOY_LOG_DIR/deploy-history.log
print_success "Historial de despliegue actualizado"

# Paso 6: Forzar nuevo despliegue en ECS
print_step "Actualizando servicio ECS"
aws ecs update-service --cluster $ECS_CLUSTER_NAME --service $ECS_SERVICE_NAME --force-new-deployment --region $AWS_REGION || print_error "Error al actualizar el servicio ECS"
print_success "Servicio ECS actualizado correctamente. El despliegue está en proceso..."

# Paso 7: Instrucciones de monitoreo y rollback
echo ""
print_step "Monitoreo y Rollback"
echo "Para monitorear el despliegue, ejecuta:"
echo "  aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --query 'services[0].deployments'"
echo ""
echo "Para hacer rollback a la versión anterior si es necesario, ejecuta:"
echo "  ./rollback.sh $VERSION"
echo ""

print_success "¡Proceso de despliegue iniciado exitosamente!"
echo "La aplicación estará disponible en unos minutos en: https://api.h2oassistant.com"
echo "Versión desplegada: $VERSION"
