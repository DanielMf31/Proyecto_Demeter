#!/bin/bash

# setup_rpi_uart.sh
# Configures Raspberry Pi UART for Data Communication (disables console, enables hardware UART)
# Usage: sudo ./setup_rpi_uart.sh [username]

USER_TO_MOD=${1:-$SUDO_USER}
if [ -z "$USER_TO_MOD" ]; then
    USER_TO_MOD=$(whoami)
fi

echo "=== Raspberry Pi UART Helper Setup ==="
echo "Configuring for user: $USER_TO_MOD"

# 1. Add user to dialout/tty groups
echo "[1] Adding user to 'dialout' and 'tty' groups..."
usermod -a -G dialout $USER_TO_MOD
usermod -a -G tty $USER_TO_MOD
echo "    -> Done. (Requires Logout/Reboot to take effect)"

# 2. Disable Serial Console (cmdline.txt)
# We want to remove 'console=serial0,115200' or similar
echo "[2] Checking Serial Console in /boot/cmdline.txt..."
if grep -q "console=serial0" /boot/cmdline.txt; then
    echo "    -> Serial Console found. Disabling..."
    sed -i 's/console=serial0,[0-9]*\s*//g' /boot/cmdline.txt
    echo "    -> Disabled."
else
    echo "    -> Serial Console not active (OK)."
fi

# 3. Enable UART in /boot/config.txt
echo "[3] Checking enable_uart in /boot/config.txt..."
if ! grep -q "enable_uart=1" /boot/config.txt; then
    echo "    -> Enabling UART..."
    echo "enable_uart=1" >> /boot/config.txt
    echo "    -> Added enable_uart=1"
else
    echo "    -> UART already enabled (OK)."
fi

# 4. Disable systemd serial-getty service if active
echo "[4] Disabling serial-getty service..."
systemctl stop serial-getty@serial0.service 2>/dev/null
systemctl disable serial-getty@serial0.service 2>/dev/null
echo "    -> Service stopped/disabled."

echo ""
echo "=== SETUP COMPLETE ==="
echo "Please REBOOT your Raspberry Pi for changes to take effect."
echo "sudo reboot"
