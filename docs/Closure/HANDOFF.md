# Handoff — cerrar la memoria del Proyecto Demeter

Documento para retomar el trabajo en otra sesión sin repetir el análisis.
Escrito el 2026-08-24 tras analizar el repositorio entero.

**El objetivo es cerrar y entregar.** No es reabrir el proyecto, no es arreglar
código, no es mejorar nada. Es rellenar una memoria que ya está escrita y
compilarla.

---

## 0. Estado a 2026-08-24 — DOCUMENTO TERMINADO

**Cero huecos.** `grep -rn '\todo{' sections/ main.tex` sale vacío. El PDF
compila limpio: 34 páginas, sin `Overfull \hbox`, sin referencias indefinidas.

Se partió de 203 huecos. Todos rellenados en dos sesiones del 2026-08-24.

**Datos aportados por Daniel (fuente de verdad, no re-derivar):**

- Proyecto nacido en **diciembre de 2024**. Veinte meses de calendario, 44 días
  de desarrollo efectivo.
- ESIBot: sede en la **ETSI** (Universidad de Sevilla), **~100 miembros**,
  líneas de robótica, electrónica, telemática y diseño 3D. Nombre a secas,
  sin denominación larga.
- Contraparte: **Departamento de Agronomía de la ETSIA**. Objetivo pactado:
  riego automatizado que sustituyera el trabajo manual de los técnicos sobre
  las plantas de una práctica docente del **Grado en Ingeniería Agrícola**.
- Equipo actual del proyecto: **5 miembros**, **1** con conocimiento profundo,
  **1** con capacidad de mantenimiento autónomo.
- Hidráulica: presupuesto **26317** (MR MICRO Sevilla), **900,00 €**, financiado
  por el **Proyecto Docente de la ETSIA**. Recibido en **enero de 2026**, en el
  **almacén de ESIBot**, sin montar.
- Electrónica: 3 ESP32-S3, 1 Raspberry Pi 4B, 10 de cada sensor → **366 €**.
- **Total hardware: 1.266 €.** GCP: **25 €/mes**, 8 meses = **200 €**.
- Coste operativo anual **459 €** frente a **0 €** de financiación recurrente.
- Esfuerzo: **155 h** (horquilla 120–180; suelo de 87 h por commits).

**Decisiones tomadas que Daniel debería validar antes de entregar:**

- Los 366 € de electrónica se atribuyen a la asociación. Si los puso él de su
  bolsillo, cambian dos tablas del Anexo A.
- Licencias: MIT (código) y CC-BY-SA 4.0 (documentación).
- Cuotas de la asociación y patrocinios declarados en 0 €/año.
- Se propone **cerrar** la cuenta de GCP, no transferirla.
- Las asignaturas concretas propuestas en el capítulo 7 son una sugerencia
  razonada, no una lista confirmada con los departamentos.

**Correcciones aplicadas al propio repositorio durante el trabajo:**

- El recuento de tests de §3 de este handoff estaba mal (contaba invocaciones
  `RUN_TEST` repetidas entre entornos). Cifras correctas más abajo.
- La memoria decía «58 páginas» del manual técnico en tres sitios; son 81.
- Se declaraba «ESP32 DevKit V1» y «DHT22» como hardware principal; el firmware
  real usa **ESP32-S3-DevKitC-1** con **DS18B20 + higrómetro capacitivo**.
- Se eliminaron la columna de cobertura y la tabla de métricas de campo: nunca
  se midieron, y declararlo refuerza el documento.

**Lo único que queda es entregar.** Ver §5.

---


## 1. Qué hay y dónde

El documento a rellenar es **LaTeX**, no PDF, así que se edita directamente:

```
docs/Closure/LaTeX/
├── main.tex                  preámbulo, portada, \input de las secciones
├── sections/*.tex            11 secciones (00-08, A, B)
└── main.pdf                  última compilación: 28 páginas
```

Documento hermano ya terminado, con la misma identidad visual, útil como
referencia de estilo: `docs/Architecture/LaTeX/` (81 páginas, 21 figuras,
9 cuadros de «Decisión de Diseño»).

**Los huecos son `\todo{...}`**, definido en `main.tex` como texto rojo en
negrita. Para verlos todos:

```bash
cd docs/Closure/LaTeX && grep -rn '\todo{' sections/ main.tex
```

**Compilar** (las herramientas están instaladas: `pdflatex`, `latexmk`, `make`):

```bash
cd docs/Closure/LaTeX && latexmk -pdf main.tex     # dos pasadas por el índice
```

---

## 2. Estado: 203 huecos, y quién puede rellenarlos

| Fichero | Huecos | Quién |
|---|---|---|
| `04_analisis_sostenibilidad.tex` | 64 | mixto (dinero + equipo) |
| `A_anexo_financiero.tex` | 59 | **solo Daniel** (facturas) |
| `03_estado_actual.tex` | 24 | mixto (repo + medidas de campo) |
| `B_anexo_plan_entrega.tex` | 23 | **solo Daniel** (inventario, cuentas) |
| `02_logros_proyecto.tex` | 14 | **repositorio** (ya medido, ver §3) |
| `01_introduccion_contexto.tex` | 6 | solo Daniel (nombres, fechas) |
| `main.tex` | 5 | trivial (fecha, nombre asociación) |
| `07_propuesta_cierre.tex` | 4 | solo Daniel |
| `05`, `06`, `00` | 4 | redacción |

Agrupados por lo que piden:

- **37 × `X\,\euro`** → importes. Hacen falta las facturas.
- **32 × `N`** y **25 × `X`** → cantidades. Buena parte están en §3.
- **9 × `MM/AAAA`** → fechas de compra.
- **8 × `Lab/almacén`** → dónde está físicamente cada cosa hoy.
- **5 × `Daniel M. (lead)`** → confirmar si hubo alguien más.

---

## 3. Cifras ya medidas del repositorio

**Todas verificadas el 2026-08-24. Se pueden pegar tal cual.**

### Historia

| Dato | Valor |
|---|---|
| Commits (todas las ramas) | **227** |
| Commits en `main` | 210 |
| Autores | **1** (DanielMf31) |
| Primer commit | 2026-01-25 |
| Último commit | 2026-03-10 |
| Duración | **44 días naturales** |
| Días con actividad | **27** (60%) |
| Reparto | enero 18 · febrero 149 · marzo 43 |

### Esfuerzo

Estimado con la heurística habitual sobre sellos de tiempo de commits (una
sesión termina tras 2 h sin commits; se añaden 45 min por sesión para el
trabajo previo al primer commit):

| Dato | Valor |
|---|---|
| Sesiones de trabajo | 38 |
| **Horas estimadas** | **≈ 87 h** |
| Media por día activo | 3,2 h |
| Commits entre 22:00 y 06:00 | **52 %** (118 de 227) |
| Commits entre 14:00 y 22:00 | 46 % |
| Commits en horario de mañana | **2 %** |

**Las 87 h son un SUELO, no una estimación completa.** Solo capturan tiempo
próximo a un commit. Quedan fuera: montaje y cableado del hardware, lectura de
hojas de características, depuración sin commit, y buena parte de las 81 páginas
del manual técnico. Una estimación honesta para la memoria estaría entre **120 y
180 h**, y conviene decir en el texto de dónde sale el número.

Ese **52 % de commits nocturnos** es probablemente el dato más elocuente de toda
la memoria para justificar la insostenibilidad: el proyecto se sacaba adelante
fuera de cualquier horario razonable, por una sola persona.

> **No usar reparto de horas por área a partir de líneas movidas.** Se probó y no
> sirve: el 48 % de la rotación está en la raíz, y es ruido — ficheros de log
> commiteados por error (`demeter_service.log`, 16.495 líneas) más una
> **estructura anterior del proyecto** (`Python/`, `C++/`, `web/`,
> `proyecto_demeter/`) que después se reorganizó en el árbol actual. Si hacen
> falta horas por área, estimarlas a mano.

### Código

Cifras **sin dependencias ni ficheros generados** (se excluyen `node_modules`,
`.venv`, `.pio`, `docs_doxygen`, `package-lock`):

| Dato | Valor |
|---|---|
| Ficheros propios | **685** |
| Total líneas (código + docs + config) | **48.603** |
| **Solo código** | **27.025** |
| Documentación en Markdown | 14.575 |
| LaTeX | 2.370 |

> **Ojo con la cifra de 545.000 líneas.** Es la que sale si se cuenta el
> repositorio entero, pero `node_modules` **está versionado** y `Firmware/docs_doxygen/`
> es HTML generado por Doxygen (35.562 líneas). Poner esa cifra en una memoria
> sería inflar el trabajo diez veces. Usar 27.025 líneas de código.

Por zona:

| Zona | Líneas | Principal |
|---|---|---|
| `Software/Servidor` | 11.823 | TypeScript 4.847, Python 4.115 |
| `docs` | 10.710 | Markdown 7.545, LaTeX 2.370 |
| raíz | 8.474 | Markdown 5.751 |
| `Firmware` | 6.846 | C++ 4.793, cabeceras 1.938 |
| `Software/Raspberry` | 4.208 | Python 4.131 |
| `Playground` | 2.891 | Python 2.292 |
| `SDK` | 2.768 | Python 2.095 |

Por lenguaje: Python 14.788 · Markdown 14.575 · C++ 5.062 · TypeScript 4.847 ·
LaTeX 2.370 · CSS 2.052 · cabeceras C/C++ 1.938.

### Sistema

| Dato | Valor |
|---|---|
| **Tipos de mensaje del protocolo** | **15** (`CommandType`): PING, ACK, NACK, SYN, SYN_ACK, ROUTE_ADD, TEMP_HUM_REPORT, PIN_REPORT, SYSTEM_REPORT, SENSOR_CLUSTER_REPORT, SET_GPIO, SET_PWM, EXEC_SEQUENCE, GET_SENSORS, UNKNOWN — **14 útiles** si se descuenta UNKNOWN |
| **Endpoints REST** | **31** (19 GET, 10 POST, 1 PATCH, 1 DELETE) |
| **Tablas de base de datos** | **13**: User, Device, Sequence, SequenceStep, ActivityLog, ExperimentoPlantaLink, Experiment, Plant, PlantSensorMap, TelemetryAmbient, TelemetrySoil, PinHistory, SystemHistory |
| Servicios Docker | hasta **10** (`docker-compose.yml`); 5 entornos: dev, override, staging, prod, rpi |
| Clases del firmware | 12: SystemManager, ProtocolEngine, SensorManager, GpioController, IComms, INode, Node_Gateway, Node_Sensor, Node_Actuator, EspNowStrategy, GatewayStrategy, UartStrategy |
| Tipos de nodo | 3 (gateway, sensor, actuador) + 4 firmwares auxiliares |
| Placa | ESP32-S3-DevKitC-1, framework Arduino |
| Transporte | ESP-NOW (82 menciones) y UART |
| Sensores | DS18B20, SHT30, DHT22, higrómetro capacitivo |
| Actuadores | relé + bomba (61 menciones) |

### Pruebas

> **Corregido el 2026-08-24.** El recuento original de esta tabla estaba mal:
> contaba invocaciones `RUN_TEST` (que se repiten entre los entornos `native` e
> `integration`) en vez de funciones de test, y agrupaba mal las suites de
> Python. Cifras verificadas contando funciones `test_` / `it(` distintas:

| Componente | Framework | Tests |
|---|---|---|
| Firmware ESP32 | Unity (C++) | **37** |
| Servicio Raspberry Pi | pytest | **37** |
| Backend FastAPI | pytest | **16** |
| Frontend | Vitest | **3** |
| SDK científico | pytest | **52** |
| **Total entregado** | | **145** |

`Playground/` tiene además 18 tests, pero no es una capa entregable y queda
fuera de la cifra.

**No hay ningún informe de cobertura en el repositorio**, ni configuración de
`--cov` ni `fail_under`. La memoria pide un `X\%` de cobertura por componente en
dos sitios (`02` línea 86-89 y `03` línea 63-67). Dos opciones honestas:

1. Ejecutar `pytest --cov` por componente y usar el número real.
2. **Recomendado:** quitar la columna de cobertura y poner el número de tests,
   diciendo en una línea que no se midió cobertura. Cerrar un proyecto no
   justifica montar la infraestructura de medida que nunca tuvo.

### Documentos

| Dato | Valor |
|---|---|
| Manual técnico (`Architecture`) | **81 páginas**, 21 figuras, 9 cuadros de Decisión de Diseño |
| Memoria de cierre (`Closure`) | 28 páginas (con los huecos aún sin rellenar) |
| **Diagramas** | **15** en versión clara + 15 en oscura + 3 de clases = **18 distintos** |
| Documentación Markdown | 14.575 líneas repartidas en `docs/` |

---

## 4. Lo que hace falta de Daniel

Esto no está en el repositorio y **no se puede inventar**. Es lo que bloquea el
cierre:

### Bloqueante — dinero (37 huecos)

1. **Facturas del hardware.** Por cada componente: unidades, fecha de compra,
   coste, número de factura. Mínimo ESP32, Raspberry Pi 4B y sensores.
2. **Facturas de Google Cloud.** Importe mes a mes y total acumulado. También el
   identificador o correo de la cuenta GCP, que va citado en el anexo.
3. **Financiación recibida.** Qué puso la Universidad, qué puso ESIBot, qué
   pusiste tú de tu bolsillo, con fechas e importes.

### Bloqueante — inventario físico (8 huecos)

4. **Dónde está cada cosa ahora mismo.** Laboratorio, almacén de la asociación,
   en tu casa. Y a quién hay que devolver qué según quién lo pagó.

### Necesario — contexto institucional (unos 12 huecos)

5. Nombre completo de la asociación, escuela o centro concreto, departamento o
   profesor responsable, fecha de inicio del proyecto, composición y número
   aproximado de miembros activos de ESIBot.
6. **Confirmar si trabajó alguien más.** El repositorio dice que no: 227 commits,
   un solo autor. Si hubo aportaciones fuera de git (hardware, diseño, gestión),
   hay que decirlo; si no, la tabla de horas se simplifica a una sola fila y el
   argumento del cierre se vuelve más contundente.

### Opcional — medidas de campo (6 huecos)

7. `03_estado_actual.tex` pide latencia extremo a extremo, tasa de pérdida de
   tramas ESP-NOW, vida útil del nodo con 3000 mAh, rendimiento sostenido, nodos
   simultáneos probados y tiempo de reconexión del WebSocket. **Si nunca se
   midieron, quitar la tabla entera** y decir en una frase que no se llegó a
   caracterizar el sistema en campo. Es más honesto que rellenarla a ojo, y de
   hecho refuerza la tesis del documento.

---

## 5. Orden de trabajo propuesto

1. **Rellenar lo del repositorio** (§3). Son unos 40 huecos y no requieren nada
   de nadie. Deja el documento visiblemente más cerca del final y da impulso.
2. **Decidir sobre cobertura y medidas de campo** (quitar tablas o medir).
   Quitar es la opción recomendada en ambos casos.
3. **Pedir a Daniel el bloque económico y el inventario.**
4. Rellenar `A_anexo_financiero.tex` y `B_anexo_plan_entrega.tex`.
5. Revisar la redacción de `05_razones_no_sostenibilidad` y `06_lecciones` con
   los datos ya dentro: las cifras de arriba les dan un respaldo que ahora no
   tienen.
6. `latexmk -pdf main.tex`, comprobar que **no queda ni un `\todo`**:
   ```bash
   grep -rn '\todo{' sections/ main.tex   # debe salir vacío
   ```
7. Entregar.

---

## 6. Notas para quien lo retome

**El tono correcto ya está en el documento**: es un informe de viabilidad que
concluye en cierre formal, no una disculpa. Los datos del §3 lo respaldan sin
necesidad de adjetivos — 227 commits de un solo autor en 44 días, con más de la
mitad del trabajo hecho de noche, dice por sí solo por qué esto no era
sostenible. **Dejar que hablen los números y no cargar el texto.**

**No ampliar el alcance.** Hay tentación de arreglar cosas del repositorio
mientras se lee (los logs commiteados, `node_modules` versionado, el README
vacío en la raíz). No es el trabajo. El trabajo es cerrar la memoria.

**Cifras que no se deben usar sin la advertencia correspondiente:**
- 545.000 líneas → incluye dependencias y ficheros generados. Usar 27.025.
- 87 h → es un suelo, no el total. Explicar de dónde sale.
- Reparto de horas por área según líneas movidas → no sirve, ver §3.
