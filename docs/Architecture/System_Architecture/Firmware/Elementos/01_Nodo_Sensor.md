# Nodo Sensor (Firmware)

Este documento detalla las capacidades, configuración y funcionamiento del **Nodo Sensor** dentro de la red Demeter.

## 1. Descripción General

El Nodo Sensor es un dispositivo basado en ESP32 encargado del monitoreo ambiental. Utiliza el protocolo ESP-Now para transmitir datos al Gateway de forma eficiente y con bajo consumo.

*   **Archivo Principal**: `C++/src/main_node.cpp`
*   **ID del Nodo**: `2`
*   **Comunicación**: ESP-Now (Ruta registrada hacia Gateway ID 1)

## 2. Hardware y Sensores

El nodo está configurado para gestionar múltiples sensores mediante una arquitectura modular.

| Sensor | Pin (GPIO) | Descripción | Clase C++ |
| :--- | :--- | :--- | :--- |
| **DHT22** | `4` | Temperatura y Humedad relativa. | `Demeter::Sensors::DHTSensor` |
| **DS18B20** | `5` | Temperatura de precisión (sonda). | `Demeter::Sensors::DS18B20Sensor` |
| **Humedad Suelo** | `34` (ADC) | Sensor analógico capacitivo/resistivo. | `Demeter::Sensors::SoilMoistureSensor` |

### Configuración de Pines
*   **DHT22**: Pin digital 4.
*   **DS18B20**: Pin digital 5 (requiere resistencia pull-up 4.7k).
*   **Analógico**: Pin 34 (Solo entrada, ADC1).

## 3. Funcionalidad

### Ciclo de Vida
1.  **Setup**:
    *   Inicializa Serial (115200 baudios).
    *   Registra la ruta ESP-Now hacia el Gateway (MAC Hardcoded).
    *   Registra los sensores en el gestor `Node`.
2.  **Loop**:
    *   Ejecuta `demeterNode.update()` para gestionar lecturas y transmisiones.

### Reportes
*   **Intervalo**: Configurado para reportar cada **5000 ms (5 segundos)**.
*   **Deep Sleep**: Deshabilitado actualmente (`false`).
*   **Tipo de Datos**: Envía reportes de Temperatura y Humedad usando el Protocolo Demeter V2.

## 4. Notas de Desarrollo

*   **Mock Sensors**: El firmware tiene una flag `USE_MOCK_SENSORS` (actualmente `true`) que permite simular lecturas si no hay sensores físicos conectados.
*   **Depuración**: Admite comandos básicos por Serial (e.g., enviar 'p' para PING).
