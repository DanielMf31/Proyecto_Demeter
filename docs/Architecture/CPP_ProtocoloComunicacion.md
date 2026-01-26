# Documentación: ProtocoloComunicacion

**Archivo:** `src/Compartidos/ProtocoloComunicacion.cpp` / `include/ProtocoloComunicacion.h`

## Descripción
Implementa la lógica del protocolo de intercambio de datos entre la Raspberry Pi y el ESP32. Define los estados de la conversación (Handshake, Datos, Verificación) y los códigos de mensaje.

## Protocolo Definido
El sistema usa mensajes ASCII con códigos numéricos al inicio:
*   `101`: Solicitud de Conexión (Handshake Start)
*   `102`: Confirmación de Conexión (Handshake ACK)
*   `103`: Inicio de envío de datos de verificación (Eco)
*   `104`: Verificación Correcta (ACK final)
*   `105`: Error de Verificación (NACK)

## Responsabilidades
*   Gestionar la máquina de estados del protocolo (INICIAL -> ESPERANDO_102 -> ...).
*   Empaquetar y desempaquetar las matrices de comandos (5 comandos x 5 parámetros).
*   Realizar el handshake y la verificación de integridad (Eco de datos).

## Funciones Principales

### `procesarComunicacionReceptor()`
Función principal llamada en el loop.
*   Lee datos de `ComunicacionUART`.
*   Interpreta el código recibido (101, 104, etc.).
*   Avanza el estado del protocolo.
*   Si recibe datos de comandos, los almacena en el buffer interno.

### `getComandos(int destino[100][5])`
Copia los comandos recibidos y validados al buffer de la aplicación principal (para ser usados por `MaquinaEstado`).

## Uso en el Sistema
Actúa como puente e intérprete. Recibe bytes crudos, valida que sean una conversación coherente y válida, y entrega comandos limpios a `MaquinaEstado`.
