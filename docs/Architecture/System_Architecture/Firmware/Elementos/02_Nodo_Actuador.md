# Nodo Actuador (Implementación)

El **Nodo Actuador** (ID 3) es una implementación concreta de la clase `Node` especializada en control.

## Arquitectura Específica
Siguiendo el patrón `Node -> SystemContext`, esta implementación tiene una configuración particular:

1.  **Executor**: **ACTIVO**. Habilitado para controlar el Relé (Pin 2).
2.  **ProtocolEngine**: **ACTIVO**. Escucha `SET_GPIO` y `PING`.
3.  **SensorManager**: **DESACTIVADO** (o Vacío).
    *   *Razón*: No requiere lecturas ambientales periódicas.
    *   *Nota*: El monitoreo de batería se maneja como una lectura de sistema directa, no vía SensorManager en esta versión.

## Main (`main_node_actuador_ventana.cpp`)
El punto de entrada instancia la clase `NodeAccuator` (o configuración equivalente) y establece:
*   ID = 3.
*   Ruta al Gateway.
*   Callbacks específicos para acciones de ventana.

Esta separación permite que el código del Actuador sea ligero, cargando solo los módulos de `SystemContext` necesarios.
