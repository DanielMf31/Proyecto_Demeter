# Guia de Flasheo de Firmware (Raspberry Pi)

## Requisitos

- ESP32-S3 conectado a la RPi por USB
- PlatformIO instalado (`pip install platformio`)
- Entorno virtual activado: `source .venv/bin/activate`

## Comandos rapidos

```bash
# Compilar sin flashear
make fw-build

# Flashear firmware del gateway
make fw-flash

# Flashear firmware de test de sensores
make fw-flash-sensor

# Abrir monitor serie (ver logs del ESP32)
make fw-monitor
```

## Firmware disponibles

| Entorno | Comando | Descripcion |
|---------|---------|-------------|
| `gateway` | `make fw-flash` | Nodo gateway (UART + ESP-NOW) |
| `sensor_test` | `make fw-flash-sensor` | Test de sensores DS18B20 + Capacitivo |
| `sensor` | `pio run -e sensor -t upload` | Nodo sensor (ESP-NOW, Node ID 2) |
| `actuador` | `pio run -e actuador -t upload` | Nodo actuador (ESP-NOW, Node ID 3) |
| `get_mac` | `pio run -e get_mac -t upload` | Utilidad: muestra la MAC del ESP32 |

## Sensor Test — Pines

| Sensor | GPIO | Notas |
|--------|------|-------|
| DS18B20 (temperatura) | 4 | Requiere resistencia pull-up 4.7k a 3.3V |
| Capacitivo v1.2 (humedad suelo) | 5 | Lectura analogica (ADC) |

### Calibracion del sensor capacitivo

Los valores por defecto estan en `main_sensor_test.cpp`:

```cpp
static constexpr int SOIL_AIR_VALUE   = 3000;  // ADC con sensor al aire (seco)
static constexpr int SOIL_WATER_VALUE = 1000;  // ADC con sensor en agua
```

Para calibrar:
1. Flashea `sensor_test` y abre el monitor: `make fw-flash-sensor && make fw-monitor`
2. Deja el sensor al aire, anota el valor Raw ADC → ese es tu `SOIL_AIR_VALUE`
3. Sumerge en agua, anota el valor Raw ADC → ese es tu `SOIL_WATER_VALUE`
4. Actualiza los valores en el codigo y reflashea

## Verificar puerto USB

```bash
# Listar dispositivos conectados
pio device list

# Si hay multiples ESP32, especificar puerto:
cd Firmware && pio run -e gateway -t upload --upload-port /dev/ttyACM1
```

## Flujo tipico: test de sensores

```bash
# 1. Flashear firmware de test
make fw-flash-sensor

# 2. Abrir monitor para ver lecturas
make fw-monitor

# Salida esperada:
# [DS18B20]    Temp: 23.45 C
# [Capacitivo] Humedad: 65%  |  Raw ADC: 1850
# ----------------------------------------

# 3. Cuando termines, volver al gateway
make fw-flash
```
