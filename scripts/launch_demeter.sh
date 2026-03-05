#!/bin/bash

# =============================================================================
# DEMETER - Lanzador de Sistema Avanzado (RPi Edge)
# =============================================================================
# 1. Activa el entorno virtual (.venv)
# 2. Asegura que PlatformIO esté instalado
# 3. Abre el Monitor Serie en una terminal separada (ttyACM0)
# 4. Reinicia los contenedores de Docker
# 5. Abre la interfaz local en Chromium
# =============================================================================

PROJECT_DIR="/home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter"
VENV_PATH="$PROJECT_DIR/.venv"
PORT="/dev/ttyACM0"

echo "🚀 Iniciando Demeter (Modo Inicialización Hardware)..."
cd "$PROJECT_DIR" || exit

# 1. Activar Entorno Virtual e instalar PIO si es necesario
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Activando entorno virtual..."
    source "$VENV_PATH/bin/activate"
    echo "📦 Asegurando PlatformIO..."
    pip install -U platformio --quiet
else
    echo "⚠️ No se encontró .venv en $VENV_PATH. Continuando sin venv..."
fi

# 2. Abrir Monitor Serie en SEGUNDA TERMINAL (Crítico para despertar el hardware)
echo "🔌 Despertando Hardware en $PORT..."
if command -v lxterminal &> /dev/null; then
    lxterminal -e "bash -c 'cd $PROJECT_DIR && source .venv/bin/activate && pio device monitor -p $PORT -b 115200; exec bash'" &
else
    x-terminal-emulator -e "bash -c 'cd $PROJECT_DIR && source .venv/bin/activate && pio device monitor -p $PORT -b 115200; exec bash'" &
fi

# 3. Reiniciar Docker
echo "🛑 Parando servicios antiguos..."
make rpi-down
echo "🆙 Levantando Gateway y UI Local..."
make rpi-up

# 4. Abrir Interfaz
echo "⏳ Esperando inicialización (5s)..."
sleep 5
echo "🌐 Abriendo Interfaz Local..."
if command -v chromium-browser &> /dev/null; then
    chromium-browser http://localhost --start-fullscreen --remote-debugging-port=9222 &
else
    xdg-open http://localhost
fi

echo "✅ Todo listo. Revisa la otra terminal para ver los logs del hardware."
sleep 2
exit 0
