# PRD: GpioController MVP & Serial Control

## 1. Introducción
Este documento define los requisitos para el Producto Mínimo Viable (MVP) del controlador de GPIOs en el firmware Demeter. El objetivo es validar el control físico de los pines 4, 5, 6 y 7 del ESP32 S3 mediante comandos directos desde el Monitor Serial.

## 2. Requisitos Funcionales

### 2.1. Inicialización de Hardware
*   **Pines Soportados:** 4, 5, 6, 7.
*   **Modo:** `OUTPUT` (Salida Digital).
*   **Estado Inicial:** `LOW` (Apagado).
*   **Inicialización:** Debe ocurrir en `main_receptor.cpp` durante el `setup()`.

### 2.2. GpioController
*   **Método `init()`:** Debe configurar los pines definidos.
*   **Método `execute(cmd)`:** Debe recibir un `SetGpioCmd` y aplicar `digitalWrite` al pin correspondiente.
*   **Validación:** Debe ignorar comandos para pines no inicializados o protegidos (ej. Pines de UART 0/1).

### 2.3. Interfaz de Control (Serial Menu)
*   **Menú Interactivo:** El `main_receptor.cpp` debe mostrar opciones para controlar los pines manualmente.
*   **Teclas:**
    *   `'1'`: Toggle Pin 4
    *   `'2'`: Toggle Pin 5
    *   `'3'`: Toggle Pin 6
    *   `'4'`: Toggle Pin 7
*   **Feedback:** Imprimir por Serial el estado resultante ("PIN 4 -> ON").

## 3. Criterios de Aceptación
1.  Al pulsar '1' en el monitor serial, el Pin 4 debe cambiar de estado.
2.  El cambio debe reflejarse físicamente (medible con LED/Multímetro) y lógicamente (mensaje serial).
3.  El sistema no debe bloquearse tras múltiples pulsaciones.
4.  Los tests nativos deben validar la lógica de `execute` sin hardware real.

## 4. Estrategia de Pruebas
*   **Unitarias (Nativas):** Usar Mocks de `digitalWrite` para verificar que `GpioController` llama a la función correcta con los parámetros correctos.
*   **Integración (Manual):** Subir al ESP32 y verificar visualmente con LEDs.
