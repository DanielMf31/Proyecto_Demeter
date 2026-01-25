Quiero saber todos los comandos que ha ido usando la IA para generar el código de este proyecto. De esta forma puedo tener un índice de todo lo que se usa que me permite fácilmente entender por qué y los comandos útiles


# Mejora de Metodología

Okay quiero empezar a desarrollar una metodología seria para programar este proyecto. Combinaremos ciertas metodologías

1. Metódología SCRUM
2. Metodología apoyo Agente de IA Antigrativy

Como haremos:

1. Primero crearemos el Product Backlog inicial de todas las tareas que se deben hacer. 
    1. Se estudiará muy bien la metodología SCRUM para entender cómo poder organizar estos documentos y la metodología de trabajo.
    2. Se llevará a cabo una reunión cada dos semanas para revisar el Product Backlog y el Sprint Backlog. (Revisar terminología)
    3. Una vez elegido el Sprint Backlog se empezará a llevar a cabo las tareas.
2. Durante el trabajo, llevaremos un diario de desarrollo diario con las tareas que realicemos. Se encuentra en Human_Development/Daily_Journal.md
3. Practicas de buen desarrollo
    1. Se elige la tarea que se va a realizar
    2. Se lee la documentación general, la arquitectura y todos los módulos necesarios. 
        1. Se crea y se linkea la documentación necesaria para entender cómo funciona cada componente, en especial la Documentación externa
        2. Se procede a crear el código para esa funcionalidad específica.
            1. Se crea el PRD para esa funcionalidad
            2. Se revisa el código generado y se prueba.
            3. Si no Funciona
                1. Revisar los logs
                2. Revisar documentación
                3. Probar esa funcionalidad de forma separada
            4. Si funciona
                1. Se actualiza la documentación
                2. Se actualiza el PRD
                3. Se actualiza el Daily Journal
                4. Se pasa a la siguiente tarea.

# TODO

1. Crear mejores logs que si fallan en un momento del Workflow se vea la data generada
2. Leer bien la documentación de Langchain para implementar el agente de Google, ya que hay varias clases y es liosa, sólo una tiene la función de with_structured_output
3. Crear un sistema con .md que indique de forma completa al agente los documentos que tiene que revisar para saber dónde está cada cosa del proyecto y los archivos relevantes.

