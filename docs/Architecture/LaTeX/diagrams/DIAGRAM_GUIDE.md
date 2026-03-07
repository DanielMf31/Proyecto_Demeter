# Guia de Diagramas de Arquitectura - Proyecto Demeter

## Estructura de directorios

```
diagrams/
├── raw/                    # Fuentes .d2 (editar aqui)
│   ├── NN_nombre.d2        # Tema oscuro (original, se edita)
│   ├── NN_nombre_dark.d2   # Tema claro (AUTO-GENERADO por make_print.py)
│   └── make_print.py       # Script de transformacion de colores
├── dark/                   # Renders tema oscuro (para pantalla)
│   ├── NN_nombre.svg
│   └── NN_nombre.pdf
├── light/                  # Renders tema claro (para impresion)
│   ├── NN_nombre_light.svg
│   └── NN_nombre_light.pdf
├── NN_nombre_light.pdf     # Copias para LaTeX (main.tex los referencia aqui)
└── DIAGRAM_GUIDE.md        # Esta guia
```

**Convencion de nombres (confusa pero establecida):**
- `NN_nombre.d2` = fuente original, tema OSCURO (fondo negro)
- `NN_nombre_dark.d2` = variante AUTO-GENERADA, tema CLARO (fondo blanco, para impresion)
- El sufijo `_dark` en los `.d2` significa "versión para impresión" (nombre historico invertido)

## Pipeline de generacion completo

### 1. Editar el diagrama fuente

```bash
cd docs/Architecture/LaTeX/diagrams/raw

# Editar con hot-reload (abre navegador con preview en vivo):
d2 --watch NN_nombre.d2 /tmp/preview.svg

# O editar directamente con tu editor de texto
```

### 2. Generar variante light (print)

```bash
cd raw/
python3 make_print.py NN_nombre.d2
# Genera: NN_nombre_dark.d2 (colores claros para impresion)
```

Para regenerar TODOS:
```bash
python3 make_print.py
```

### 3. Renderizar SVG + PDF

```bash
# Tema oscuro (pantalla)
d2 NN_nombre.d2 ../dark/NN_nombre.svg
d2 NN_nombre.d2 ../dark/NN_nombre.pdf

# Tema claro (impresion)
d2 NN_nombre_dark.d2 ../light/NN_nombre_light.svg
d2 NN_nombre_dark.d2 ../light/NN_nombre_light.pdf

# Copiar PDF light a raiz para LaTeX
cp ../light/NN_nombre_light.pdf ../
```

### 4. Recompilar LaTeX (si aplica)

```bash
cd docs/Architecture/LaTeX
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex  # segunda pasada para referencias
```

### Pipeline completo (todos los diagramas)

```bash
cd docs/Architecture/LaTeX/diagrams/raw

# 1. Generar variantes light
python3 make_print.py

# 2. Renderizar todo
for f in $(ls *.d2 | grep -v _dark); do
  name="${f%.d2}"
  d2 "$f" "../dark/${name}.svg"
  d2 "$f" "../dark/${name}.pdf"
done

for f in $(ls *_dark.d2); do
  name="${f%_dark.d2}"
  d2 "$f" "../light/${name}_light.svg"
  d2 "$f" "../light/${name}_light.pdf"
done

# 3. Copiar PDFs light a raiz para LaTeX
cp ../light/*_light.pdf ../

# 4. Recompilar LaTeX
cd ../../ && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
```

## IMPORTANTE: NO usar cairosvg

Los SVGs de d2 usan fuentes embebidas en base64 via `@font-face`. `cairosvg` NO las renderiza correctamente, produciendo PDFs borrosos o con solo lineas negras.

Usar SIEMPRE `d2` nativo para generar PDFs:
```bash
# CORRECTO
d2 archivo.d2 archivo.pdf

# INCORRECTO - produce PDFs rotos
# cairosvg archivo.svg -o archivo.pdf
```

## Como crear un diagrama nuevo

### 1. Elegir numero y nombre

Seguir la numeracion existente:
- `01-07`: Protocolo binario y firmware
- `08-12`: Raspberry Pi (edge)
- `13-16`: Backend
- `17-18`: Diagramas de clases

### 2. Escribir el .d2

Crear `raw/NN_nombre.d2`. Usar las clases de estilo del proyecto:

```d2
direction: down

classes: {
  internal: {
    shape: rectangle
    style: {
      border-radius: 10
      fill: "#21262d"
      stroke: "#388bfd"
      stroke-width: 2
      font-color: "#e6edf3"
      font-size: 13
      shadow: true
    }
  }
  external: {
    shape: rectangle
    style: {
      border-radius: 10
      fill: "#0d1117"
      stroke: "#484f58"
      stroke-width: 2
      font-color: "#8b949e"
      font-size: 13
      shadow: true
    }
  }
  orchestrator: {
    shape: rectangle
    style: {
      border-radius: 10
      fill: "#1f2d1f"
      stroke: "#3fb950"
      stroke-width: 3
      font-color: "#3fb950"
      font-size: 14
      bold: true
      shadow: true
    }
  }
}
```

### 3. Paleta de colores del proyecto

| Uso | Fill (fondo) | Stroke (borde) | Font-color |
|-----|-------------|-----------------|------------|
| Componente interno | `#21262d` | `#388bfd` | `#e6edf3` |
| Actor externo | `#0d1117` | `#484f58` | `#8b949e` |
| Orquestador | `#1f2d1f` | `#3fb950` | `#3fb950` |
| EdgeServer | `#0f1a28` | `#58a6ff` | `#58a6ff` |
| Contenedor/grupo | `#161b22` | `#e3b341` | `#e3b341` |
| Pydantic model | `#2d0f0f` | `#f85149` | `#f85149` |
| Enum | `#2d2a14` | `#e3b341` | `#e3b341` |
| Cola (queue) | `#1a1520` | `#d2a8ff` | `#d2a8ff` |
| Nota | `#2d2a14` | `#e3b341` | `#e3b341` |

### Colores de conexiones

| Flujo | Color | Uso |
|-------|-------|-----|
| UART / hardware | `#388bfd` / `#e3b341` | Tramas binarias |
| Ascendente (telemetria) | `#3fb950` | Datos sensor → backend |
| Descendente (comandos) | `#d2a8ff` | Backend → actuador |
| Error | `#f85149` | Nack, validacion fallida |
| Local (EdgeServer) | `#58a6ff` | UI local → RPi |
| Gris (dependencia debil) | `#484f58` | uses, config |

### 4. Markdown en labels (tablas)

Si el contenido del label usa `|` (tablas markdown), usar triple pipe como delimitador:

```d2
MiNodo: {
  label: |||md
    # Titulo
    | Col1 | Col2 |
    |------|------|
    | a    | b    |
  |||
}
```

### 5. Limitaciones del motor dagre

- NO se puede conectar un contenedor con un hijo directo:
  ```d2
  # INCORRECTO - dagre no lo soporta
  Container -> Container.Child

  # CORRECTO - usar un actor externo
  External -> Container.Child
  ```

### 6. Diagramas de secuencia

Usar `shape: sequence_diagram` al inicio del archivo. No es compatible con `classes:` ni `direction:`.

```d2
shape: sequence_diagram

Actor1: "Nombre" {
  style: { fill: "#21262d"; stroke: "#388bfd"; font-color: "#58a6ff"; bold: true }
}
Actor2: "Nombre" { ... }

Actor1 -> Actor2: "mensaje" {
  style.stroke: "#3fb950"
  style.font-color: "#3fb950"
  style.bold: true
}
```

## Inventario de diagramas

| # | Nombre | Tipo | Capa |
|---|--------|------|------|
| 01 | serializacion | Flujo | Protocolo |
| 02 | deserializacion | Flujo | Protocolo |
| 03 | handshake | Secuencia | Protocolo |
| 04 | flujo_e2e | Secuencia | Protocolo |
| 05 | manejo_errores | Secuencia | Protocolo |
| 06 | ciclo_energetico | Flujo | Firmware |
| 07 | ciclo_vida_nodos | Flujo | Firmware |
| 08 | rpi_componentes | Componentes | RPi |
| 09 | rpi_secuencia_telemetria | Secuencia | RPi |
| 10 | rpi_flujo_comandos | Secuencia | RPi |
| 11 | rpi_docker_deploy | Componentes | RPi |
| 12 | rpi_asyncio_tasks | Flujo | RPi |
| 13 | backend_docker_arch | Componentes | Backend |
| 14 | backend_redis_flow | Secuencia | Backend |
| 15 | backend_db_schema | Componentes | Backend |
| 17 | rpi_class_diagram | Clases UML | RPi + Common |
| 18 | backend_class_diagram | Clases UML | Backend |

## Datos de referencia (pyreverse)

Los diagramas de clases raw generados por `pyreverse` estan en:
```
docs/Architecture/class_diagrams/
├── common/    # classes_Common.dot/.svg
├── rpi/       # classes_RPi_Full.dot/.svg (+ por modulo)
└── backend/   # classes_Backend_Full.dot/.svg (+ por modulo)
```

Estos sirvieron como base para los `.d2` curados (17, 18). Para regenerarlos:
```bash
cd /ruta/al/proyecto
PYTHONPATH=Software/Common:Software/Raspberry/src pyreverse -o dot -p RPi_Full --all-ancestors \
  -d docs/Architecture/class_diagrams/rpi \
  Software/Raspberry/src/proyecto_demeter/Hardware/transport/interface.py \
  Software/Raspberry/src/proyecto_demeter/Hardware/transport/async_uart.py \
  Software/Raspberry/src/proyecto_demeter/Hardware/transport/uart_processor.py \
  Software/Raspberry/src/proyecto_demeter/Hardware/orchestration/command_dispatcher.py \
  Software/Raspberry/src/proyecto_demeter/Hardware/orchestration/edge_server.py \
  Software/Raspberry/src/proyecto_demeter/Hardware/ws_client/client.py \
  Software/Raspberry/src/proyecto_demeter/Hardware/management/device_manager.py

dot -Tsvg classes_RPi_Full.dot -o classes_RPi_Full.svg
```
