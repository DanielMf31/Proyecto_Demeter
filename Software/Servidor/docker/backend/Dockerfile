FROM python:3.11-slim

WORKDIR /app

# 1. Install Dependencies
# Copy requirements from Backend
COPY Software/Servidor/Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy Code
# Copy Common (Standardized Config)
COPY Software/Common /app/Software/Common

# Copy Backend Code
COPY Software/Servidor/Backend /app/Software/Servidor/Backend

# 3. Environment
# Set PYTHONPATH to include Backend and Common
ENV PYTHONPATH="/app/Software/Servidor/Backend:/app/Software/Common"
# ENV PORT=8000 (Optional, can be overridden)

# 4. Run
# Run from /app to match python path structure
CMD ["uvicorn", "Software.Servidor.Backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
