# Despliegue, Sincronización y Mantenimiento Remoto

Este documento detalla las estrategias para mantener actualizados tanto la Raspberry Pi como los nodos ESP32 en el entorno de producción (Invernadero).

## 1. Sincronización de Código en Raspberry Pi

Existen dos métodos principales para llevar tu código a la Raspberry Pi.

### Método A: Git (Recomendado)
Es la forma más profesional y eficiente. Convierte tu Raspberry Pi en un "cliente" del repositorio.

*   **Flujo**:
    1.  Desarrollas en tu PC.
    2.  Subes cambios: `git push origin develop`.
    3.  En la RPi (por SSH): `git pull origin develop`.
*   **Ventajas**: Historial de versiones, fácil de revertir cambios, descarga solo las diferencias (rápido).
*   **Comando Rápido**:
    ```bash
    # En la RPi
    cd ~/Proyecto_Demeter && git pull && sudo systemctl restart demeter-service
    ```

### Método B: SCP / SFTP (Copia Directa)
Útil para pruebas rápidas de archivos sueltos o si no usas Git (no recomendado).

*   **Comando desde tu PC**:
    ```bash
    # Copiar un archivo
    scp Python/src/main_poc.py usuario@raspberrypi.local:~/Proyecto_Demeter/Python/src/
    
    # Copiar carpeta entera (recursivo)
    scp -r Python/ usuario@raspberrypi.local:~/Proyecto_Demeter/
    ```
*   **Desventajas**: Sobrescribe sin control de versiones, más lento si copias todo cada vez.

### Método C: Rsync (Sincronización Inteligente)
Una versión avanzada de SCP que solo copia lo modificado.
*   **Comando**:
    ```bash
    rsync -avz --exclude 'venv' --exclude '.git' ./ usuario@raspberrypi.local:~/Proyecto_Demeter/
    ```

---

## 2. Automatización de la Instalación (SD Card)

Para configurar una Raspberry Pi "desde cero" de forma casi mágica:

### Nivel 1: Raspberry Pi Imager (Básico)
Al grabar la SD en tu PC, usa el botón de **configuración avanzada (engranaje)**:
*   Configura Hostname (`demeter-pi`).
*   Habilita SSH.
*   Configura Usuario/Pass.
*   Configura Wi-Fi.

Esto permite que al arrancar, la Pi ya se conecte y tenga SSH. Solo tendrías que entrar y ejecutar:
```bash
git clone https://github.com/tu-usuario/Proyecto_Demeter.git
cd Proyecto_Demeter/setup_rpi
sudo ./rpi_bootstrap.sh
```

### Nivel 2: Script en Partición Boot (Semi-Automático)
Puedes colocar el script `rpi_bootstrap.sh` directamente en la partición `/boot` de la tarjeta SD desde tu PC.
Al arrancar la Pi:
1.  Conectas por SSH.
2.  Ejecutas: `sudo /boot/rpi_bootstrap.sh`.
Esto te ahorra tener que clonar el repo antes de tener las herramientas instaladas.

---

## 3. Actualización Remota del ESP32 (Flashing)

¿Cómo cambiar el código del ESP32 si ya está soldado/instalado en el invernadero?

### Estrategia 1: Actualización vía Raspberry Pi (UART/Serial)
Si el ESP32 está conectado a la Raspberry Pi por UART, ¡puedes usar la RPi como programador!

**Requisitos de Hardware Adicionales**:
Para que funcione, la Raspberry Pi necesita controlar dos pines extra del ESP32 para ponerlo en "Modo Download":
1.  **EN (Reset)**
2.  **IO0 (Boot)**

**Conexión**:
*   RPi GPIO X -> ESP32 EN
*   RPi GPIO Y -> ESP32 IO0

**Software (`esptool.py`)**:
Puedes usar la herramienta oficial de Espressif directamente en la Pi.
```bash
# 1. Poner ESP32 en modo boot (Script Python en RPi)
#    - GPIO Y (IO0) -> LOW
#    - GPIO X (EN) -> LOW (Reset)
#    - Esperar 100ms
#    - GPIO X (EN) -> HIGH (Soltar Reset)
#    - Esperar 100ms
#    - GPIO Y (IO0) -> HIGH

# 2. Flashear Firmware
esptool.py -p /dev/serial0 -b 460800 write_flash 0x0 firmware.bin

# 3. Reiniciar ESP32 (Script Python en RPi)
#    - Toggle EN (Reset)
```

**Ventaja**: No requiere código especial en el ESP32. Robusto.
**Desventaja**: Requiere 2 cables extra.

### Estrategia 2: OTA (Over-The-Air) vía Wi-Fi
Si los ESP32 tienen acceso a Wi-Fi.
*   **Librería**: `ArduinoOTA`.
*   El ESP32 escucha en un puerto de red.
*   Desde la RPi (o tu PC) envías el firmware por la red:
    ```bash
    python espota.py -i <IP_ESP32> -f firmware.bin
    ```
*   **Ventaja**: No requiere cables.
*   **Desventaja**: Si subes un código con error que rompe el Wi-Fi, pierdes el acceso para siempre (ladrillo hasta ir físicamente).

### Estrategia 3: Actualización vía USB
Si conectas el ESP32 a la Raspberry Pi por **cable USB** en lugar de UART directo a pines.
*   Es lo más fácil. La RPi lo ve como `/dev/ttyUSB0`.
*   Si instalas **PlatformIO Core** en la Raspberry Pi (`pip install platformio`), puedes compilar y subir remotamente:
    ```bash
    # En la RPi
    cd ~/Proyecto_Demeter/C++
    pio run -t upload
    ```
    O usando **PlatformIO Remote** desde tu casa:
    ```bash
    # En tu PC de casa
    pio remote run -t upload
    ```
    *(Esto requiere cuenta de PlatformIO).*

## Recomendación para tu Proyecto
Dado que estás diseñando la PCB/Conexiones ahora:

1.  **Cableado**: Conecta, además de TX/RX, dos GPIOs de la Raspberry a EN y IO0 del ESP32.
2.  **Método**: Usa la **Estrategia 1 (UART)**. Es la más robusta para un sistema "headless" cableado. Te permite "revivir" un ESP32 incluso si el firmware anterior falló completamente, ya que el control es por hardware.
