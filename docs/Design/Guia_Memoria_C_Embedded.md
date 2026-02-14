# Guía de Gestión de Memoria y Variables en C para Sistemas Embebidos

Esta guía explica conceptos fundamentales de C que son críticos cuando programamos para microcontroladores (como ESP32 o Arduino), donde la memoria y el control del hardware son limitados y directos.

## 1. Tipos de Calificadores de Variables

### `static` (Estático)
El significado de `static` cambia según dónde se declare:

1.  **Dentro de una función (Local Static):**
    *   **Comportamiento:** La variable mantiene su valor entre llamadas a la función. Se inicializa solo una vez al inicio del programa.
    *   **Uso:** Contadores, estados de máquinas de estados finitos, detectores de flancos.
    *   **Ejemplo:**
        ```c
        void contar() {
            static int contador = 0; // Se crea solo la primera vez
            contador++;
            Serial.println(contador); // Imprime 1, 2, 3...
        }
        ```

2.  **Fuera de una función (Global Static / File Scope):**
    *   **Comportamiento:** La variable solo es visible dentro de **ese archivo** `.cpp`. Es como una variable "privada" del archivo.
    *   **Uso:** Evitar colisiones de nombres con otras librerías. Encapsulamiento en C.
    *   **Ejemplo:** `static int configInterna;` en `main.cpp` no chocará con `static int configInterna;` en `wifi.cpp`.

3.  **En una Clase (Class Static Members):**
    *   **Comportamiento:** La variable es compartida por **todas** las instancias de la clase. No pertenece a un objeto, sino a la clase en sí.
    *   **Uso:** Contadores de instancias, buffers compartidos (cuidado aquí), constantes de configuración de la clase.
    *   **Riesgo:** Si dos objetos escriben a la vez, se sobrescriben (Race Condition).

### `volatile` (Volátil)
*   **Significado:** Le dice al compilador: "No optimices esta variable. Su valor puede cambiar en cualquier momento fuera del flujo normal del código (por ejemplo, por hardware o interrupciones)".
*   **Uso Crítico:**
    1.  Registros de Hardware (puertos IO).
    2.  Variables compartidas entre el código principal (`loop`) y una Interrupción (`ISR`).
*   **Ejemplo:**
    ```c
    volatile bool botonPulsado = false; // Modificada en ISR

    void IRAM_ATTR isrBoton() {
        botonPulsado = true;
    }

    void loop() {
        if (botonPulsado) { // Si no fuera volatile, el compilador podría asumir que siempre es false y borrar este if
            // ...
        }
    }
    ```

### `const` (Constante)
*   **Significado:** Variable de solo lectura.
*   **En Embebidos:** A menudo ayuda a guardar datos en Flash (PROGMEM) en lugar de RAM, ahorrando memoria preciosa.

### `extern` (Externo)
*   **Significado:** "Esta variable existe, pero está definida en otro archivo".
*   **Uso:** Compartir variables globales entre archivos (desaconsejado excepto para casos muy específicos como objetos de hardware `Serial`).

---

## 2. Segmentos de Memoria (¿Dónde vive cada cosa?)

Entender el mapa de memoria es vital para evitar crashes.

### 1. Flash / .text (Code)
*   **Qué es:** Memoria no volátil (el "disco duro").
*   **Qué guarda:** El código de tu programa y variables `const` (si se indica).
*   **Características:** Lenta de escribir, rápida de leer. Muy grande (MBs).

### 2. RAM - Stack (Pila)
*   **Qué es:** Memoria de trabajo temporal y rápida. Crece "hacia abajo".
*   **Qué guarda:** Variables locales dentro de funciones, direcciones de retorno de funciones, argumentos.
*   **Ciclo de vida:** Automático. Nace al entrar en la función, muere al salir.
*   **Peligro:** **Stack Overflow**. Si llamas a muchas funciones anidadas o creas arrays locales gigantes (`int datos[10000];`), te quedas sin espacio y el micro se reinicia.

### 3. RAM - Heap (Montón)
*   **Qué es:** Memoria dinámica gestionada manualmente. Crece "hacia arriba".
*   **Qué guarda:** Objetos creados con `new` o `malloc`.
*   **Ciclo de vida:** Manual. Nace con `new`, vive hasta `delete`.
*   **Peligro:** **Memory Leak** (olvidar `delete`) y **Fragmentación** (crear/borrar objetos de distinto tamaño deja huecos inutilizables). En embebidos críticos, se suele evitar el Heap.

### 4. RAM - BSS / Data (Global/Static)
*   **Qué es:** Memoria estática.
*   **Qué guarda:** Variables globales y estáticas.
*   **Ciclo de vida:** Todo el tiempo que el micro está encendido.

---

## 3. Resumen Práctico para nuestro Proyecto

1.  **Por qué `static` en EspNowStrategy (Hardware Real):**
    *   La librería de Espressif necesita una función C "pura" para el callback. Una función C no tiene contexto de objeto (`this`).
    *   Al hacer el método `static`, se comporta como una función C y puede ser llamada por la librería.
    *   Al ser el método estático, solo puede acceder a variables estáticas.
    *   Esto está bien en el ESP32 real porque **solo hay una radio**.

2.  **Por qué `dynamic` en Test (Simulación):**
    *   En el test en PC, simulamos 5 nodos a la vez.
    *   Si usamos `static`, los 5 nodos escribirían en el mismo buffer estático. ¡Caos!
    *   Al pasarlo a dinámico (solo en test), cada objeto `EspNowStrategy` tiene su propia memoria, simulando chips independientes.

3.  **Cuándo usar `volatile`:**
    *   Solo si añades interrupciones de hardware (timers, pines). Para `ProtocolEngine` puro, raramente lo necesitarás.
