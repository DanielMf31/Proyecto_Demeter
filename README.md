# Proyecto Demeter

Plataforma IoT para monitorización y riego automatizado de entornos de cultivo,
desarrollada en la Asociación Universitaria ESIBot (Universidad de Sevilla) en
colaboración con el Departamento de Agronomía de la ETSIA.

> **Estado: versión 1.0 archivada.** El desarrollo activo terminó en marzo de
> 2026 y el proyecto se cierra formalmente en agosto de 2026. No hay desarrollo
> planificado ni mantenimiento comprometido. El repositorio se publica como
> artefacto estable, documentado y reproducible. Ver
> [Informe de Viabilidad y Cierre](docs/Closure/LaTeX/main.pdf).

## Qué hace

Una red de nodos ESP32-S3 recoge temperatura de suelo, humedad de suelo y
variables ambientales por planta, y los envía por una malla ESP-NOW a un nodo
*gateway*. Ese *gateway* habla por UART con una Raspberry Pi, que traduce el
protocolo binario a JSON y lo publica por WebSocket a un backend en
contenedores. Desde el dashboard se consultan los datos, se actúa sobre los
GPIO de los nodos y se programan secuencias de riego. Un SDK de Python permite
extraer las series y calcular indicadores agronómicos sin tocar la
infraestructura.

## Arquitectura

```
ESP32-S3 sensor  ──ESP-NOW──▶  ESP32-S3 gateway  ──UART──▶  Raspberry Pi
                                                                  │
                                                                WSS
                                                                  ▼
  Navegador  ◀──WS/REST──  Backend FastAPI + PostgreSQL + Redis + workers
                                                                  ▲
                                                          SDK Python (análisis)
```

| Capa | Ubicación | Tecnología |
|---|---|---|
| Firmware | `Firmware/` | C++ / Arduino sobre ESP32-S3, ESP-NOW + UART |
| Borde | `Software/Raspberry/` | Python `asyncio`, cliente WebSocket, caché local |
| Backend | `Software/Servidor/Backend/` | FastAPI, PostgreSQL, Redis, RQ, Alembic |
| Frontend | `Software/Servidor/Frontend/` | TypeScript, WebSocket |
| SDK | `SDK/demeter_sdk/` | Python, Pandas, caché Parquet |
| Común | `Software/Common/` | Modelos Pydantic y protocolo compartidos |

El protocolo binario propio (Demeter V2) y las decisiones de diseño que
sostienen esta arquitectura se documentan en la
[Documentación Técnica](docs/Architecture/LaTeX/main.pdf) (84 páginas).

## Arranque rápido

Requiere Docker y Docker Compose.

```bash
cp .env.example .env.local     # y ajusta las credenciales
make dev-build                 # levanta el stack completo
make dev-seed                  # migra la base de datos y carga datos de prueba
```

Frontend en `localhost:5173`, API y documentación OpenAPI en
`localhost:8000/api/docs`.

Para el firmware:

```bash
cd Firmware
pio run -e gateway             # compila el gateway
pio run -t upload -e gateway   # y lo flashea
```

`make help` lista el resto de objetivos (staging, producción, Raspberry Pi,
migraciones, claves de experimento).

## Tests

```bash
make test-all
```

Son 140 tests automatizados repartidos en cinco suites: firmware (Unity),
servicio de borde y backend (pytest), frontend (Vitest) y SDK (pytest). El
detalle por fichero está en el capítulo 7 de la Documentación Técnica.

## Configuración

Todos los servicios leen variables `DEMETER_*` mediante Pydantic
`BaseSettings`. **Los ficheros `.env` no se versionan**: usa `.env.example`
como plantilla y crea el que necesites (`.env.local`, `.env.staging`,
`.env.prod`, `.env.rpi`); los objetivos del `Makefile` los copian a `.env`.

El entorno de *staging* necesita además un token de túnel de Cloudflare en
`CLOUDFLARE_TUNNEL_TOKEN`, que debes generar en tu propia cuenta.

## Documentación

| Documento | Qué contiene |
|---|---|
| [Documentación Técnica](docs/Architecture/LaTeX/main.pdf) | Arquitectura de las cuatro capas, protocolo, testing, despliegue y conclusiones. 84 páginas |
| [Informe de Viabilidad y Cierre](docs/Closure/LaTeX/main.pdf) | Análisis económico, de recursos humanos y técnico que motiva el cierre. 36 páginas |
| `docs/Manuals/` | Guías de flasheo y gestión de datos |
| `docs/spikes/` | Exploraciones técnicas acotadas |

## Qué NO hace

Por honestidad con quien llegue aquí buscando algo que funcione en producción:

- **Nunca se desplegó en un invernadero real.** Toda la validación es de banco.
- **Nunca se actuó sobre una bomba real.** La instalación hidráulica se
  adquirió y no llegó a montarse.
- **El enlace ESP-NOW no está cifrado.** Cualquier ESP32 cercano sintonizado al
  canal puede leer las tramas.
- **No hay observabilidad ni alarmas**, ni medida de cobertura de tests, ni
  caracterización de latencia, pérdida de tramas o autonomía real.
- **Añadir un nodo exige recompilar**: la MAC del *gateway* y el identificador
  de nodo se fijan en tiempo de compilación.

El capítulo 9 de la Documentación Técnica desarrolla estas limitaciones y qué
haría falta para levantarlas.

## Licencia

Código bajo [MIT](LICENSE). Documentación bajo
[CC BY-SA 4.0](docs/LICENSE).

## Autoría

Daniel Montero Fernández — Asociación Universitaria ESIBot, Escuela Técnica
Superior de Ingeniería, Universidad de Sevilla.
