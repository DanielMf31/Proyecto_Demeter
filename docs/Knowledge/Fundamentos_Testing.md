# Fundamentos del Testing de Software: Filosofía y Conceptos Clave

Este documento resume los pilares fundamentales del testing de software, desligándose de lenguajes específicos (Python/C++) para centrarse en la **filosofía**, **metodologías** y **recursos de aprendizaje**.

---

## 1. ¿Por qué testeamos? (La Filosofía)

El testing no es solo "buscar bugs". Es una disciplina intelectual para gestionar el riesgo y ganar confianza.

*   **Mitigación de Riesgos:** El software fallará. El testing reduce la probabilidad de que falle en producción donde cuesta dinero y prestigio.
*   **Documentación Viva:** Un test bien escrito documenta qué *debería* hacer el código mejor que cualquier manual, porque si el manual miente, el test falla.
*   **Velocidad de Desarrollo:** Parece contraintuitivo, pero testear te hace ir más rápido a largo plazo. Sin tests, cada cambio requiere verificar manualmente todo el sistema (fear-driven development). Con tests, cambias código con confianza (courage-driven development).

### Principios del ISTQB (Estándar de la Industria)
1.  **El testing demuestra la presencia de defectos, no su ausencia.** Nunca podrás asegurar que no hay bugs, solo que no encontraste ninguno en tus escenarios.
2.  **El testing exhaustivo es imposible.** No puedes probar todas las combinaciones de inputs. Debes priorizar por riesgo.
3.  **La paradoja del pesticida.** Si repites los mismos tests siempre, dejarán de encontrar nuevos bugs. El software evoluciona, los tests también deben hacerlo.

---

## 2. La Pirámide de Testing (Estrategia)

Popularizada por Mike Cohn y Martin Fowler, es la guía definitiva para testear eficientemente.

### 🔺 Cima: Tests End-to-End (E2E) / UI
*   **Qué son:** Simulan al usuario real (clic en botón, esperar respuesta, ver resultado).
*   **Cantidad:** Pocos (10%).
*   **Pros:** Validan el flujo completo y real.
*   **Contras:** Lentos, frágiles (si cambia un color del botón, el test falla), difíciles de mantener.
*   *Ejemplo:* Un script que abre el navegador, se loguea y compra un producto.

### 🟦 Medio: Tests de Integración
*   **Qué son:** Verifican que dos módulos hablen bien entre sí (API <-> Base de Datos, Frontend <-> Backend).
*   **Cantidad:** Medios (20-30%).
*   **Pros:** Encuentran errores de contrato o interfaz.
*   **Contras:** Requieren levantar servicios reales o mocks complejos.
*   *Ejemplo:* Verificar que al enviar un comando `SET_GPIO` desde el Gateway, el módulo `EspNowStrategy` realmente intenta enviar bytes.

### 🟩 Base: Tests Unitarios
*   **Qué son:** Aíslan una función o clase y prueban su lógica matemática/negocio pura.
*   **Cantidad:** Muchos (60-70%).
*   **Pros:** Velocidad extrema (milisegundos), pinpointing exacto del error.
*   **Contras:** No garantizan que el sistema funcione en conjunto, solo que la pieza es correcta.
*   *Ejemplo:* Verificar que la función `calculateCRC([0x01, 0x02])` devuelve `0x03`.

---

## 3. Conceptos Clave

### Black Box vs White Box
*   **Black Box (Caja Negra):** Testeas sin saber cómo está hecho el código. Solo te importan Inputs y Outputs. (Ej. Testing funcional, E2E).
*   **White Box (Caja Blanca):** Testeas conociendo el código interno. Buscas cubrir todas las ramas (`if/else`) y caminos. (Ej. Tests Unitarios, Coverage).

### TDD (Test Driven Development)
Filosofía de diseño: Primero escribes el test (que falla), luego el código mínimo para pasarlo, y luego refactorizas.
*   *Ciclo:* **Red** (Falla) -> **Green** (Pasa) -> **Refactor** (Limpia).
*   *Ventaja:* Te obliga a escribir código testearble y diseñado desde la perspectiva del usuario (API client).

### Mocks vs Stubs (Dobles de Prueba)
Cuando testeas un componente A que depende de B (que es lento o complejo):
*   **Dummy:** Objeto vacío para rellenar argumentos.
*   **Stub:** Objeto que devuelve respuestas fijas ("si te piden la hora, di siempre 12:00").
*   **Mock:** Objeto que verifica comportamiento ("asegúrate de que A llamó a B exactamente 3 veces").

---

## 4. Recursos Recomendados (Lectura Profunda)

Para aprender las bases sólidas, huye de tutoriales de herramientas y busca estos recursos canónicos:

### Webs y Blogs Clásicos
1.  **Martin Fowler (Testing Guide):** La biblia moderna del desarrollo ágil.
    *   *Web:* [martinfowler.com/testing](https://martinfowler.com/testing/)
    *   *Qué leer:* "The Practical Test Pyramid", "Mocks Aren't Stubs".
2.  **Google Testing Blog:** Lecciones aprendidas por ingenieros de Google a escala masiva.
    *   *Web:* [testing.googleblog.com](https://testing.googleblog.com/)
    *   *Qué leer:* Los artículos sobre "Flaky Tests" y "TotT" (Testing on the Toilet).
3.  **Ministry of Testing:** La comunidad más grande y amigable. Recursos muy prácticos.
    *   *Web:* [ministryoftesting.com](https://www.ministryoftesting.com/)
    *   *Qué buscar:* "Testing Feeds", "The Club" (foro).
4.  **ISTQB Glossary:** Para hablar con propiedad y conocer los términos estándar.
    *   *Web:* [glossary.istqb.org](https://glossary.istqb.org/)

### Libros Fundamentales (Agnósticos)
*   **"xUnit Test Patterns"** (Gerard Meszaros): La enciclopedia de patrones de test. Denso pero definitivo.
*   **"Test Driven Development: By Example"** (Kent Beck): El libro que originó el movimiento TDD.
*   **"Clean Code"** (Robert C. Martin): El capítulo sobre Unit Tests es oro puro ("F.I.R.S.T. principals").

### Métricas que Importan
Más allá del % de Cobertura (Code Coverage), busca:
*   **Mutation Testing:** Cambia tu código al azar y corre los tests. Si los tests siguen pasando, tus tests son malos (falsos positivos).
*   **Defect Density:** Bugs encontrados por cada 1000 líneas de código.

---
**Resumen para Demeter:**
En nuestro proyecto, estamos aplicando la **Pirámide de Testing**:
1.  Muchos tests **Nativos (Unitarios)** para `ProtocolEngine` y Lógica de Nodos (Base).
2.  Algunos tests de **Integración** simulando envío de tramas entre Gateway y Nodos.
3.  Tests de **Sistema** manuales (ver si el LED se enciende) para la validación final.
