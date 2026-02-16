# Arquitectura Frontend - API - Backend: Conceptos Básicos

Este documento explica los fundamentos de la arquitectura moderna de desarrollo web que vamos a implementar en el proyecto, separando la interfaz de usuario (Frontend) de la lógica y datos (Backend).

## 1. Arquitectura Desacoplada

En lugar de tener una sola aplicación que genera el HTML en el servidor (como en tecnologías antiguas), separamos el sistema en dos partes independientes que se comunican a través de una API.

- **Frontend (Cliente)**: Lo que ve el usuario. Se ejecuta en el navegador.
- **Backend (Servidor)**: Donde vive la lógica, la base de datos y la conexión con el hardware (Raspberry Pi).
- **API (Interfaz)**: El puente entre ambos.

### Diagrama de Flujo

```mermaid
graph LR
    User((Usuario)) -->|Interactúa| Frontend[Frontend (HTML/JS)]
    Frontend -->|Petición HTTP (JSON)| API[API (FastAPI)]
    API -->|Consulta| DB[(Base de Datos)]
    API -->|Controla| HW[Hardware/Sensores]
    API -->|Respuesta JSON| Frontend
    Frontend -->|Actualiza UI| User
```

## 2. Conceptos Clave del Frontend

### HTML (HyperText Markup Language)
Es el esqueleto de la página. Define la estructura y el contenido (títulos, párrafos, botones).
- **No es un lenguaje de programación**, es un lenguaje de marcado.

### CSS (Cascading Style Sheets)
Es la piel y la ropa. Define cómo se ve el contenido (colores, fuentes, diseño, espaciado).
- Permite separar el contenido (HTML) de la presentación.

### JavaScript (JS)
Es el cerebro y los músculos. Define el comportamiento y la interactividad.
- ** DOM (Document Object Model)**: Representación en memoria del HTML que JS puede manipular (cambiar texto, ocultar elementos).
- **Fetch API**: Herramienta de JS para hacer peticiones HTTP al backend sin recargar la página.

## 3. Conceptos del Backend y API

### API REST (Representational State Transfer)
Un estilo de arquitectura para diseñar servicios web. Se basa en recursos (ej: `sensores`, `usuarios`) a los que se accede mediante URLs estándar.

### Métodos HTTP
Son los verbos que indican la acción a realizar sobre un recurso:
- **GET**: Obtener datos (ej: `GET /sensors` -> Dame la lista de sensores).
- **POST**: Crear datos nuevos (ej: `POST /sensors` -> Registra un nuevo sensor).
- **PUT**: Actualizar datos existentes.
- **DELETE**: Eliminar datos.

### JSON (JavaScript Object Notation)
El formato estándar para enviar y recibir datos entre el Frontend y el Backend. Es ligero y fácil de leer para humanos y máquinas.

Ejemplo de respuesta JSON:
```json
{
  "sensor_id": 1,
  "tipo": "temperatura",
  "valor": 25.4,
  "unidad": "C"
}
```

### FastAPI
Es el framework de Python que usaremos para construir la API. Es muy rápido, fácil de usar y genera documentación automática.

## 4. Flujo de Desarrollo Local

Como estás desarrollando en tu ordenador (Localhost) pero el sistema final correrá en una Raspberry Pi, simulamos el entorno.

### Herramientas Recomendadas

1.  **VS Code Live Server**: Una extensión que crea un pequeño servidor web local para tu Frontend. Recarga la página automáticamente cuando guardas cambios en HTML/CSS/JS.
2.  **Uvicorn**: El servidor web para ejecutar FastAPI.
    - Comando típico: `uvicorn main:app --reload` (el flag `--reload` reinicia el servidor al cambiar código Python).

### ¿Cómo simular la Raspberry Pi?

En tu código de Backend (Python), puedes crear una "capa de abstracción" para el hardware.
- Si detecta que está en la RPi -> Lee los sensores reales.
- Si detecta que está en tu PC -> Genera números aleatorios o devuelve datos fijos.

Esto te permite trabajar en la interfaz y la lógica de la API sin tener el hardware físico conectado todo el tiempo.
