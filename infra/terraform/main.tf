provider "aws" {
  region = var.aws_region
}

# Módulo para red (VPC, subnets, security groups)
module "networking" {
  source = "./modules/networking"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  public_subnets      = var.public_subnets
  private_subnets     = var.private_subnets
}

# Módulo para base de datos PostgreSQL (RDS)
module "database" {
  source = "./modules/database"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  subnet_ids          = module.networking.private_subnet_ids
  security_group_ids  = [module.networking.db_security_group_id]
  
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  db_instance_class   = var.db_instance_class
}

# Módulo para Redis (ElastiCache)
module "redis" {
  source = "./modules/redis"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  subnet_ids          = module.networking.private_subnet_ids
  security_group_ids  = [module.networking.redis_security_group_id]
  
  redis_node_type     = var.redis_node_type
  redis_engine_version = var.redis_engine_version
}

# Módulo para ECS (Cluster, Service, Task Definition)
module "ecs" {
  source = "./modules/ecs"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  subnet_ids          = module.networking.public_subnet_ids
  security_group_ids  = [module.networking.app_security_group_id]
  
  ecr_repository_url  = module.ecr.repository_url
  task_definition_cpu = var.task_definition_cpu
  task_definition_memory = var.task_definition_memory
  
  db_host             = module.database.db_endpoint
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  
  redis_host          = module.redis.redis_endpoint
}

# Módulo para ECR (Repositorio de Docker)
module "ecr" {
  source = "./modules/ecr"
  
  project_name        = var.project_name
  environment         = var.environment
}

# Módulo para ALB (Application Load Balancer)
module "alb" {
  source = "./modules/alb"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  subnet_ids          = module.networking.public_subnet_ids
  security_group_ids  = [module.networking.alb_security_group_id]
  
  ecs_service_name    = module.ecs.service_name
  ecs_service_id      = module.ecs.service_id
}
