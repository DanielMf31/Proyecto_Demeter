# Conceptos: Tkinter y Threading (La Cocina y el Camarero)

Crear una interfaz gráfica (GUI) que se comunique con hardware (UART) requiere entender por qué no podemos hacerlo todo en un solo lugar.

## 1. El Hilo Principal (Main Thread) = El Dibujante
Imagina que Tkinter es un **Dibujante** muy rápido que tiene que pintar la pantalla 60 veces por segundo.
*   Si pulsas un botón, el Dibujante deja de pintar, atiende tu pulsación, y vuelve a pintar.
*   Si le dices: *"Espera a que llegue un mensaje por el puerto serie"*, el Dibujante se queda quieto esperando.
*   **Resultado:** La ventana se congela. No responde a clics, se pone en blanco.

## 2. El Hilo Secundario (Worker Thread) = El Escucha
Para evitar congelar al Dibujante, contratamos a un ayudante: el **Escucha (UART Thread)**.
*   Su único trabajo es estar sentado mirando el cable USB/Serial.
*   Cuando llega un dato, lo anota en una libreta (Buffer/Cola) o avisa al Dibujante.
*   Funciona en paralelo. Mientras el Dibujante mantiene los botones bonitos, el Escucha está trabajando de fondo.

## 3. ¿Cómo se comunican? (La Cola / Queue)
El Escucha no puede tocar el dibujo (No es "Thread Safe"). Si intenta cambiar un texto en la pantalla mientras el Dibujante está pintando, el programa explota.
*   **Solución:** El Escucha deja mensajes en un buzón (`queue.Queue` o `after()`).
*   El Dibujante revisa el buzón cada pocos milisegundos (`root.after(100, check_queue)`).

---

## 4. Implementación en Demeter MVP

### A. Estructura Simple
1.  **`root.mainloop()`**: Es el bucle infinito del Dibujante.
2.  **`UartTransport.start()`**: Inicia el Hilo del Escucha.

### B. Flujo al Pulsar Botón (TX)
*   **Tú:** Pulsas "LED 1 ON".
*   **Dibujante:** Detecta el clic.
*   **Acción:** Llama a `uart.send(bytes)`.
*   **Nota:** Enviar es rápido (milisegundos), así que el Dibujante lo hace directamente sin bloquearse.

### C. Flujo al Recibir Dato (RX)
*   **Escucha:** Recibe `[ACK]`.
*   **Acción:** Llama al `callback`.
*   **Problema:** El callback se ejecuta en el Hilo del Escucha.
*   **Truco:** Si queremos cambiar el color del botón al recibir ACK, debemos usar `root.after` o una variable compartida con cuidado. Para este MVP, simplemente imprimiremos por consola para simplificar.
