# gunicorn_config.py
# Configuración para Gunicorn + Uvicorn

# Número de workers basado en núcleos de CPU (ajusta según tu servidor)
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1

# Usar el worker de Uvicorn
worker_class = 'uvicorn.workers.UvicornWorker'

# Tiempo máximo de espera (en segundos)
timeout = 120

# Mantener conexiones vivas
keepalive = 5

# Dirección de escucha
bind = '0.0.0.0:8000'

# Nivel de log
loglevel = 'info'

# Archivo de logs
accesslog = 'gunicorn_access.log'
errorlog = 'gunicorn_error.log'

# Configuración para manejo de múltiples peticiones
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
