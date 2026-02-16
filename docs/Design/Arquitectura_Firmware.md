Hay que realizar un cambio en la Arquitectura del Firmware

1. Los Nodos son la Unidad Abstracta mayor
2. Los Nodos usan SystemContxt como orquestador de sus capacidades que son
    1. Executor
    2. ProtocolEngine
    3. SensorManager
3. SystemContext se encarga de gestionarlo todo mientras que Node maneja la configuración del sistema y del módulo de Hardware específico

Tenemos un Nodo Actuador que:
1. Es un NODO actuador que tiene acceso a SystemContext con acceso a Executor y ProtocolEngine.
2. SensorManager está desactivado dado que no hay ningún sensor específico que crear.
3. El Main importa una clase NodoActuador que ya tiene esos valores configurados de base pero te permite cambiarlos si es necesario.

1. Si quieres implementar un nuevo tipo de NODO creas una clase que herede de Node.
2. Si quieres crear un Nodo específico creas un main que importe la clase Node y configure los parámetros específicos. Este es el firmware que se termina cargando a la placa.

SOC:

1. Nodo se encarga de la implementación del Sistema
2. SystemContext se encarga de la gestión interna de los sistemas
3. ProtocoloEngine se encarga de la comunicación en general
4. Executor se encarga de la ejecución de comandos
5. SensorManager se encarga de la gestión de los sensores   