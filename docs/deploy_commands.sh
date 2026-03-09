#!/usr/bin/env bash
# ============================================================================
# Demeter — Comandos de despliegue y monitorización
# Deep Sleep Sensor Cluster + Actuador + Gateway + RPi Edge Server
# ============================================================================
#
# Dispositivos (pio device list):
#   /dev/ttyACM0 → Gateway   (MAC: 9C:13:9E:A8:6F:CC) — Node ID 1
#   /dev/ttyACM1 → USB Serial (UART RPi ↔ Gateway)
#   /dev/ttyACM2 → Actuador  (MAC: 9C:13:9E:AC:50:C4) — Node ID 3
#   /dev/ttyACM3 → Sensor    (MAC: 20:6E:F1:85:58:D0) — Node ID 2
#
# Pines sensor cluster:
#   Plant 1: Capacitivo GPIO4, DS18B20 GPIO5
#   Plant 2: Capacitivo GPIO6, DS18B20 GPIO7
#
# Pines actuador (LEDs): GPIO 4, 5, 6, 7
# ============================================================================

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── 1. Flashear firmware ────────────────────────────────────────────────────

flash_gateway() {
    echo "=== Flasheando Gateway (ttyACM0) ==="
    cd "$PROJECT_ROOT/Firmware"
    pio run -e gateway -t upload
}

flash_sensor() {
    echo "=== Flasheando Sensor Cluster (ttyACM3) ==="
    cd "$PROJECT_ROOT/Firmware"
    pio run -e sensor_cluster -t upload
}

flash_actuador() {
    echo "=== Flasheando Actuador (ttyACM2) ==="
    cd "$PROJECT_ROOT/Firmware"
    pio run -e actuador -t upload
}

flash_all() {
    flash_gateway
    flash_sensor
    flash_actuador
}

# ── 2. Monitorizar serial ───────────────────────────────────────────────────

monitor_gateway() {
    echo "=== Monitor Gateway (ttyACM0) ==="
    cd "$PROJECT_ROOT/Firmware"
    pio device monitor -p /dev/ttyACM0 -b 115200
}

monitor_sensor() {
    echo "=== Monitor Sensor Cluster (ttyACM3) ==="
    cd "$PROJECT_ROOT/Firmware"
    pio device monitor -p /dev/ttyACM3 -b 115200
}

monitor_actuador() {
    echo "=== Monitor Actuador (ttyACM2) ==="
    cd "$PROJECT_ROOT/Firmware"
    pio device monitor -p /dev/ttyACM2 -b 115200
}

# ── 3. Arrancar RPi Edge Server (modo local) ────────────────────────────────

start_edge_server() {
    echo "=== Arrancando Edge Server (localhost:8001) ==="
    cd "$PROJECT_ROOT/Software/Raspberry"
    DEMETER_ENV=rpi-local PYTHONPATH=src:../Common \
        python src/proyecto_demeter/Hardware/orchestration/edge_server.py
}

# ── 4. Verificar datos ─────────────────────────────────────────────────────

check_sqlite() {
    echo "=== Últimas lecturas en SQLite ==="
    sqlite3 "$PROJECT_ROOT/Software/Raspberry/data/demeter_local.db" \
        "SELECT * FROM soil_readings ORDER BY id DESC LIMIT 10;"
}

check_csv() {
    echo "=== Últimas líneas CSV ==="
    tail -10 "$PROJECT_ROOT/Software/Raspberry/data/csv/telemetry_"*.csv 2>/dev/null \
        || echo "No CSV files found yet."
}

# ── 5. Uso ──────────────────────────────────────────────────────────────────

usage() {
    cat <<'USAGE'
Uso: ./docs/deploy_commands.sh <comando>

Comandos disponibles:
  flash-gateway     Flashear gateway (ttyACM0)
  flash-sensor      Flashear sensor cluster (ttyACM3)
  flash-actuador    Flashear actuador (ttyACM2)
  flash-all         Flashear los 3 nodos

  monitor-gateway   Monitor serial gateway
  monitor-sensor    Monitor serial sensor cluster
  monitor-actuador  Monitor serial actuador

  edge-server       Arrancar RPi Edge Server (localhost:8001)

  check-db          Ver últimas lecturas en SQLite
  check-csv         Ver últimas líneas de CSV

Flujo típico de test:
  1. ./docs/deploy_commands.sh flash-all
  2. Terminal 1: ./docs/deploy_commands.sh edge-server
  3. Terminal 2: ./docs/deploy_commands.sh monitor-sensor
  4. Terminal 3: ./docs/deploy_commands.sh monitor-gateway
  5. Abrir http://localhost:8001 para la UI local
  6. Esperar 60s y verificar:
     ./docs/deploy_commands.sh check-db
     ./docs/deploy_commands.sh check-csv

  Para probar actuador desde la UI:
  - Abrir http://localhost:8001 → Panel Manual → Pulsar Bomba 1/2/3/4
  - Los LEDs en GPIO 4/5/6/7 del actuador deben encenderse
USAGE
}

# ── Dispatcher ──────────────────────────────────────────────────────────────
case "${1:-}" in
    flash-gateway)   flash_gateway ;;
    flash-sensor)    flash_sensor ;;
    flash-actuador)  flash_actuador ;;
    flash-all)       flash_all ;;
    monitor-gateway) monitor_gateway ;;
    monitor-sensor)  monitor_sensor ;;
    monitor-actuador) monitor_actuador ;;
    edge-server)     start_edge_server ;;
    check-db)        check_sqlite ;;
    check-csv)       check_csv ;;
    *)               usage ;;
esac
