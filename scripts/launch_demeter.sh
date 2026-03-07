#!/bin/bash

# =============================================================================
# DEMETER - Lanzador de Sistema (RPi Edge)
# =============================================================================
# 1. Limpia contenedores antiguos y huerfanos
# 2. Levanta Gateway + UI Local con Docker
# 3. Espera a que ambos esten healthy
# 4. Abre el monitor serie en una segunda terminal
# 5. Abre la interfaz local en Chromium
# =============================================================================

PROJECT_DIR="/home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter"
PORT="/dev/ttyACM0"
COMPOSE="docker compose -f docker-compose.rpi.yml --env-file .env.rpi"

export DISPLAY="${DISPLAY:-:0}"

echo "=== Iniciando Demeter (RPi Edge Mode) ==="
cd "$PROJECT_DIR" || exit 1

# ── 1. Limpiar estado anterior ───────────────────────────────────────────────
echo "[1/5] Parando servicios anteriores..."
$COMPOSE down --remove-orphans 2>/dev/null

# ── 2. Levantar contenedores ────────────────────────────────────────────────
echo "[2/5] Levantando Gateway y UI Local..."
$COMPOSE up -d

# ── 3. Esperar a que el gateway este healthy ─────────────────────────────────
echo "[3/5] Esperando a que el Gateway este healthy..."
MAX_WAIT=120
WAITED=0
while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' demeter-gateway 2>/dev/null)
    if [ "$STATUS" = "healthy" ]; then
        echo "       Gateway healthy!"
        break
    fi
    if [ "$STATUS" = "unhealthy" ]; then
        echo "ERROR: Gateway unhealthy. Revisa: docker logs demeter-gateway"
        exit 1
    fi
    if [ "$WAITED" -ge "$MAX_WAIT" ]; then
        echo "ERROR: Timeout (${MAX_WAIT}s). Revisa: docker logs demeter-gateway"
        exit 1
    fi
    sleep 3
    WAITED=$((WAITED + 3))
    echo "       ...esperando gateway (${WAITED}s/${MAX_WAIT}s) [status: ${STATUS:-starting}]"
done

# Esperar a que la UI responda (ya deberia arrancar rapido tras gateway healthy)
echo "       Esperando UI Local en http://localhost ..."
WAITED=0
while ! curl -sf http://localhost > /dev/null 2>&1; do
    sleep 2
    WAITED=$((WAITED + 2))
    if [ "$WAITED" -ge 60 ]; then
        echo "WARN: UI no responde tras 60s. Continuando de todos modos..."
        break
    fi
done
echo "       UI Local lista!"

# ── 4. Monitor Serie (segunda terminal) ──────────────────────────────────────
echo "[4/5] Abriendo monitor serie en $PORT..."
if [ -e "$PORT" ]; then
    VENV_PATH="$PROJECT_DIR/.venv"
    if [ -d "$VENV_PATH" ]; then
        MONITOR_CMD="source $VENV_PATH/bin/activate && pio device monitor -p $PORT -b 115200; exec bash"
    else
        MONITOR_CMD="pio device monitor -p $PORT -b 115200; exec bash"
    fi

    if command -v lxterminal &> /dev/null; then
        lxterminal -e "bash -c '$MONITOR_CMD'" &
    elif command -v x-terminal-emulator &> /dev/null; then
        x-terminal-emulator -e "bash -c '$MONITOR_CMD'" &
    else
        echo "WARN: No se encontro terminal grafico. Usa: pio device monitor -p $PORT -b 115200"
    fi
else
    echo "WARN: Puerto $PORT no encontrado. Saltando monitor serie."
fi

# ── 5. Abrir navegador ──────────────────────────────────────────────────────
echo "[5/5] Abriendo interfaz local..."
if command -v chromium &> /dev/null; then
    chromium http://localhost --start-fullscreen --noerrdialogs --disable-infobars --disable-gpu --no-sandbox &
elif command -v firefox &> /dev/null; then
    firefox http://localhost &
else
    xdg-open http://localhost 2>/dev/null
fi

echo ""
echo "=== Demeter listo ==="
echo "  UI:      http://localhost"
echo "  API:     http://localhost:8001/api/docs"
echo "  Logs:    make rpi-logs"
echo "  Parar:   make rpi-down"
