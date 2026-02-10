#!/bin/bash
set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Demeter V2 - Raspberry Pi Setup Helper${NC}"
echo "=============================================="

# 1. Check System Dependencies
echo -e "\n${BLUE}[1/5] Checking System Dependencies...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed.${NC}"
    exit 1
fi

# Try to install Tkinter and Venv if apt is available (Debian/Ubuntu/RPi OS)
if command -v apt-get &> /dev/null; then
    echo "Installing system libraries (requires sudo)..."
    sudo apt-get update
    sudo apt-get install -y python3-venv python3-tk python3-pip
else
    echo -e "${RED}Warning: 'apt-get' not found. Ensure python3-venv and python3-tk are installed manually.${NC}"
fi

# 2. Setup Python Virtual Environment
echo -e "\n${BLUE}[2/5] Setting up Python Environment...${NC}"
PROJECT_ROOT="$(dirname "$0")/../.."
PYTHON_DIR="$PROJECT_ROOT/Python"
VENV_DIR="$PYTHON_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate
source "$VENV_DIR/bin/activate"

# 3. Install Dependencies
echo -e "\n${BLUE}[3/5] Installing Python Dependencies...${NC}"
pip install --upgrade pip
pip install -r "$PYTHON_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies.${NC}"
    exit 1
fi

# Install PlatformIO if not present
if ! command -v pio &> /dev/null; then
    echo "Installing PlatformIO Core..."
    pip install platformio
fi

# 4. Run Python Tests
echo -e "\n${BLUE}[4/5] Running Python Integration Tests...${NC}"
cd "$PROJECT_ROOT"
python -m pytest Python/tests/test_data_integration.py Python/tests/test_integration_v2.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python Tests Passed!${NC}"
else
    echo -e "${RED}❌ Python Tests Failed! Check logs.${NC}"
    # We exit here to prevent deployment of broken code? 
    # User said "tests por si acaso", implied stopping if fail is good.
    exit 1
fi

# 5. Run PlatformIO Native Tests
echo -e "\n${BLUE}[5/5] Running C++ Native Tests...${NC}"
pio test -e native
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ C++ Native Tests Passed!${NC}"
else
    echo -e "${RED}❌ C++ Tests Failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Setup Complete! You are ready to run './start.sh'.${NC}"
