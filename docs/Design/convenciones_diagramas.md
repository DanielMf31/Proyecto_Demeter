# Convenciones de Diagramas Técnicos — Proyecto Demeter

> Este documento responde a la pregunta: **¿fondos oscuros o claros en documentación oficial?**
> Y define las convenciones que sigue este proyecto.

---

## El debate oscuro vs. claro en documentación técnica

### Lo que hacen los estándares oficiales

La tradición de la documentación técnica académica e industrial (IEEE, ISO, RFC, memorias de TFG/TFM) usa **fondo blanco** por razones muy concretas:

| Criterio | Fondo blanco | Fondo oscuro |
|----------|-------------|--------------|
| **Impresión** | ✅ Sin gasto de tinta, máximo contraste | ❌ Consume mucha tinta, grises al imprimir |
| **Accesibilidad** | ✅ Cumple WCAG AA por defecto | ⚠️ Depende del contraste elegido |
| **Compatibilidad PDF** | ✅ Universal | ⚠️ Puede perder colores en lectores básicos |
| **Estándares IEEE/ACM** | ✅ Requerido | ❌ No aceptado en papers |
| **Documentación web** | ✅ / ⚠️ | ✅ Si hay modo oscuro nativo |
| **Presentaciones** | ⚠️ Depende del fondo de slide | ✅ Más impacto visual en pantalla |

### ¿Cuándo se usa fondo oscuro en documentación profesional?

Los fondos oscuros son estándar en contextos técnicos modernos como:

- **Documentación de infraestructura** (Grafana dashboards, Datadog, arquitecturas de red como la imagen de referencia)
- **READMEs de GitHub y documentación web** (Docusaurus dark mode, MkDocs Material)
- **Documentación interna de empresa** (Notion, Confluence con dark mode)
- **Presentaciones técnicas** (slides en conferencias de ingeniería)
- **Sistemas IoT y embebidos** (documentación de producto/proyecto, no papers)

👉 **Conclusión**: Para una **memoria académica impresa** → fondo blanco obligatorio. Para **documentación técnica digital del proyecto** (como este) → fondo oscuro es perfectamente válido y más legible en pantalla.

---

## Principios que deben cumplirse siempre

Independientemente del tema elegido, todo diagrama técnico debe cumplir:

### 1. Contraste suficiente (WCAG AA mínimo)
El texto sobre cualquier fondo debe tener relación de contraste ≥ 4.5:1.

```
✅ #e6edf3 sobre #21262d  → ratio ~9:1
✅ #3fb950 sobre #0f2d24  → ratio ~5.2:1
❌ #8b949e sobre #21262d  → ratio ~3.1:1  (solo para texto secundario)
```

### 2. Semántica de color consistente
Los colores deben tener **significado fijo** en todos los diagramas:

| Color | Hex | Significado |
|-------|-----|-------------|
| 🔵 Azul | `#388bfd` | Flujo principal, ESP32 Sensor, datos |
| 🟢 Verde | `#3fb950` | Éxito, completado, Backend |
| 🟡 Amarillo | `#e3b341` | Advertencia, espera, Raspberry Pi |
| 🔴 Rojo | `#f85149` | Error, descarte, timeout |
| 🟣 Morado | `#d2a8ff` | Decisión, Gateway, bifurcación |
| ⚫ Gris | `#6e7681` | Ignorar, inactivo, secundario |

### 3. Jerarquía visual clara
- **Nodos de inicio/fin**: ovales (`shape: oval`), borde + relleno de color
- **Pasos normales**: rectángulos redondeados (`border-radius: 10`)
- **Decisiones**: diamantes (`shape: diamond`), borde morado
- **Contenedores**: borde grueso (3px), esquinas redondeadas grandes (14–16px)

### 4. Tipografía legible
- Tamaño mínimo en nodos: **13px**
- Tamaño en títulos de contenedores: **15–16px, bold**
- No más de 4–5 líneas de texto por nodo

### 5. Dirección coherente con el tipo de diagrama

| Tipo | `direction` | Razón |
|------|-------------|-------|
| Flowchart de validación | `down` | Se lee de arriba abajo |
| Pipeline / E2E multi-subsistema | `down` con contenedores | Evita compresión horizontal |
| Arquitectura de componentes | `down` | Capas bien diferenciadas |
| Sequence diagram | N/A (automático) | No se especifica |

> [!CAUTION]
> **Evita `direction: right`** en diagramas con más de 6 nodos o subgraphs.
> D2 (y Mermaid) tienden a comprimir todo en una sola línea horizontal ilegible.

### 6. Etiquetas en conexiones cuando el canal importa
Si una flecha representa un protocolo, velocidad o interfaz física, **ponla en la etiqueta**:
```d2
ESP32 -> RPi: "UART · 115200 bps"
RPi -> Backend: "wss:// · JSON"
```

### 7. Un solo tema visual en todo el proyecto
Todos los diagramas del proyecto usan el mismo conjunto de clases y paleta. Si cambias un color en un sitio, actualiza la guía `d2_diagramas.md`.

---

## Convención para este proyecto

Este proyecto usa **tema oscuro** (`--theme=200`) en todos los diagramas porque:

1. La documentación es **digital-first** (web, PDF en pantalla, GitHub)
2. El contexto es **IoT / sistemas embebidos** — dark mode es estándar en el sector
3. Los diagramas son **más legibles en pantalla** con fondo oscuro y colores vibrantes
4. Si en el futuro se necesita versión para impresión, se puede recompilar con `--theme=0` (claro)

---

## Adaptar diagramas para una memoria académica impresa

Las memorias académicas (TFG/TFM, papers IEEE/ACM) tienen requisitos muy específicos:

### Problema: el fondo oscuro en impresión
- Los fondos oscuros consumen mucha tinta y a menudo se convierten en grises apagados
- El contraste texto/fondo se invierte o se pierde en impresoras en blanco y negro
- Las normas IEEE/ACM exigen figuras sobre fondo blanco

### Solución: dos versiones desde un mismo `.d2`

```bash
# ── Versión digital (dark, para la web/README) ─────────────────
d2 --theme=200 --layout=elk --pad=40 01_serializacion.d2 01_serializacion.svg

# ── Versión impresión (clara, para LaTeX/memoria) ─────────────
d2 --theme=0  --layout=elk --pad=40 01_serializacion.d2 01_serializacion_print.svg
# ó tema "Neutral" más limpio:
d2 --theme=1  --layout=elk --pad=40 01_serializacion.d2 01_serializacion_print.svg
```

> [!TIP]
> El tema `0` (Neutral) es el más limpio para imprimir: fondo blanco, texto negro,
> colores suaves. El tema `1` tiene algo más de personalidad pero sigue siendo claro.

### Insertar SVG en LaTeX

```latex
\usepackage{svg}          % paquete requerido
\usepackage{graphicx}     % alternativa si se convierte a PDF primero

% Opción A – SVG directamente (requiere Inkscape instalado)
\begin{figure}[H]
  \centering
  \includesvg[width=0.9\linewidth]{diagrams/01_serializacion_print}
  \caption{Flujo de serialización del protocolo binario Demeter.}
  \label{fig:serializacion}
\end{figure}

% Opción B – Convertir a PDF con Inkscape primero (más robusta)
% inkscape 01_serializacion_print.svg --export-pdf=01_serializacion_print.pdf
\begin{figure}[H]
  \centering
  \includegraphics[width=0.9\linewidth]{diagrams/01_serializacion_print}
  \caption{Flujo de serialización del protocolo binario Demeter.}
  \label{fig:serializacion}
\end{figure}
```

### Script para compilar versión académica de todos los diagramas

```bash
#!/bin/bash
# compile_print.sh — Genera versiones claras para la memoria
DIAGRAMS_DIR="docs/Architecture/LaTeX/diagrams"
THEME=0  # ó 1 para Neutral

for f in "$DIAGRAMS_DIR"/*.d2; do
  name="${f%.d2}"
  echo "Compilando: $f"
  # Flowcharts (con ELK)
  d2 --theme=$THEME --layout=elk --pad=40 "$f" "${name}_print.svg"
done

# Sequence diagrams (sin ELK — compilar manualmente)
# d2 --theme=$THEME --pad=40 03_handshake.d2 03_handshake_print.svg
echo "✓ Listo. SVGs claros en $DIAGRAMS_DIR"
```

### Convertir todos los SVG a PDF (para LaTeX con pdflatex)

```bash
# Requiere Inkscape instalado
for svg in docs/Architecture/LaTeX/diagrams/*_print.svg; do
  inkscape "$svg" --export-pdf="${svg%.svg}.pdf"
done
```

### Principios adicionales para memoria académica

| Criterio | Recomendación |
|----------|---------------|
| Tamaño de fuente | Mínimo 12pt en el diagrama (ajustar con `font-size: 16` en D2) |
| Ancho en el documento | `\linewidth` o `0.9\linewidth` para diagramas anchos |
| Leyenda obligatoria | Siempre añadir `\caption{}` y `\label{}` |
| Fuente de referencia | Indicar "Elaboración propia" si no hay fuente externa |
| Numeración | LaTeX numera automáticamente las figuras con `\ref{fig:nombre}` |

---

## Referencia rápida: comandos del proyecto

```bash
# Compilar (flowchart) — versión dark
d2 --theme=200 --layout=elk --pad=40 <archivo>.d2 <archivo>.svg

# Compilar (flowchart) — versión académica/impresión
d2 --theme=0 --layout=elk --pad=40 <archivo>.d2 <archivo>_print.svg

# Compilar (sequence diagram — sin elk)
d2 --theme=200 --pad=40 <archivo>.d2 <archivo>.svg
d2 --theme=0   --pad=40 <archivo>.d2 <archivo>_print.svg

# Watch mode (edición en tiempo real)
d2 --watch --theme=200 --layout=elk <archivo>.d2 <archivo>.svg

# Ver todos los temas disponibles
d2 themes
```
