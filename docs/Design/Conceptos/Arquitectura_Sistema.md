El sistema se compone de varios cotnenedores Docker que tienen código especializado para realizar tareas específicas

Tenemos un Proxy Inverso con Nginx que se encarga de exponer y servir el html al navegador y gestionar las peticiones a la API o las conexiones de Websocket que llegan a través de Cloudflare

Luego tenemos la API, que se encarga de redireccionar o realizar una tarea específica según el comando http específico que hayamos realizado a ese endpoint. Por ejemplo, cuando enviamos un comando desde el frontend lo que estmaos haciendo es que la API publica esa tarea en pub/sub o en una cola de redis para que se gestione

Luego tenemos Redis. Redis es una base de datos en memoria que se utiliza como caché y como cola de tareas. Nos permite guardar información que queremos leer rápidamente gracias a su formato de key-valor, lo que permite realizar consultas de datos en microsegundos. Esto nos permite no tener que llamar a la BD constantemente cada vez que queremos un dato muy recurrente, sino que lo guardamos en Redis

Luego tenemos la BD en PostgreSQL. Esta BD es la que se encarga de almacenar la información de forma persistente. Es decir, la información que se guarda en PostgreSQL se guarda de forma permanente, a diferencia de Redis que se guarda de forma temporal. Por lo tanto, PostgreSQL es la base de datos que se utiliza para almacenar la información que queremos guardar de forma permanente, como por ejemplo los datos de los sensores, los experimentos, las plantas, etc.

Finalmente tenemos el Worker. El Worker es un contenedor que se encarga de realizar tareas específicas que requieren de un mayor tiempo de procesamiento. Por ejemplo, el Worker es el encargado de realizar los cálculos de los experimentos y las gráficas. Además, el Worker es el encargado de realizar la sincronización de los datos de los sensores de la BD a Redis.

En resumen, la arquitectura del sistema es la siguiente:

1. El usuario envía un comando desde el frontend
2. La API recibe el comando y lo publica en pub/sub o en una cola de redis para que se gestione
3. El Worker recibe el comando y realiza la tarea específica
4. El Worker guarda la información en PostgreSQL
5. El Worker guarda la información en Redis
6. El usuario puede ver la información en el frontend   