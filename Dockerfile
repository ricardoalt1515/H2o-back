FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-traditional \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0

# Crear directorio para uploads y logs
RUN mkdir -p /app/uploads /app/logs

# Copiar aplicación y configuración de Gunicorn
COPY . .
COPY gunicorn_config.py .

# Script para esperar a que los servicios estén disponibles
COPY ./scripts/wait-for-services.sh /wait-for-services.sh
RUN dos2unix /wait-for-services.sh 2>/dev/null || true && chmod +x /wait-for-services.sh

# Puerto para la API
EXPOSE 8000

# Comando para producción con Gunicorn + Uvicorn
CMD ["/wait-for-services.sh", "gunicorn", "app.main:app", "-c", "gunicorn_config.py"]
