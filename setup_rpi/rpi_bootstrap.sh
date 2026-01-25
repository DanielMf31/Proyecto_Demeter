#!/bin/bash

# ==============================================================================
# RASPBERRY PI BOOTSTRAP SCRIPT
# Proyecto Demeter - Universal Setup
# ==============================================================================
# Este script configura una Raspberry Pi desde cero para desarrollo IoT.
# Incluye: Updates, Herramientas, SSH, Tailscale, UART y Docker (Opcional).
# ==============================================================================

# Colores para logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Comprobar privilegios de root
if [ "$EUID" -ne 0 ]; then
  log_error "Por favor, ejecute este script como root: sudo ./rpi_bootstrap.sh"
  exit 1
fi

log_info "Iniciando configuración inicial de Raspberry Pi..."

# ------------------------------------------------------------------------------
# 1. ACTUALIZACIÓN DEL SISTEMA
# ------------------------------------------------------------------------------
log_info "1. Actualizando lista de paquetes y sistema (esto puede tardar)..."
apt-get update && apt-get full-upgrade -y
apt-get autoremove -y
log_success "Sistema actualizado."

# ------------------------------------------------------------------------------
# 2. HERRAMIENTAS ESENCIALES
# ------------------------------------------------------------------------------
log_info "2. Instalando herramientas de desarrollo y utilidades..."
PACKAGES=(
    git curl wget htop vim nano net-tools
    python3 python3-pip python3-venv build-essential
    i2c-tools
)

apt-get install -y "${PACKAGES[@]}"
log_success "Herramientas instaladas: ${PACKAGES[*]}"

# ------------------------------------------------------------------------------
# 3. CONFIGURACIÓN DE CONECTIVIDAD (SSH Y TAILSCALE)
# ------------------------------------------------------------------------------
log_info "3. Configurando conectividad..."

# SSH
log_info "   -> Habilitando servicio SSH..."
systemctl enable ssh
systemctl start ssh
log_success "SSH habilitado y arrancado."

# Tailscale
if command -v tailscale &> /dev/null; then
    log_warn "   -> Tailscale ya está instalado."
else
    log_info "   -> Instalando Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
    log_success "Tailscale instalado."
fi

log_info "   -> Iniciando Tailscale (Prepare su navegador)..."
log_warn "   ¡ATENCIÓN! Se mostrará un enlace de autenticación abajo. Ábralo en su PC."
tailscale up
log_success "Tailscale configurado."

# ------------------------------------------------------------------------------
# 4. CONFIGURACIÓN DE HARDWARE (UART)
# ------------------------------------------------------------------------------
log_info "4. Configurando Hardware UART (para conexión con ESP32)..."

if command -v raspi-config &> /dev/null; then
    # Habilitar Hardware UART (0 = Enable)
    raspi-config nonint do_serial_hw 0
    # Deshabilitar Consola Serial (1 = Disable)
    raspi-config nonint do_serial_cons 1
    log_success "UART configurado (Hardware: ON, Console: OFF)."
else
    log_error "'raspi-config' no encontrado. Configure UART manualmente en /boot/config.txt."
fi

# ------------------------------------------------------------------------------
# 5. PERMISOS DE USUARIO
# ------------------------------------------------------------------------------
ACTUAL_USER=${SUDO_USER:-$USER}
if [ -n "$ACTUAL_USER" ]; then
    log_info "5. Añadiendo usuario '$ACTUAL_USER' a grupos de hardware..."
    usermod -a -G dialout,gpio,i2c,video "$ACTUAL_USER"
    log_success "Permisos actualizados."
fi

# ------------------------------------------------------------------------------
# 6. EXTRAS (DOCKER)
# ------------------------------------------------------------------------------
read -p "¿Desea instalar Docker y Docker Compose? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    log_info "6. Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    if [ -n "$ACTUAL_USER" ]; then
        usermod -aG docker "$ACTUAL_USER"
        log_success "Docker instalado y usuario agregado al grupo docker."
    fi
else
    log_info "Saltando instalación de Docker."
fi

# ------------------------------------------------------------------------------
# RESUMEN FINAL
# ------------------------------------------------------------------------------
echo ""
log_success "=========================================================="
log_success " CONFIGURACIÓN COMPLETADA"
log_success "=========================================================="
echo "Resumen de acciones:"
echo "  [x] Sistema actualizado"
echo "  [x] Herramientas instaladas (git, python, i2c...)"
echo "  [x] SSH habilitado"
echo "  [x] Tailscale instalado (verifique estado con 'tailscale status')"
echo "  [x] UART habilitado (/dev/serial0)"
echo ""
log_warn "IMPORTANTE: Es necesario REINICIAR para aplicar cambios de hardware y permisos."
read -p "¿Desea reiniciar ahora? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    reboot
fi
