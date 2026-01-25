# Human Development Log

## [2026-01-22]
### Developer: [Daniel Montero]

#### Focus

1. Terminar de crear la estructura del proyecto
2. Crear sistema de linter automático que permita obtener toda la información del proyecto. IMPLEMENTADO. TODO: GENERAR DOCUMENTACIÓN.
3. Crear sistema que arregla depedencias automaticamente. IMPLEMENTADO. TODO: GENERAR DOCUMENTACIÓN.
4. Crea docs automatizados de todas las partes del proyecto. IMPLEMENTADO. TODO: GENERAR DOCUMENTACIÓN.
5. Probar el worflow completo.
    PROBLEMAS: Falla en la fase de OCR. SOLUCIONADO: Intalado OCR a nivel de sistema operativo. Añadido a docs
    PROBLEMAS: Falla en la fase de LLM. NO SOLUCIONADO; He creado un sistema de fallbacks que permite probar con diferentes LLMs. El problema creo que es por un problema de with_structured_output o de API. 
        ACCIONES: 
            1. Modificar el sistema de logging para que cree un archivo con la información generada en ese momento específico. 
            2. Saber si cada fase produce un output y aislar mejor el problema. 3. Intentar simplificar o buscar otra forma de generar structured_output. Revisar los docs de Langchain. 
            4. Crear una carpeta específica de src que permita probar funcionaidades atómicas para comprobar dónde está el fallo. Permite aislar y no modificar todo el código. Crear sistema para saber cómo gestionar este tipo de desarrollos. 

## [2026-01-23]
### Developer: [Daniel Montero]

#### Focus

1. Crear el Product Backlog inicial de todas las tareas que se deben hacer.
    1.  Empezar y poner los 10 primeros user stories en el Product Backlog.
    2.  Planificar el Sprint que se va a realizar.
        1. Planificar las tareas para dentro de dos semanas mediante filosofía SCRUMban
        2. Empezar a trabajar. Modificables en cualquier momento. 
2. Establecer la metodología de trabajo del agente mediante los artifacts de desarrollo personalizados


## [2026-01-24]
### Developer: [Daniel Montero]

#### Focus

1. Cambiar la estructura del proyecto y los docs para asegurar un desarrollo agéntico automático
2. Cambiar y mejorar el sistemas de los logs para saber en qué parte del programa falla. 
