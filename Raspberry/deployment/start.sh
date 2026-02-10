#!/bin/bash

# Demeter Launcher

# Resolve Paths
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$DIR/../.."
PYTHON_DIR="$PROJECT_ROOT/Python"
VENV_DIR="$PYTHON_DIR/.venv"

# Check Venv
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Environment not found. Please run './setup.sh' first."
    exit 1
fi

# Detect Terminal Emulator
if command -v gnome-terminal &> /dev/null; then
    # GNOME Terminal (Ubuntu/Raspberry Pi Desktop)
    echo "🚀 Launching Demeter System..."
    
    gnome-terminal --window --title="Demeter Backend" --geometry=100x20 \
        -- bash -c "source $VENV_DIR/bin/activate; python $PYTHON_DIR/main_async.py; exec bash"
        
    gnome-terminal --tab --title="Demeter GUI" \
        -- bash -c "sleep 2; source $VENV_DIR/bin/activate; python $PYTHON_DIR/main_gui.py; exec bash"

elif command -v lxterminal &> /dev/null; then
    # LXTerminal (Default on lighter RPi OS)
    lxterminal -t "Demeter Backend" -e "bash -c 'source $VENV_DIR/bin/activate; python $PYTHON_DIR/main_async.py; read -p \"Press Enter to close...\"'" &
    sleep 2
    lxterminal -t "Demeter GUI" -e "bash -c 'source $VENV_DIR/bin/activate; python $PYTHON_DIR/main_gui.py; read -p \"Press Enter to close...\"'" &

else
    # Fallback to simple XTerm or background
    echo "⚠️  No fancy terminal found. Running in background/foreground."
    source "$VENV_DIR/bin/activate"
    python "$PYTHON_DIR/main_async.py" &
    PID_BACKEND=$!
    sleep 2
    python "$PYTHON_DIR/main_gui.py"
    
    # Kill backend when GUI closes
    kill $PID_BACKEND
fi
