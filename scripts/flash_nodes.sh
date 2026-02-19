#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# Demeter Firmware Flasher
# Script to automate flashing of multiple ESP32 nodes via PIO CLI
# ═══════════════════════════════════════════════════════════════

# --- CONFIGURATION (Change these to match your USB Hub ports) ---
# Use 'pio device list' to identify which port is which.
GATEWAY_PORT="/dev/ttyACM0"
SENSOR_PORT_2="/dev/ttyACM1"
ACTUATOR_PORT_3="/dev/ttyACM2"

# Paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIRMWARE_DIR="$PROJECT_ROOT/Firmware"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo "  ./scripts/flash_nodes.sh [command] [port_override]"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  gateway   - Flash Node 1 (Gateway)"
    echo "  sensor    - Flash Node 2 (Sensor)"
    echo "  actuator  - Flash Node 3 (Actuator)"
    echo "  all       - Flash all nodes sequentially"
    echo "  list      - List connected devices and ports"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  ./scripts/flash_nodes.sh gateway"
    echo "  ./scripts/flash_nodes.sh all"
    echo "  ./scripts/flash_nodes.sh gateway /dev/ttyUSB0"
}

check_pio() {
    if ! command -v pio &> /dev/null; then
        echo -e "${RED}[ERROR] PlatformIO (pio) not found.${NC}"
        echo "Please install it with: pip install platformio"
        exit 1
    fi
}

flash_node() {
    local env=$1
    local port=$2
    local label=$3

    echo -e "${YELLOW}─── Flashing $label ($env) on $port ───${NC}"
    
    cd "$FIRMWARE_DIR" || exit 1
    
    # Run PIO upload
    # We use --upload-port to override platformio.ini settings
    if pio run -e "$env" --target upload --upload-port "$port"; then
        echo -e "${GREEN}[SUCCESS] $label flashed correctly!${NC}\n"
        return 0
    else
        echo -e "${RED}[FAILED] Error flashing $label.${NC}\n"
        return 1
    fi
}

# --- MAIN ENGINE ---

check_pio

case "$1" in
    "list")
        pio device list
        ;;
    "gateway")
        PORT=${2:-$GATEWAY_PORT}
        flash_node "gateway" "$PORT" "GATEWAY (Node 1)"
        ;;
    "sensor")
        PORT=${2:-$SENSOR_PORT_2}
        flash_node "sensor" "$PORT" "SENSOR (Node 2)"
        ;;
    "actuator")
        PORT=${2:-$ACTUATOR_PORT_3}
        flash_node "actuador" "$PORT" "ACTUATOR (Node 3)"
        ;;
    "all")
        echo -e "${BLUE}Starting Sequential Flash of all Nodes...${NC}"
        flash_node "gateway" "$GATEWAY_PORT" "GATEWAY (Node 1)"
        flash_node "sensor" "$SENSOR_PORT_2" "SENSOR (Node 2)"
        flash_node "actuador" "$ACTUATOR_PORT_3" "ACTUATOR (Node 3)"
        echo -e "${GREEN}All flash operations completed.${NC}"
        ;;
    *)
        print_usage
        ;;
esac
