# 📓 Bitácora de Desarrollo (Master Log)

Este documento centraliza los avances significativos, decisiones técnicas y bloqueos del proyecto.

---

## 📅 Febrero 2026 - Fase de Prototipado y MVP

### 10/02/2026 - Reestructuración de Documentación
*   **Cambio:** Se migró toda la documentación de `Design` a `Architecture`.
*   **Hardware:** Se separó el "Inventario" en documentos específicos para RPi, Gateway y Nodo.
*   **Plan:** Definición del Product Backlog y Sprint Backlog para organizar el trabajo con la ETSIA.

### 09/02/2026 - Planificación ETSIA
*   **Objetivo:** Preparar el despliegue en el Invernadero.
*   **Cronograma:** 2 semanas para validar el prototipo en "seco" (Laboratorio) antes de ir a campo.
*   **Funcionalidades Clave:**
    *   Persistencia de datos (SQLite) funcionando.
    *   Lectura vía ESP-Now operativa.
    *   GUI Táctil básica lista.

### 08/02/2026 - MVP Control GPIO
*   **Hito:** Se logró controlar pines (LEDs) desde la GUI Python atravesando todo el stack (Python -> UART -> Gateway -> ESP-Now -> Nodo).
*   **Decisión Técnica:** Se optó por una GUI "hardcoded" para este MVP para validar la latencia y fiabilidad del protocolo V2.
*   **Infraestructura:** Se crearon los scripts de despliegue para la Raspberry Pi (`scripts/deploy.sh` idealmente).

---

## 📅 Enero 2026 - Cimientos

### Definición de Arquitectura
*   Se estableció la arquitectura híbrida C++/Python.
*   Creación del Protocolo Demeter V2 (Binario).
*   Configuración del entorno PlatformIO con Tests Nativos.

---

> *Nota: Para detalles diarios muy específicos, consultar los archivos históricos en `archive/` si existen.*
