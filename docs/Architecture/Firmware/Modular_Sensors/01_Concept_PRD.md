# Product Requirement Document (PRD): Sistema Modular de Sensores

| Atributo | Valor |
| :--- | :--- |
| **Título** | Sistema Modular de Sensores y Nodos |
| **Estado** | Borrador |
| **Autor** | Agent (Antigravity) |
| **Fecha** | 10-Feb-2026 |

## 1. Introducción y Propósito

Actualmente, el firmware de los nodos está muy acoplado a sensores específicos hardcodeados en el bucle principal. Se requiere migrar a una arquitectura orientada a objetos modular donde:
1.  Los **Sensores** sean drivers intercambiables que implementen una interfaz común.
2.  Los **Nodos** sean entidades configurables que puedan comportarse como Emisores (Sensores), Receptores (Actuadores) o Mixtos, sin reescribir el firmware base.

El objetivo es permitir que agregar un nuevo sensor (ej. BH1750) sea tan fácil como crear una clase `BH1750Sensor` e instanciarla en el `main`, sin tocar la lógica de transmisión ni de red.

## 2. Objetivos del Sistema

*   **Modularidad:** Desacoplar la lógica de *lectura* de la lógica de *transmisión*.
*   **Extensibilidad:** Facilitar la adición de nuevos drivers de hardware.
*   **Polimorfismo:** Poder iterar sobre una lista de sensores genéricos (`ISensor*`) para leerlos todos en bucle.
*   **Eficiencia:** Mantener el uso de RAM bajo, evitando asignaciones dinámicas excesivas en tiempo de ejecución.
*   **Tipado de Nodos:** Definir claramente qué *rol* juega un dispositivo (Sensor, Actuador, Híbrido) para optimizar su comportamiento (ej. deep sleep para sensores puros).

## 3. Historias de Usuario

*   **Como desarrollador**, quiero agregar un nuevo sensor creando solo un archivo `.h/.cpp` que implemente `read()` y `init()`, para no romper el código del protocolo.
*   **Como integrador**, quiero definir qué sensores tiene un nodo específico en el `main.cpp` mediante una lista de configuración, para desplegar distintos kits de hardware con el mismo núcleo de firmware.
*   **Como sistema**, quiero que los datos obtenidos de los sensores se empaqueten automáticamente en el formato del Protocolo Demeter V2 sin intervención manual.

## 4. Requerimientos Funcionales

1.  **Interfaz `ISensor`:**
    *   Debe proveer métodos para inicializar (`init`).
    *   Debe proveer métodos para obtener datos (`read`).
    *   Debe manejar su propio tiempo de muestreo (opcional, o gestionado externamente).
2.  **Clase `Node`:**
    *   Debe contener una colección de `ISensor`.
    *   Debe contener una colección de `IActuator` (futuro) o lógica de actuación.
    *   Debe encargarse de orquestar la lectura de todos los sensores registrados.
    *   Debe inyectar los datos leídos en el `ProtocolEngine` para su envío.
3.  **Roles de Nodo:**
    *   `SensorNode`: Lee -> Envía -> Duerme (Deep Sleep).
    *   `ActuatorNode`: Escucha -> Ejecuta (Always On).
    *   `HybridNode`: Lee -> Envía -> Escucha (Light Sleep / Intervalos).

## 5. Requerimientos No Funcionales

*   **Lenguaje:** C++17 o superior.
*   **Hardware:** ESP32 (S3/C3/Original).
*   **RAM:** Minimizar el overhead de vtables y punteros inteligentes. Uso de `std::vector` acotado o `std::array` si es posible.
*   **Latencia:** La lectura de sensores no debe bloquear el loop de comunicación por tiempos prolongados (uso de máquinas de estado internos en sensores lentos si aplica).

## 6. Métricas de Éxito

*   Tiempo para integrar un nuevo sensor reducido de 2 horas a 30 minutos.
*   Código `main_node.cpp` reducido a instanciación y configuración, sin lógica de negocio.
