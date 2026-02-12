# 3. Modelo Cliente-Servidor (IPC)

La comunicación entre la interfaz de usuario y el servicio de fondo se realiza mediante sockets TCP locales (IPC). Esto desacopla la interfaz gráfica (que puede bloquearse o cerrarse) del proceso de control crítico (que debe permanecer siempre activo).

## 3.1 Protocolo de Intercambio (JSON/TCP)

A diferencia del protocolo binario usado en UART, la comunicación Cliente-Servidor usa **JSON** sobre flujos TCP por su facilidad de depuración y parseo en Python.

### Puerto por Defecto
*   **Socket:** `8888` (Configurable vía `DEMETER_SOCKET_PORT`).
*   **Host:** `0.0.0.0` (Permite conexiones remotas) o `127.0.0.1`.

### Estructura del Mensaje (Request)
Los clientes envían objetos JSON con un campo `type` obligatorio.

#### Ejemplo: Comando GPIO
```json
{
  "type": "GPIO_CMD",
  "pin": 4,
  "action": "ON" 
}
```

#### Ejemplo: Solicitar Secuencia
```json
{
  "type": "SEQ_CMD",
  "target_id": 2,
  "steps": [
    {"pin": 4, "value": 1, "delay_ms": 1000},
    {"pin": 4, "value": 0, "delay_ms": 0}
  ]
}
```

### Estructura de la Respuesta (Response)
El servidor responde con un objeto `ActionResponse` serializado.

```json
{
  "status": "OK",
  "message": "Command Sent to UART",
  "pin_state": true
}
```

## 3.2 Implementación en GUI

La GUI (`proyecto_demeter.ui`) actúa como un cliente tonto:
1.  Al iniciar, conecta al socket `host:port`.
2.  Para enviar una acción (click de botón), serializa el comando Pydantic y lo envía por el socket.
3.  Mantiene un hilo de escucha (o `loop.create_task` en AsyncTkinter) para leer mensajes del socket.
4.  Si recibe un JSON tipo `DATA_REPORT`, actualiza la vista de sensores en tiempo real.

## 3.3 Ventajas de este Diseño

1.  **Resiliencia:** Si la GUI crashea, el servicio sigue operando (manteniendo conexiones, logs y estado).
2.  **Multi-Cliente:** Se pueden tener múltiples GUIs abiertas, o una GUI y un script de monitoreo simultáneamente.
3.  **Remoto:** La GUI podría ejecutarse en un PC diferente al que tiene el hardware conectado, simplemente apuntando a la IP de la Raspberry Pi.
