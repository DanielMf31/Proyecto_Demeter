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
# Set PYTHONPATH to include Common (for configuration.py)
ENV PYTHONPATH="/app/Software/Common"

# 4. Run
# Switch to Backend directory to simplify imports
WORKDIR /app/Software/Servidor/Backend
# Run app:app directly
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
