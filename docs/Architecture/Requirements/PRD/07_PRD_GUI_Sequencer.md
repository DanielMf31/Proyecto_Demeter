# PRD: Planificador Temporal (Secuenciador) GUI

## 1. Introducción
El módulo **Sequencer** es una nueva ventana en la aplicación GUI de Python que permite al usuario programar activaciones de pines GPIO con una duración específica. Estas secuencias se envían al ESP32 para su ejecución autónoma.

## 2. Objetivos
*   **Automatización:** Permitir encendidos temporizados sin requerir intervención continua del usuario.
*   **Precisión:** La temporización es manejada por el ESP32, eliminando la latencia de red.
*   **Interfaz Gráfica:** Proporcionar una forma visual de construir la secuencia.

## 3. Requerimientos Funcionales

### 3.1 Ventana Secundaria (`Toplevel`)
*   Debe abrirse desde la ventana principal (`MainWindow`).
*   No debe bloquear la ventana principal (puede ser modal o no, preferible no modal).

### 3.2 Constructor de Secuencia
*   Selector de **Pin** (4, 5, 6, 7).
*   Selector de **Acción** (ON, OFF).
*   Campo de **Duración** (ms).
*   Botón **"Añadir Paso"**.
*   Lista Visual de Pasos añadidos (Treeview o Listbox).

### 3.3 Ejecución
*   Botón **"Enviar Secuencia"**:
    1.  Serializa la lista de pasos en un comando `ExecSequence` (Protocolo V2).
    2.  Envía la trama al ESP32.

## 4. Diseño Técnico

### 4.1 Modelo de Datos (Python)
```python
class SequenceStep(BaseModel):
    pin: int
    value: int
    delay_ms: int
```

### 4.2 Interfaz de Usuario (Tkinter)
*   **Clase:** `SequencerWindow(tk.Toplevel)`
*   **Widgets:**
    *   `ttk.Combobox` para Pin y Acción.
    *   `ttk.Entry` para Duración.
    *   `ttk.Treeview` para mostrar la tabla de pasos.
    *   `ttk.Button` para Añadir/Borrar/Enviar.

## 5. Protocolo (V2)
Se utiliza el comando existente `EXEC_SEQUENCE (0x30)`.
*   El payload contiene el número de pasos seguido de la estructura de cada paso (8 bytes cada uno).
*   El ESP32 parsea y ejecuta (o encola) esta secuencia.
