# PRD: Aprendizaje Práctico de SQL con SQLite

## 1. Objetivo
Entender cómo funcionan las Bases de Datos SQL mediante la práctica directa.
Pasaremos de conceptos abstractos a crear un sistema de registro de sensores funcional.

## 2. Herramientas
- **Motor**: SQLite (Viene con Python, no requiere instalación).
- **Visor Visual**: `DB Browser for SQLite` (Para ver los datos como en Excel).
- **Código**: Python (Para automatizar).

## 3. Hoja de Ruta (Learning Path)

### Nivel 1: El Almacén (Tablas y Columnas)
**Concepto**: Una Base de Datos es un archivo. Dentro hay "Hojas" llamadas Tablas.
- **Actividad**: Crear base de datos `playground.db`.
- **Actividad**: Crear tabla `sensores` con columnas (`id`, `nombre`, `tipo`).
- **Script**: `01_crear_almacen.py`.

### Nivel 2: Llenando el Almacén (INSERT)
**Concepto**: Meter datos en las filas.
- **Actividad**: Insertar un Sensor de Temperatura y uno de Humedad.
- **Concepto Clave**: Tipos de datos (TEXT, REAL, INTEGER).
- **Script**: `02_guardar_datos.py`.

### Nivel 3: El Buscador (SELECT)
**Concepto**: Recuperar datos haciendo preguntas.
- **Actividad**: "¿Dame todos los sensores?", "¿Dame solo los de tipo Temperatura?".
- **Concepto Clave**: `SELECT * FROM ...`, `WHERE ...`.
- **Script**: `03_consultar_datos.py`.

### Nivel 4: El Registrador Automático (Proyecto Final)
**Concepto**: Unir todo en un sistema real.
- **Actividad**: Simular un sensor que manda datos cada segundo y guardarlos.
- **Script**: `04_logger_simulado.py`.

## 4. Estructura de Carpetas
```text
Python/Playground/SQL/
    ├── playground.db      (El archivo mágico)
    ├── 01_crear.py
    ├── 02_guardar.py
    └── ...
```
