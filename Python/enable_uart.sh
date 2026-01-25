#!/bin/bash

# Comprobar si se está ejecutando como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, busca ejecutar este script como root (sudo ./enable_uart.sh)"
  exit 1
fi

echo "=== Configuración Automática de UART en Raspberry Pi ==="

# Verificar si raspi-config está instalado
if ! command -v raspi-config &> /dev/null; then
    echo "Error: 'raspi-config' no encontrado. Este script está pensado para Raspberry Pi OS."
    echo "Si estás en otro sistema, asegúrate de habilitar el puerto serial manualmente."
    exit 1
fi

# Habilitar UART Hardware y Deshabilitar Consola Serial
# do_serial <login_shell> <serial_port>
# 1 = No login shell (Disable)
# 0 = Serial port enabled (Enable)
# Nota: Los argumentos de do_serial pueden variar según versión, usamos la lógica estándar:
# Queremos: Login Shell = NO, Serial HW = YES.

echo "Configurando: Login Shell -> NO, Serial Hardware -> YES..."

# Método usando raspi-config nonint (non-interactive)
# do_serial_hw 0 = Enable hardware UART
# do_serial_cons 1 = Disable console over serial

# Intentar habilitar hardware UART
raspi-config nonint do_serial_hw 0
HW_STATUS=$?

# Intentar deshabilitar consola serial
raspi-config nonint do_serial_cons 1
CONS_STATUS=$?

if [ $HW_STATUS -eq 0 ]; then
    echo "✔ Hardware UART habilitado correctamente."
else
    echo "✘ Error al habilitar Hardware UART."
fi

if [ $CONS_STATUS -eq 0 ]; then
    echo "✔ Consola serial deshabilitada correctamente."
else
    echo "✘ Error al deshabilitar Consola serial."
fi

# Añadir usuario actual al grupo dialout para permisos sin sudo
USER_NAME=${SUDO_USER:-$USER}
if [ -n "$USER_NAME" ]; then
    usermod -a -G dialout $USER_NAME
    echo "✔ Usuario '$USER_NAME' añadido al grupo 'dialout'."
fi

echo "========================================================"
echo "Configuración finalizada."
echo "IMPORTANTE: Es necesario REINICIAR para que los cambios surtan efecto."
echo "Ejecuta: sudo reboot"
