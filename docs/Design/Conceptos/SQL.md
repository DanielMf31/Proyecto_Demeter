BD, SQL, 1:N N:1 N:M, consultas avanzadas, JOIN, subconsultas, funciones de agregación, índices, transacciones ACID, normalización, desnormalización, optimización de consultas, migraciones, Alembic, SQLModel, PostgreSQL, Redis, JSON, 

# SQL

## Índice de contenidos

1. Relaciones entre tablas
2. Comprobar API key
3. Alembic: Como migrar y actualizar la BD


## 1: Relaciones entre tablas

1. Cómo hacer para permitir que una planta pueda ser usada en varios experimentos.
    1. Creamos una Tabla intermedia que se encargue de relacionar una planta con un experimento físico.
    2. Cada planta tiene una lista con el número de experimentos en los que participa
    3. Cada experimento tiene una lista con el número de plantas que participan

## 2: Comprobar API key

    1. Enviamos la API Key al Backend
    2. El Backend hashea la API Key
    3. El Backend busca en la BD si existe una API Key hasheada igual
    4. Si existe, devuelve los datos del experimento
    5. Si no existe, devuelve un error

## 3: Alembic: Como migrar y actualizar la BD

1. Usamos Alembic para generar un script de migración. Alembic es como un sistema de control de versiones para la BD. Identifica los cambios que hemos hecho en los modelos de SQLModel y genera un script para aplicar esos cambios a la BD.
    1. Instalamos alembic con "pip install alembic" e iniciamos el proyecto con "alembic init alembic"
    2. Se crea una carpeta "alembic" en el proyecto
    3. En la carpeta "alembic" se encuentra el archivo "env.py" que contiene la configuración de alembic
    4. En la carpeta "alembic" se encuentra la carpeta "versions" que contiene los scripts de migración
    5. En la carpeta "alembic" se encuentra el archivo "script.py.mako" que es una plantilla para generar scripts de migración
    6. El código de Python queda como: 
    ```python
    from sqlmodel import SQLModel, create_engine, Session
    from .models import User, Experiment, Plant, Device, Sequence, SequenceStep, ActivityLog, TelemetryTH, PinHistory, SystemHistory
    from .config import settings

    engine = create_engine(settings.database_url, echo=True)

    def create_db_and_tables():
        SQLModel.metadata.create_all(engine)

    def get_session():
        with Session(engine) as session:
            yield session
    ```
    7. Ejecutaos algo como alembic revision --autogenerate -m "Añadida relacion muchos a muchos plantas y experimentos"
    8. Se crea un archivo en la carpeta "versions" que contiene el script de migración
    9. Ejecutamos el script de migración con "alembic upgrade head"
    10. Para no tener que hacerlo de forma manual, podemos añadir un script que ejecute el script de migración al iniciar el servidor o en el contenedor de Docker a la hora de inicializarlo, ya que centraliza todo. Por ejemplo, en el contenedor de Docker, podemos añadir un script que ejecute el script de migración al iniciar el servidor.