# 📚 Estrategia de Documentación Proyecto Demeter

Este documento define la estructura y los estándares de documentación para el proyecto, asegurando que cualquier desarrollador pueda entender qué es, cómo funciona y cómo modificar el sistema.

## 1. Niveles de Documentación

En proyectos de ingeniería IoT complejos como este, dividimos la documentación en 4 cuadrantes:

### A. **Arquitectura y Diseño** (`docs/Architecture`, `docs/Design`)
*   **Qué es:** La visión de alto nivel. Diagramas de bloques, decisiones tomadas, protocolos y estructuras de datos.
*   **Para quién:** Arquitectos, nuevos desarrolladores que necesitan entender "el todo".
*   **Ejemplos:**
    *   `00_System_Inventory.md`: Catálogo de hardware (Lo que vamos a crear).
    *   `02_Protocol_Demeter_V2.md`: Cómo hablan los dispositivos.
    *   `Python/04_Configuration.md`: Cómo se configura el backend.

### B. **Manuales y Guías (DevOps)** (`docs/Manuals`, `docs/DevOps`)
*   **Qué es:** Instrucciones paso a paso "Recetas de Cocina". Cómo instalar, desplegar o arreglar algo.
*   **Para quién:** Operadores, SysAdmins, o tú mismo dentro de 6 meses.
*   **Ejemplos:**
    *   `Deployment_Guide.md`: Cómo ponerlo en marcha en la Raspi.
    *   `02_Grafana_Access_Guide.md`: Cómo arreglar permisos.

### C. **Referencia de Código (API)** (En el código / Doxygen / Docstrings)
*   **Qué es:** Explicación detallada de funciones, clases y métodos.
*   **Para quién:** El desarrollador que está escribiendo código *ahora mismo*.
*   **Formato:** Docstrings en Python (`"""..."""`) y Javadoc/Doxygen en C++ (`/** ... */`).

### D. **Bitácora de Desarrollo** (`docs/Desarrollo`)
*   **Qué es:** Diario de a bordo. Qué hice hoy, qué falló, ideas sueltas.
*   **Para quién:** Para el yo del futuro, para recordar por qué hice algo "raro".

---

## 2. Estándar para "Device Catalog" (Inventario)

Para cumplir con tu solicitud sobre los dispositivos (Nodo, Gateway, Raspi), crearemos un documento vivo que actúe como "Hoja de Datos" del sistema. Debe contener:

1.  **Rol:** ¿Qué hace este aparato?
2.  **Hardware:** Modelo exacto, pines usados, conexiones físicas.
3.  **Firmware/Software:** Qué código corre, versiones, servicios.
4.  **Capacidades:** Qué PUEDE hacer (sensores, actuadores, protocolos).
5.  **Interacción:** Cómo lo controlo (Terminal, GUI, Botones físicos).

A continuación, procederé a crear este documento específico (`docs/Architecture/Hardware/00_System_Inventory.md`) basado en el análisis del código actual.
