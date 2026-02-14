#!/bin/bash

# ==============================================================================
# DEMETER MONITORING INSTALLER (GRAFANA + LOKI + PROMTAIL)
# ==============================================================================
# This script automates the setup of the monitoring stack for the Demeter Project.
# Target Hardware: Raspberry Pi (ARM64)
# Target OS: Raspberry Pi OS (64-bit) / Debian / Ubuntu
# ==============================================================================

# --- CONFIGURATION ---
USER_HOME="/home/montero"
PROJECT_ROOT="$USER_HOME/Documentos/Proyectos_Personales/Proyecto_Demeter"
PYTHON_DIR="$PROJECT_ROOT/Python"
LOGS_DIR="$PYTHON_DIR/logs"
DB_PATH="$PYTHON_DIR/data/demeter_data.db"
LOKI_VERSION="2.9.2"
GRAFANA_USER="grafana"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== STARTED DEMETER MONITORING SETUP ===${NC}"

# 1. CHECK ROOT
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo ./install_monitoring.sh)${NC}"
  exit 1
fi

# 2. INSTALL DEPENDENCIES
echo -e "${GREEN}[1/8] Installing Dependencies...${NC}"
apt-get update
apt-get install -y wget curl unzip acl apt-transport-https software-properties-common

# 3. INSTALL GRAFANA
echo -e "${GREEN}[2/8] Installing Grafana...${NC}"
mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | tee /etc/apt/sources.list.d/grafana.list
apt-get update
apt-get install -y grafana

# Enable Service
systemctl daemon-reload
systemctl enable grafana-server
systemctl start grafana-server

# Install SQLite Plugin (Manual Install to avoid 404 on community plugins)
echo -e "${GREEN}[3/8] Installing SQLite Plugin...${NC}"
cd /var/lib/grafana/plugins
# Check if already installed
if [ ! -d "fr-ser-sqlite-datasource" ]; then
    wget -q https://github.com/fr-ser/grafana-sqlite-datasource/releases/download/v3.4.0/fr-ser-sqlite-datasource-3.4.0.zip
    unzip -o fr-ser-sqlite-datasource-3.4.0.zip
    rm fr-ser-sqlite-datasource-3.4.0.zip
    # Enable unsigned plugins if necessary (usually not needed for this one, but good practice for manual installs)
    # in grafana.ini: allow_loading_unsigned_plugins = fr-ser-sqlite-datasource
else
    echo "Plugin already exists."
fi

# Set permissions for the plugin directory
chown -R grafana:grafana /var/lib/grafana/plugins

systemctl restart grafana-server

# 4. DOWNLOAD LOKI & PROMTAIL
echo -e "${GREEN}[4/8] Installing Loki & Promtail (v$LOKI_VERSION)...${NC}"
cd /tmp
wget -q https://github.com/grafana/loki/releases/download/v$LOKI_VERSION/loki-linux-arm64.zip
wget -q https://github.com/grafana/loki/releases/download/v$LOKI_VERSION/promtail-linux-arm64.zip

unzip -o loki-linux-arm64.zip
unzip -o promtail-linux-arm64.zip

mv loki-linux-arm64 /usr/local/bin/loki
mv promtail-linux-arm64 /usr/local/bin/promtail
chmod +x /usr/local/bin/loki /usr/local/bin/promtail

# Create Directory for configs
mkdir -p /etc/loki

# 5. CONFIGURE LOKI
echo -e "${GREEN}[5/8] Configuring Loki...${NC}"
# Default Config
wget -q https://raw.githubusercontent.com/grafana/loki/main/cmd/loki/loki-local-config.yaml -O /etc/loki/config-loki.yaml

# Create Service
cat <<EOF > /etc/systemd/system/loki.service
[Unit]
Description=Loki Log Aggregator
After=network.target

[Service]
ExecStart=/usr/local/bin/loki -config.file=/etc/loki/config-loki.yaml
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# 6. CONFIGURE PROMTAIL
echo -e "${GREEN}[6/8] Configuring Promtail...${NC}"
cat <<EOF > /etc/loki/config-promtail.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
- job_name: system
  static_configs:
  - targets:
      - localhost
    labels:
      job: demeter_logs
      __path__: ${LOGS_DIR}/*.log
EOF

# Create Service
cat <<EOF > /etc/systemd/system/promtail.service
[Unit]
Description=Promtail Log Shipper
After=network.target

[Service]
ExecStart=/usr/local/bin/promtail -config.file=/etc/loki/config-promtail.yaml
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable loki promtail
systemctl start loki promtail

# 7. AUTOMATIC DATASOURCE PROVISIONING
echo -e "${GREEN}[7/8] Provisioning Grafana Datasources...${NC}"
mkdir -p /etc/grafana/provisioning/datasources

cat <<EOF > /etc/grafana/provisioning/datasources/demeter.yaml
apiVersion: 1

datasources:
  - name: Demeter SQLite
    type: fr-ser-sqlite-datasource
    access: proxy
    uid: demeter-sqlite
    isDefault: true
    jsonData:
      path: "${DB_PATH}"

  - name: Demeter Loki
    type: loki
    access: proxy
    uid: demeter-loki
    url: http://localhost:3100
EOF

systemctl restart grafana-server

# 8. PERMISSIONS (ACLs)
echo -e "${GREEN}[8/8] Configuring Access Permissions (ACL)...${NC}"

# Check paths exist
if [ ! -d "$PYTHON_DIR" ]; then
    echo -e "${RED}WARNING: Path $PYTHON_DIR does not exist yet. Please clone the project to $PROJECT_ROOT first.${NC}"
else
    # Database Permissions for Grafana
    # Need +x on parent dirs to traverse
    setfacl -m u:$GRAFANA_USER:x "$USER_HOME"
    setfacl -m u:$GRAFANA_USER:x "$USER_HOME/Documentos"
    setfacl -m u:$GRAFANA_USER:x "$USER_HOME/Documentos/Proyectos_Personales"
    setfacl -m u:$GRAFANA_USER:x "$PROJECT_ROOT"
    setfacl -m u:$GRAFANA_USER:x "$PYTHON_DIR"
    setfacl -m u:$GRAFANA_USER:x "$PYTHON_DIR/data"
    
    # If DB exists, give read permission
    if [ -f "$DB_PATH" ]; then
        setfacl -m u:$GRAFANA_USER:r "$DB_PATH"
        echo "Granted Read Access to DB for user $GRAFANA_USER"
    else
        echo "DB File not found (yet). Run this script again after running the app once, OR manually run: setfacl -m u:$GRAFANA_USER:r $DB_PATH"
    fi
fi

echo -e "${GREEN}=== SETUP COMPLETE ===${NC}"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Logs configured from: $LOGS_DIR"
echo "DB configured from: $DB_PATH"
echo "Data Sources have been auto-provisioned. You can start creating dashboards immediately."
