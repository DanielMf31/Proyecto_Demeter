1. Que se envíe los datos de sensores a la Raspberry
    1. Modificar el código para que envíe a la Raspberry en vez de al gateway (dst=0)
2. Raspberry recibe comandos y parsea y cachea
    1. Comprobar que Raspberry guarda las cosas en el .db y meterme dentro
3. Que se puede conectar la Raspberry al servidor y recibir los datos y guardarlos en la base de datos y en Redis
    1. Meter el entorno de staging en el servidor y que la Raspberry se conecte y envíe los datos
    2. Ver en la base de datos que se guardan y poder consultarlos
    3. Configurar que se lea cada 1 hora
4. Poder controlar desde la página web los actuadores
    1. Enviar el comando desde la página web usando pub/sub
    2. Solucionar el problema del admin admin de momento con un botón de dev.
    3. Revisar si la imagen del backend está bien configurada.
5. Dejarlo funcionar un día, obtener los datos de ayer y analizarlos