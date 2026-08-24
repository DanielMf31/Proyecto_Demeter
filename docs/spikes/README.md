# Spikes — exploraciones técnicas timeboxed

Esta carpeta contiene **spikes** del Proyecto Demeter: exploraciones técnicas cortas, con caja de tiempo cerrada, cuyo objetivo es **aprender + decidir**, no producir código final.

## ¿Qué es un spike?

Concepto procedente de [Extreme Programming](https://www.extremeprogramming.org/rules/spike.html). Un spike es:

- **Timeboxed**: duración fija (típicamente 1–3 días). Si pasa el plazo sin resolverse, se reevalúa la hipótesis, no se extiende el plazo.
- **Hipótesis-dirigido**: cada spike tiene 1–5 hipótesis concretas y testables, con criterios explícitos de éxito o fallo.
- **De código y montaje descartables**: el resultado no se integra directamente en producción. Lo que sobrevive es el **aprendizaje** y la **decisión documentada**.
- **De inversión mínima**: se prueba con la cantidad mínima de recursos posible (1 componente, no N) para descubrir problemas pronto.

Un spike termina siempre con una **decisión binaria**: continuar, pivotar o abortar.

## Convención de nombrado

- Formato: `SPIKE-NNN-titulo-kebab-case.md`.
- `NNN`: número correlativo de tres dígitos (`001`, `002`, …) por orden de creación.
- Título descriptivo en kebab-case.
- Idioma: español (coherente con el resto del proyecto).

Ejemplos:

- `SPIKE-001-validacion-bomba-5v.md`
- `SPIKE-002-migracion-backend-rpi.md`
- `SPIKE-003-tunel-cloudflare-acceso-remoto.md`

## Estados posibles

Cada spike lleva un campo `Estado` en la cabecera. Valores válidos:

- 🟡 **Pendiente** — escrito pero no iniciado.
- 🔵 **En progreso** — en ejecución activa, dentro del timebox.
- 🟢 **Completado** — terminado con decisión documentada.
- 🔴 **Abortado** — cerrado sin completar todos los tests porque la hipótesis se invalidó pronto.

## Estructura mínima de un spike

Todo spike debería incluir, como mínimo:

1. **Cabecera**: autor, fecha inicio, fecha cierre, timebox, estado, decisión final, coste real total.
2. **Contexto y motivación**: por qué este spike, qué pregunta resuelve.
3. **Objetivo**: una frase clara con la pregunta principal.
4. **Hipótesis**: 1–5 hipótesis numeradas (H1, H2, …) con predicción + cómo medir + criterio de éxito.
5. **Materiales**: tabla con coste estimado y total.
6. **Setup experimental**: diagrama y notas de seguridad.
7. **Plan de tests**: tests numerados que validan cada hipótesis.
8. **Tabla resumen de resultados**: pasa/falla por test.
9. **Aprendizajes**: bullets con observaciones (anotar durante, no al final).
10. **Decisión final**: continuar / pivotar / abortar, con justificación basada en datos.
11. **Próximos pasos**: bifurcados según la decisión.
12. **Referencias internas**: enlaces a otros documentos del proyecto.

Ver `SPIKE-001-validacion-bomba-5v.md` como referencia.

## Cómo cerrar un spike

1. Rellenar todos los placeholders `<!-- rellenar -->` durante la ejecución (no al final).
2. Marcar la opción de decisión final con `[x]`.
3. Actualizar `Estado` y `Fecha cierre` en la cabecera.
4. Si se generó código o montaje provisional, **moverlo a una rama descartable o eliminarlo**: el spike no va a producción tal cual.
5. Si la decisión implica un cambio técnico costoso de revertir más adelante, **abrir un ADR** (Architecture Decision Record) posterior que referencie este spike y formalice la decisión.
6. Si la decisión afecta al alcance del Proyecto Docente o al cierre, comunicarlo a la asociación.

## Cuándo hacer un spike vs cuándo no

**Hacer un spike cuando:**

- Hay incertidumbre técnica concreta (¿funciona X? ¿es viable Y?).
- La inversión completa en la solución sería significativa (tiempo o dinero).
- La pregunta puede responderse con un experimento de pocos días.
- El resultado cambiará la dirección del trabajo posterior.

**No hacer un spike cuando:**

- Ya sabes que algo funciona (pasa directamente a la integración).
- La pregunta es de diseño puro y se resuelve mejor con un Design Doc o ADR.
- La duración estimada de la exploración excede 1–2 semanas (subdividir en varios spikes pequeños).
- Es un mero refactor o una mejora incremental ya validada.

## Referencias metodológicas

- Andrew Hunt & David Thomas — *The Pragmatic Programmer* (capítulos sobre tracer bullets y prototypes).
- Kent Beck — *Extreme Programming Explained*.
- Eric Ries — *The Lean Startup* (build–measure–learn loop).
- Martin Fowler — artículos sobre walking skeleton y evolutionary architecture.
