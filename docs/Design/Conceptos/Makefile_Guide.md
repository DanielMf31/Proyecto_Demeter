# Guía de Makefiles — Qué son y cómo los usamos en Demeter

## ¿Qué es un Makefile?

Un `Makefile` es un archivo de automatización. Originalmente se creó para compilar código C, pero hoy se usa como **atajo de comandos** en cualquier proyecto. Es el equivalente a tener un conjunto de scripts de terminal, pero organizados en un solo archivo con nombres cortos.

```
make staging-build
```
↑ Esto ejecuta internamente una secuencia de comandos que habrías tenido que escribir a mano:
```bash
cp .env.staging .env
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

---

## Anatomía de una regla

```makefile
nombre-del-comando:
	comando-de-terminal
	otro-comando
```

Reglas importantes:
- La **indentación usa TAB**, no espacios (error común)
- Todo lo que empiece con `@` no se imprime en pantalla (`@echo` muestra el texto sin mostrar el propio `echo`)
- Las variables se definen arriba y se usan con `$(VARIABLE)`

Ejemplo del nuestro:
```makefile
STAGING_COMPOSE = docker compose -f docker-compose.yml -f docker-compose.staging.yml

staging-build:
	@cp .env.staging .env
	$(STAGING_COMPOSE) up -d --build
```

---

## `.PHONY` — ¿Para qué sirve?

```makefile
.PHONY: dev staging seed logs
```

Le dice a `make` que estos nombres son **comandos**, no archivos. Sin esto, si existiera un archivo llamado `dev` en la carpeta, `make dev` no funcionaría porque pensaría que el archivo ya está actualizado.

---

## Lo que hace nuestro Makefile

### Estructura de entornos

```
make dev            <- copia .env.local como .env  + docker compose up
make staging        <- copia .env.staging como .env + compose con staging.yml
make staging-build  <- igual pero fuerza rebuild de imágenes Docker
```

El truco clave es el **`cp .env.X .env`** antes de cada comando. Docker Compose siempre lee el archivo `.env` de la raíz, así que dependiendo del entorno copiamos el `.env` correcto antes de arrancar.

### Por qué el seed usa `BD.seed_data` y no la ruta completa

El `Dockerfile` del backend tiene:
```dockerfile
WORKDIR /app/Software/Servidor/Backend
```

Esto significa que dentro del contenedor el directorio de trabajo ya es `/app/Software/Servidor/Backend`. Por eso:
```bash
# CORRECTO (relativo al WORKDIR):
docker exec demeter-api python -m BD.seed_data

# INCORRECTO (repite el path):
docker exec demeter-api python -m Software.Servidor.Backend.BD.seed_data
```

### Por qué el sequencer tenía el path duplicado

El mismo motivo: el `docker-compose.yml` tenía:
```yaml
command: python Software/Servidor/Backend/Secuenciador/main.py
```
Pero como el WORKDIR ya es `/app/Software/Servidor/Backend`, Python buscaba:
```
/app/Software/Servidor/Backend/Software/Servidor/Backend/Secuenciador/main.py
          ^^^^^^^^ WORKDIR ^^^^^^^^  ^^^^^^^^ command ^^^^^^^^^
```
Arreglado a:
```yaml
command: python Secuenciador/main.py
```

---

## Referencia rápida de comandos

| Comando | Qué hace |
|---|---|
| `make help` | Lista todos los comandos disponibles |
| `make dev` | Arranca desarrollo en localhost con hot-reload |
| `make dev-build` | Dev con rebuild forzado |
| `make dev-down` | Para el stack de desarrollo |
| `make staging` | Arranca staging + túnel Cloudflare → patata.monters.org |
| `make staging-build` | Staging con rebuild completo |
| `make staging-down` | Para staging |
| `make staging-seed` | Puebla la DB de staging con 20 plantas y telemetría |
| `make seed` | Puebla la DB del stack activo |
| `make status` | Estado de todos los contenedores Demeter |
| `make logs-api` | Logs de la API FastAPI en tiempo real |
| `make logs-db` | Logs de PostgreSQL |
| `make api-key` | Muestra las API keys de los experimentos (para el Colab) |
| `make clean` | Para contenedores sin borrar la DB |
| `make clean-all` | Para todo y borra volúmenes (pierde datos) |

---

## Flujo completo de staging (desde cero)

```bash
# 1. Asegúrate de que el token del túnel está en .env.staging
nano .env.staging   # CLOUDFLARE_TUNNEL_TOKEN=eyJhI...

# 2. Levanta el stack completo (build + cloudflared + todo)
make staging-build

# 3. Espera ~60s y comprueba que todo está en pie
make status

# 4. Siembra datos de prueba
make staging-seed

# 5. Obtén la API key para usar en el Colab
make api-key

# 6. Abre el navegador
# https://patata.monters.org

# 7. (Opcional) Sigue los logs mientras usas la app
make logs-api
```

---

## Ampliar el Makefile

Para añadir un nuevo comando:
```makefile
mi-comando:  ## Descripcion del comando
	docker exec demeter-api python alguna-cosa
```

Ejecutas: `make mi-comando`
