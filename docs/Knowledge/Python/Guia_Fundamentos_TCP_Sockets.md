# Fundamentos de Redes: TCP/IP y Sockets

## 1. Introducción
Este documento detalla los conceptos fundamentales de la comunicación en red utilizada en el Proyecto Demeter, específicamente el uso de sockets TCP/IP para la comunicación entre procesos (IPC).

## 2. Diferenciación de Puertos

Es crucial distinguir entre los dos tipos de "puertos" que interactúan en el sistema:

### 2.1 Puertos Físicos (Hardware)
Representan interfaces físicas de conexión para periféricos. En sistemas Linux, estos se exponen como archivos de dispositivo en el directorio `/dev/`.
*   **Ejemplo:** `/dev/ttyUSB0` o `/dev/serial0`.
*   **Uso:** Comunicación UART con microcontroladores (ESP32).

### 2.2 Puertos Lógicos (Software)
Son construcciones abstractas utilizadas por el kernel del sistema operativo para multiplexar el tráfico de red. Permiten que múltiples aplicaciones utilicen la misma interfaz de red simultáneamente.
*   **Rango:** 0 a 65535.
*   **Asignación:** El puerto **8888** ha sido designado para el servicio backend de Demeter.
*   **Analogía:** Si la dirección IP es la dirección de un edificio, el puerto lógico es el número de apartamento o extensión telefónica.

## 3. Arquitectura Cliente-Servidor

El sistema implementa una arquitectura TCP estándar:

### 3.1 El Servidor (Backend)
*   **Bind:** Reserva un puerto específico en el sistema operativo.
*   **Listen:** Espera pasivamente conexiones entrantes.
*   **Accept:** Establece una conexión dedicada para cada cliente, permitiendo concurrencia.

### 3.2 El Cliente (Interfaz/TUI)
*   **Connect:** Inicia la solicitud de conexión hacia la IP y Puerto del servidor.
*   **Send/Receive:** Intercambia flujos de bytes una vez la conexión es establecida.

Esta abstracción permite que la interfaz de usuario esté desacoplada de la lógica de control de hardware, aumentando la estabilidad del sistema.
