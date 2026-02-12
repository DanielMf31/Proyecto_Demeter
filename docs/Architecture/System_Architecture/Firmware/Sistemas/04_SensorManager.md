# SensorManager (Gestor de Sensores)

## Descripción
El **SensorManager** es el subsistema encargado de la abstracción, lectura y gestión del ciclo de vida de los sensores conectados al nodo.

## Responsabilidades
1.  **Ciclo de Vida**: Inicializa (`begin`) y actualiza (`update`) todos los sensores registrados.
2.  **Abstracción**: Permite tratar cualquier sensor (DHT22, Soil, DS18B20) bajo una interfaz común (`ISensor`).
3.  **Recolección**: Itera sobre los sensores activos para recolectar datos y pasarlos al `ProtocolEngine` para su envío.

## Integración en SystemContext
Dentro del orquestador `SystemContext`:
*   Si el Nodo es un **Actuador Puro**, el `SensorManager` puede estar desactivado o vacío.
*   Si el Nodo es un **Sensor**, el `SensorManager` orquesta las lecturas periódicas.

## Interfaz ISensor
Todos los drivers de sensores deben implementar:
*   `read()`: Devuelve el valor flotante.
*   `getType()`: Retorna el tipo de medición (Temp, Hum, etc.).
*   `init()`: Configuración de hardware.
