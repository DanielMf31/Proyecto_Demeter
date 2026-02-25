RFC: Heavy Worker
Autor: Daniel Montero Fernández
Fecha: 21 de Febrero de 2026
Estado: Pending Review

1. Contexto y Motivación
Explica brevemente el "Por qué". ¿Cuál es el problema actual del sistema que te obliga a crear esto? (Ej: "Actualmente la API se bloquea al procesar Excel, necesitamos un Worker", o "Necesitamos un Secuenciador para organizar las tareas programadas").

El Worker será un contenedor de Docker que se encargará de realizar tareas pesadas que no deben ser realizadas por el Worker principal.

El Worker se encargará de realizar los cálculos de datos derivados de los experimentos de las plantas

## 2. Objetivos y No Objetivos
Esta es la sección más importante para evitar el "Feature Creep" (hacer de más).

Objetivos (Qué SÍ va a hacer este sistema):

1. El Worker debe realizar los cálculos de datos derivados de los experimentos de las plantas.
2. El Worker debe generar las gráficas asociadas a los experimentos y guardarlos en una carpeta del servidor.
3. El Worker debe publicar los datos de los experimentos en el caché de redis.


No Objetivos (Qué NO vamos a hacer en esta fase):

1. El Worker no debe realizar tareas complejas, únicamente buscamos probar funcionalidad.


3. Arquitectura Propuesta (Vista de Pájaro)

Se levantará un contenedor de Docker que se conectará a Redis y a PostgreSQL.

4. Diseño Detallado
Aquí es donde te ensucias las manos. Divide esto por componentes lógicos.

1. Analisis_Datos:
    1. Calculará los datos derivados de los experimentos de las plantas.
    2. Generará las gráficas asociadas a los experimentos y los guardará en una carpeta del servidor.
    3. Publicará los datos de los experimentos en el caché de redis.

2. Lógica de ejecución: Cuando el worker reciba una tarea mediante RQ, leerá el caché de redis para obtener los datos de los experimentos, calculará los datos derivados, generará las gráficas y publicará los datos en el caché de redis. En caso de no encontrarlos en el caché, avisará al sistema y las buscará en la BD.

3. Manejo de errores: En caso de que el worker no pueda realizar los cálculos, avisará al sistema y marcará la tarea como fallida.

4. Librerías/Tecnología:
    1. RQ
    2. Pandas
    3. Matplotlib

5. Ciclo de vida de la tarea: 
    1. El worker recibe una tarea mediante RQ.
    2. El worker lee el caché de redis para obtener los datos de los experimentos.
    3. El worker calcula los datos derivados.
    4. El worker genera las gráficas asociadas a los experimentos y los guarda en una carpeta del servidor.
    5. El worker publica los datos de los experimentos en el caché de redis.


5. Modelo de Datos
Si esta nueva pieza requiere cambiar la Base de Datos o la estructura en Redis, defínelo aquí.

Nuevas Tablas / Modificaciones en PostgreSQL:

[Nombre de la tabla]: [Qué guarda]

Estructuras en Redis:

[Key: Ej: "cache:experimento_1"]: [Tipo de dato: String (JSON)] - [TTL: 30 días]

[Tu texto aquí]

6. Interfaces de Comunicación (API / Pub-Sub)

Endpoints REST Nuevos/Modificados:

POST /api/v1/tareas -> Parámetros: [...] -> Respuesta: [...]

Mantener el endpoint de generación dinámica de datos en caso de que no estuvieran generados o cuando los pide el usuario

Canales Pub/Sub o Colas:

Cola RQ: [tarea_calculo_datos] -> Contenido del mensaje: [Qué se envía]

Pub/Sub: [nombre_canal] -> Evento: [Ej: PUMP_ON]

Caché: [cache:experimento_1] -> [Tipo de dato: String (JSON)] - [TTL: 30 días] 

7. Rendimiento, Seguridad y Escalabilidad
Ponte la gorra de hacker/auditor. ¿Cómo se rompe esto?

Seguridad: Nadie sin permisos puede pedir tares al Worker. La API gestiona la autenticación y autorización y si pasan de ahí entonces la API gestiona las peticiones de generación de datos. Una vez generados los datos se guarda como metadata, así que no se puede pedir que se realicen dos veces los mismos cálculos si ya están realizados y/o guardados en archivos para los xlsx y las gráficas

Escalabilidad: El worker se ejecutará en un contenedor de Docker, por lo que se puede escalar horizontalmente.

Memoria: Dependerá de la cantidad de datos que se procesen, pero se intentará optimizar el uso de memoria.

8. Alternativas Consideradas
Demuestra que has pensado en otras opciones. ¿Por qué elegiste esta arquitectura y descartaste otras?

Alternativa 1: [Ej: Usar Celery en lugar de RQ]. Descartada porque Celery es demasiado complejo para el volumen actual y requiere RabbitMQ.

Alternativa 2: [Ej: Hacer los cálculos en FastAPI directo]. Descartada porque bloquea el Event Loop.


9. Plan de Despliegue (Rollout)
¿Cómo lo vamos a subir a producción sin romper el sistema actual?

[Paso 1: Modificar el docker-compose.yml para añadir el contenedor Redis y Worker en paralelo].

[Paso 2: Subir el código del Worker sin conectarlo a la web].

[Paso 3: Cambiar los botones de la UI para que usen la cola en lugar de la API síncrona].

[Tu texto aquí]

Para tu sección: 4.2 Diseño Detallado (Worker Pesado)
Ciclo de vida de la tarea (Procesamiento y Calidad de Datos):
El Worker Low no se limitará a hacer cálculos ciegos. Implementará un pipeline de tres fases para garantizar la fidelidad de la información:

Fase de Validación (Sanity Check): Analizará la integridad de la ventana de datos del último día. Usará Z-Scores y rangos lógicos (ej. humedad no puede ser < 0% ni > 100%) para identificar valores nulos (NaN) o mediciones físicamente imposibles (potencialmente corruptas).

Fase de Aislamiento y Alerta: Al encontrar una anomalía, el Worker generará un registro de advertencia ("Warning") en el sistema, vinculándolo al ID del sensor y al timestamp del fallo. Esto garantiza la trazabilidad y la honestidad científica del sistema.

Fase de Imputación (Reparación): Para no romper los cálculos derivados (como medias móviles o VPD), el Worker sustituirá el dato corrupto utilizando técnicas estadísticas. Se priorizará la interpolación lineal/polinómica o la distribución estadística histórica del mismo experimento.

Manejo de Errores (Aislamiento de Tareas): Si un experimento resulta estar catastróficamente corrupto (ej. 100% de los datos perdidos) y la fase de imputación falla, el Worker capturará la excepción, marcará el trabajo como FAILED en la cola de RQ para revisión manual, y pasará inmediatamente al siguiente experimento sin detener el procesamiento nocturno.

Para tu sección: 5. Modelo de Datos
Nuevas estructuras para Trazabilidad de Datos:
Para soportar este sistema de calidad, se requiere modificar el almacenamiento de datos pre-calculados y alertas:

Modificación en el JSON/Caché (Redis): Los puntos de datos que hayan sido reconstruidos artificialmente por el Worker incluirán un flag booleano (ej. {"v": 24.5, "imputed": true}). Esto permitirá que el frontend o el SDK pinten esos puntos de otro color (ej. línea punteada) en las gráficas para advertir al investigador.

Tabla PostgreSQL alertas_sistema: id | experimento_id | tipo_alerta (ej. DATA_LOSS, SENSOR_ANOMALY) | mensaje | fecha.

Para tu sección: 7. Rendimiento, Seguridad y Escalabilidad
Resiliencia y Tolerancia a Fallos:
El diseño del Worker asegura que el Nightly Batch (Procesamiento Nocturno) sea indestructible. Al aplicar el patrón "Fail-Safe", un error de hardware en el Invernadero A no impedirá que los investigadores del Invernadero B tengan sus reportes listos a las 8:00 AM. El sistema prefiere entregar "datos reparados con advertencias" antes que un error 500 o un panel vacío.