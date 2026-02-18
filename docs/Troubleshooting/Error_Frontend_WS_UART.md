# Solución de Problemas (Frontend y UART)

## 1. Error de WebSocket en Frontend

### Síntoma
La página web carga, pero dice "No hay conexión WS" al intentar controlar algo.

### Causa
Cuando accedes por Cloudflare (`https://patata.monters.org`), estás en un sitio **Seguro (HTTPS)**.
El navegador bloquea cualquier conexión que no sea segura.
El código intentaba conectar con `ws://` (Inseguro) en lugar de `wss://` (Seguro).

### Solución
He actualizado `script.js` para que detecte automáticamente si estás en HTTPS y use `wss://` en consecuencia.

---

## 2. Error de UART en Raspberry Pi

### Síntoma
```
[Errno 2] could not open port /dev/ttyUSB0: No such file or directory
```

### Causa
Aunque intentamos usar `/dev/ttyUSB0` por compatibilidad con drivers genéricos, parece que tu Raspberry Pi usa físicamente `/dev/serial0` (el puerto serie por defecto en los pines GPIO).

### Solución
Vamos a configurar Docker para que **"engañe"** al contenedor:
*   **Fuera (Realidad):** Usaremos `/dev/serial0`.
*   **Dentro (Contenedor):** Lo mapearemos como `/dev/ttyUSB0`.

De esta forma, no tenemos que cambiar ni el código ni la configuración que espera `ttyUSB0`.

**Cambio en `docker-compose.yml` (Raspberry):**
```yaml
    devices:
      - "/dev/serial0:/dev/ttyUSB0"  # Mapea serial0 (Host) a ttyUSB0 (Contenedor)
```
