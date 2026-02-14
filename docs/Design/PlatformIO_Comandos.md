# Guía Rápida de Comandos PlatformIO (PIO)

PlatformIO es una herramienta extremadamente potente para gestionar proyectos embebidos. Aquí tienes los comandos más útiles y sus principales flags.

> [!TIP]
> Todos los comandos deben ejecutarse desde la **raíz del proyecto** (donde está el archivo `platformio.ini`).

## 1. Ejecución de Tests (`pio test`)

Este es el comando que más vas a utilizar para TDD.

**Comando básico:**
```bash
pio test -e <entorno>
```

**Flags Clave (`-f` / `--filter` y `-i` / `--ignore`):**
La magia para ejecutar **un solo test** está en el flag `-f`.

- **Ejecutar un archivo específico**:
  ```bash
  pio test -e native -f test_protocol
  ```
  *Nota: No necesitas poner `.cpp` ni la ruta completa si el nombre es único. PIO busca por coincidencias.*

- **Ejecutar una carpeta específica**:
  Si tienes `test/comms/test_uart.cpp` y `test/comms/test_spi.cpp`:
  ```bash
  pio test -e native -f comms/*
  ```

- **Ejecutar múltiples filtros**:
  ```bash
  pio test -e native -f test_protocol -f test_sensor
  ```

- **Ignorar tests específicos**:
  ```bash
  pio test -e native -i test_broken
  ```

- **Ver más detalle (Verbose)**:
  ```bash
  pio test -vvv
  ```
  *Útil para ver los errores de compilación completos.*

---

## 2. Gestión de Entornos (`pio run`)

Compila y sube el código.

**Comando básico:**
```bash
pio run
```
*Compila todos los entornos definidos en `platformio.ini`.*

Flags:
- `-e <entorno>`: Especifica qué entorno compilar.
  ```bash
  pio run -e gateway
  pio run -e sensor
  ```
- `-t <target>`: Define el objetivo (target).
  - `upload`: Compila y sube a la placa.
    ```bash
    pio run -e sensor -t upload
    ```
  - `clean`: Limpia los archivos compilados (borra `.pio/build`).
    ```bash
    pio run -t clean
    ```
  - `monitor`: Abre el monitor serie después de subir (aunque es mejor usar `pio device monitor`).

---

## 3. Monitor Serie (`pio device monitor`)

Para ver los logs de tu dispositivo.

**Comando básico:**
```bash
pio device monitor
```

Flags:
- `-p <puerto>`: Especifica el puerto.
  ```bash
  pio device monitor -p /dev/ttyUSB0
  ```
- `-b <baudrate>`: Especifica la velocidad (si es diferente a `platformio.ini`).
  ```bash
  pio device monitor -b 115200
  ```
- `--filter <filtro>`: Aplica filtros como `esp32_exception_decoder` (para decodificar crash dumps) o `time` (añade timestamps).
  ```bash
  pio device monitor -f esp32_exception_decoder
  ```

---

## 4. Gestión de Librerías (`pio pkg`)

El gestor de paquetes moderno (reemplaza al antiguo `pio lib`).

- **Buscar librerías**:
  ```bash
  pio pkg search "json"
  ```
- **Instalar una librería**:
  ```bash
  pio pkg install --library "bblanchon/ArduinoJson"
  ```
- **Actualizar librerías**:
  ```bash
  pio pkg update
  ```

---

## 5. Gestión del Proyecto (`pio project`)

- **Inicializar un proyecto nuevo**:
  ```bash
  pio project init --board esp32dev
  ```
- **Limpiar cache y dependencias corruptas** (Mano de santo cuando nada compila):
  ```bash
  rm -rf .pio
  ```
  *(Técnicamente es un comando de bash, pero es parte esencial del flujo de PIO).*
