#!/bin/bash
set -e

# Colores para la salida
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración para Hydrous App en AWS
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="hydrous-backend"
ALB_DNS="hydrous-alb-1088098552.us-east-1.elb.amazonaws.com"

# Estos valores dependen de cómo hayas nombrado tus recursos en ECS
# Si no estás seguro, puedes consultar en la consola de AWS
ECS_CLUSTER_NAME="hydrous-cluster"   # Verifica este nombre en la consola de ECS
ECS_SERVICE_NAME="hydrous-service"   # Verifica este nombre en la consola de ECS

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
print_step "Iniciando proceso de despliegue a AWS"
echo "Región AWS: $AWS_REGION"
echo "Repositorio ECR: $ECR_REPOSITORY_NAME"
echo "Cluster ECS: $ECS_CLUSTER_NAME"
echo "Servicio ECS: $ECS_SERVICE_NAME"
echo ""

# Solicitar confirmación
read -p "¿Son correctos estos valores? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    echo "Por favor, edita este script con los valores correctos."
    exit 1
fi

# Paso 1: Construir la imagen Docker
print_step "Construyendo imagen Docker"
docker build -t $ECR_REPOSITORY_NAME:latest . || print_error "Error al construir la imagen Docker"
print_success "Imagen Docker construida correctamente"

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
docker tag $ECR_REPOSITORY_NAME:latest $ECR_REPOSITORY_URI:latest || print_error "Error al etiquetar la imagen"
docker push $ECR_REPOSITORY_URI:latest || print_error "Error al subir la imagen a ECR"
print_success "Imagen subida a ECR correctamente"

# Paso 5: Forzar nuevo despliegue en ECS
print_step "Actualizando servicio ECS"
aws ecs update-service --cluster $ECS_CLUSTER_NAME --service $ECS_SERVICE_NAME --force-new-deployment --region $AWS_REGION || print_error "Error al actualizar el servicio ECS"
print_success "Servicio ECS actualizado correctamente. El despliegue está en proceso..."

# Paso 6: Monitorear el despliegue
print_step "Monitoreo del despliegue"
echo "Puedes verificar el estado del despliegue en la consola AWS ECS o ejecutando:"
echo "aws ecs describe-services --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME --region $AWS_REGION"

print_success "¡Proceso de despliegue iniciado exitosamente!"
echo "La aplicación estará disponible en unos minutos en: https://api.h2oassistant.com"
echo "Recuerda verificar los logs en CloudWatch para asegurarte de que las tablas se inicializaron correctamente."
