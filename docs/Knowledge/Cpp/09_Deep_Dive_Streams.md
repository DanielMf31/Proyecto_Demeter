# Deep Dive: ¿Qué es "realmente" un Stream?

**Referencia:** `examples/03_Estado_Streams.cpp`

Un `Stream` (`std::cout`, `std::cin`) no es una función simple. **Es un OBJETO con MEMORIA.**

Imagina que `std::cout` es un robot pintor.
*   Tú le das instrucciones: "Pinta en Rojo" (`std::hex`).
*   El robot SE QUEDA con el pincel rojo hasta que le digas "Pinta en Azul".

## 1. El Concepto de "Estado" (Flags)

Dentro de `std::cout`, hay un registro de configuración (flags).
Cuando haces `std::cout << std::hex`, estás activando un bit en esa configuración.

**Efecto:** Todos los números que pasen por ahí después se convertirán a hexadecimal.
**Duración:** Para siempre (hasta que otro manipulador lo cambie).

### Manipuladores "Pegamenosos" (Sticky)
Cambian el estado permanentemente:
*   `std::hex`, `std::oct`, `std::dec` (Base numérica)
*   `std::boolalpha` (Imprimir `true` en vez de `1`)
*   `std::uppercase` (Para Hex `FF` en vez de `ff`)

### Manipuladores "De un solo uso"
Solo afectan al **siguiente** dato que entre al stream:
*   `std::setw(10)`: Define el ancho. Se resetea a 0 inmediatamente después de imprimir un dato.

## 2. Buffers (La Tubería no es directa)

Cuando haces `std::cout << "Hola"`, el texto NO va a la pantalla al instante. Va a un "Buffer" (una sala de espera en memoria).

¿Por qué? Porque escribir en pantalla es LENTO. El sistema espera a tener muchos datos para enviarlos de golpe.

### `std::endl` vs `\n`
*   `\n`: Solo añade un salto de línea al buffer. Rápido.
*   `std::endl`: Añade salto de línea Y **fuerza el vaciado del buffer** (`flush`). Asegura que se vea ya, pero es más lento.

**Resumen Visual:**
```text
Dato (10) --> [ Manipuladores (Hex activado?) ] --> [ Buffer (Esperando...) ] --> PANTALLA
```
