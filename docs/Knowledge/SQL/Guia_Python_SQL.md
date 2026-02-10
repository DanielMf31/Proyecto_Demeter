# Guía: Python + SQL (El Dúo Dinámico)

## 1. ¿Cómo se comunican?
Python no "habla" SQL nativamente. Necesita un **Driver** (conductor) y un **Cursor** (puntero).

Imagínalo así:
*   **Base de Datos**: Es un archivo cerrado (`.db`).
*   **Conexión (`conn`)**: El túnel que abre Python hacia el archivo.
*   **Cursor (`cursor`)**: El "robot" que enviamos por el túnel para ejecutar órdenes y traernos los resultados.

## 2. Los 3 Pasos Mágicos
Siempre es el mismo ritual:

```python
import sqlite3

# 1. CONECTAR
conn = sqlite3.connect("mi_base.db")
cursor = conn.cursor()

# 2. EJECUTAR (El "robot" hace el trabajo)
cursor.execute("SELECT * FROM sensores")

# 3. GUARDAR/CERRAR
conn.commit()  # ¡IMPORTANTE! Si insertas/borras datos, si no, se pierden.
conn.close()   # Cierra el túnel.
```

---

## 3. ¿Dónde escribo el SQL? ¿Archivos aparte?

### A. Strings en Python (Lo más común para cosas simples)
Para consultas cortas, se escriben directamente en el código como texto:
```python
sql = "SELECT * FROM usuarios WHERE id = 1"
cursor.execute(sql)
```

### B. Archivos `.sql` (Para crear la estructura o cosas complejas)
Si tienes un script gigante para crear 20 tablas, es mejor tener un archivo `schema.sql` y leerlo desde Python:
```python
with open("schema.sql", "r") as f:
    sql_script = f.read()
cursor.executescript(sql_script)
```

---

## 4. La Regla de Oro: ¡No uses f-strings! ⚠️

**ERROR (Peligroso - Inyección SQL):**
Nunca pegues variables directamente en el texto SQL.
```python
# ❌ MAL: Un hacker podría poner "; DROP TABLE sensores;" en la variable nombre
cursor.execute(f"INSERT INTO sensores VALUES ('{nombre}')")
```

**CORRECTO (Usa "Placeholders" `?`):**
Deja que la librería de Python ponga los datos de forma segura.
```python
# ✅ BIEN: Usar ? como hueco
datos = ("Sensor 1", 25.5)
cursor.execute("INSERT INTO sensores (nombre, valor) VALUES (?, ?)", datos)
```
