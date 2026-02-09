# Modelos de Concurrencia en Python

## 1. Introducción
Este documento analiza los diferentes modelos de ejecución concurrente disponibles en Python y justifica la elección de `asyncio` para el servicio backend de Demeter.

## 2. Comparativa de Modelos

### 2.1 Multiprocesamiento (Multiprocessing)
*   **Descripción:** Ejecución de múltiples instancias del intérprete de Python. Cada proceso tiene su propio espacio de memoria aislado.
*   **Ventaja:** Verdadero paralelismo en CPUs multinúcleo. Evita el bloqueo del GIL (Global Interpreter Lock).
*   **Uso en Demeter:** Se utiliza a nivel de sistema para separar el Backend (`async_service.py`) de la Interfaz de Usuario. Esto asegura que un fallo crítico en la interfaz no detenga el control del hardware.

### 2.2 Hilos (Threading)
*   **Descripción:** Múltiples flujos de ejecución dentro de un mismo proceso, compartiendo memoria.
*   **Limitación:** En CPython, el GIL impide que dos hilos ejecuten bytecode simultáneamente, limitando su eficacia para tareas intensivas de CPU.
*   **Riesgo:** Introduce complejidad en la sincronización (Race Conditions).

### 2.3 Asincronía (Asyncio)
*   **Descripción:** Modelo de concurrencia cooperativa en un solo hilo (Single-Threaded Event Loop).
*   **Funcionamiento:** Las tareas ceden el control voluntariamente cuando esperan operaciones de I/O (Entrada/Salida), como leer de un socket o escribir en un puerto serial.
*   **Uso en Demeter:** Es el núcleo del servicio backend. Permite manejar simultáneamente:
    1.  Recepción de comandos por TCP.
    2.  Lectura de datos del puerto Serial (UART).
    3.  Escritura de logs.
*   **Beneficio:** Alta eficiencia para tareas limitadas por I/O sin la sobrecarga de memoria de múltiples hilos o procesos.

## 3. Diagrama de Flujo Asíncrono
El servicio opera un "Bucle de Eventos" (Event Loop) que monitoriza descriptores de archivo (Sockets y UART). Cuando uno está listo para lectura, invoca la retrollamada (callback) correspondiente, procesa los datos y retorna el control al bucle inmediatamente.
