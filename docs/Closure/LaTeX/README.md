# Informe de Viabilidad y Cierre — Proyecto Demeter

Documento LaTeX hermano de `docs/Architecture/LaTeX/`. Misma identidad visual,
mismo preámbulo, mismas convenciones de cuadros y listings.

## Estructura

```
docs/Closure/LaTeX/
├── main.tex                              ← preámbulo + portada + inputs
├── README.md                             ← este archivo
├── diagrams/
│   └── logo_esibot.png                   ← symlink a Architecture/LaTeX/diagrams/
└── sections/
    ├── 00_resumen_ejecutivo.tex
    ├── 01_introduccion_contexto.tex
    ├── 02_logros_proyecto.tex
    ├── 03_estado_actual.tex
    ├── 04_analisis_sostenibilidad.tex   ⭐ sección clave (tablas)
    ├── 05_razones_no_sostenibilidad.tex
    ├── 06_lecciones_aprendidas.tex
    ├── 07_propuesta_cierre.tex
    ├── 08_recomendaciones_futuras.tex
    ├── A_anexo_financiero.tex
    └── B_anexo_plan_entrega.tex
```

## Compilación

Desde `docs/Closure/LaTeX/`:

```bash
pdflatex main.tex
pdflatex main.tex     # 2ª pasada para resolver TOC y referencias
```

Resultado: `main.pdf` con ~12 páginas + 2 anexos.

Si `pdflatex` falla por símbolo `\euro` no definido en algún sistema, instalar
paquete `marvosym` o `eurosym` y añadir al preámbulo de `main.tex`:

```latex
\usepackage{eurosym}
\renewcommand{\euro}{\text{\eurosym}}
```

## Cómo rellenar los placeholders

Todos los datos pendientes están marcados con el comando `\todo{...}` que
renderiza el contenido **en rojo y bold** en el PDF compilado, lo que los hace
fáciles de localizar visualmente.

### Búsqueda global de placeholders

```bash
# Listar todos los placeholders pendientes:
grep -rn '\\todo{' sections/ main.tex

# Contar cuántos quedan:
grep -rn '\\todo{' sections/ main.tex | wc -l
```

### Convenciones de placeholders

| Patrón                  | Significado                                    |
|-------------------------|------------------------------------------------|
| `\todo{N}`              | Número entero (cantidad)                       |
| `\todo{X}`              | Número genérico (sustituir por valor real)     |
| `\todo{X €}`            | Cantidad económica                             |
| `\todo{MM/AAAA}`        | Mes/Año                                        |
| `\todo{descripción...}` | Texto a redactar / decisión a tomar            |

### Datos a recopilar antes de rellenar

Inventario rápido de información necesaria:

- [ ] Inventario hardware con cantidades reales y precios
- [ ] Facturas mensuales GCP de los meses operativos
- [ ] Estimación de horas por fase (rangos honestos)
- [ ] Importes de financiación recibida con fechas
- [ ] Cobertura de tests por capa (output de coverage tools)
- [ ] Métricas medidas (latencia, throughput, etc.)
- [ ] Lista TODOs/FIXMEs significativos del repositorio
- [ ] Fecha real de inicio del proyecto
- [ ] Nombre del departamento/profesor de contacto
- [ ] Número de miembros activos de ESIBot actualmente
- [ ] Decisión sobre licencias (MIT/Apache 2.0 + CC-BY-SA)
- [ ] URL final del repositorio público

## Verificación pre-entrega

Antes de presentar el documento:

1. `grep -rn '\\todo{' sections/ main.tex` → debe devolver 0 resultados
2. `grep -rn 'RELLENAR' sections/ main.tex` → debe devolver 0 resultados
3. Compilar 2 veces: `pdflatex main.tex && pdflatex main.tex`
4. Verificar que no hay `??` en el PDF (cross-references rotas)
5. Verificar que la TOC y la lista de páginas son coherentes
6. Comparar visualmente con `docs/Architecture/LaTeX/main.pdf` para coherencia

## Convenciones de tablas

Todas las tablas usan el patrón estándar del proyecto:

```latex
\begin{table}[H]
    \centering
    \caption{Título descriptivo.}
    \label{tab:identificador}
    \begin{tabular}{...}
        \toprule
        \textbf{Cabecera 1} & \textbf{Cabecera 2} \\
        \midrule
        valor1 & valor2 \\
        \bottomrule
    \end{tabular}
\end{table}
```

Sin líneas verticales. Cabeceras en bold. Uso de `\toprule`, `\midrule`,
`\bottomrule` del paquete `booktabs`.

## Cajas especiales

Tres environments disponibles (mismo estilo que Architecture/LaTeX):

```latex
\begin{designnote}      % "Decisión de Diseño"
...
\end{designnote}

\begin{warningbox}       % "Consideración Importante"
...
\end{warningbox}

\begin{conclusionbox}    % "Conclusión"  (nuevo en Closure)
...
\end{conclusionbox}
```

## Logo

El logo está symlink-eado a `Architecture/LaTeX/diagrams/logo_esibot.png` para
no duplicar el binario. Si en algún momento se compila este documento en otro
sistema sin la carpeta de Architecture disponible, copiar el PNG manualmente
o restaurar el symlink.

## Autoría

- **Autor**: Daniel Montero Fernández (danmonfer@us.es)
- **Asociación**: ESIBot — Universidad de Sevilla
- **Versión**: 1.0
- **Estado**: Cierre formal propuesto
