# Sistemas de Logging Profesional en Python

Este documento explica los principios de diseño para sistemas de registro (logging) robustos y escalables, orientados a aplicaciones de control y hardware como el Proyecto Demeter.

## 1. Filosofía del Logging
Un buen sistema de logs debe responder tres preguntas:
1.  **¿Qué pasó?** (Evento)
2.  **¿Cuándo pasó?** (Timestamp preciso)
3.  **¿Dónde y Por qué pasó?** (Contexto y Stack Trace)

## 2. Niveles de Severidad (Estándar)
Python utiliza una jerarquía de niveles. Es crucial usar el nivel adecuado para filtrar ruido.

| Nivel | Valor | Uso | Ejemplo |
| :--- | :--- | :--- | :--- |
| **DEBUG** | 10 | Información detallada para diagnóstico. Volumen alto. | `RX Raw Byte: 0xA4`, `Calculando checksum...` |
| **INFO** | 20 | Confirmación de que las cosas funcionan según lo previsto. | `Conexión establecida`, `Comando enviado`, `Botón pulsado` |
| **WARNING** | 30 | Algo inesperado pasó, pero el sistema sigue funcionando. | `Reintento de conexión (1/3)`, `Temperatura alta` |
| **ERROR** | 40 | Una función falló. Se perdió una operación. | `Timeout esperando respuesta`, `Actuador no responde` |
| **CRITICAL** | 50 | El programa no puede continuar. | `Hardware no detectado`, `Sin permisos de escritura` |

## 3. Arquitectura de Loggers

En sistemas profesionales, no se usa un solo `print()`. Se utiliza una arquitectura de **Handlers** y **Formatters**.

### A. Logger de Instancia (Session Logging)
Para cumplir con el requisito de *"un log por cada ejecución"*:
*   Se genera un nombre de archivo único al iniciar: `session_2023-10-27_14-30-00.log`.
*   Esto permite "viajar en el tiempo" y revisar exactamente qué pasó en la sesión del martes pasado sin mezclarlo con la de hoy.

### B. Separación de Concerns (Canales)
Podemos tener múltiples "canales" de log escribiendo al mismo archivo o a archivos diferentes:

1.  **Logger Operativo (App flow):**
    *   Registra acciones de usuario (`User clicked Button 1`).
    *   Cambios de estado (`System State: IDLE -> EXECUTING`).
    *   Nivel típico: `INFO`.

2.  **Logger de Trazabilidad (Data flow):**
    *   Registra el **contenido** de los datos.
    *   Ejemplo: `TX Packet: [200, 1, 1, 0, 1000]`
    *   Nivel típico: `DEBUG`.
    *   *Tip:* A veces se guarda en un archivo separado `trace.log` si hay muchísimos datos.

## 4. Implementación Propuesta para Demeter

Basado en tu solicitud, diseñaremos una estructura así:

### Estructura de Carpetas
```
Python/
└── logs/
    ├── app.log            (Rotativo: Últimos N días)
    └── sessions/          (Detallado por ejecución)
        ├── session_20240126_1800.log
        ├── session_20240126_1805.log
        └── ...
```

### Componente `utils/logger.py`
Crearemos una clase `SystemLogger` (Singleton o Trazable) que configure automáticamente:
1.  **Console Handler:** Para que veas en la pantalla lo importante (INFO+).
2.  **File Handler:** Para guardar absolutamente todo (DEBUG+) en el archivo de sesión.

### Ejemplo de Trazabilidad Cruzada
Cuando pulses un botón, el log debería contar una historia:

```text
[INFO] [GUI] Usuario presionó 'Activar Actuador 1'
[INFO] [UART] Preparando envío de comando...
[DEBUG] [PROTOCOL] Payload generado: "200 1 1 0 1000 0"
[DEBUG] [DRIVER] TX Raw: b'200 1 1 0 1000 0\n'
[INFO] [UART] Comando enviado correctamente.
```


## 5. Estrategia de Instrumentación: ¿Dónde poner logs?

No se trata de loguear cada línea de código, sino los **Cambios de Estado** y las **Fronteras del Sistema**.

### A. Fronteras (Input/Output)
Siempre que datos entren o salgan de tu sistema, debe haber un log.
*   **GUI (Entrada):** `[INFO] Usuario pulsó botón 'Activar 5'`.
*   **UART (Salida):** `[DEBUG] Bytes enviados: AB CD EF`.
*   **UART (Entrada):** `[DEBUG] Bytes recibidos: 104`.

### B. Puntos de Decisión (Logic Branches)
Si el código toma un camino u otro, regístralo.
*   *Mal:* `if x > 5: do_something()`
*   *Bien:* `if x > 5: logger.info(f"Valor {x} supera umbral, activando freno"); do_something()`

### C. Captura de Errores (Exceptions)
Nunca uses un `except: pass`. Mínimo un log.
*   `logger.exception("Error inesperado en loop principal")` (Esto imprime automáticamente el Stack Trace).

## 6. Formatters: ¿Uno para todos?

En sistemas pequeños/medianos como Demeter, **la consistencia es rey**.

*   **Recomendación:** Usa **UN SOLO Formatter** estándar para todos los loggers. Facilita la lectura y el parseo automático (si usaras herramientas como Grafana/Loki en el futuro).
*   **Formato sugerido:** `%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`

**Ejemplo Visual:**
```text
2024-01-26 20:00:01 | INFO     | GUI      | Usuario inició conexión
2024-01-26 20:00:02 | INFO     | UART     | Abriendo puerto /dev/ttyS0...
2024-01-26 20:00:03 | DEBUG    | PROTOCOL | Enviando Handshake [101]
2024-01-26 20:00:03 | WARNING  | PROTOCOL | Timeout esperando 102 (Intento 1/3)
```


## 7. Ejemplos Prácticos para Proyecto Demeter

Aquí tienes el mapa exacto de "dónde poner el micrófono" en tu código actual.

### A. Capa de Usuario (GUI) - `gui_controller.py`
Esta capa habla de **Intenciones del Usuario**.
*   **Logger:** `logging.getLogger('Demeter.GUI')`
*   **Eventos Clave:**
    1.  **Click en Botón:**
        *   `logger.info("Usuario solicitó activación manual del Actuador 3")`
    2.  **Cambio de Configuración:**
        *   `logger.info("Puerto serial cambiado a /dev/ttyUSB1")`
    3.  **Estado Visual:**
        *   `logger.warning("Intento de comando sin conexión activa")`

### B. Capa Lógica (Protocol) - `protocol_engine.py`
Esta capa habla de **Máquinas de Estados y Validación**.
*   **Logger:** `logging.getLogger('Demeter.Protocol')`
*   **Eventos Clave:**
    1.  **Transiciones de Estado:**
        *   `logger.debug("Estado: ESPERANDO_102 -> TRANSMITIENDO")` (Nivel DEBUG porque ocurre mucho).
    2.  **Éxito de Ciclo:**
        *   `logger.info("Ciclo de transmisión completado y verificado en 450ms")`
    3.  **Fallos de Lógica:**
        *   `logger.error("Error de Verificación: Enviado [1,1,0,0,0] != Recibido/Eco [1,2,0,0,0]")`

### C. Capa de Hardware (UART) - `uart_service.py`
Esta capa habla de **Bytes y Cables**.
*   **Logger:** `logging.getLogger('Demeter.UART')`
*   **Eventos Clave:**
    1.  **Conexión Física:**
        *   `logger.info("Puerto /dev/ttyS0 abierto exitosamente @ 115200")`
    2.  **Tráfico (Trace):**
        *   `logger.debug(f"TX >> {raw_bytes.hex()}")` (Crucial para ver qué sale realmente).
        *   `logger.debug(f"RX << {raw_bytes.hex()}")` (Crucial para ver si entra ruido/basura).
    3.  **Errores Físicos:**
        *   `logger.critical("Puerto serial desconectado inesperadamente")`

### Resumen de Implementación
Tendrás 3 loggers (GUI, Protocol, UART) pero todos escribirán al mismo archivo de sesión (`session_X.log`), permitiéndote leer la historia cronológicamente:


## 8. Estandarización de Acciones de Usuario: ¿MVP vs Profesional?

Tu duda es muy buena: *"¿Logueo línea por línea o creo una función genérica?"*

### A. Enfoque Manual (Ideal para MVP)
En proyectos pequeños, no sobre-ingenierices. Escribe el log explícitamente en cada función del botón.
*   **Ventaja:** Lees el código y sabes exactamente qué se va a loguear.
*   **Código:**
    ```python
    def btn_activar_1_click(self):
        logger.info("[GUI] Click: Activar Actuador 1")  # <--- Manual y claro
        self.enviar_comando(1)
    ```

### B. Enfoque "Decorador" (Nivel Profesional)
Cuando tienes 50 botones, no quieres escribir 50 logs. Usas un **Decorador** (`@log_action`).
*   **Ventaja:** Si mañana quieres cambiar el formato del log, lo cambias en un solo sitio.
*   **Código:**
    ```python
    # En utils/decorators.py
    def log_gui_action(func):
        def wrapper(*args, **kwargs):
            logger.info(f"[GUI] Acción iniciada: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper

    # En tu GUI
    @log_gui_action
    def btn_activar_1_click(self):
        self.enviar_comando(1)
    ```

### C. Recomendación para Demeter (Hoy)
Para tu sistema actual (5-6 botones), usa el **Enfoque A (Manual) pero Estandarizado**.
Crea una función helper `log_action(nombre_accion)` en tu clase GUI y llámala.

```python
def log_action(self, action_name, params=None):
    logger.info(f"[GUI] ACTION: {action_name} | PARAMS: {params}")

# Uso
self.log_action("ACTIVATE_ACTUATOR", {"id": 1, "duration": 1000})
```
Esto te da la limpieza del profesionalismo sin la complejidad de los decoradores todavía.


