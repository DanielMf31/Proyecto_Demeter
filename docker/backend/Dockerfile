FROM python:3.11-slim

WORKDIR /app

# Copy requirements from Python directory
COPY Python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to have access to projeto_demeter package
COPY . .

# Set PYTHONPATH to include the Python/src directory
ENV PYTHONPATH="/app/Python/src"

# Run the remote hub
CMD ["uvicorn", "proyecto_demeter.server.remote_hub.app:app", "--host", "0.0.0.0", "--port", "8000"]
