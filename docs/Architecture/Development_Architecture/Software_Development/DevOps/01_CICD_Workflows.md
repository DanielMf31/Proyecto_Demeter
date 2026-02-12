# 1. Flujos de Trabajo CI/CD (DevOps)

El proyecto utiliza **GitHub Actions** para automatizar las pruebas y el despliegue, asegurando la calidad del código tanto en el firmware C++ como en el backend Python.

## Estructura de Workflows (`.github/workflows`)

### 1. Integración Continua (`ci_develop.yml`)

Este flujo se ejecuta en cada `push` o `pull_request` hacia la rama `develop`. Su objetivo es verificar que los cambios no rompan la funcionalidad existente.

#### Job: `test-cpp` (Firmware Reliability)
*   **Entorno:** `ubuntu-latest`.
*   **Herramientas:** Python 3.11, PlatformIO.
*   **Pasos:**
    1.  Instala PlatformIO (`pip install platformio`).
    2.  Ejecuta las pruebas nativas (`pio test -e native`). Esto compila la lógica de negocio C++ en el entorno Linux y ejecuta los tests unitarios (GoogleTest/Unity) sin necesidad de hardware real.

#### Job: `test-python` (Backend Stability)
*   **Entorno:** `ubuntu-latest`.
*   **Herramientas:** Python 3.11, Pytest.
*   **Pasos:**
    1.  Instala dependencias del sistema para GUI (`python3-tk`, `xvfb`). `xvfb` (X Virtual Framebuffer) permite probar código de interfaz gráfica en un servidor sin monitor.
    2.  Instala dependencias del proyecto (`requirements.txt`).
    3.  Ejecuta `pytest` sobre el directorio `Python/tests`.

### 2. Despliegue Continuo (`deploy_main.yml`)

Este flujo se ejecuta **solo** cuando se hacen cambios en la rama `main` (Producción).

#### Job: `build-and-push`
*   **Objetivo:** Construir una imagen Docker lista para producción y publicarla.
*   **Registry:** GitHub Container Registry (`ghcr.io`).
*   **Pasos:**
    1.  **Login:** Se autentica en GHCR usando el token del repositorio.
    2.  **Metadata:** Genera etiquetas para la imagen (ej. `latest`, `sha-xyz`, nombre de rama).
    3.  **Build & Push:** Usa `docker/build-push-action` para construir la imagen basada en el `Dockerfile` raíz y subirla al registro.
    
---

## Estrategia de Ramas (Git Flow Simplificado)

1.  **`develop`:** Rama de integración principal. Todo el código nuevo pasa por aquí y debe pasar el CI (`ci_develop.yml`).
2.  **`main`:** Rama de producción. Solo recibe código estable desde `develop`. Al hacer merge, se dispara el despliegue (`deploy_main.yml`).
