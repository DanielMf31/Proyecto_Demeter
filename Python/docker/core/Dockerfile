FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for serial)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements or just install directly
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pyserial-asyncio \
    pydantic-settings \
    aiosqlite

# Copy the source code
COPY ./src /app/src
COPY .env /app/.env

# Add src to PYTHONPATH
ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "proyecto_demeter.server.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
