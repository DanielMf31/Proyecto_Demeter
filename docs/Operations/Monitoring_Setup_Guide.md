# Guía de Instalación y Configuración de Monitorización (Grafana + Loki) en Raspberry Pi

Esta guía detalla paso a paso cómo instalar Grafana, Loki y Promtail en una Raspberry Pi para visualizar los datos de sensores (SQLite) y los logs del sistema (Archivos de texto).

## 1. Prerrequisitos
Asegúrate de que tu Raspberry Pi esté actualizada:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y wget curl unzip acl
```

---

## 2. Instalación de Grafana

### Paso 2.1: Añadir Repositorio e Instalar
Grafana tiene un repositorio oficial para Debian/Ubuntu/Raspbian.

```bash
# Instalar dependencias
sudo apt-get install -y apt-transport-https software-properties-common wget

# Importar clave GPG
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null

# Añadir repositorio estable
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Instalar Grafana
sudo apt-get update
sudo apt-get install -y grafana
```

### Paso 2.2: Iniciar y Habilitar Servicio
```bash
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```
Accede a Grafana en: `http://<IP-DE-TU-RASPBERRY>:3000` (Usuario/Pass por defecto: `admin` / `admin`).

### Paso 2.3: Instalar Plugin de SQLite
Si `grafana-cli` falla, instálalo manualmente con estos comandos:

```bash
cd /var/lib/grafana/plugins
sudo wget https://github.com/fr-ser/grafana-sqlite-datasource/releases/download/v3.4.0/fr-ser-sqlite-datasource-3.4.0.zip
sudo unzip fr-ser-sqlite-datasource-3.4.0.zip
sudo rm fr-ser-sqlite-datasource-3.4.0.zip
sudo chown -R grafana:grafana /var/lib/grafana/plugins
sudo systemctl restart grafana-server
```

---

## 3. Instalación de Loki y Promtail (Logs)
Loki recibe los logs y Promtail los lee de tus archivos y los envía a Loki.

### Paso 3.1: Descargar Binarios (Para ARM64 - Raspberry Pi 3/4/5)
Busca la última versión en GitHub (ej. v2.9.x o superior). Usaremos v2.9.2 como ejemplo.

```bash
mkdir -p ~/loki-stack && cd ~/loki-stack

# Descargar Loki y Promtail
wget https://github.com/grafana/loki/releases/download/v2.9.2/loki-linux-arm64.zip
wget https://github.com/grafana/loki/releases/download/v2.9.2/promtail-linux-arm64.zip

# Descomprimir
unzip loki-linux-arm64.zip
unzip promtail-linux-arm64.zip

# Movel a /usr/local/bin
sudo mv loki-linux-arm64 /usr/local/bin/loki
sudo mv promtail-linux-arm64 /usr/local/bin/promtail
sudo chmod +x /usr/local/bin/loki /usr/local/bin/promtail
```

### Paso 3.2: Configuración de Loki
Crear archivo `config-loki.yaml`:
```bash
wget https://raw.githubusercontent.com/grafana/loki/main/cmd/loki/loki-local-config.yaml -O config-loki.yaml
```
*(Generalmente la config por defecto funciona bien para local).*

### Paso 3.3: Configuración de Promtail (Lectura de Logs)
Este es el paso crítico. Crear `config-promtail.yaml`:

```yaml
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
      __path__: /ruta/absoluta/a/tu/proyecto/Python/logs/*.log
```
**IMPORTANTE**: Cambia `/ruta/absoluta/a/tu/proyecto/` por la ruta real donde está `Proyecto_Demeter` en tu Raspberry.

### Paso 3.4: Crear Servicios Systemd
Para que se ejecuten automáticamente.

**Servicio Loki (`/etc/systemd/system/loki.service`)**:
```ini
[Unit]
Description=Loki Log Aggregator
After=network.target

[Service]
ExecStart=/usr/local/bin/loki -config.file=/home/tu_usuario/loki-stack/config-loki.yaml
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

**Servicio Promtail (`/etc/systemd/system/promtail.service`)**:
```ini
[Unit]
Description=Promtail Log Shipper
After=network.target

[Service]
ExecStart=/usr/local/bin/promtail -config.file=/home/tu_usuario/loki-stack/config-promtail.yaml
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```
*(Nota: Usamos `root` para simplificar la lectura de logs, pero veremos los permisos abajo para hacerlo seguro).*

```bash
sudo systemctl enable loki promtail
sudo systemctl start loki promtail
```

---

## 4. Gestión de Permisos (La parte "Complicada")
Si ejecutas Grafana/Promtail con usuarios dedicados (recomendado), necesitan permiso para leer los archivos de tu usuario.

### Opción A: Listas de Control de Acceso (ACL) - **Recomendada**
Es la forma más limpia y no requiere cambiar grupos principales.

1.  **Para la Base de Datos (SQLite):**
    El usuario `grafana` necesita leer el archivo `.db` y ejecutar (entrar) en la carpeta contenedora.
    # Dar permiso de lectura al archivo DB
    setfacl -m u:grafana:r /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data/demeter_data.db
    
    # Dar permiso de ejecución (búsqueda) a las carpetas padre (Vital para que llegue al archivo)
    setfacl -m u:grafana:x /home/montero
    setfacl -m u:grafana:x /home/montero/Documentos
    setfacl -m u:grafana:x /home/montero/Documentos/Proyectos_Personales
    setfacl -m u:grafana:x /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter
    setfacl -m u:grafana:x /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python
    setfacl -m u:grafana:x /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data

    /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data/demeter_data.db

2.  **Para los Logs:**
    Si corres Promtail como `root`, no necesitas esto. Si creaste un usuario `promtail`:
    ```bash
    setfacl -m u:promtail:r /ruta/a/Proyecto_Demeter/Python/logs/demeter_service.log
    setfacl -m u:promtail:x /ruta/a/Proyecto_Demeter/Python/logs
    ```

### Opción B: Grupos
Añadir el usuario `grafana` al grupo de tu usuario principal (ej. `pi` o `daniel`).
```bash
sudo usermod -aG daniel grafana
```
Luego asegúrate de que tus archivos tengan permisos de lectura para el grupo:
```bash
chmod g+r /ruta/a/Proyecto_Demeter/Python/data/demeter_data.db
chmod g+x /ruta/a/Proyecto_Demeter/Python/data
```

---

## 5. Configuración Final en Grafana

1.  **Entra a Grafana** (`http://IP:3000`).
2.  **Añadir Data Source SQLite**:
    *   Ve a *Connections* -> *Data Sources* -> *Add*.
    *   Busca "SQLite".
    *   **Path**: `/home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data/demeter_data.db`
    *   Pulsa "Save & Test". Debería salir verde si los permisos están bien.
3.  **Añadir Data Source Loki**:
    *   *Add Data Source* -> "Loki".
    *   **URL**: `http://localhost:3100`
    *   "Save & Test".


## 6. Crear Dashboard - Cheatsheet

### 6.1 Gráfico de Temperatura y Humedad (SQLite)
Para ver los datos de los sensores:

1.  Crea un nuevo **Panel**.
2.  En **Data Source**, selecciona `Demeter SQLite`.
3.  En el editor de query, selecciona formato **Time Series** (si está disponible) o usa **Raw SQL**:

**Query para Temperatura (Nodo 2):**
```sql
SELECT 
  timestamp, 
  temperature 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```

**Query para Humedad (Nodo 2):**
```sql
SELECT 
  timestamp, 
  humidity 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```

### 6.2 Visualizar Logs (Loki)
Para ver qué está pasando en el sistema:

1.  Crea un nuevo **Panel**.
2.  En **Data Source**, selecciona `Demeter Loki`.
3.  En el navegador de etiquetas (Log Browser), selecciona:
    *   **job**: `demeter_logs`
4.  O escribe la query directamente:
    ```logql
    {job="demeter_logs"}
    ```
    *   Para ver solo errores: `{job="demeter_logs"} |= "ERROR"`
    *   Para filtrar por nodo: `{job="demeter_logs"} |= "Node 2"`
