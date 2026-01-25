# Especificación Técnica: Datos, Almacenamiento y API

## 📋 Índice
1. [Capa de Almacenamiento](#capa-de-almacenamiento)
2. [Estructura de Carpetas de Datos](#estructura-de-carpetas-de-datos)
3. [API REST y Dashboard](#api-rest-y-dashboard)

---

## 💾 Capa de Almacenamiento
Gestiona la persistencia de datos. Inicialmente basada en sistema de archivos (Local Storage), extensible a Base de Datos.

*   **Ubicación**: `src/storage/`
*   **Interfaz**: `LocalStorage` maneja lecturas y escrituras seguras a disco.

### Estructura de Carpetas de Datos
El directorio `data/` se organiza para facilitar la trazabilidad:

*   `input/`: Landing zone de tickets nuevos.
*   `processed/`: Tickets procesados con éxito (se mueven aquí desde input).
*   `output/`: JSONs intermedios y resultados crudos.
*   `exports/`: Archivos finales para el usuario (Excel, CSV).

---

## 🌐 API REST y Dashboard

### API (FastAPI)
Interfaz programática para integraciones.
*   **Endpoint**: `POST /process`
    *   Body: Imagen o URL.
    *   Response: JSON con datos extraídos + estado.
*   **Endpoint**: `GET /status/{ticket_id}`
    *   Estado del procesamiento asíncrono.

### Dashboard (Streamlit)
Interfaz visual para usuarios finales y debugging.
*   **Funciones**:
    *   Subida manual de tickets (Drag & Drop).
    *   Visualización lado-a-lado (Imagen vs Datos Extraídos).
    *   Edición manual de correcciones.
    *   Descarga de Excels.
