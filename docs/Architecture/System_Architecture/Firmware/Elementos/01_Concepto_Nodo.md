# Concepto de Nodo (Abstracto)

## Arquitectura General
En la nueva arquitectura del Firmware Demeter V2, el **Nodo** es la unidad abstracta principal.

### Responsabilidades
1.  **Configuración**: Define la identidad del dispositivo (ID) y sus parámetros básicos.
2.  **Hardware Inyección**: Inicializa los módulos de hardware específicos.
3.  **Orquestación**: Utiliza `SystemContext` como núcleo central para gestionar las capacidades del sistema.

### Estructura
Todo Nodo compone un `SystemContext` que a su vez agrupa los tres pilares funcionales:
1.  **Executor**: Ejecución de comandos (GPIO/Hardware).
2.  **ProtocolEngine**: Comunicación y reglas de negocio.
3.  **SensorManager**: Gestión de sensores y lecturas.

## Herencia e Implementación
Para crear un nuevo dispositivo en la red:
1.  Heredar de la clase `Node`.
2.  En el constructor, inyectar las dependencias específicas al `SystemContext`.
3.  Configurar la periodicidad de reportes.

```cpp
// Ejemplo conceptual
class MiNodo : public Node {
    void setup() {
        systemContext->sensorManager->add(new DHTSensor(4));
        systemContext->begin();
    }
}
```
