# Skills de Agente Recomendadas

Para potenciar el desarrollo de **Proyecto Demeter** (Sistema Híbrido C++/Python), recomiendo instalar las siguientes "Habilidades" (Skills) en tu agente.

## 1. Skills ya Instaladas
*   ✅ **python-best-practices** (`0xbigboss/claude-code`):
    *   **¿Qué hace?**: Asegura que el código Python use type hints, docstrings y siga PEP-8.
    *   **Uso**: Automático al generar código Python.

*   ✅ **find-skills** (`vercel-labs/skills`):
    *   **¿Qué hace?**: Permite buscar nuevas skills con `npx skills search`.

---

## 2. Skills Imprescindibles (A Instalar)

Te recomiendo buscar e instalar estas skills para mejorar la calidad del Firmware y la Documentación.

### A. C++ Moderno & Embedded
*   **Nombre Sugerido**: `cpp-best-practices` o `modern-cpp`
*   **Fuente Probable**: `0xbigboss/claude-code` (Suele tener un pack completo).
*   **Por qué**:
    *   Nos ayudará a usar `std::unique_ptr` en vez de `new/delete` crudos.
    *   Recordará usar `const` y `override`.
    *   Evitará el uso de macros C (`#define`) en favor de `constexpr`.
*   **Comando de Búsqueda**:
    ```bash
    npx skills search cpp
    ```

### B. Git & Control de Versiones
*   **Nombre Sugerido**: `git-conventional-commits` o `git-expert`
*   **Por qué**:
    *   Estandariza los mensajes de commit (ej: `feat: add uart strategy`, `fix: crc calculation`).
    *   Ayuda a generar CHANGELOGs automáticos.
*   **Comando de Búsqueda**:
    ```bash
    npx skills search git
    ```

### C. Documentación Técnica
*   **Nombre Sugerido**: `documentation-expert` o `markdown-style`
*   **Por qué**:
    *   Mantiene consistencia en los diagramas Mermaid.
    *   Asegura que todos los archivos `.md` tengan cabeceras de metadatos claras.

---

## 3. Cómo Instalar (Ejemplo General)
Si encuentras una skill interesante (por ejemplo, dentro del repositorio de `0xbigboss`), el comando estándar es:

```bash
# Ejemplo genérico (Verificar nombre exacto con 'search')
npx skills add https://github.com/0xbigboss/claude-code --skill cpp-best-practices
```

> **Consejo:** Mantén las skills al mínimo necesario para no "confundir" al agente con demasiadas instrucciones contradictorias. Con **Python**, **C++** y **Git** tendrás el 90% cubierto.
