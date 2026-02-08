# Habilidades Recomendadas para Desarrolladores Antigravity

Basado en la naturaleza de tu proyecto (Embedded C++, Python GUI, Documentation), estas son las skills más relevantes que te recomiendo explorar e instalar para potenciar tu flujo de trabajo con el Agente.

> **Nota:** Para instalar una skill, usa el comando `npx skills add <paquete>`.

## Top 10 Skills Recomendadas

### 1. Python Best Practices
**Paquete:** `vercel-labs/agent-skills@python-best-practices`
*   **Por qué:** Esencial para mantener un código Python limpio (PEP 8), estructurado y eficiente, especialmente útil para tu GUI y scripts de backend.
*   **Uso:** "Check if this Python code follows best practices".

### 2. C++ Google Style Guide
**Paquete:** `google/styleguide@cpp` (o equivalente en el ecosistema)
*   **Por qué:** Para el firmware del ESP32. Ayuda a mantener consistencia en nombramiento, gestión de memoria y punteros.
*   **Uso:** "Refactor this C++ class to follow Google Style".

### 3. Documentation Engineer
**Paquete:** `vercel-labs/agent-skills@documentation-engineer`
*   **Por qué:** Ya la hemos usado. Es crucial para mantener tus PRDs, Arquitectura y Guías de Usuario sincronizadas y profesionales.
*   **Uso:** "Update the architecture doc based on these changes".

### 4. Git Expert
**Paquete:** `git/git-skills` (Genérico)
*   **Por qué:** Para gestionar tu flujo de trabajo de "Feature Branching" (git flow) de manera eficiente, resolver conflictos y generar buenos commits.
*   **Uso:** "Help me resolve this merge conflict".

### 5. PlatformIO Helper
**Paquete:** `platformio/agent-skills` (Si existe, o general Embedded)
*   **Por qué:** Específico para tu entorno de desarrollo. Ayuda con `platformio.ini`, gestión de librerías y scripts de compilación.
*   **Uso:** "Optimize my platformio.ini for faster builds".

### 6. Pytest Master
**Paquete:** `pytest-dev/skills`
*   **Por qué:** Para robustecer tus tests unitarios en Python (como los que hicimos para el Sequencer).
*   **Uso:** "Generate parametrized tests for this function".

### 7. Tkinter Wizard
**Paquete:** (Búsqueda recomendada: `python-gui-automation`)
*   **Por qué:** Dado que tu GUI es Tkinter, una skill especializada puede sugerir mejores widgets, manejo de eventos y layouts.

### 8. Markdown Advanced
**Paquete:** `marked/skills`
*   **Por qué:** Para crear documentación rica con diagramas Mermaid, tablas complejas y formatos avanzados.

### 9. Linux/Bash scripting
**Paquete:** `bash/skills`
*   **Por qué:** Para tus scripts de despliegue (`setup_deployment.sh`) y automatización en Raspberry Pi.

### 10. Serial Communication Debugger
**Paquete:** (Custom o IoT specific)
*   **Por qué:** Ayuda a interpretar tramas hexadecimales y debuggear protocolos binarios como el de Demeter.

## Cómo Descubrir Más
Usa el comando `npx skills find <termino>` para buscar herramientas específicas.
Ejemplo: `npx skills find arduino` o `npx skills find mqtt`.
