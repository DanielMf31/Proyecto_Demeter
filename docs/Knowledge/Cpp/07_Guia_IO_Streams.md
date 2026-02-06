# Guía de Streams (I/O) en C++

**Referencia:** Código de ejemplo `examples/01_IO_Basico.cpp`

## ¿Por qué "Streams" (Flujos)?
En C (`printf`), pensabas en "formatear texto".
En C++ (`cout`), piensas en **"empujar datos a una tubería"**.

Imagina que `std::cout` es un tubo que va a la pantalla.
*   `<<` es el operador para **meter** cosas al tubo.
*   `>>` es el operador para **sacar** cosas del tubo (`std::cin`).

## Componentes Principales

| Objeto | Equivalente C | Descripción |
| :--- | :--- | :--- |
| `std::cout` | `stdout` / `printf` | Salida estándar (con buffer). |
| `std::cin` | `stdin` / `scanf` | Entrada estándar. |
| `std::cerr` | `stderr` | Error estándar (**sin buffer**, sale al instante). |
| `std::clog` | `stderr` | Log estándar (con buffer). |

## Trucos de Manipulación (`<iomanip>`)

A veces necesitas controlar cómo se ve el dato. Para eso usamos manipuladores que se "meten" en el flujo.

### 1. Hexadecimal
```cpp
std::cout << std::hex << 255; // Imprime "ff"
std::cout << std::dec << 255; // Vuelve a decimal "255"
```
*Ojo:* Los manipuladores cambian el estado del stream permanentemente hasta que lo cambies de nuevo.

### 2. Ancho fijo (Columnas)
Ideal para tablas bonitas en consola.
```cpp
std::cout << std::setw(10) << "Hola";
// Imprime: "      Hola" (rellena con espacios a la izquierda)
```

## Input Seguro (`std::string`)
En C, `scanf("%s", buffer)` es peligroso (buffer overflow).
En C++, `std::cin >> string` **redimensiona la memoria automáticamente**. Nunca escribirás fuera de memoria.

```cpp
std::string nombre;
std::cin >> nombre; // Seguro. Si escribes 1 millón de letras, C++ pide RAM para guardarlas.
```
