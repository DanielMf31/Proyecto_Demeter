# Guía Básica de SQL: El Lenguaje de los Datos

**SQL** (Structured Query Language) es el idioma universal para hablar con las Bases de Datos. No importa si usas SQLite, MySQL, PostgreSQL o Oracle; el 90% del idioma es idéntico.

---

## 1. Conceptos Fundamentales

Imagina una Base de Datos como un **Archivador físico**.
*   **Base de Datos (Database)**: El archivador completo (`playground.db`).
*   **Tabla (Table)**: Una carpeta dentro del archivador (ej: `sensores`). Es como una hoja de Excel.
*   **Columna (Column)**: Los títulos de la hoja (ej: `nombre`, `temperatura`). Define QUÉ tipo de dato guardas.
*   **Fila (Row)**: Cada registro o línea de datos individual (ej: "Sensor Cocina, 25ºC").

---

## 2. Tipos de Datos (Los Ingredientes)

En SQLite (y SQL en general), debes decir qué tipo de dato va en cada columna:
*   **INTEGER**: Números enteros (1, 2, 45, -10). Usado para IDs o contadores.
*   **REAL / FLOAT**: Números con decimales (23.5, 3.1416). Usado para sensores.
*   **TEXT**: Texto o cadenas ("Hola", "Sensor 1").
*   **NULL**: La ausencia de dato (vacío).

---

## 3. Los 4 Comandos Sagrados (CRUD)

Todo lo que haces con datos se resume en estas 4 operaciones:

### A. CREATE (Crear la Estructura)
Antes de guardar nada, debes diseñar la tabla.
```sql
CREATE TABLE sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Un número único que se pone solo
    nombre TEXT NOT NULL,                  -- Texto obligatorio
    tipo TEXT,                             -- Texto opcional
    valor REAL                             -- Número decimal
);
```

### B. INSERT (Guardar Datos)
Meter nueva información en la tabla.
```sql
-- Insertar una fila completa
INSERT INTO sensores (nombre, tipo, valor) 
VALUES ('Sensor Cocina', 'Temperatura', 24.5);

-- Insertar otra fila
INSERT INTO sensores (nombre, tipo, valor) 
VALUES ('Sensor Baño', 'Humedad', 60.2);
```

### C. SELECT (Leer/Consultar Datos)
La operación más usada. Es "hacer preguntas" a la base de datos.
```sql
-- 1. Dame TODO lo que hay en la tabla
SELECT * FROM sensores;

-- 2. Dame SOLO el nombre y el valor (ignora el resto)
SELECT nombre, valor FROM sensores;

-- 3. FILTRAR: Dame solo los que sean 'Temperatura' (WHERE)
SELECT * FROM sensores WHERE tipo = 'Temperatura';

-- 4. FILTRAR AVANZADO: Temperaturas mayores a 20 grados
SELECT * FROM sensores WHERE tipo = 'Temperatura' AND valor > 20;

-- 5. ORDENAR: Dame los sensores ordenados por valor (el más alto primero)
SELECT * FROM sensores ORDER BY valor DESC;

-- 6. LIMITAR: Dame solo los 5 primeros
SELECT * FROM sensores LIMIT 5;
```

### D. UPDATE (Modificar Datos)
Cambiar algo que ya existe. **¡Cuidado con el WHERE o cambiarás todo!**
```sql
-- Cambiar el valor del sensor con ID 1 a 25.0
UPDATE sensores SET valor = 25.0 WHERE id = 1;
```

### E. DELETE (Borrar Datos)
Eliminar filas. **¡Peligroso!**
```sql
-- Borrar el sensor con ID 2
DELETE FROM sensores WHERE id = 2;

-- ¡PELIGRO! Esto borra TODA la tabla
DELETE FROM sensores;
```

---

## 4. Resumen

| Comando | Acción | Ejemplo |
| :--- | :--- | :--- |
| **CREATE** | Fabrica la tabla | `CREATE TABLE ...` |
| **INSERT** | Añade una fila nueva | `INSERT INTO ... VALUES ...` |
| **SELECT** | Lee y busca datos | `SELECT * FROM ... WHERE ...` |
| **UPDATE** | Modifica filas existentes | `UPDATE ... SET ... WHERE ...` |
| **DELETE** | Borra filas | `DELETE FROM ... WHERE ...` |
