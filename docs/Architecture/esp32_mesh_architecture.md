# Arquitectura de la Red Edge (ESP32 y Raspberry Pi)

Este documento detalla el comportamiento lógico y de red del subsistema IoT en el proyecto Demeter, enfocado en el despliegue del invernadero, excluyendo conectividad Wi-Fi a nivel de nodo para enfatizar en una comunicación confiable por Radiofrecuencia (RF) y serial (UART).

## 1. Topología Física
- **Servidor Central**: Repositorio y procesador final en la nube o master local.
- **Raspberry Pi (Servidor Edge)**: Actúa como pasarela principal, almacenamiento local temporal (buffer) y puente de procesamiento pesado.
- **Nodo Gateway (ESP32)**: Único microcontrolador conectado físicamente por cable (UART) a la Raspberry Pi. Sirve exclusivamente como coordinador de la red y emisor/receptor de tramas de radio.
- **Nodos Sensores (ESP32)**: Unidades esclavas de campo dedicadas exclusivamente a la recolección pasiva de variables ambientales.
- **Nodos Actuadores (ESP32)**:
  - **Actuador 1**: Controla bombas hidráulicas y electroválvulas de riego.
  - **Actuadores 2 y 3**: Controlan los motores para la apertura y cierre de ventanas.

## 2. Flujo Lógico de Comunicaciones

El enrutamiento de red sigue un patrón estricto de solicitud-respuesta comandado desde la Raspberry Pi a nivel superior, o accionado localmente:

### 2.1 Petición de Telemetría (GetSensor)
1. El coordinador o la Raspberry Pi envía un comando `GetSensor` a un nodo sensor en la red.
2. El **Nodo Sensor** procesa el comando, lee sus periféricos (I2C, Analógico, DHT) y construye la trama de estado.
3. El Nodo Sensor emite de vuelta los datos brutos por radiofrecuencia.
4. El **Nodo Gateway** los intercepta y los reescribe puramente a través del bus serie (UART).
5. La **Raspberry Pi** recibe la telemetría UART, guarda los datos en su almacenamiento temporal de forma asíncrona, para procesarlos y unificarlos antes de emitirlos hacia la API en el Servidor Central.

### 2.2 Reacción y Control (setGPIO)
1. Para realizar una acción en el entorno, la orden de actuación nace del Servidor temporal o reglas locales e ingresa a la Raspberry Pi.
2. Ésta despacha por UART una orden de escritura de Hardware al Gateway.
3. El **Nodo Gateway** emite un comando estructurado `setGPIO` hacia la red RF.
4. Los **Nodos Actuadores (1, 2 o 3)** interceptan la orden si su identificador de malla coincide, y alteran sus pines físicos correspondientes con la instrucción.

### 2.3 Retroalimentación Bi-direccional (pinreport / systemreport)
* Siempre que un actuador cambia de estado, o por base de pulsos (keep-alive), emite tramas llamadas `pinreport` o `systemreport`.
* Éstas advierten del estado lógico actual del sistema eléctrico local del nodo.
* Son recuperadas en la pasarela RF del Gateway y enviadas a la Raspberry Pi para cerrar los bucles de control reactivos.
