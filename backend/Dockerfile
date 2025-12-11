# Imagen base ligera con Python 3.11; reduce superficie de ataque y tamaño
FROM python:3.11-slim

# Evita bytecode y buffer para logs deterministas en contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor para aislar la aplicación
WORKDIR /app

# Paquetes de sistema mínimos para compilar dependencias (limpieza al final)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copiamos solo requirements para aprovechar cache de capas en instalaciones
COPY requirements.txt /app/requirements.txt

# Instalación sin caché para reducir tamaño final de la imagen
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el código fuente del backend al contenedor
COPY . /app

# Exponemos el puerto HTTP usado por uvicorn en despliegues estándar
EXPOSE 8000

# Comando de arranque en producción; workers se pueden ajustar por entorno
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
