# Hoja de Ruta Técnica: Demeter v2.0

Este documento detalla la implementación técnica de las nuevas funcionalidades y la evolución de la arquitectura del proyecto Proyecto_Demeter.

## 1. Evolución de la Infraestructura Central

### 1.1 Migración a PostgreSQL
Actualmente usamos SQLite. Para manejar múltiples nodos y datos históricos a largo plazo, migraremos a un contenedor dedicado de PostgreSQL.
- **Implementación**:
    - Añadir servicio `db` en `docker-compose.server.yml` usando la imagen `postgres:15-alpine`.
    - Actualizar `DatabaseManager` en Python para usar `SQLAlchemy` o `asyncpg`.
    - Definir esquemas para: `device_readings`, `system_logs`, `user_profiles`, y `sequence_history`.

### 1.2 Redis para Gestión de Estado
Redis servirá como memoria de corto plazo para el sistema.
- **Uso**:
    - **Estado Real de Pines**: Guardar si un pin está ON/OFF sin consultar la base de datos.
    - **Progreso de Secuencias**: Almacenar el paso actual de una secuencia activa.
    - **Caché de API**: Acelerar la carga de tableros de control.
- **Implementación**: Servicio `redis:alpine` en el servidor.

### 1.3 Microservicio de Análisis de Datos
Un contenedor independiente (Python/FastAPI) enfocado en cálculos matemáticos pesados.
- **Funciones**:
    - Cálculo de VPD (Déficit de Presión de Vapor).
    - Predicción de necesidades de riego basado en clima.
    - Generación de reportes PDF/Excel automáticos.

---

## 2. Estrategia de Sincronización (Local -> Cloud)

Para garantizar la integridad de los datos ante cortes de internet en la Raspberry Pi:

### Arquitectura "Store and Forward"
1. **Almacenamiento Local**: La Pi sigue guardando telemetría en un SQLite local (`pi_local.db`).
2. **Servicio de Sincronización**: Un script independiente en la Pi se activa cada 6 horas.
3. **Proceso de Envío**:
    - Consulta todas las filas de `pi_local.db` marcaras como `synced = 0`.
    - Envía los datos en un solo bloque (Batch) mediante un endpoint `/api/sync/bulk` en el Servidor.
    - El servidor valida e inserta en Postgres.
    - Tras el éxito (HTTP 200), la Pi actualiza su DB local a `synced = 1`.

---

## 3. Integración de Grafana en Ruta Web

Para servir Grafana bajo `patata.monters.org/grafana/`:

### Configuración de Nginx
```nginx
location /grafana/ {
    proxy_pass http://grafana:3000/;
    proxy_set_header Host $host;
}
```

### Configuración de Grafana (Variables de Entorno)
- `GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s:%(http_port)s/grafana/`
- `GF_SERVER_SERVE_FROM_SUB_PATH=true`

---

## 4. Frontend Avanzado

### 4.1 Sequencer UI
- **Interfaz**: Un constructor visual donde el usuario añade "bloques" (Acción: ON, Pin: 4, Duración: 10s).
- **Lógica**: Convertir el diseño visual en un objeto JSON `SequenceCommand` y enviarlo al Backend.

### 4.2 Auth & Personalización
- **JWT (JSON Web Tokens)**: Implementar login seguro.
- **Perfiles**: Permitir que un usuario solo vea sus nodos o sus experimentos específicos.

---

## 5. Funcionalidades Sugeridas "Demeter+"

1. **Alertas Inteligentes**: Microservicio que conecta con Telegram/Whatsapp para avisar: "Batería del Nodo 2 baja (3.2V)".
2. **Modo Offline con HMI**: Si la Pi tiene pantalla, mostrar un panel táctil local usando la caché de Redis.
3. **Escucha de Voz**: Integración básica con comandos de voz (ej. "Riega la zona 1").
4. **Firmware OTA**: Capacidad de subir binarios `.bin` desde la web para actualizar los ESP32 de forma remota a través del Gateway UART.

---
