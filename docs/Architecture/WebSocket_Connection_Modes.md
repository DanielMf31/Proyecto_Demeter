# Modos de Conexión WebSocket (Raspberry Pi -> Backend)

La Raspberry Pi actúa como **CLIENTE** WebSocket. Esto significa que **ella inicia** la conexión hacia el Backend (Servidor). No se queda "escuchando" en un puerto (salvo para la UART), sino que busca activamente al servidor.

## Arquitectura Actual

```mermaid
graph LR
    R[Raspberry Pi (Cliente)] -->|Inicia Conexión| S[Backend/Servidor (Host)]
    R -->|Pide| ws://HOST:PORT/ws/raspberry_gateway
```

Gracias a esto, la Raspberry **no necesita abrir puertos en su router**. Solo necesita salida a Internet.

---

## Modo 1: Red Local (LAN)
Ideal para desarrollo o si ambos dispositivos están en la misma casa/oficina.

*   **Host:** IP Local del PC Servidor (ej: `192.168.1.35`)
*   **Puerto:** `8000` (HTTP estándar del backend)
*   **Seguridad:** Baja (texto plano), pero rápido.

**Configuración en `docker-compose.yml` de Raspberry:**
```yaml
environment:
  - DEMETER_HOST=192.168.1.35   # Cambiar por TU IP local real
  - DEMETER_SOCKET_PORT=8000
```
*URL Resultante:* `ws://192.168.1.35:8000/ws/raspberry_gateway`

---

## Modo 2: Internet (Cloudflare Tunnel)
Ideal para producción o si la Raspberry está en el campo (otra red).

*   **Host:** Tu dominio público (ej: `patata.monters.org`)
*   **Puerto:** `443` (HTTPS/WSS Estándar)
*   **Seguridad:** Alta (Encriptado SSL/TLS).
*   **Requisito:** `cloudflared` debe estar corriendo en el Servidor y apuntando al backend puerto 8000.

**Configuración en `docker-compose.yml` de Raspberry:**
```yaml
environment:
  - DEMETER_HOST=patata.monters.org
  - DEMETER_SOCKET_PORT=443    # Puerto HTTPS estándar
```
*URL Resultante:* `wss://patata.monters.org:443/ws/raspberry_gateway`

> **Nota:** El código detecta automáticamente si el puerto es 443 y cambia `ws://` por `wss://` (Seguro).
