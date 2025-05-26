# Infraestructura H₂O Allegiant

## Estructura de directorios

```
infra/
├── ecs/                    # Definiciones de tareas ECS
│   ├── task-definition.json        # Definición de tarea actual
│   └── previous-task-definition.json # Definición de tarea anterior (referencia)
│
├── terraform/              # Infraestructura como Código (IaC)
│   ├── environments/       # Configuraciones específicas por entorno
│   │   ├── dev/            # Entorno de desarrollo
│   │   ├── staging/        # Entorno de pruebas
│   │   └── prod/           # Entorno de producción
│   │
│   ├── modules/            # Módulos reutilizables
│   │   ├── alb/            # Application Load Balancer
│   │   ├── database/       # RDS PostgreSQL
│   │   ├── ecr/            # Elastic Container Registry
│   │   ├── ecs/            # ECS Fargate
│   │   ├── networking/     # VPC, subnets, security groups
│   │   └── redis/          # ElastiCache Redis
│   │
│   ├── main.tf             # Configuración principal
│   ├── variables.tf        # Definición de variables
│   ├── outputs.tf          # Salidas
│   └── terraform.tfvars    # Valores de variables (no en control de versiones)
│
└── scripts/                # Scripts de automatización
    └── deploy.sh           # Script de despliegue
```

## Infraestructura actual

El proyecto H₂O Allegiant utiliza los siguientes servicios de AWS:

1. **Amazon RDS para PostgreSQL (db.t3.micro)**
   - Base de datos PostgreSQL con extensión pgvector
   - Almacenamiento de usuarios, conversaciones y embeddings

2. **Amazon ElastiCache para Redis (cache.t3.micro)**
   - Caché para mejorar rendimiento
   - Rate limiting
   - Gestión de sesiones

3. **Amazon ECR**
   - Registro de imágenes Docker

4. **Amazon ECS con Fargate**
   - Ejecución de contenedores sin servidor
   - Escalado automático

5. **Application Load Balancer**
   - Exponer la API
   - HTTPS y terminación SSL
   - Balanceo de carga
