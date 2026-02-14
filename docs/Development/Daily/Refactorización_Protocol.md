ProtocolEngine se encarga de TX y RX de mensajes e interpretación

El RX se lleva a cabo con Callbacks específicos que se implementan dentro de SystemContext
El TX se implementa dentro con funciones de SendComando que implementan a nivel de UART/ESP-Now.

SystemContext se encarga de implementar la función que se encarga de ejecutar la acción según el mensaje que venga y 
de implementar la función que se encarga de enviar los mensajes a través de UART/ESP-Now.

Tiene redundancia con respecto a 


Internal Types define los estándares y los tipos de Callbacks
ProtocolEngine aplica esos estándares y obliga a que todas las funciones que quieran implementar envío de comandos sigan esas estructuras. Además, las funciones de Callbacks usan esos tipos de estructuras
SystemContext implementa funciones de Callbacks de los distintos tipos. A su vez, implementa las estrategias o secuencias de comandos de handshake y estado e implementa sus propias funciones basadas en ProtocolEngine pero que sirven para unificar la interfaz en SystemContext
Nodo simplemente añade e implementa el comportamiento específico del sistema según el Nodo que es. Nodo Gateway trabaja diferente al recibir un comando de data que otro. 

Refactorización

1. Asegurar que todos los métodos de ProtocolEngine asociados a un comando usando el struct de ese comando en:
    1. Callbacks
    2. Funciones 
    3. Mensajes
    4. Implementaciones de comandos
    5. Nodos



