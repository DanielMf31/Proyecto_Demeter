# Guía de Flujo de Trabajo con Git (Git Workflow)

Esta guía explica cómo gestionar ramas, fusionar cambios (merge) y resolver conflictos, priorizando siempre la rama de `feature` activa.

## 1. Conceptos Básicos

*   **`main`**: Rama de producción (código estable y probado).
*   **`develop`**: Rama de integración (donde se juntan todas las funcionalidades).
*   **`feature/...`**: Ramas de desarrollo de nuevas funcionalidades (donde trabajas tú).

## 2. El Problema Actual

Tengo cambios en `feature/Migracion_Protocolo_Demeter` y quiero pasarlos a `develop`. Quiero que mi versión (feature) "gane" si hay conflictos, porque es la más actualizada.

## 3. Estrategias de Fusión (Merge)

### Opción A: Merge Estándar (Lo Recomendado)
Si `develop` no ha cambiado mucho, Git fusionará automáticamente.

```bash
# 1. Asegúrate de tener todo guardado en tu rama actual
git add .
git commit -m "Guardando cambios antes de merge"

# 2. Cámbiate a develop
git checkout develop

# 3. Trae los cambios más recientes de la nube (por si acaso)
git pull origin develop

# 4. Fusiona tu rama feature en develop
git merge feature/Migracion_Protocolo_Demeter
```

### Opción B: Forzar Prioridad de Feature ("Theirs")
Si hay conflictos (mismos archivos modificados en ambas ramas), le decimos a Git que **siempre elija la versión de nuestra rama (`theirs`)** y descarte la de `develop` (`ours` en este contexto).

```bash
git checkout develop
git merge -X theirs feature/Migracion_Protocolo_Demeter
```
*Nota: `-X theirs` significa "En caso de conflicto, usa la versión de LA OTRA rama (la que estoy trayendo)".*

### Opción C: Reemplazo Total (Reset Hard)
Si `develop` es un desastre y simplemente quieres que sea **idéntica** a tu rama feature:

```bash
git checkout develop
git reset --hard feature/Migracion_Protocolo_Demeter
# Esto borrará CUALQUIER cambio que hubiera en develop que no esté en feature. ¡Cuidado!
```

## 4. Subir los Cambios (Push)

Una vez fusionado en `develop` localmente, súbelo a GitHub:

```bash
git push origin develop
```

## 5. Despliegue a Producción (Main y Tags)

Cuando tienes una versión estable en `develop` (como el MVP funcionando), es hora de llevarla a `main` y ponerle una "etiqueta" (Tag) para saber que esa versión es la v1.0.

### Paso 1: Fusión en Main
```bash
# 1. Ir a la rama principal
git checkout main

# 2. Actualizar por si acaso
git pull origin main

# 3. Traer los cambios de develop
git merge develop
```

### Paso 2: Crear la Etiqueta (Tag)
Esto crea un punto fijo en la historia. Ideal para volver atrás si algo se rompe en el futuro.

```bash
# Crear etiqueta anotada (-a) con mensaje (-m)
git tag -a v0.1.0 -m "Versión MVP: Control GPIO Básico (C++ & Python)"
```

### Paso 3: Subir todo a la Nube
OJO: El `git push` normal NO sube las tags. Hay que indicarlo explícitamente.

```bash
# Subir código y tags
git push origin main --tags
```

---

## 6. Resumen de Comandos Útiles

| Acción | Comando |
| :--- | :--- |
| Ver ramas | `git branch -a` |
| Cambiar rama | `git checkout <nombre_rama>` |
| Crear rama | `git checkout -b <nombre_nueva_rama>` |
| Guardar cambios | `git add .` + `git commit -m "Mensaje"` |
| Subir a GitHub | `git push origin <nombre_rama>` |
| Traer de GitHub | `git pull origin <nombre_rama>` |
| Ver tags | `git tag` |
