# Pruebas y Validación: Python Data Layer

Este documento detalla la estrategia de pruebas implementada para verificar la capa de persistencia (SQLite) y logging del backend Python.

## 1. Estrategia de Pruebas

Se han creado pruebas de integración que ejecutan el `DemeterService` en un entorno controlado, utilizando una base de datos SQLite temporal y archivos de log de prueba.

### Entorno de Pruebas
*   **Framework:** `pytest` con plugins `pytest-asyncio` y `pytest-mock`.
*   **Ubicación:** `Python/tests/test_data_integration.py`.
*   **Ejecución:**
    ```bash
    cd Python
    # Crear entorno virtual (recomendado)
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    
    # Ejecutar tests
    pytest tests/test_data_integration.py
    ```

## 2. Escenarios Cubiertos

### 2.1 DatabaseManager (Unitario)
*   **Objetivo:** Verificar operaciones CRUD asíncronas.
*   **Validación:**
    *   Inicialización correcta del esquema (`sensor_readings`).
    *   Inserción de lecturas con timestamp ISO8601 explícito (evita warnings de deprecación en Python 3.12).
    *   Recuperación de estadísticas (Promedio, Min, Max).
    *   Ordenamiento descendente por timestamp.

### 2.2 SensorLogger (Unitario)
*   **Objetivo:** Verificar escritura en archivo plano CSV.
*   **Validación:**
    *   Formato correcto: `TIMESTAMP,NODE_ID,TEMP,HUM`.
    *   Creación automática de directorios.

### 2.3 DemeterService (Integración)
*   **Objetivo:** Verificar el flujo completo desde la "recepción" (simulada) de un comando hasta la persistencia.
*   **Flujo:**
    1.  Se instancia `DemeterService` con DB y Logger de prueba.
    2.  Se simula la llegada de un objeto `MockDataReport` (imitando un comando parseado del protocolo).
    3.  Se invoca `handle_protocol_command`.
    4.  **Aserción:** Se consulta la DB para verificar que el registro existe con los valores correctos (`node_id=99`, `temp=12.3`).

## 3. Resultados

Las pruebas pasan exitosamente (`PASSED`), confirmando que:
1.  El servicio no bloquea el loop al escribir en disco (gracias a `aiosqlite` y logging optimizado).
2.  Los datos se guardan correctamente para su posterior visualización en Grafana.
