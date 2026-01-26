#!/bin/bash
# ===================================================================================
# PROYECTO DEMETER - Deployment Script
# Autor: Equipo Demeter
# Descripción: Prepara una Raspberry Pi virgen para ejecutar el Proyecto Demeter.
# ===================================================================================

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== INICIANDO DESPLIEGUE PROYECTO DEMETER ===${NC}"

# 1. Comprobaciones Iniciales (Root)
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Error: Este script necesita permisos de superusuario.${NC}"
  echo "Ejecuta: sudo ./setup_deployment.sh"
  exit 1
fi

# Detectar Usuario Real (SUDO_USER)
REAL_USER=${SUDO_USER:-$USER}
echo "Usuario detectado: $REAL_USER"

# 2. Configuración UART (raspi-config)
echo -e "\n[1/5] Configurando UART..."

if command -v raspi-config &> /dev/null; then
    # Habilitar Hardware UART
    raspi-config nonint do_serial_hw 0
    # Deshabilitar Consola Serial
    raspi-config nonint do_serial_cons 1
    echo -e "${GREEN}✔ UART Hardware Habilitado / Consola Deshabilitada.${NC}"
else
    echo -e "${RED}✘ raspi-config no encontrado (¿No es Raspbian?). Saltando paso UART.${NC}"
fi

# 3. Permisos de Usuario
echo -e "\n[2/5] Configurando Permisos..."
usermod -a -G dialout $REAL_USER
echo -e "${GREEN}✔ Usuario '$REAL_USER' añadido al grupo 'dialout'.${NC}"
echo "Nota: Necesitarás cerrar sesión/reiniciar para que esto aplique."

# 4. Dependencias del Sistema
echo -e "\n[3/5] Verificando Dependencias del Sistema..."
apt-get update -y
apt-get install -y python3-venv python3-pip python3-tk
echo -e "${GREEN}✔ Paquetes del sistema instalados.${NC}"

# 5. Entorno Python
echo -e "\n[4/5] Configurando Entorno Python..."

# Cambiar al directorio del script para rutas relativas
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creando virtual environment..."
    # Ejecutar creación como el usuario real, no como root
    sudo -u $REAL_USER python3 -m venv venv
    echo -e "${GREEN}✔ Venv creado.${NC}"
else
    echo "Venv ya existe."
fi

echo "Instalando librerías Python..."
# Instalar dentro del venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
echo -e "${GREEN}✔ Dependencias Python instaladas.${NC}"

# 6. Directorios de Log
echo -e "\n[5/5] Preparando Sistema de Archivos..."
mkdir -p logs/sessions
# Ajustar dueño de logs al usuario real
chown -R $REAL_USER:$REAL_USER logs
echo -e "${GREEN}✔ Carpetas de log creadas.${NC}"

echo -e "\n${GREEN}=== DESPLIEGUE COMPLETADO ===${NC}"
echo "Pasos siguientes:"
echo "1. Reinicia la Raspberry Pi: sudo reboot (Para aplicar cambios UART/Permisos)"
echo "2. Para ejecutar:"
echo "   cd Python"
echo "   source venv/bin/activate"
echo "   python3 main.py"
