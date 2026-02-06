# Arquitectura del Sistema

Este documento describe la arquitectura técnica del proyecto, diseñada para ser modular, escalable e híbrida (Python + C++).

## 1. Visión General: Arquitectura Híbrida

El proyecto adopta una estructura de **Monorepo Ligero** que permite la coexistencia pacífica de componentes de alto rendimiento (C++) y lógica de orquestación/IA (Python).

```text
Raíz del Proyecto/
├── cpp/                    # [Mundo C++]: Rendimiento Crítico
│   ├── CMakeLists.txt      # Sistema de construcción
│   ├── src/                # Implementación
│   └── include/            # Headers públicos
│
├── python/                 # [Mundo Python]: Orquestación e IA
│   ├── config/             # Configuración Centralizada (Pydantic)
│   ├── src/                # Código fuente Python
│   ├── tests/              # Tests automatizados
│   └── pyproject.toml      # Gestión de dependencias
│
└── docs/                   # Documentación Global
```

Esta separación permite ciclos de vida independientes: se pueden compilar los binarios de C++ sin afectar el entorno virtual de Python, y viceversa.

## 2. Filosofía de Configuración: "Code First"

Abandonamos los archivos JSON estáticos monolíticos en favor de **Configuración como Código** usando Pydantic.

*   **Única Fuente de Verdad**: La clase `Settings` en `python/config/settings.py`.
*   **Tipado Fuerte**: Errores al arrancar si un puerto es un string en vez de un int.
*   **Zero-Config Inicial**: El proyecto arranca "out-of-the-box" con defaults sensatos definidos en código.

### Módulos de Configuración
La configuración se compone de bloques modulares:

*   **`DeviceConfig`**: Gestión de Hardware (Puertos serie, baudrates).
*   **`LLMConfig`**: Control de IA (Modelos, temperatura, tokens).
*   **`OCRConfig`**: Visión artificial (Motor, idioma, DPI).
*   **`ValidationConfig`**: Reglas de negocio y calidad de datos.
*   **`PathsConfig`**: Mapa dinámico del sistema de archivos.

## 3. Gestión de Datos (Data Lake Local)

El proyecto estructura automáticamente el flujo de datos en carpetas estandarizadas, gestionadas por `PathsConfig`:

*   `data/input`: Punto de entrada de archivos crudos.
*   `data/processed`: Almacenamiento intermedio.
*   `data/output`: Resultados finales para el usuario.
*   `data/logs`: Logs del sistema rotativos.
*   `data/exports`: Reportes generados.

El sistema de archivos (`FileSystemManager`) asegura que estas carpetas existan al iniciar la aplicación, eliminado errores de "Directorio no encontrado".

## 4. Componentes Principales (Python)

El código Python sigue el patrón "Src Layout":

*   **`core`**: Utilidades base agnósticas del dominio (Manejo de archivos, Logs, Wrappers).
*   **`protocols`**: Definiciones de interfaces y contratos de comunicación.
*   **`services`**: Lógica de negocio específica de la aplicación.
