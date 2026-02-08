#!/bin/bash

# Demeter Raspberry Pi Deployment Script
# --------------------------------------
# This script sets up the environment to run the Proyecto Demeter GUI/Controller.
# It handles system dependencies, Python virtual environment, and permissions.

set -e  # Exit on error

echo "🍌 Starting Deployment Setup for Demeter..."

# 1. Update System & Install Dependencies
echo "[1/5] Updating System Dependencies..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip python3-tk git

# 2. Check for Serial Port Permissions
echo "[2/5] Configuring Serial Permissions..."
if groups $USER | grep &>/dev/null 'dialout'; then
    echo "User $USER is already in 'dialout' group."
else
    echo "Adding user $USER to 'dialout' group..."
    sudo usermod -a -G dialout $USER
    echo "⚠️  You may need to logout and login again for group changes to take effect."
fi

# 3. Setup Python Virtual Environment
echo "[3/5] Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created venv."
else
    echo "venv already exists."
fi

# Activate venv
source venv/bin/activate

# 4. Install Python Requirements
echo "[4/5] Installing Python Dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found! Installing minimal dependencies..."
    pip install pydantic pyserial
fi

# 5. Create Logs Directory
echo "[5/5] Creating Directory Structure..."
mkdir -p logs

echo "✅ Setup Complete!"
echo ""
echo "To run the application:"
echo "1. source venv/bin/activate"
echo "2. python3 main.py"
