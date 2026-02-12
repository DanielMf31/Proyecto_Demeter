# SystemContext (Orquestador)

## Descripción
El **SystemContext** integra los subsistemas principales del firmware, actuando como el cerebro operativo de cualquier Nodo.

## Componentes Gestionados
1.  **Executor**: Para acciones físicas (Actuadores).
2.  **ProtocolEngine**: Para comunicación (Gateway/Nodos).
3.  **SensorManager**: Para recolección de datos (Sensores).

## Responsabilidad (SOC)
*   **Gestión Interna**: Asegura que los componentes se inicialicen en el orden correcto.
*   **Enrutamiento de Eventos**: Conecta los eventos del `ProtocolEngine` (e.g., recepción de comandos) con el `Executor`.
*   **Ciclo Principal**: Expone un método `loop()` único que el `Node` llama, delegando la actualización a sus componentes hijos.

## Modos de Operación
*   Actúa como fachada para cambiar entre modos de ejecución (Inmediato, Cola, Bajo Consumo), afectando a todos los subsistemas coordinadamente.
