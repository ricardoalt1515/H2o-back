-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Establecer zona horaria
SET TIME ZONE 'UTC';

-- Configuración de esquema de base de datos
-- Las tablas se crearán con las migraciones Alembic
