variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "hydrous"
}

variable "environment" {
  description = "Entorno de despliegue (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

# Variables de red
variable "vpc_cidr" {
  description = "CIDR para la VPC"
  type        = string
  default     = "172.31.0.0/16"
}

variable "availability_zones" {
  description = "Lista de zonas de disponibilidad a utilizar"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnets" {
  description = "CIDRs para subnets públicas"
  type        = list(string)
  default     = ["172.31.0.0/24", "172.31.1.0/24"]
}

variable "private_subnets" {
  description = "CIDRs para subnets privadas"
  type        = list(string)
  default     = ["172.31.2.0/24", "172.31.3.0/24"]
}

# Variables de Base de Datos
variable "db_name" {
  description = "Nombre de la base de datos"
  type        = string
  default     = "hydrous_db"
}

variable "db_username" {
  description = "Usuario de la base de datos"
  type        = string
  default     = "hydrous"
}

variable "db_password" {
  description = "Contraseña de la base de datos"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "Clase de instancia de RDS"
  type        = string
  default     = "db.t3.micro"
}

# Variables de Redis
variable "redis_node_type" {
  description = "Tipo de nodo para ElastiCache Redis"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_engine_version" {
  description = "Versión del motor Redis"
  type        = string
  default     = "6.0"
}

# Variables de ECS
variable "task_definition_cpu" {
  description = "Unidades de CPU para la definición de tarea"
  type        = string
  default     = "256"
}

variable "task_definition_memory" {
  description = "Memoria en MB para la definición de tarea"
  type        = string
  default     = "512"
}

# Variables para la aplicación
variable "api_domain" {
  description = "Dominio para la API"
  type        = string
  default     = "api.h2oassistant.com"
}

variable "app_domain" {
  description = "Dominio para la aplicación web"
  type        = string
  default     = "www.h2oassistant.com"
}

# Otras variables
variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {
    Project     = "H2O Allegiant"
    ManagedBy   = "Terraform"
  }
}
