#!/bin/bash

# =============================================================================
# DEMETER - Lanzador de Sistema (RPi Edge)
# =============================================================================
# Este script reinicia los contenedores y abre la interfaz local.
# =============================================================================

# Directorio del proyecto
PROJECT_DIR="/home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter"

echo "🚀 Iniciando Demeter..."
cd "$PROJECT_DIR" || exit

# 1. Parar y limpiar contenedores huérfanos
echo "🛑 Parando servicios antiguos..."
make rpi-down

# 2. Levantar servicios
echo "🆙 Levantando Gateway y UI Local..."
make rpi-up

# 3. Esperar a que Nginx y el Edge Server estén listos
echo "⏳ Esperando inicialización (5s)..."
sleep 5

# 4. Abrir el navegador en modo pantalla completa
# Usamos chromium-browser que es el estándar en Raspberry Pi OS
echo "🌐 Abriendo Interfaz Local..."
if command -v chromium-browser &> /dev/null; then
    chromium-browser http://localhost --start-fullscreen --remote-debugging-port=9222 &
else
    # Fallback si no está Chromium (ej: Firefox)
    xdg-open http://localhost
fi

echo "✅ Listo. Puedes cerrar esta terminal."
sleep 2
exit 0
