FROM python:3.11-slim-bookworm

# 1. Install System Dependencies
# libgpiod is needed for modern GPIO access on Pi
RUN apt-get update && apt-get install -y \
    libgpiod2 \
    gpiod \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python Dependencies
COPY Software/Raspberry/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy Code
# Copy Common Configuration
COPY Software/Common /app/Software/Common

# Copy Raspberry Code
COPY Software/Raspberry /app/Software/Raspberry

# 4. Environment Variables
# Add Common and Raspberry to PYTHONPATH
ENV PYTHONPATH="/app/Software/Raspberry:/app/Software/Common:/app/Software/Raspberry/src"
ENV DEMETER_ENV=production

# 5. Run Command
# Launch the Async Main Service (Command Dispatcher)
CMD ["python", "Software/Raspberry/src/proyecto_demeter/Hardware/orchestration/command_dispatcher.py"]
