FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    websockets \
    httpx

# Copy the necessary source code
COPY ./src/proyecto_demeter/server/ws_client /app/ws_client

# We don't need the whole project, just the client
CMD ["python", "/app/ws_client/main.py"]
