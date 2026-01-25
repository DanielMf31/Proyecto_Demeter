#!/bin/bash
# Script para configurar el entorno virtual de Python

echo "Configurando entorno para Proyecto Demeter (Python)..."

# Verificar si python3-venv está instalado
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "El paquete 'python3-venv' no parece estar instalado."
    echo "Por favor instálalo con: sudo apt install python3-venv"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual ('venv')..."
    python3 -m venv venv
else
    echo "El entorno virtual ya existe."
fi

# Activar e instalar dependencias
echo "Activando entorno e instalando dependencias..."
source venv/bin/activate
pip install -r requirements.txt

echo "========================================"
echo "Instalación completada."
echo "Para ejecutar la prueba:"
echo "  source venv/bin/activate"
echo "  python src/main_poc.py --port /dev/ttyUSB0"
echo "========================================"
