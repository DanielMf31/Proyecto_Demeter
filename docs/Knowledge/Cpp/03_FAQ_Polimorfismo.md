# FAQ 01: Polimorfismo e Interfaces en C++ demeter

**Pregunta del Usuario:**
> *"Cuando usamos IComms, ¿estamos usando una clase que hereda de IComms (UartStrategy) pero la tratamos como IComms? ¿Usamos punteros para referenciar la instancia creada sin copiar? ¿Es esto correcto?"*

**Respuesta Corta:**
¡SÍ! Has dado en el clavo. Esa es la esencia del **Strategy Pattern**.

## Explicación Visual

Aquí tienes un diagrama generado para visualizar lo que ocurre en la memoria del ESP32:

![Diagrama Polimorfismo](/home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/docs/images/cpp_polymorphism.png)

## Desglose Técnico

### 1. La Máscara (La Interface)
Cuando dices "tratamos la clase como `IComms`", es exacto.
Al `ProtocolEngine` no le importa si debajo hay un chip LoRa, un cable UART o una paloma mensajera. Solo ve la máscara `IComms`.
*   **Código:** `IComms* radio;`
*   **Realidad:** El puntero apunta a un bloque de memoria que contiene un objeto completo de tipo `UartStrategy`.

### 2. La Herencia ("Es un...")
`UartStrategy` **hereda** de `IComms`. Esto garantiza al compilador que `UartStrategy` tiene *al menos* los mismos métodos que `IComms`.
*   Por eso podemos guardar la dirección de un `UartStrategy` dentro de un puntero de tipo `IComms*`.
*   Esto se llama **Upcasting** (ir hacia arriba en la jerarquía). Es seguro y automático.

### 3. El Puntero (El Mando a Distancia)
Tienes toda la razón sobre no copiar.
*   Si hiciéramos `IComms radio = miUart;` (sin puntero), ocurriría un desastre llamado **Object Slicing**. C++ cortaría la parte "Uart" del objeto y dejaría solo la parte "IComms" (que está vacía), rompiendo el programa.
*   Al usar `IComms* radio = &miUart;`, estamos creando un "Mando a Distancia Universal" (el puntero) que apunta al televisor real (el objeto `UartStrategy`).

## Resumen
Tu comprensión es 100% correcta.
1.  **Herencia:** `UartStrategy` cumple el contrato de `IComms`.
2.  **Polimorfismo:** Usamos la máscara genérica para llamar al código específico.
3.  **Punteros:** Usamos referencias para no destruir (copiar/cortar) el objeto original.
