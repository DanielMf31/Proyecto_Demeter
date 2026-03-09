# Flash Instructions — Demeter ESP32 Nodes

## Hardware Detected (RPi `pio device list`)

| Puerto       | MAC                  | Rol             |
|-------------|----------------------|-----------------|
| `/dev/ttyACM0` | `9C:13:9E:A8:6F:CC` | **Gateway** (Node 1) |
| `/dev/ttyACM1` | `5AB9080948`         | USB Serial (no ESP32) |
| `/dev/ttyACM2` | `20:6E:F1:85:58:D0` | **Sensor Cluster** (Node 2) |

## 1. Flash Gateway

```bash
cd ~/Documentos/Proyectos_Personales/Proyecto_Demeter/Firmware
pio run -e gateway -t upload --upload-port /dev/ttyACM0
```

Verificar con monitor:
```bash
pio device monitor --port /dev/ttyACM0 --baud 115200
```

Deberías ver:
```
=== DEMETER GATEWAY V2 (Direct Control) ===
[Setup] Ready.
```

## 2. Flash Sensor Cluster

```bash
pio run -e sensor_cluster -t upload --upload-port /dev/ttyACM2
```

Verificar con monitor:
```bash
pio device monitor --port /dev/ttyACM2 --baud 115200
```

Deberías ver:
```
[SENSOR_CLUSTER] Active plants: X
[SENSOR_CLUSTER] Sending report...
```

## 3. MACs Configuradas en Firmware

- `main_gateway.cpp`: `SENSOR_MAC = {0x20, 0x6E, 0xF1, 0x85, 0x58, 0xD0}` (ACM2)
- `main_sensor_cluster.cpp`: `GATEWAY_MAC = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC}` (ACM0)

## 4. Verificar comunicación

Con ambos flasheados, en el monitor del Gateway deberías ver:
```
>> [CLUSTER] Node 2: X entries
   Plant 1: 22.50 C, 45% soil
```

Esto confirma que ESP-NOW funciona y el gateway recibe los cluster reports.
