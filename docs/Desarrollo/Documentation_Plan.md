# Plan de Documentación Integral - Proyecto Demeter

Este documento define la estrategia para documentar todo el código fuente y la arquitectura del sistema.

## 1. Estándares de Código

### 1.1. C++ (Doxygen)
Usaremos el formato **Javadoc-style** para Doxygen en archivos C++.
*   **Archivos (.h/.cpp):** Bloque `@file` con descripción, autor y fecha.
*   **Clases:** Bloque `@brief` y `@details` explicando la responsabilidad.
*   **Métodos:**
    *   `@brief`: Resumen corto.
    *   `@param`: Explicación de cada parámetro.
    *   `@return`: Qué devuelve.
    *   `@note`: Detalles importantes de implementación.

**Ejemplo C++:**
```cpp
/**
 * @brief Controlador de Actuadores GPIO.
 * 
 * Gestiona el estado físico de los pines del ESP32.
 */
class GpioController {
public:
    /**
     * @brief Ejecuta una orden de cambio de estado.
     * @param cmd Estructura con el pin y el valor deseado.
     */
    void execute(const Demeter::SetGpioCmd& cmd);
};
```

### 1.2. Python (Docstrings)
Usaremos el formato **Google Style** para Docstrings.
*   **Módulos:** Descripción general al inicio del archivo.
*   **Clases:** Descripción bajo la definición `class`.
*   **Métodos:** Descripción bajo `def`, con secciones `Args:`, `Returns:`, y `Raises:`.

**Ejemplo Python:**
```python
def send_command(self, cmd_bytes: bytes) -> bool:
    """Envía una trama de bytes por el puerto serial.

    Args:
        cmd_bytes (bytes): Trama binaria ya serializada.

    Returns:
        bool: True si se escribió correctamente en el buffer de salida, False si hubo error.
    """
    pass
```

## 2. Reestructuración de Documentación (Architecture)

La carpeta `docs/Architecture` se reorganizará para separar claramente los dominios:

### Estructura Propuesta
```
docs/
├── Architecture/
│   ├── CPP/                  <-- Nuevo directorio
│   │   ├── 00_Overview_Firmware.md
│   │   ├── 01_ProtocolEngine.md
│   │   └── ...
│   ├── Python/               <-- Nuevo directorio
│   │   ├── 00_Overview_Backend.md
│   │   └── ...
│   └── 00_System_Overview.md <-- Visión Alto Nivel (Se mantiene)
├── Design/                   <-- Nuevo directorio
│   └── Protocolo_Demeter.md  <-- Especificación V2 Detallada
└── Knowledge/                <-- Guías y Conceptos (Se mantiene)
```

## 3. Archivos Prioritarios a Documentar

### C++ Firmware
1.  `InternalTypes.h`: Definición de estructuras de datos.
2.  `IComms.h`: Interfaz de comunicación.
3.  `UartStrategy.h/cpp`: Implementación UART.
4.  `ProtocolEngine.h/cpp`: Lógica de parseo.
5.  `SystemContext.h/cpp`: Orquestador.
6.  `main_receptor.cpp`: Punto de entrada.

### Python Backend
1.  `mvp_gui.py`: Aplicación principal MVP.
2.  `protocol_v2.py`: Lógica del protocolo.
3.  `uart.py`: Driver serial.
4.  `ui/main_window.py`: Interfaz gráfica.
