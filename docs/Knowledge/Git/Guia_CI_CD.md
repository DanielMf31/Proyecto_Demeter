# Guía de Automatización CI/CD (GitHub Actions)

Este documento detalla la implementación del sistema de Integración y Despliegue Continuo (CI/CD) para el Proyecto Demeter.

## 1. Estrategia de Ramas y Flujos

Hemos definido dos flujos de trabajo principales basados en las ramas del repositorio:

### A. Rama `develop` (Integración Continua)
**Objetivo**: Asegurar que el código nuevo no rompa la funcionalidad existente.
**Disparador**: Cada vez que se hace `push` a la rama `develop`.
**Acciones**:
1.  **Tests de C++ (Firmware)**:
    - Se instala PlatformIO.
    - Se ejecuta el entorno de pruebas nativo (`env:native`).
    - Se validan la lógica de protocolo y utilidades sin necesidad de hardware real.
2.  **Tests de Python (Backend/GUI)**:
    - Se instala Python y las dependencias (`requirements.txt`).
    - Se ejecuta `pytest` para validar los parsers, la lógica de negocio y la integración asíncrona.

> ⛔ **Bloqueo**: Si alguno de estos tests falla, el workflow se marca como fallido y se notifica al desarrollador. No se debe mergear a `main` si esto falla.

### 🔍 ¿Dónde veo esto?
1. Ve a la pestaña **Actions** en tu repositorio de GitHub.
2. Verás un workflow llamado "CI (Develop)" en ejecución (amarillo) o finalizado (verde ✅ / rojo ❌).
3. Si entras, verás el detalle paso a paso (Instalar, Test C++, Test Python).

### B. Rama `main` (Despliegue Continuo / Entrega)
**Objetivo**: Generar una versión ejecutable y lista para usar del software.
**Disparador**: Cada vez que se hace `push` a la rama `main` (generalmente tras un Merge desde `develop`).
**Acciones**:
1.  **Construcción de Imagen Docker**:
    - Se crea una imagen que contiene todo el entorno de Python (Servidor + GUI).
    - Se incluye soporte para X11 (para que la GUI pueda visualizarse en el host).
2.  **Publicación (Registry)**:
    - La imagen se sube a **GitHub Container Registry (GHCR)**.
    - Etiquetada como `latest` y con el SHA del commit.

---

## 2. Cómo ejecutar los Tests Localmente

Antes de subir cambios, es recomendable ejecutar los tests en tu máquina:

### C++ (PlatformIO)
```bash
cd C++
pio test -e native
```

### Python
```bash
# Desde la raíz del proyecto
export PYTHONPATH=$PYTHONPATH:$(pwd)/Python/src
pytest Python/tests
```

---

## 3. Prerrequisitos (Entorno Local)

Para ejecutar los scripts de Docker localmente, necesitas tener Docker instalado:
```bash
# Ubuntu / Debian
sudo apt update
sudo apt install docker.io
sudo usermod -aG docker $USER
newgrp docker
```

## 4. Cómo usar la Imagen Docker (Autocarga)

Una vez que el pipeline de `main` termina, la imagen está disponible en el registro del repositorio.

### Requisitos Previos para GUI en Docker
Para ver la interfaz gráfica desde Docker en Linux, necesitas permitir el acceso al servidor X11:
```bash
xhost +local:docker
```

### Ejecución (Comando Rápido)
Puedes usar este comando (o el script `run_docker.sh` incluido).

> **¿Cómo veo la GUI si está en Docker?**
> El script usa "X11 Forwarding" (`--env="DISPLAY"` y volumen `.Xauthority`). Esto le dice al contenedor: "No tienes pantalla propia, usa la pantalla de mi ordenador Linux principal para dibujar las ventanas".
> 
> **Resultado**: Verás la ventana de Demeter aparecer en tu escritorio como si fuera una aplicación nativa, pero todo su entorno (Python, librerías) está aislado dentro del contenedor.

```bash
docker run -it --rm \
  --net=host \
  --env="DISPLAY" \
  --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
  ghcr.io/danielmf31/proyecto_demeter:latest
```

Esto descargará automáticamente la última versión (`autocarga`) y arrancará el sistema.

---

## 4. Archivos de Configuración

- **.github/workflows/ci_develop.yml**: Definición del pipeline de pruebas.
- **.github/workflows/deploy_main.yml**: Definición del pipeline de Docker.
- **Dockerfile**: Receta para construir la imagen del entorno Python.
