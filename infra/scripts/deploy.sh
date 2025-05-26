#!/bin/bash
# Script de despliegue automatizado para H₂O Allegiant

set -e

# Configuración
AWS_REGION="us-east-1"
ECR_REPOSITORY="hydrous"
ECS_CLUSTER="hydrous-cluster"
ECS_SERVICE="hydrous-service"
TASK_FAMILY="hydrous-task"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando despliegue de H₂O Allegiant...${NC}"

# 1. Autenticación con ECR
echo -e "\n${YELLOW}[1/5] Autenticando con Amazon ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Construir la imagen Docker
echo -e "\n${YELLOW}[2/5] Construyendo imagen Docker...${NC}"
docker build -t $ECR_REPOSITORY:latest -f Dockerfile.prod .

# 3. Etiquetar la imagen
echo -e "\n${YELLOW}[3/5] Etiquetando imagen...${NC}"
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 4. Subir la imagen a ECR
echo -e "\n${YELLOW}[4/5] Subiendo imagen a ECR...${NC}"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 5. Actualizar el servicio ECS
echo -e "\n${YELLOW}[5/5] Actualizando servicio ECS...${NC}"
aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment --region $AWS_REGION

echo -e "\n${GREEN}¡Despliegue completado con éxito!${NC}"
echo -e "Puedes monitorear el estado del despliegue en la consola de AWS ECS"
echo -e "URL de la aplicación: http://hydrous-alb-1088098552.us-east-1.elb.amazonaws.com"
