# RFC 01: Migración del Protocolo a Pydantic

**Estado:** Implementado
**Fecha:** 31 Enero 2026

## 1. El Problema Actual (Argumentos Crudos)
Actualmente, para construir tramas dependemos de recordar el orden de los argumentos en funciones.

```python
# CÓDIGO ACTUAL (V2 Original)
# Tengo que recordar qué es '1', '10', '4' y '1'.
# Si pongo '500' en pin, el código intentará enviarlo hasta que el ESP32 falle.
protocol.create_set_gpio(10, 4, 1)

# Peor aún con Secuencias (Diccionarios sin tipado)
step = {'target': 10, 'cmd': 0x10, 'pin': 4, 'val': 1, 'delay': 5000}
# Si escribo 'target_id' en vez de 'target', crash en runtime.
```

## 2. La Solución Pydantic

Definiremos modelos estrictos en `protocols/schemas.py`.

### 2.1 Modelos Base
```python
from pydantic import BaseModel, Field

class DemeterCommand(BaseModel):
    target_id: int = Field(ge=0, le=255, description="ID del Nodo destino")
    
    def get_cmd_id(self) -> int:
        raise NotImplementedError
```

### 2.2 Comando GPIO (Ejemplo Código Real)
```python
class SetGpio(DemeterCommand):
    pin: int = Field(ge=0, le=40, description="GPIO físico (0-40)")
    value: int = Field(ge=0, le=1, description="1=HIGH, 0=LOW")
    
    def get_cmd_id(self) -> int:
        return 0x10
```

**Uso:**
```python
# CÓDIGO NUEVO
cmd = SetGpio(target_id=10, pin=4, value=1)
# Boom. Si pongo pin=99, lanza ValidationError inmediatamente.
```

### 2.3 Secuencias Complejas (Validación Anidada)
Aquí es donde Pydantic brilla. Una secuencia es una lista de pasos validados.

```python
class SequenceStep(BaseModel):
    # Composición: Un paso CONTIENE un comando GPIO
    action: SetGpio 
    post_delay_ms: int = Field(default=0, ge=0)

class ExecSequence(DemeterCommand):
    steps: list[SequenceStep]
    
    def get_cmd_id(self) -> int:
        return 0x30
```

**Uso:**
```python
# Crear una rutina de riego completa
rutina = ExecSequence(
    target_id=1, # Gateway orquesta
    steps=[
        SequenceStep(
            action=SetGpio(target_id=10, pin=4, value=1),
            post_delay_ms=5000
        ),
        SequenceStep(
            action=SetGpio(target_id=10, pin=4, value=0),
            post_delay_ms=0
        )
    ]
)
# Serialización
bytes_trama = protocol.serialize(rutina)
```

## 3. Serialización Automática
La clase `DemeterProtocolV2` simplificará su interfaz drásticamente.

**Antes:**
```python
def create_set_gpio(...): ...
def create_sequence(...): ...
def create_ping(...): ...
```
(Un método por cada comando existente)

**Después:**
```python
def serialize(self, command: DemeterCommand) -> bytes:
    # 1. Detectar tipo
    cmd_id = command.get_cmd_id()
    
    # 2. Generar Payload binario según el tipo
    if isinstance(command, SetGpio):
        payload = struct.pack('<BBB', command.pin, command.value, 0)
    elif isinstance(command, ExecSequence):
        payload = self._pack_sequence(command.steps)
        
    # 3. Empaquetar Header + CRC (Común)
    return self._pack_frame(command.target_id, cmd_id, payload)
```

## 4. Beneficios Tangibles
1.  **Seguridad:** Imposible crear comandos malformados (Pin negativo, Delay negativo, MACs de longitud incorrecta).
2.  **Autocompletado IDE:** VSCode sabrá que `SetGpio` tiene un campo `.pin`, ayudando al desarrollador.
3.  **Logs Estructurados:** Podemos hacer `logger.info(cmd.model_dump_json())` y obtener un log JSON perfecto automáticamente para depuración.

¿Está aprobado este diseño detallado?
