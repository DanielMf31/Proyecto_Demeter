# Conceptos de Arquitectura de Memoria en Sistemas Embebidos (ESP32 vs Clasico)

Esta guía profundiza en la arquitectura de memoria, comparando conceptos modernos (ESP32) con arquitecturas clásicas (Motorola 68k/HCS12) para facilitar la transición.

## 1. Tipos de Memoria Física

### RAM (Random Access Memory)
*   **Volátil:** Se borra al apagar. Rápida (1 ciclo de reloj).
*   **Motorola (Clásico):** Solía ser externa o muy pequeña (SRAM interna de 4KB-12KB). Dirección `0x0000`.
*   **ESP32 (Moderno):**
    *   **Internal SRAM (520 KB):** Dividida en IRAM (Instrucciones) y DRAM (Datos).
    *   **PSRAM (External):** Hasta 4MB/8MB conectados por SPI. Más lenta pero enorme.
*   **Uso:** Variables, Stack, Heap.

### Flash (Program Memory)
*   **No Volátil:** Retiene datos sin energía.
*   **Motorola:** EEPROM o Flash interna. Donde "quemabas" el programa.
*   **ESP32:** Externa (conectada por SPI). El ESP32 usa una caché (Mapping) para ejecutar código desde Flash como si fuera RAM transparente (XIP - Execute In Place).
*   **Uso:** Código (`.text`), Constantes (`.rodata`, `PROGMEM`).

### EEPROM / NVS (Non-Volatile Storage)
*   **No Volátil:** Para guardar configuraciones (WiFi, IDs) que sobreviven al reinicio.
*   **Motorola:** Una zona específica de memoria EEPROM accesible por registros.
*   **ESP32:**
    *   **No tiene EEPROM real.**
    *   **Emulación:** Usa una partición de la Flash llamada **NVS (Non-Volatile Storage)**.
    *   **Librería `Preferences`:** Guarda pares Clave-Valor (`key-value`). Mucho más seguro que escribir direcciones crudas.

---

## 2. Mapa de Memoria (Memory Map)

### Modelo Von Neumann vs Harvard
*   **Von Neumann (Motorola 68k):** Código y Datos comparten el mismo bus y mapa de memoria.
*   **Harvard Modificado (ESP32):**
    *   Bus de Instrucciones (IRAM) y Bus de Datos (DRAM) separados para velocidad.
    *   **Curiosidad:** No puedes ejecutar código si está en DRAM, y no puedes leer datos (fácilmente) si están en IRAM.
    *   Por eso usamos `const` para guardar tablas en Flash (`.rodata`) que se mapean a DRAM virtualmente.

---

## 3. Gestión de Memoria en Ejecución

### Stack (Pila) - "El rápido y automático"
*   **Qué es:** Memoria LIFO (Last In, First Out).
*   **Motorola:** Registro `SP` (Stack Pointer). Crecía hacia abajo desde el final de la RAM.
*   **ESP32:** Cada **Tarea (Task)** de FreeRTOS tiene su propio Stack.
    *   `setup()` y `loop()` corren en la tarea "main" (aprox 8KB por defecto).
    *   **Peligro:** Si declaras `char buffer[10000]` dentro de una función, desbordas el Stack de la tarea y el ESP32 crashea (`Guru Meditation Error: Stack canary watchpoint triggered`).

### Heap (Montón) - "El grande y manual"
*   **Qué es:** El resto de la RAM que no usa el Stack ni las Globales.
*   **Motorola:** Apenas se usaba `malloc`. Todo era estático.
*   **ESP32:** Muy usado por WiFi, Bluetooth, Strings y `std::vector`.
*   **Fragmentación:**
    *   Imagina un queso gruyère. Si pides 100 bytes, los liberas, pides 50... quedan huecos.
    *   En Arduino/C++, `String` causa mucha fragmentación. **Evitar `String` en favor de `char[]` o `std::string` reservado.**

---

## 4. Comparativa Práctica

| Concepto | Motorola HCS12 / 68k | ESP32 |
| :--- | :--- | :--- |
| **Enteros (`int`)** | 16-bit (usualmente) | 32-bit (siempre). `short` es 16-bit. |
| **Punteros** | 16-bit o 32-bit (flat) | 32-bit. |
| **Endianness** | Big Endian (MSB primero) | Little Endian (LSB primero). **OJO al enviar bytes por red.** |
| **Alineación** | A veces permitía acceso impar. | Acceso desalineado a memoria causa Excepción (Crash inmediato). |
| **Reinicio** | Watchdog simple. | Watchdog dual (Timer + Task Watchdog). |

### Ejemplo Real: Alineación y Padding
En Motorola podías tener estructuras compactas. En ESP32 (32-bit), el compilador añade "relleno" (padding) para alinear datos.

```cpp
struct Paquete {
    uint8_t id;    // 1 byte
    // 3 bytes de PADDING oculto
    uint32_t val;  // 4 bytes
};
// Tamaño total: 8 bytes (no 5).
```
**Solución:** Usar `__attribute__((packed))` para eliminar el padding al enviar por radio (como hicimos en `ProtocolEngine`).

---

## 5. Resumen
1.  **Ahorra RAM:** Usa `const` para textos y tablas fijas.
2.  **Cuidado con el Stack:** No crees arrays enormes en funciones. Usa globales o Heap (con cuidado).
3.  **Little Endian:** Recuerda que `0x1234` se guarda en memoria como `34 12`.
4.  **Packed:** Siempre empaqueta estructuras que viajen por aire.
