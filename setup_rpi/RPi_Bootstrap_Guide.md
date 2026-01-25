# Guía de Inicialización Raspberry Pi (Universal)

Esta guía explica cómo utilizar el script `rpi_bootstrap.sh` para configurar rápidamente cualquier Raspberry Pi nueva para este proyecto.

## ¿Qué hace este script?
Automatiza la instalación y configuración de todo lo necesario para empezar a trabajar, evitándote horas de configuración manual.

### Resumen de Tareas
1.  **Actualización Total**: Ejecuta `apt update` y `upgrade` para tener el SO al día.
2.  **Kit de Herramientas**: Instala `Git`, `Python 3` (con `venv` y `pip`), editores (`vim`, `nano`) y utilidades de red.
3.  **Acceso Remoto**:
    *   Habilita **SSH** permanentemente.
    *   Instala e inicia **Tailscale** para acceso VPN seguro desde cualquier lugar.
4.  **Hardware (UART/I2C)**:
    *   Habilita el puerto Serial (/dev/serial0) y deshabilita la consola serial (crucial para conectar con ESP32).
    *   Añade tu usuario a los grupos `dialout`, `gpio` e `i2c`.
5.  **Docker (Opcional)**: Te pregunta si quieres instalar Docker para desplegar contenedores.

## ¿Cómo usarlo?

### Paso 1: Descargar el script en la Raspberry Pi
Si ya clonaste el repositorio en la RPi:
```bash
cd Proyecto_Demeter/setup_rpi
```

Si no tienes nada aún en la RPi, puedes copiar solo el contenido del archivo y crearlo:
```bash
nano rpi_bootstrap.sh
# Pega el contenido, guarda (Ctrl+O) y sal (Ctrl+X)
chmod +x rpi_bootstrap.sh
```

### Paso 2: Ejecutar
Debes ejecutarlo con permisos de superusuario (`sudo`):

```bash
sudo ./rpi_bootstrap.sh
```

### Paso 3: Interacción durante el proceso
El script es mayormente automático, pero requerirá tu atención en dos puntos:

1.  **Autenticación Tailscale**:
    Durante la ejecución, verás un mensaje como este:
    ```text
    To authenticate, visit: https://login.tailscale.com/a/xxxxxxxxx
    ```
    Debes copiar ese enlace y abrirlo en tu navegador (PC/Móvil) para autorizar a la Raspberry Pi en tu red Tailscale. **El script esperará a que hagas esto.**

2.  **Instalación de Docker**:
    Al final, te preguntará `¿Desea instalar Docker y Docker Compose? (s/N)`. Responde `s` si planeas usar contenedores (recomendado).

### Paso 4: Reinicio
Al finalizar, el script te pedirá reiniciar. **Es obligatorio reiniciar** para que los permisos de usuario y la configuración de UART surtan efecto.

## Verificación Post-Instalación

Una vez reiniciado, puedes verificar:

1.  **Estado de Tailscale**:
    ```bash
    tailscale status
    ```
2.  **Puerto Serial**:
    ```bash
    ls -l /dev/serial0
    ```
    Debe existir.
3.  **Permisos de Usuario**:
    ```bash
    groups
    ```
    Debes ver `dialout` en la lista.

---
**Nota**: Este script está diseñado para Raspberry Pi OS (basado en Debian). Si usas Ubuntu Server en la RPi, la mayoría de pasos funcionarán igual, pero `raspi-config` podría no estar disponible por defecto.
