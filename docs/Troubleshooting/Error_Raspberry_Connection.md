# Errores de Conexión en Raspberry Pi

Este documento explica los dos errores persistentes que estás viendo y cómo solucionarlos definitivamente.

## 1. Error UART: "No such file or directory: '/dev/serial0'"

### Síntoma
A pesar de que cambiaste el `docker-compose.yml` para usar `/dev/ttyUSB0`, el log sigue diciendo:
```
Connecting to /dev/serial0 ... Failed
```

### Causa
El sistema de configuración (`configuration.py`) no estaba "escuchando" las variables de entorno que empiezan por `DEMETER_`. Por tanto, ignoraba `DEMETER_PORT=/dev/ttyUSB0` y seguía usando el valor por defecto (`/dev/serial0`).

### Solución (Aplicada en el código)
He actualizado `configuration.py` para que busque automáticamente variables con el prefijo `DEMETER_`. Ahora:
*   `DEMETER_PORT` -> Sobrescribe `PORT`
*   `DEMETER_HOST` -> Sobrescribe `HOST`

---

## 2. Error WebSocket: "Connection Failed ... 127.0.0.1"

### Síntoma
```
Connection Failed: ... ('127.0.0.1', 8000)
```

### Causa
Estás ejecutando el sistema en **dos máquinas diferentes**:
1.  **Servidor/PC:** Donde corre el Backend (Docker `demeter-backend`).
2.  **Raspberry Pi:** Donde corre el Core.

Cuando la Raspberry intenta conectarse a `localhost` (127.0.0.1), se busca a sí misma, **no a tu PC**. Como el backend no está en la Raspberry, falla.

### Solución
Debes decirle a la Raspberry la **Dirección IP Real** de tu PC/Servidor en la red local (ej: `192.168.1.XX`).

**Pasos:**
1.  En tu PC (Servidor), averigua tu IP:
    *   Linux/Mac: `ip addr` o `ifconfig` (busca `192.168...`)
2.  En la Raspberry, edita el `docker-compose.yml`:
    ```yaml
    environment:
      - DEMETER_HOST=192.168.1.35  <-- ¡PON LA IP DE TU PC AQUÍ!
    ```
3.  Reconstruye el contenedor.
