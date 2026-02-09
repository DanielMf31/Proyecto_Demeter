# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# Install system dependencies (TKinter for GUI, etc)
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first (for caching)
COPY Python/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python Code
COPY Python /app/Python

# Add Python/src to path
ENV PYTHONPATH="${PYTHONPATH}:/app/Python/src"

# Create start script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Demeter Server & GUI..."\n\
python3 Python/main_async.py > /app/Python/logs/server.log 2>&1 &\n\
SERVER_PID=$!\n\
echo "✅ Server started (PID $SERVER_PID). Waiting 2s..."\n\
sleep 2\n\
python3 Python/main_gui.py\n\
kill $SERVER_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

# Create logs directory
RUN mkdir -p /app/Python/logs

# Default command
CMD ["/app/start.sh"]
