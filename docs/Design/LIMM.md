RFC: Secuenciador
Autor: Daniel Montero Fernández
Fecha: 21 de Febrero de 2026
Estado: Pending Review

## 1. Contexto y Motivación

Para que los investigadores puedan seleccionar las plantas que les interesen para cada experimento, hemos decidido implementar un sistema de selección de plantas. Este sistema tendrá un apartado específico dentro de la interfaz web que permitirá a los investigadores poder estudiar y analizar las plantas.

Cada planta debe ser independiente y tener su propio registro en la base de datos. En la interfaz gráfica se podrán ver cualidades comunes a cada planta como el nombre, la especie, la fecha de plantación, la fecha de cosecha, el estado de la planta, ubicación y demás

Dentro de la interfaz se podrá filtrar por nombre, por especie, por fecha de plantación, por fecha de cosecha, por estado de la planta, por ubicación y demás. 

Se mostrará un catálogo de plantas. Cada planta será una tarjeta específica que al clicar mostrará la información más en detalle. Será posible clicar en cada tarjeta y se abrirá una nueva pestaña con la información de la planta. Además, dentro de la pestaña tendrá otras subpestañas donde clicar y se desplegará unas ventanas secundarias con características como las tablas de humedad y temperatura en cualquier periodo de la planta, las gráficas, así como los datos específicos de cada planta. Es posible que podamos meter la tabla detallada ya directamente desde la web, permitiendo que sea un visor muy avanzado y que se puedan ver exáctamente los datos que se van a leer. 

El Investigador debe poder acceder a los datos más relevantes de la planta muy rápidamente, lo que le permitirá tomar decisiones rápidas sobre el cuidado de la planta. Por lo tanto, la interfaz debe ser muy rápida y responsive.

1. Principalmente las subpestañas deberán ser: 
    1. Subpestaña de gráficas: Para poder consultar las gráficas más relevantes de la planta
    2. Subpestaña de tablas: Para poder consultar las tablas de datos de la planta
    3. Subpestaña de experimentos: Para poder consultar los experimentos relacionados con la planta
        3.1. Dentro de ellos cada experimento si es público tendrá su propia información y datos relevantes, permitiendo centralizar la información de cada experimento en un solo lugar. Es posible seleccionar si queremos que el experimento sea público o privado.
    4. Subpestaña de información: Para poder consultar la información general de la planta

## 2. Objetivos y No Objetivos
Esta es la sección más importante para evitar el "Feature Creep" (hacer de más).

1. Objetivos:

- Queremos poder ver la planta, datos más importantes y gráficas y tablas de datos de la planta
- Queremos poder ver los experimentos relacionados con la planta
- Queremos poder ver la información general de la planta
- Debe ser agradable a la vista
- Debemos poder filtrar según una serie de parámetros.
- Debemos poder modificar cada una de las cosas sobre estas plantas. Modificar directamente el nombre, la especie, la fecha de plantación, la fecha de cosecha, el estado de la planta, ubicación y demás. Todo debe poder hacerse desde la interfaz gráfica
- Gráficamente la tarjeta debe tener unas pestañas laterales para poder acceder a las subpestañas, permitiéndote clica más de una para ver la información. Al presionar dentro de una tarjeta se deberá ampliar bastante en vertical para mostrar la información y dejar espacio a la derecha para expandir las subpestañas

2. No Objetivos

- No es necesario que 


## 3. Arquitectura Propuesta (Vista de Pájaro)

La información de las plantas se guardará en la BD de PostgreSQL, mientas que la información más relevante se guardará en caché en redis. Se priorizarán las plantas más vistas para guardar el caché en caso de que el sistema escale

La interfaz gráfica vivirá dentro de la aplicación de React que ya hemos creado. 

El cahcé se implementará en Redis

Cada vez que se realice un experimento se deberá actualizar el caché lo primero y luego realizar las modificaciones pertienentes dentro de la BD para reflejar todo.


## 4. Diseño Detallado
Aquí es donde te ensucias las manos. Divide esto por componentes lógicos.

Componente 1: Secuenciador (main):

Responsabilidad: 



## 5. Modelo de Datos


6. Interfaces de Comunicación (API / Pub-Sub)

7. Rendimiento, Seguridad y Escalabilidad
Ponte la gorra de hacker/auditor. ¿Cómo se rompe esto?


9. Plan de Despliegue (Rollout)
