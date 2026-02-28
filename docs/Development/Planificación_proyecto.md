# Objetivos

El Proyecto Demeter tiene el objetivo de desplegar los sistemas en el Invernadero durante este año. Los objetivos son:

1. Montar Sistema de Riego (4 tanques + bombas + Electroválvulas)
2. Nodo de Sensores midiendo datos de 9 plantas (temperatura y humedad)
3. ESP32 Gateway y Raspberry Pi como procesador inicial y con acceso a Internet
4. ESP32 conectado a los motores del techo para regular temperatura del Invernadero

Para conseguirlo debemos trabajar estas 4 áreas:

1. Riego
2. Electrónica
3. Eléctrica
4. Despliegue en campo

A continuación se detallan las tareas pendientes en cada área:

# Áreas de trabajo

## Riego

Miguel Antonio es el encargado del riego. Actualmente está probando el sistema de riego y las electroválvulas. Dispone de una lista de tareas que pondré más detalladamente en otro documento.

Su objetivo es conseguir que el sistema funcione mediante control manual y que el agua se distribuya mediante activación manual. 

Más adelante se conectará el sistema a relés controlados por el ESP32 para probar el control remoto. Se propone reunión el día 7 de Marzo (Viernes) para montar el sistema de control remoto de las electróvalulas.

## Electrónica

Actualmente nadie se encuentra trabajando activamente en esto. Las necesidades son las siguientes:

1. Diseñar una carcasa que proteja los componentes electrónicos de la intemperie y el desgaste por humedad o temperatura
2. Diseñar un sistema de alimentación para el ESP32 que reduzca el trabajo de mantenimiento (cambio de batería). Se propone un sistema de alimentación solar con batería de litio.
3. Desplegar el sistema con la alimentación independiente y la carcasa protectora. 
4. Documentar los consumos y valores de alimentación para estimar la duración de la batería y la frecuencia de mantenimiento.

Tanto Pablete, Chema o Rod se pueden poner con eso tranquilamente. 

## Eléctrica

Actualmente nadie se encuentra trabajando activamente en esto. Las necesidades son las siguientes:

1. Conectar la fuente de alimentación a la corriente
2. Obtener varias líneas de corriente de distintos voltajes:
    1. 12V para actuadores
    2. 5V para electrónica
    3. 3.3V para electrónica

Para obtener los voltajes de 5V y 3.3V se puede usar una fuente de alimentación de 12V y un convertidor de voltaje. Tenemos Buck y Boost Converters en el armario de los componentes. Alguien puede ponerse a hacer pruebas y conseguir esos voltajes.
3. Integrar los componentes de alimentación e incorporar algún componente de seguridad para evitar sobretensiones o cortocircuitos.

Una vez conseguidos estos voltajes el objetivo es conectar la tensión a los distintos componentes del sistema. Es especialmente importante los actuadores. 

Tanto Pablete, Chema o Rod se pueden poner con eso tranquilamente. 

## Despliegue en campo

Para cumplir los objetivos propuestos es necesario desplegar los sistemas en el invernadero. El plan es el siguiente:

1. Terminar las pruebas del sistema de riego y asegurarse de que todo funciona.
2. Visitar el Invernadero para planificar el despliegue. Necesitamos conocer exáctamente:
    1. Espacio del Invernadero
    2. Espacio para montar la estructura de tanques y disposición (altura, espacio, estructura de soporte)
    3. Espacio físico donde colocar el nodo de sensores
    4. Espacio donde colocar el cuadro eléctrico. Dentro irán la alimentación y conectado directamente la Raspberry y el ESP32 Gateway.
    5. Cómo llevar cable Ethernet directamente desde la caseta hasta el Invernadero
    6. Conocer el modelo de los motores y los sensores de final de carrera para diseñar el control remoto

Una vez obtenida esta información y diseñados y probados los sistemas finales:

1. Instalaremos el cuadro eléctrico
2. Colocaremos el sistema de riego junto con los tanques
3. Instalaremos el nodo actuador para controlar el sistema de riego y el techo
4. Instalaremos el nodo sensor para medir datos de las plantas
5. Conectaremos todo
6. Haremos pruebas finales
7. Daremos acceso a los profesores para controlar el sistema de riego y a los investigadores para consultar los datos de las plantas y crear experimentos

# Reuniones previstas

1. Se propone reunión el día 7 de Marzo (Viernes) para montar el sistema de control remoto de las electróvalulas.
    1. Se probará la conexión de los relés a las electroválvulas
    2. Se programará el ESP32 para controlar las electroválvulas
    3. Se probará el sistema de control remoto de las electroválvulas
    4. Se harán pruebas de funcionamiento del sistema y se probarán configuraciones y secuencias de riego
2. Se propone reunión el día 14 de Marzo (Viernes) para montar el nodo de sensores.
    1. Se probará la conexión de los sensores al ESP32
    2. Se programará el ESP32 para controlar los sensores
    3. Se probará el sistema de lectura de sensores remotos
    4. Se probará el envío de datos a través de Internet y recepción del sistema
3. Durante el mes de Marzo se realizarán las pruebas finales y se planificará un día para ir al Invernadero a realizar el despliegue. Se detallará la información más adelante. 
