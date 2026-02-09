# Serialización y Validación de Datos con Pydantic

## 1. Introducción
La integridad de los datos es crítica en la comunicación entre procesos. Este documento describe el uso de **Pydantic** para la definición de esquemas, validación y serialización de mensajes en el Proyecto Demeter.

## 2. El Problema de los Tipos Dinámicos
Python, al ser de tipado dinámico, permite estructuras de datos flexibles (diccionarios). Sin embargo, esto introduce riesgos en sistemas distribuidos:
*   Falta de garantías sobre la existencia de claves.
*   Tipos de datos incorrectos (ej. recibir un string "25" donde se espera un entero 25).

## 3. Validación de Esquemas con Pydantic
Pydantic aplica validación estricta de tipos en tiempo de ejecución.

### 3.1 Definición de Modelos
Los mensajes se definen como clases que heredan de `BaseModel`. Esto actúa como un contrato formal entre el Cliente y el Servidor.

```python
class GpioCommand(BaseModel):
    pin: int
    action: str
```

### 3.2 Ciclo de Vida del Dato

1.  **Instanciación:** Se crea un objeto Python validado. Si los datos no cumplen el esquema, se lanza una excepción `ValidationError` inmediatamente.
2.  **Serialización (Marshalling):** El método `.model_dump_json()` convierte el objeto en una cadena JSON estándar para su transmisión por la red.
3.  **Transmisión:** La cadena JSON viaja por el socket TCP.
4.  **Deserialización (Unmarshalling):** El receptor utiliza `.model_validate_json()` para reconstruir el objeto. Esto garantiza que si el objeto se crea con éxito, los datos son seguros y correctos.

## 4. Beneficios en Arquitectura Desacoplada
*   **Robustez:** El servidor rechaza automáticamente mensajes mal formados antes de procesarlos.
*   **Autodocumentación:** El código define claramente qué estructura de datos espera.
*   **Interoperabilidad:** JSON es un estándar universal, permitiendo futuros clientes en otros lenguajes (ej. JavaScript/Web).
