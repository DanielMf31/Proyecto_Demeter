#!/bin/bash
set -e

# Colores para que quede bonito
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_PATH="/home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/Python/Playground/SQL/logs"

echo -e "${BLUE}🚀 Iniciando Instalación Automática de Loki & Promtail${NC}"
echo -e "${BLUE}-----------------------------------------------------${NC}"

# 1. Instalar dependencias previas
echo -e "${GREEN}📦 Añadiendo repositorio oficial de Grafana...${NC}"
sudo apt-get update
sudo apt-get install -y wget gpg

# Crear directorio de llaves si no existe
sudo mkdir -p /etc/apt/keyrings/
# Descargar llave GPG
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
# Añadir repo
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt-get update

# 2. Instalar Loki y Promtail
echo -e "${GREEN}⬇️  Instalando paquetes (esto puede tardar un poco)...${NC}"
sudo apt-get install -y loki promtail

# 3. Configurar Promtail
echo -e "${GREEN}⚙️  Configurando Promtail para leer tus logs...${NC}"

CONFIG_FILE="/etc/promtail/config.yml"

# Backup por si acaso
if [ ! -f "$CONFIG_FILE.bak" ]; then
    sudo cp $CONFIG_FILE "$CONFIG_FILE.bak"
fi

# Inyectar configuración
echo "   -> Apuntando a: $LOG_PATH/*.log"

cat <<EOF | sudo tee $CONFIG_FILE > /dev/null
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
- job_name: playground_logs
  static_configs:
  - targets:
      - localhost
    labels:
      job: python_generators
      __path__: ${LOG_PATH}/*.log
      host: $(hostname)
EOF

# 4. Arreglar Permisos (Promtail necesita leer tus archivos)
echo -e "${GREEN}🔓 Ajustando permisos de lectura...${NC}"
# Añadimos al usuario promtail al grupo de tu usuario (para que pueda leer)
sudo usermod -aG $(whoami) promtail || true
# Aseguramos que la carpeta tenga permisos de lectura para "otros" (o+r)
chmod -R o+r "$LOG_PATH" || true
# Hacer ejecutable el directorio para que pueda entrar
chmod o+x $(dirname "$LOG_PATH") || true
chmod o+x "$LOG_PATH" || true


# 5. Reiniciar Servicios
echo -e "${GREEN}🔄 Reiniciando Loki y Promtail...${NC}"
sudo systemctl restart loki
sudo systemctl restart promtail

echo -e "${BLUE}-----------------------------------------------------${NC}"
echo -e "${GREEN}✅ ¡INSTALACIÓN COMPLETADA!${NC}"
echo -e "Pasos Siguientes:"
echo -e "1. Ejecuta tu generador: python3 generador_datos.py"
echo -e "2. Ve a Grafana -> Data Sources -> Add 'Loki'"
echo -e "3. URL: http://localhost:3100"
echo -e "4. ¡Listo para ver logs!"
