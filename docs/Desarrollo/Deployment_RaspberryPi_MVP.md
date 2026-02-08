# Despliegue en Raspberry Pi (MVP GPIO)

Sigue estos pasos para ejecutar la interfaz de control en la Raspberry Pi.

## 1. Preparación del Sistema Operativo

### A. Instalar Dependencias del Sistema
Al igual que en tu portátil, la Raspberry Pi necesita las librerías gráficas de Python.
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### B. Habilitar el Puerto Serial (UART)
Es crucial que la Raspberry Pi tenga el puerto serial habilitado y **no lo esté usando la consola de Linux**.
1.  Ejecuta: `sudo raspi-config`
2.  Ve a **Interface Options** -> **Serial Port**.
3.  Pregunta 1: *Would you like a login shell to be accessible over serial?* -> **NO**.
4.  Pregunta 2: *Would you like the serial port hardware to be enabled?* -> **YES**.
5.  Sal y reinicia (`sudo reboot`).

## 2. Preparación del Proyecto

1.  **Clonar/Actualizar el Repo:**
    ```bash
    cd ~/Proyecto_Demeter  # O donde lo tengas
    git pull origin feature/Migracion_Protocolo_Demeter
    ```

2.  **Entorno Virtual (Recomendado):**
    ```bash
    cd Python
    python3 -m venv venv
    source venv/bin/activate
    
    # Instalar requerimientos mínimos para el MVP
    pip install -r requirements_mvp.txt
    
    # Nota: Tkinter se instala con apt (paso 1A), no con pip.
    ```

## 3. Ejecución

No hace falta modificar el código para cambiar el puerto. El script `mvp_gui.py` acepta el puerto como **argumento**.

**Comando para Raspberry Pi (usando `/dev/serial0`):**

```bash
# Desde la carpeta Python/
python3 mvp_gui.py /dev/serial0
```

*Nota: `/dev/serial0` es un alias (symlink) que apunta al UART correcto (normalmente `ttyS0` o `ttyAMA0`) configurado por el sistema.*

## 4. Troubleshooting
*   **Permisos:** Si da error "Permission denied", añade tu usuario al grupo `dialout`:
    `sudo usermod -a -G dialout $USER` (y reloguea).
*   **Display:** Si te conectas por SSH, necesitas redirigir las X11 o conectar una pantalla HDMI y teclado a la Pi.
