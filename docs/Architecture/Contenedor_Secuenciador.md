RFC: Secuenciador
Autor: Daniel Montero Fernández
Fecha: 21 de Febrero de 2026
Estado: Pending Review

## 1. Contexto y Motivación

El Backend de nuestro servidor debe ser capaz de realizar una serie de tareas rutinarias de sincronización, cálculos y tareas varias. 

Actualmente no tenemos un sistema que haga esto. Por lo tanto, hemos decido crear un contenedor llamada Secuenciador que se encargue de raelizar estas tareas. 

Será un contenedor simple con poca RAM dedicado únicamente a realizar estas tareas.

## 2. Objetivos y No Objetivos
Esta es la sección más importante para evitar el "Feature Creep" (hacer de más).

1. Objetivos:

- El secuenciador deberá realizar una sincronización de los datos de sensores de la BD cada hora hacia Redis
- Deberá encolar una tarea de cálculo de experimentos y gráficas a las 3 AM para que el Worker las realice.

2. No Objetivos

- El secuenciador no deberá realizar tareas complejas, únicamente buscamos probar funcionalidad.


## 3. Arquitectura Propuesta (Vista de Pájaro)
Describe a alto nivel cómo encaja esta nueva pieza con lo que ya existe. ¿Qué contenedores de Docker interactúan? ¿Cómo fluye la información? Si vas a poner un diagrama (Mermaid o C4), este es el lugar.

El Secuenciador será un nuevo contenedor de Docker que se comunicará con Redis y PostgreSQL.

Publicará las taresa necesarias en una cola de Redis para que el worker las realice

Leerá de la base de datos de PostgreSQL para obtener los datos necesarios y los colocará en el caché de redis

## 4. Diseño Detallado
Aquí es donde te ensucias las manos. Divide esto por componentes lógicos.

Componente 1: Secuenciador (main):

Responsabilidad: 

1. LLamará a la función de sincronización de datos de sensores de la BD cada hora hacia Redis

2. Encolará la tarea de cálculo de experimentos y gráficas a las 3 AM para que el Worker las realice.

Lógica de ejecución: 

Usará APScheduler para ejecutar las tareas en los intervalos de tiempo definidos.

Manejo de errores: 

- Si falla la sincronización de datos, se reintentará cada 5 minutos.

- Si falla el encolado de tareas, se reintentará cada 5 minutos.

- Guardará un registro de los errores en logs de texto y en la base de datos.

4.2 Componente B: tasks.py

1. Definirá la función de sincronización de datos de sensores de la BD cada hora hacia Redis

2. Definirá la función de encolado de tareas de cálculo de experimentos y gráficas a las 3 AM para que el Worker las realice.

Usará SQLAlchemy para la conexión con la BD y redis para la cola de tareas.

Ciclo de vida:

1. Se despertará a la hora programada para realizar la tarea

2. Selección tarea

    2.1 Sincronización BD -> Redis

        2.1.1 Se conectará a la BD y obtendrá los datos necesarios

        2.1.2 Se conectará a Redis y publicará la tarea en la cola

    2.2 Cálculo de gráficas y experimentos

        2.2.1 Publicará la tarea en la cola de Redis

3. Se dormirá hasta la siguiente tarea programada.

## 5. Modelo de Datos

Si esta nueva pieza requiere cambiar la Base de Datos o la estructura en Redis, defínelo aquí.

Nuevas Tablas / Modificaciones en PostgreSQL:

Tabla de experimentos

Tabla de plantas


Estructuras en Redis:

[Key: Ej: "cache:experimento_1"]: [Tipo de dato: String (JSON)] - [TTL: 30 días]
[Datos: 
    1. Temperatura
    2. Humedad
    3. Parámetros calculados
    ]

6. Interfaces de Comunicación (API / Pub-Sub)
¿Cómo van a hablar los otros componentes con este nuevo sistema?

Endpoints REST Nuevos/Modificados:

- No es necesario un cambio de Endpoints. Se comunicará directamente con Redis y PostgreSQL.

Canales Pub/Sub o Colas:

Cola RQ: [tareas_calculo] -> Contenido del mensaje: [ID del experimento, ID de la planta]

Pub/Sub: No

Caché: [cache:experimento_1] -> Contenido del mensaje: [Los datos de los sensores del experimento durante esa hora]

7. Rendimiento, Seguridad y Escalabilidad
Ponte la gorra de hacker/auditor. ¿Cómo se rompe esto?

1. El usuario sólo podrá pedir una nueva exportación de los datos después de 1 segundo. Si pide más de 5 exportaciones en 1 minuto se enviará una advertencia y se bloqueará la posibilidad de pedir más exportaciones durante 1 hora.

2. El secuenciador se ejecutará cada hora y se dormirá hasta la siguiente tarea programada. Por lo tanto, no consumirá recursos de forma continua.

3. El secuenciador no realizará cálculos complejos, solo sincronización de datos y encolado de tareas. Por lo tanto, no consumirá muchos recursos.

8. Alternativas Consideradas
Demuestra que has pensado en otras opciones. ¿Por qué elegiste esta arquitectura y descartaste otras?

Alternativa 1: [El secuenciador mismo realiza las cálculos a las 3:00 AM. Descartado dado que puede bloquear el despertar del secuenciador cuando debe ejecutar otras tareas programadas]

9. Plan de Despliegue (Rollout)
¿Cómo lo vamos a subir a producción sin romper el sistema actual?

Paso 1: Modificar el docker-compose.yml para añadir el contenedor Secuenciador con la imágen del propio Backend pero que realizará la tarea programada únicamente.

Paso 2: Añadir el código necesario para la sincronización de datos de sensores de la BD cada hora hacia Redis

Paso 3: Añadir el código necesario para encolar la tarea de cálculo de experimentos y gráficas a las 3 AM para que el Worker las realice.

Paso 4: Probar el secuenciador y verificar que realiza las tareas correctamente.

Paso 5: Desplegar el secuenciador en producción. Levantar el contenedor Secuenciador y verificar que realiza las tareas correctamente.