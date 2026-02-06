Arquitectura del programa de C++

Capa Física -> ProcesamientoDatos -> Procolo -> Aplicacion -> MaquinaEstado supervisando todo

Capa Física

0. Clase Abstracta de Comunicación a lo Python
1. Comunicacion UART

Funcionalidades

1. Enviar y recibir mensajes por UART
2. 

ProcesamientoDatos

1. ProcesamientoDatos (Instancia Activa)
2. ProtocoloComunicacion
3. DeviceManager (Configuracion.h)

Funcionalidades

1. 

Aplicacion

1. EjecucionComandos

Funcionalidades

1. Apagar y encender LEDS
2. Controlar el tiempo de activación
3. Ser controlado según los mensajes del ProtocoloComunicacion

MaquinaEstado

1. MaquinaEstado (Instancia Activa)


