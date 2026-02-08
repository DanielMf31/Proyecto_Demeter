# Guía Maestra: Callbacks, Punteros y Memoria en C++ (Proyecto Demeter)

Esta guía consolida todo lo aprendido sobre cómo el `ProtocolEngine` y el `SystemContext` se comunican eficientemente usando la memoria.

## 1. Conceptos Clave (`Conceptos`)

### A. Memoria y Punteros (El "Dónde")
*   **La Memoria es un Hotel:** Cada byte tiene un número de habitación (Dirección).
*   **Puntero (`*`):** Es el papel con el número de habitación, no el huésped.
*   **Zero-Copy:** No movemos a los huéspedes (datos) de habitación. Solo pasamos el papel (puntero) de una mano a otra.
*   **`reinterpret_cast`:** Le dice al compilador: "Mira esta fila de huéspedes como si formaran un equipo estructurado (Header)".

### B. Callbacks (El "Qué")
*   **Definición:** Una función guardada para ser ejecutada después.
*   **Desacoplamiento:** Permite que el `ProtocolEngine` dispare acciones sin saber *quién* las ejecuta ni *cómo*.
*   **`std::function` (El Contrato):** Define la forma exacta que debe tener la función (qué recibe y qué devuelve) para encajar en el hueco del Engine.
*   **Lambdas (`[](){}`):** La forma moderna de empaquetar una función y su contexto (puntero `this`) en un solo objeto transportable.

---

## 2. Preguntas Frecuentes (`Preguntas`)

### Sobre el Flujo
1.  **¿Quién ejecuta realmente el código del LED?**
    *   No es el Engine. Es el `SystemContext`. El Engine solo aprieta el gatillo.
2.  **¿Se mueven los datos de un lado a otro?**
    *   NO. Los datos (`SetGpioCmd`) se crean en la memoria una vez. Pasamos una **referencia** (`&`) a `SystemContext` para que los lea sin copiarlos.

### Sobre la Magia
3.  **¿Cómo sabe el programa volver a `SystemContext`?**
    *   Gracias a la **Captura Lambda (`[this]`)**. El objeto Lambda tiene guardada la dirección de memoria del `SystemContext` en una variable oculta.

---

## 3. La Revelación (`Respuestas`)

*Esta es la conclusión final a la que hemos llegado, refinada:*

**"El Protocolo del Interruptor"**

Al definir un Callback en el `ProtocolEngine`, no estamos moviendo lógica de un sitio a otro. Estamos instalando un **cable** (puntero).

1.  **Conexión (Setup):** `SystemContext` le da al `ProtocolEngine` una dirección de memoria (un puntero a su función `handleGpioCommand`).
2.  **Acción (Runtime):** Cuando llega una trama válida, el `ProtocolEngine` no "envía" el paquete por mensajería. Simplemente **salta** a esa dirección de memoria que le dimos.
3.  **Eficiencia:**
    *   El código de `ProtocolEngine` deja de ejecutarse momentáneamente.
    *   El procesador empieza a ejecutar las instrucciones de `SystemContext` (encender LED).
    *   Los datos del comando (`cmd`) están quietos en la memoria; `SystemContext` los lee directamente de allí.

**En resumen:**
El `ProtocolEngine` es el **vigilante** que detecta la llegada. El Callback es el **número de teléfono** que el vigilante marca. El `SystemContext` es el **policía** que responde a la llamada y actúa. Todo ocurre instantáneamente sin mover datos pesados, solo pasando la voz (memoria).
