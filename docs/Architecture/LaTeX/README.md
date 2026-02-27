# LaTeX — Documentación Técnica del Proyecto Demeter

Esta carpeta contiene el documento LaTeX de documentación técnica del sistema.

## Estructura

```
LaTeX/
├── main.tex                   ← Documento raíz (compilar desde aquí)
├── sections/
│   ├── 01_introduccion.tex    ← Visión del proyecto y estado actual
│   ├── 02_firmware_architecture.tex  ← Nodos ESP32, capas, orquestador
│   └── 03_protocolo_demeter.tex      ← Protocolo binario, tramas, flujos
└── diagrams/
    ├── 01_serializacion.mmd   ← Algoritmo de serialización
    ├── 02_deserializacion.mmd ← Pipeline de validación y deserialización
    ├── 03_handshake.mmd       ← Handshake SYN/SYN-ACK/ACK con reintentos
    ├── 04_flujo_e2e.mmd       ← Flujo extremo a extremo de telemetría
    ├── 05_manejo_errores.mmd  ← Árbol de decisión ante tramas inválidas
    ├── 06_ciclo_energetico.mmd← Gantt de ciclo energético con Deep Sleep
    └── 07_ciclo_vida_nodos.mmd← Ciclo de vida de los tres tipos de nodo
```

## Compilación

### Requisitos
```bash
sudo apt install texlive-full   # Ubuntu/Debian
# o: brew install mactex        # macOS
```

### Exportar diagramas Mermaid a PDF (paso previo)
Los diagramas `.mmd` se deben convertir a imagen antes de compilar el PDF:

```bash
# Instalar la CLI de Mermaid
npm install -g @mermaid-js/mermaid-cli

# Exportar todos los diagramas a PDF
cd docs/Architecture/LaTeX/diagrams
for f in *.mmd; do mmdc -i "$f" -o "${f%.mmd}.pdf"; done
```

### Compilar el PDF
```bash
cd docs/Architecture/LaTeX
pdflatex main.tex
pdflatex main.tex   # Segunda pasada para TOC y referencias
```

### Makefile (atajo)
Desde la raíz del proyecto, si está disponible:
```bash
make docs-latex
```

## Añadir nuevas secciones

1. Crear el archivo `sections/0X_nombre_seccion.tex`.
2. Descomentar (o añadir) la línea `\input{sections/0X_nombre_seccion}` en `main.tex`.
3. Si la sección incluye diagramas, añadirlos a `diagrams/` y exportarlos a PDF.
