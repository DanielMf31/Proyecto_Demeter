# PRD: Visualización en Grafana con SQLite

## 1. 🎯 Objetivo
Crear un sistema de **monitoreo en tiempo real** (simulado) utilizando **Python** para generar datos, **SQLite** para guardarlos y **Grafana** para visualizarlos.

## 2. 🛠️ Arquitectura
1.  **Generador (Python)**: Script que inventa datos de temperatura cada 5 segundos.
2.  **Base de Datos (SQLite)**: Archivo local (`playground.db`) que actúa como puente.
3.  **Visualizador (Grafana)**: Lee el archivo `.db` y dibuja la gráfica.

## 3. 📂 Estructura de Archivos
En `Python/Playground/SQL/`:
*   `generador_datos.py`: El script maestro.
*   `playground.db`: La base de datos (se crea sola).

## 6. 🎨 Catálogo de Visualizaciones Recomendadas (Proyecto Demeter)

Para un invernadero profesional, no basta con líneas. Aquí tienes el "Menú Degustación" de Grafana:

### A. El "Cuenta-Kilómetros" (Gauge) 🏎️
*   **Ideal para**: Temperatura Actual, Humedad, Batería, Nivel de Depósito.
*   **Cómo se ve**: Un arco de colores (Verde -> Amarillo -> Rojo).
*   **Configuración**:
    *   Visualization: **Gauge**.
    *   Thresholds: Pon "80" en rojo para alertar de batería baja o calor extremo.

### B. El "Semáforo" (Stat Panel) 🚦
*   **Ideal para**: ¿Está encendido el Riego?, ¿Hay Error?
*   **Cómo se ve**: Un cuadrado grande que cambia de color (Verde = OK, Rojo = ERROR).
*   **Configuración**:
    *   Visualization: **Stat**.
    *   Value mappings: `1` -> "ON" (Verde), `0` -> "OFF" (Gris).

### C. La "Cronología" (State Timeline) 📅
*   **Ideal para**: Ver *cuándo* se encendió el riego ayer.
*   **Cómo se ve**: Una barra horizontal que cambia de color por tramos.
*   **Configuración**:
    *   Visualization: **State timeline**.

### D. Ideas de Datos a Graficar 💡
| Métrica | Tipo de Gráfica | Query Ejemplo |
| :--- | :--- | :--- |
| **Batería** | Gauge (0-100%) | `SELECT ... WHERE tipo='Bateria'` |
| **Humedad** | Bar Gauge | `SELECT ... WHERE tipo='Humedad'` |
| **Riego** | State Timeline | `SELECT ... WHERE tipo='Riego_Estado'` |
| **Última Conexión** | Stat (Time From Now) | `SELECT max(fecha)...` |

## 4. 💾 Esquema de Base de Datos
Tabla: `mediciones`

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Identificador único (autoincremental) |
| `nombre` | TEXT | Nombre del sensor (ej: "Sensor_Patio") |
| `tipo` | TEXT | Tipo de medida (ej: "Temperatura") |
| `valor` | REAL | El dato numérico (ej: 25.4) |
| `fecha` | DATETIME | **Crucial para Grafana**. Cuándo ocurrió. |

## 5. 🚀 Pasos de Implementación

### Paso A: Script Python
Debe insertar un registro como este cada 5s:
`INSERT INTO mediciones (nombre, tipo, valor, fecha) VALUES ('Sensor_1', 'Temperatura', 23.5, datetime('now', 'localtime'))`

### Paso B: Instalar Plugin en Grafana
Grafana no lee SQLite por defecto. Necesitas este plugin:
1.  Abre terminal.
2.  Ejecuta:
    ```bash
    sudo grafana-cli plugins install frser-sqlite-datasource
    ```
3.  Reinicia Grafana:
    ```bash
    sudo systemctl restart grafana-server
    ```

### Paso C: Configurar Grafana
1.  Ve a **Administration** -> **Data Sources**.
2.  Click **Add new data source**.
3.  Busca **SQLite**.
4.  En **Path**, pon: `/tmp/grafana_demo.db`
    *   Al moverlo a `/tmp`, evitamos todos los problemas de permisos de Linux.
5.  Click **Save & Test**.

### Paso D: Crear Dashboard
1.  **New Dashboard** -> **Add Visualization**.
2.  Selecciona tu fuente SQLite.
3.  **CONFIGURACIÓN DE QUERIES (Monitor Multi-Sensor)** 🖥️

3.  **CONFIGURACIÓN DE QUERIES (Monitor Multi-Sensor)** 🖥️
    *Si te da error de sintaxis, prueba estas opciones en ORDEN hasta que una funcione.*

    ### OPCIÓN 1: La "A Prueba de Fallos" (Sin Filtro de Tiempo) 🆘
    *Esta query ignora el selector de tiempo de Grafana y muestra siempre los últimos 50 datos. Úsala para confirmar que funciona.*
    ```sql
    -- Query A (Patio)
    SELECT CAST(strftime('%s', fecha) as INTEGER) as time, valor 
    FROM mediciones WHERE nombre = 'Sensor_Patio' ORDER BY id DESC LIMIT 50
    ```

    ### OPCIÓN 2: La "Comparador de Texto" (String Comparison) 🔡
    *A veces SQLite prefiere comparar fechas como texto directo.*
    ```sql
    -- Query A (Patio)
    SELECT CAST(strftime('%s', fecha) as INTEGER) as time, valor 
    FROM mediciones 
    WHERE nombre = 'Sensor_Patio' AND fecha > datetime('now', '-5 minutes')
    ORDER BY fecha ASC
    ```

    ### OPCIÓN 3: La "Matemática Estricta" (Macros Grafana) 📐
    *La forma canónica, convirtiendo todo a números.*
    ```sql
    -- Query A (Patio)
    SELECT 
      CAST(strftime('%s', fecha) as INFO) as time, 
      valor
    FROM mediciones 
    WHERE 
      nombre = 'Sensor_Patio' AND 
      CAST(strftime('%s', fecha) as INTEGER) >= ($__from / 1000)
    ORDER BY time ASC
    ```

    **Instrucciones:**
    1.  Elige una Opción (empieza por la 1).
    2.  Pon esa query en la **Caja A**.
    3.  Abre **+ Query** para la **Caja B** y cambia `'Sensor_Patio'` por `'Sensor_Cocina'`.
    4.  Abre **+ Query** para la **Caja C** y cambia `'Sensor_Patio'` por `'Sensor_Salon'`.

### Paso F: Añadir "Relojes" (Gauges) para Batería y Humedad 🏎️

Para ver el valor actual (no el histórico), usamos la visualización **Gauge**.

**1. El Medidor de Batería (Estilo Gasolina)**
1.  Añade un panel nuevo.
2.  En **Visualization** (a la derecha), busca y selecciona **Gauge**.
3.  **SQL Query**:
    ```sql
    SELECT strftime('%s', fecha) as time, valor
    FROM mediciones 
    WHERE nombre = 'Bateria_General' AND time >= $__from/1000
    ORDER BY time ASC
    ```
    *(Nota: Grafana cogerá automáticamente el último valor de la lista).*
4.  **Configuración Visual (Panel derecho)**:
    *   **Unit**: Busca "Percent (0-100)".
    *   **Standard options** (Más abajo en la lista):
        *   **Min**: Escribe `0`.
        *   **Max**: Escribe `100`. *(¡Esto es clave para que el arco se dibuje bien!)*.
    *   **Thresholds** (Los colores):
        *   Rojo: 80 (Si quieres que rojo sea "lleno") ... Espera, para batería es al revés.
        *   **Base**: Rojo (Muerto).
        *   **20**: Amarillo (Reserva).
        *   **50**: Verde (Sano).

**2. El Termómetro de Humedad (Bar Gauge)**
1.  Nuevo Panel -> Visualization: **Bar Gauge** (Barra vertical).
2.  **SQL Query**:
    ```sql
    SELECT strftime('%s', fecha) as time, valor
    FROM mediciones 
    WHERE nombre = 'Humedad_Patio' AND time >= $__from/1000
    ORDER BY time ASC
    ```
3.  **Configuración Visual**:
    *   **Orientation**: Vertical.
    *   **Display Mode**: LCD (queda muy "Cyberpunk").
    *   **Unit**: Humidity (%H).
    *   **Thresholds**: Azul para mojado, amarillo para seco.

---
**Truco Pro**: Si la gráfica sale vacía, asegúrate de que el script `generador_datos.py` está corriendo y generando datos de tipo "Bateria" y "Humedad". (Lo actualizamos en el paso anterior).

### Paso E: Configurar Ejes y Escala (Bonus) 🎛️
Si se ve raro o "demasiado comprimido":
1.  Mira arriba a la derecha en Grafana.
2.  Cambia **"Last 6 hours"** a **"Last 5 minutes"**.
    *   Como insertamos cada 5s, verás los puntos aparecer en tiempo real.
3.  En la derecha, pestaña **Panel options**:
    *   **Refresh dashboard**: Ponlo en `5s`.
    *   Así la gráfica se mueve sola como un monitor cardíaco. 
