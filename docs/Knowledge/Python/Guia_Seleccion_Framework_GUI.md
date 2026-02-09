# Selección de Framework GUI de Escritorio para Python

## 1. Objetivo
Analizar las opciones disponibles para desarrollar una aplicación de escritorio nativa para Raspberry Pi (Linux) que reemplace la interfaz de terminal (TUI), priorizando la facilidad de desarrollo, estética y rendimiento.

## 2. Opciones Principales

### 2.1 Tkinter (Con `customtkinter`)
*   **Descripción:** La biblioteca gráfica estándar de Python.
*   **Pros:**
    *   Viene preinstalada.
    *   Curva de aprendizaje muy suave.
    *   **CustomTkinter:** Una librería moderna que añade temas oscuros, esquinas redondeadas y widgets modernos sobre Tkinter, eliminando el aspecto "antiguo" de Windows 95.
*   **Contras:**
    *   Arquitectura "Thread-blocking" (requiere integración cuidadosa con `asyncio`).
*   **Veredicto:** **Recomendado para prototipos rápidos y herramientas funcionales.**

### 2.2 PyQt6 / PySide6 (Qt)
*   **Descripción:** Bindings de Python para el framework Qt (C++). Estándar industrial profesional.
*   **Pros:**
    *   Herramientas de diseño visual (Qt Designer).
    *   Widget set inmenso y muy potente.
    *   Aspecto nativo y muy profesional.
*   **Contras:**
    *   Curva de aprendizaje pronunciada.
    *   Licenciamiento complejo (GPL/LGPL) si se comercializa.
    *   Más pesado en recursos para la Raspberry Pi.
*   **Veredicto:** Recomendado para aplicaciones comerciales complejas.

### 2.3 Aplicación Web Local (Flask/FastAPI + Navegador)
*   **Descripción:** El backend sirve HTML/JS y la Raspberry Pi ejecuta un navegador en modo Kiosk (pantalla completa).
*   **Pros:**
    *   Desacoplamiento total: El backend ya lo tenemos (`async_service.py`).
    *   Estética ilimitada (HTML/CSS).
    *   Permite control remoto desde otros móviles/PC sin cambios.
*   **Contras:**
    *   Requiere conocimientos de tecnologías Web (HTML/CSS/JS).
    *   Consumo de RAM del navegador (Chromium es pesado en RPi).
*   **Veredicto:** **Muy Recomendado** si se busca acceso remoto y estética moderna.

## 3. Recomendación de Implementación

Dado que el objetivo es *"algo funcional, simple y consolidado"*, y ya tenemos una arquitectura separada (Cliente-Servidor), la opción más lógica es:

**Opción A: CustomTkinter (Modern Tkinter)**
Es Python puro, se ve moderno, es fácil de escribir y se conecta fácilmente a nuestro Socket TCP existente.

**Opción B: Interfaz Web**
Si prefieres usar HTML/CSS para el diseño, podemos montar un pequeño servidor Web.

### Ejemplo de Arquitectura con GUI
```mermaid
graph LR
    User[Usuario] --> GUI[GUI Escritorio (CustomTkinter)]
    GUI -- TCP Socket (JSON) --> Service[Backend Async]
    Service -- UART --> ESP32[Hardware]
```
