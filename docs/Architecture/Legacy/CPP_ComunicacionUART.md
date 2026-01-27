# Documentación: ComunicacionUART

**Archivo:** `src/Compartidos/ComunicacionUART.cpp` / `include/ComunicacionUART.h`

## Descripción
Clase encargada de la comunicación serie de bajo nivel entre dispositivos. Envuelve la funcionalidad de `HardwareSerial` del ESP32, proporcionando métodos robustos de envío y recepción con timeouts controlados.

## Responsabilidades
*   Inicializar el puerto UART (Serial2) con pines y baudrate específicos.
*   Enviar cadenas de texto y arrays de bytes.
*   Recibir datos con control de flujo (lectura de línea completa).
*   Parsear comandos numéricos básicos (array de 5 enteros).
*   Limpiar buffers para evitar lecturas de datos residuales.

## Funciones Principales

### `inicializar()`
Configura el puerto serial.
*   **Importante:** Establece un `setTimeout(10)` para evitar que las lecturas bloqueen el ciclo principal del programa.

### `recibir()`
Lee una línea completa hasta encontrar `\n`.
*   Retorna `String`: La línea limpia (trim).
*   Si no hay datos, retorna string vacío.

### `recibirComando(int comando[5])`
Intenta parsear una línea recibida como una secuencia de 5 enteros separados por espacios.
*   Retorna `true` si se decodificaron 5 valores correctamente.

## Uso en el Sistema
Es la capa más baja de comunicación. `ProtocoloComunicacion` utiliza esta clase para enviar y recibir sus paquetes sin preocuparse por los detalles del hardware serial.
