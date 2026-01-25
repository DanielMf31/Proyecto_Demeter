# Guía de Implementación: Raspberry Pi <-> ESP32 UART

Esta guía detalla cómo conectar tu Raspberry Pi al ESP32 (Receptor) y ejecutar la lógica de control.

## 1. Diagrama de Conexión (Wiring)

La comunicación UART requiere conectar los pines cruzados (TX->RX, RX->TX) y compartir la tierra (GND).

> [!WARNING]
> Ambos dispositivos (Raspberry Pi y ESP32) operan a **3.3V Logic Level**. Si usaras un Arduino Uno (5V), necesitarías un conversor de nivel. En este caso, **la conexión directa es segura**.

| Raspberry Pi (GPIO) | ESP32-S3 (Pin) | Descripción |
| :--- | :--- | :--- |
| **TX** (GPIO 14 / Pin 8) | **RX** (GPIO 16) | Datos enviados RPi -> ESP32 |
| **RX** (GPIO 15 / Pin 10) | **TX** (GPIO 17) | Datos recibidos ESP32 -> RPi |
| **GND** (Pin 6) | **GND** | Referencia común (¡Obligatorio!) |

### Esquema Visual
```text
[ RASPBERRY PI ]            [ ESP32 RECEPTOR ]
   Pin 8  (TX)  ------------>  GPIO 16 (RX)
   Pin 10 (RX)  <------------  GPIO 17 (TX)
   Pin 6  (GND) -------------  GND
```

## 2. Configuración en Raspberry Pi

Por defecto, la UART en Raspberry Pi puede estar deshabilitada o asignada a la consola serial. Debes habilitarla para aplicaciones.

1.  Abre la configuración: `sudo raspi-config`
2.  Ve a **Interface Options** -> **Serial Port**.
3.  Pregunta 1: "¿Would you like a login shell to be accessible over serial?" -> **NO** (No queremos consola).
4.  Pregunta 2: "¿Would you like the serial port hardware to be enabled?" -> **YES** (Queremos el hardware).
5.  Reinicia la Raspberry Pi (`sudo reboot`).

El puerto serial suele aparecer como `/dev/serial0` (alias de `ttyS0` o `ttyAMA0`).

## 3. Ejecución de la Prueba (PoC)

Esta prueba enviará 5 comandos predefinidos al ESP32, que validará integridad y ejecutará.

1.  Accede a la carpeta del proyecto en la RPi.
2.  Configura el entorno (solo la primera vez):
    ```bash
    cd Python
    ./setup_env.sh
    ```
3.  Activa el entorno y ejecuta:
    ```bash
    source venv/bin/activate
    # Asegúrate de usar el puerto correcto, usualmente /dev/serial0
    python src/main_poc.py --port /dev/serial0
    ```

## 4. Qué Esperar

Si la conexión es correcta, verás logs indicando el flujo del protocolo:

1.  `Iniciando Handshake (Enviando 101)`
2.  `Recibido 102 (ACK). Iniciando transmisión...`
3.  `-> Enviado [x]: ...` (5 veces)
4.  `Recibido 103 (Inicio de Eco)`
5.  `<- Eco recibido: ...` (5 veces)
6.  `✅ Verificación CORRECTA. Enviando 104.`
7.  `>>> ÉXITO <<<`

En el lado del **ESP32**, verás (si tienes un monitor serial conectado a su USB) que pasa a estado `EJECUTANDO` y comenzará a activar los pines 4, 5, 6, 7 y 8 secuencialmente.

## 5. Solución de Problemas

- **Timeout / No respuesta:** Revisa el cableado. Asegúrate de TX->RX y RX->TX. Comprueba que el ESP32 no esté en un bucle bloqueante o reseteado.
- **Permisos denegados:** Si falla al abrir `/dev/serial0`, tu usuario necesita permisos: `sudo usermod -a -G dialout $USER` (requiere re-login).
