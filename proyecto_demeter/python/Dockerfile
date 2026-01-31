# Build Stage
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias de compilación si es necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Runtime Stage (Imagen final ligera)
FROM python:3.11-slim

WORKDIR /app

# Copiar paquetes instalados desde builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copiar código fuente
COPY . .


# Asegurar que 'src' esté en el path para poder importar el paquete
ENV PYTHONPATH=/app/src

# Comando por defecto (usa el nombre del paquete dinámicamente)
CMD ["python", "-m", "proyecto_demeter.main"]
