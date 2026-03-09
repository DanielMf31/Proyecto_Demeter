# Guía de Diagramas D2 — Proyecto Demeter

> Referencia de estilos, comandos y buenas prácticas para generar
> diagramas con **D2** dentro de la documentación del proyecto.

---

## Diagramas generados

| Diagrama | Fuente D2 | SVG compilado |
|----------|-----------|---------------|
| Serialización de trama | `diagrams/01_serializacion.d2` | `diagrams/01_serializacion.svg` |
| Deserialización y validación | `diagrams/02_deserializacion.d2` | `diagrams/02_deserializacion.svg` |
| Handshake SYN/SYN-ACK/ACK | `diagrams/03_handshake.d2` | `diagrams/03_handshake.svg` |
| Flujo End-to-End | `diagrams/04_flujo_e2e.d2` | `diagrams/04_flujo_e2e.svg` |

---

## Comandos de compilación

```bash
# Compilar un diagrama (flowchart)
d2 --theme=200 --layout=elk --pad=40 <entrada>.d2 <salida>.svg

# Compilar diagrama de secuencia (sin ELK, no lo necesita)
d2 --theme=200 --pad=40 03_handshake.d2 03_handshake.svg

# Watch mode para edición en tiempo real
d2 --watch --theme=200 --layout=elk <entrada>.d2 <salida>.svg

# Ver temas disponibles
d2 themes
```

| Flag | Descripción |
|------|-------------|
| `--theme=200` | Tema dark GitHub-style |
| `--theme=300` | Dracula |
| `--theme=104` | Evergarden Dark |
| `--layout=elk` | Mejor para flowcharts (requiere `d2 layout install elk`) |
| `--layout=dagre` | Alternativa sin instalación extra |
| `--pad=N` | Padding en píxeles (recomendado: 40–60) |

---

## Sistema de clases (patrón del proyecto)

Declara variantes una sola vez y aplícalas con `{class: nombre}`:

```d2
classes: {
  step: {
    shape: rectangle
    style: {
      border-radius: 10
      fill: "#21262d"
      stroke: "#388bfd"
      stroke-width: 2
      font-color: "#e6edf3"
      font-size: 14
      shadow: true
    }
  }
  decision: {
    shape: diamond
    style.fill: "#2d1f3d"
    style.stroke: "#d2a8ff"
    style.font-color: "#d2a8ff"
    style.bold: true
  }
  discard: {
    shape: oval
    style.fill: "#2d0f0f"
    style.stroke: "#f85149"
    style.font-color: "#f85149"
  }
  success: {
    shape: oval
    style.fill: "#0f2d24"
    style.stroke: "#3fb950"
    style.font-color: "#3fb950"
  }
}

mi_nodo: "Procesar datos" {class: step}
mi_decision: "¿Válido?" {class: decision}
error: "DESCARTAR" {class: discard}
ok: "Completado" {class: success}
```

---

## Paleta de colores del proyecto

| Rol | Color | Uso |
|-----|-------|-----|
| Fondo nodo | `#21262d` | Pasos normales |
| Acento azul | `#388bfd` | Bordes principales, ESP32/Sensor |
| Texto claro | `#e6edf3` | Texto general |
| Éxito / verde | `#3fb950` | Ramas OK, Backend |
| Advertencia | `#e3b341` | Espera, Raspberry Pi, reenvío |
| Error | `#f85149` | Descarte, timeout |
| Decisión | `#d2a8ff` | Diamantes, Gateway |
| Inicio | `#1f6feb` | Nodo inicial |

---

## Shapes disponibles

```d2
{shape: rectangle}    # Paso normal
{shape: oval}         # Inicio / fin / estado
{shape: diamond}      # Decisión / bifurcación
{shape: cylinder}     # Base de datos
{shape: cloud}        # Servicio externo
{shape: hexagon}      # Proceso especial
{shape: parallelogram} # Entrada / salida
{shape: queue}        # Cola de mensajes
```

---

## Contenedores (para arquitecturas multi-subsistema)

```d2
SENSOR: "Nodo Sensor · ESP32" {
  style: {
    fill: "#161b22"
    stroke: "#388bfd"
    stroke-width: 3
    border-radius: 16
    font-color: "#58a6ff"
    bold: true
  }

  S1: "Paso A" {class: step}
  S2: "Paso B" {class: step}
  S1 -> S2
}

# Conexión entre contenedores
SENSOR.S2 -> GATEWAY.G1: "Protocolo · Velocidad" {
  style.stroke: "#58a6ff"
  style.stroke-width: 3
  style.bold: true
}
```

---

## Diagramas de secuencia

```d2
shape: sequence_diagram  # Va a nivel raíz, no dentro de un nodo

Participante_A: "Nombre A"
Participante_B: "Nombre B"

Participante_A -> Participante_B: "Mensaje" {
  style.stroke: "#388bfd"
  style.bold: true
}

# Self-message (nota / estado interno)
Participante_A -> Participante_A: "Estado actual" {
  style.stroke-dash: 4
  style.font-color: "#8b949e"
}
```

> [!IMPORTANT]
> Los diagramas de secuencia **no usan** `--layout=elk`. Compilar solo con `--theme=200 --pad=40`.

---

## Conexiones estilizadas

```d2
# Flecha con color y etiqueta
A -> B: "Sí" {
  style.stroke: "#3fb950"
  style.font-color: "#3fb950"
  style.bold: true
}

# Flecha punteada (loops / callbacks)
B -> A: "" {
  style.stroke-dash: 4
  style.stroke: "#e3b341"
}

# Flecha gruesa para bordes entre subsistemas
A -> B: "RF · 2.4 GHz" {
  style.stroke-width: 3
  style.stroke: "#58a6ff"
}
```

---

## Orientación del diagrama

```d2
direction: down   # Arriba → abajo (flowcharts, validaciones)
direction: right  # Izquierda → derecha (pipelines horizontales)
```

> [!TIP]
> Para diagramas e2e con subgraphs, usa `direction: down` con contenedores verticales.
> Evita `direction: right` si el diagrama tiene muchos nodos — se comprime en una línea.
