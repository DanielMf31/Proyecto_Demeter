# Guía Básica de Tkinter: Ventanas y Eventos

Tkinter es la librería estándar de Python para interfaces gráficas. Esta guía cubre los conceptos necesarios para extender el Proyecto Demeter con un "Planificador Temporal".

## 1. Estructura Básica
Una app Tkinter tiene una ventana raíz (`root`) y un bucle de eventos (`mainloop`).

```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Mi App")
root.geometry("400x300")

# Widgets aquí...

root.mainloop()
```

## 2. Widgets y Layouts
Usamos `ttk` (Themed Tkinter) para widgets modernos.

### Botones y Acciones (Command Binding)
Para enlazar un clic a una función, usamos el parámetro `command`.

```python
def mi_accion():
    print("Botón pulsado!")

btn = ttk.Button(root, text="Púlsame", command=mi_accion)
btn.pack(pady=10)
```

**Con Argumentos (Lambda):**
Si la función necesita argumentos (ej. qué pin encender), usamos `lambda`.

```python
def toggle_pin(pin):
    print(f"Toggle Pin {pin}")

# Crea una función anónima que llama a toggle_pin(4)
btn = ttk.Button(root, text="Pin 4", command=lambda: toggle_pin(4))
```

## 3. Ventanas Secundarias (`Toplevel`)
Para crear ventanas adicionales (popups, configuraciones, secuenciadores), usamos `Toplevel`. Son ventanas independientes que viven sobre la `root`.

```python
class SecondaryWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ventana Secundaria")
        self.geometry("300x200")
        
        ttk.Label(self, text="Soy una ventana hija").pack()
        ttk.Button(self, text="Cerrar", command=self.destroy).pack()

# Uso desde la ventana principal:
def abrir_secundaria():
    win = SecondaryWindow(root)
```

## 4. Inputs y Entradas de Datos
Para el secuenciador necesitamos capturar números (tiempo) y opciones (pin).

### Entry (Texto/Números)
```python
entry = ttk.Entry(root)
entry.pack()

# Obtener valor
texto = entry.get()
```

### Combobox (Desplegable)
```python
combo = ttk.Combobox(root, values=["Pin 4", "Pin 5", "Pin 6"])
combo.current(0) # Seleccionar primero por defecto
combo.pack()

# Obtener valor
seleccion = combo.get()
```

## 5. Treeview (Listas/Tablas)
Para mostrar la lista de pasos de la secuencia.

```python
cols = ("Pin", "Acción", "Tiempo")
tree = ttk.Treeview(root, columns=cols, show='headings')

tree.heading("Pin", text="GPIO Pin")
tree.heading("Acción", text="Estado")
tree.heading("Tiempo", text="Duración (ms)")

tree.pack()

# Añadir fila
tree.insert("", "end", values=(4, "ON", 1000))
```
