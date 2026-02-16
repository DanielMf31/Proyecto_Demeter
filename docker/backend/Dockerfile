FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn websockets pydantic

COPY ./src/proyecto_demeter/server/remote_hub /app/remote_hub

EXPOSE 8000

CMD ["uvicorn", "remote_hub.app:app", "--host", "0.0.0.0", "--port", "8000"]
