# Propuesta: Demeter como Plataforma de Investigación Agronómica

## 1. Visión
Convertir el sistema Demeter en una herramienta profesional "llave en mano" para investigadores agronómicos. El objetivo es que el usuario se centre en el experimento (biología) y no en la tecnología (sensores/código).

## 2. Flujo de Trabajo del Investigador (User Journey)

### Fase 1: Configuración del Experimento ("Project Setup")
El usuario accede a una interfaz web local (en la Raspberry Pi) o en la nube.
1.  **Crear Nuevo Proyecto**: Asigna un nombre (e.g., "Estrés Hídrico Tomate 2026").
2.  **Definir Parámetros Biológicos**:
    *   Tipo de Cultivo.
    *   Variables a monitorear (T, HR, Radiación, Suelo).
    *   Número de Replicas (Plantas/Macetas).
3.  **Configuración de Hardware**:
    *   El sistema detecta automáticamente los nodos sensores conectados.
    *   El usuario asigna cada nodo a una réplica/tratamiento (e.g., Nodo A -> Tratamiento Control, Nodo B -> Tratamiento Sequía).

### Fase 2: Ejecución ("Run Experiment")
El sistema opera de forma autónoma (Headless).
*   **Data Logging Robusto**: Almacenamiento en base de datos SQL local (resistente a apagones).
*   **Cálculo en Tiempo Real**: Ejecución automática de scripts como `calculos_agronomicos.py` para generar métricas derivadas (VPD, GDD) al instante.
*   **Alertas**: Envío de correos/Telegram si un parámetro crítico se desvía (e.g., riego fallido).

### Fase 3: Análisis y Extracción ("Actionable Insights")
El investigador no necesita saber programar.
*   **Dashboard en Vivo**: Ver gráficas de tendencias en tiempo real desde cualquier tablet/PC en la misma red.
*   **Botón "Exportar Datos"**:
    *   Genera un `.zip` con:
        *   `Raw_Data.csv` (Datos crudos).
        *   `Processed_Data.xlsx` (Cálculos agronómicos completos).
        *   `Reporte_Diario.pdf` (Resumen automático).
        *   Carpeta `Graficas/` con imágenes listas para publicación (papers).

## 3. Arquitectura Técnica Propuesta

### Nivel 1: Edge Computing (Raspberry Pi)
*   **Core**: Python + SQLite/PostgreSQL.
*   **Worker**: Script de `calculos_agronomicos.py` ejecutándose como servicio systemd.
*   **Interfaz**: Web App ligera (Streamlit, FastHTML o CustomTkinter en modo kiosco).

### Nivel 2: Estandarización de Datos
Para ser profesional, los datos deben ser FAIR (Findable, Accessible, Interoperable, Reusable).
*   **Metadatos**: Cada archivo exportado incluye un encabezado JSON con la config del sensor, fecha de calibración y versión del firmware.
*   **Unidades**: Uso estricto del SI (Sistema Internacional).

## 4. Pasos para la Profesionalización
1.  **Empaquetado**: Crear una imagen ISO de Raspberry Pi pre-configurada ("Demeter OS").
2.  **Calibración**: Incluir un módulo de software para calibrar sensores con estándares de referencia.
3.  **Seguridad**: Encriptación de datos y backups automáticos a USB.
4.  **Documentación**: Manual de usuario PDF y Guía de Instalación Rápida.

## 5. Valor Diferencial
A diferencia de un data logger genérico, Demeter **entiende de agronomía**. No solo te da "22°C", te dice "0.8 kPa VPD - Zona Óptima". Eso es lo que ahorra tiempo al investigador.
