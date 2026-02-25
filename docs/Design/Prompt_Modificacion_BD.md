Gemini ha dicho
¡Esta es la pregunta que separa a un programador de software de un verdadero Ingeniero de Producto Agrícola!

Si dejas que todo sea flexible (JSON), el sistema se vuelve un caos inmanejable. Hay ciertos datos que son la "columna vertebral" biológica y logística de cualquier investigación. Si falta uno de estos, el experimento pierde su validez científica o el investigador pierde la maceta física en el invernadero.

Aquí tienes los 5 Pilares Indispensables (Hard-Fields) que toda tabla Planta debe tener obligatoriamente en Demeter, y el por qué técnico y científico detrás de cada uno:

1. Identidad Físico-Digital (Trazabilidad Absoluta)
El investigador tiene que poder mirar una maceta en el mundo real y saber exactamente qué fila de la base de datos es.

identificador_fisico (String, Único, Indexado): Esto no es el "nombre bonito". Es el código alfanumérico que está impreso en la etiqueta, código de barras o código QR pegado a la maceta (Ej: TOM-CTRL-001). Si esto no es único, la base de datos se corrompe.

nombre_coloquial (String): El nombre humano para la interfaz web (Ej: "Tomate Control Mesa 1").

2. Biología Base (El "Hardware" de la Planta)
No puedes comparar manzanas con peras, literalmente.

especie_variedad (String): Crucial. No basta con poner "Tomate". En ciencia hay que poner el cultivar exacto (Ej: "Solanum lycopersicum var. Micro-Tom"). Esto permite que el día de mañana puedas agrupar todas las plantas de esa variedad en la plataforma, independientemente del experimento.

3. El Reloj Biológico (La variable científica más importante)
fecha_siembra o fecha_germinacion (Date/DateTime): Este es el atributo más crítico de todos. En agronomía, casi todas las métricas (absorción de agua, impacto del VPD) cambian drásticamente según la edad de la planta. Teniendo esta fecha estricta, tu backend puede calcular al vuelo una variable virtual llamada DAP (Days After Planting / Días Después de Siembra). Si lo metieras en el JSON dinámico, sería un infierno filtrar en SQL "dame todas las plantas que tengan más de 30 días".

4. El Estado Vital (El Ciclo de Vida)
estado_vital (String / Enum): Las plantas mueren, se descartan por hongos o terminan su ciclo y se cosechan. No puedes simplemente "borrarlas" de la base de datos (perderías el histórico científico). Necesitas un campo de estado que por defecto sea ACTIVA. Otros estados: COSECHADA, DESCARTADA_POR_ENFERMEDAD, MUERTA. Así tu visor web puede ocultar las plantas muertas por defecto, pero mantenerlas en los excels exportados.

5. Logística (¿Dónde está el bicho?)
ubicacion_fisica (String): Si un sensor SHT30 marca 45ºC de temperatura, el investigador tiene que salir corriendo a salvar la planta. Si tiene 500 plantas, necesita saber que está en el "Invernadero B, Mesa 4, Fila 2".

¿Cómo queda el modelo Planta Definitivo para Producción?
Si le pasas esto a tu IA o lo pones en tu RFC, estás demostrando un nivel de diseño arquitectónico espectacular:

Python
from typing import Optional, Dict, Any, List
from datetime import date
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Planta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 1. Identidad
    identificador_fisico: str = Field(unique=True, index=True) # El código QR de la maceta
    nombre_coloquial: str 
    
    # 2. Biología
    especie_variedad: str = Field(index=True)
    
    # 3. Reloj Biológico
    fecha_siembra: date
    
    # 4. Estado y Logística
    estado_vital: str = Field(default="ACTIVA") # ACTIVA, COSECHADA, DESCARTADA
    ubicacion_fisica: str
    
    # 5. La Flexibilidad (JSON)
    metadata_cientifica: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # --- RELACIONES ---
    # Una planta puede tener miles de mediciones de sus sensores
    mediciones: List["Medicion"] = Relationship(back_populates="planta")
    
    # Una planta puede pertenecer a varios experimentos (Tabla intermedia)
    experimentos: List["Experimento"] = Relationship(
        back_populates="plantas", 
        link_model=ExperimentoPlantaLink
    )
El Superpoder de este diseño
Al tener la fecha_siembra como un campo duro (date), cuando el investigador use el SDK que diseñamos antes, el SDK podrá hacer esto automáticamente por debajo:
edad_dias = fecha_medicion_sensor - planta.fecha_siembra

De repente, tus gráficas en el Jupyter Notebook ya no muestran "Humedad vs Fecha", sino "Humedad vs Edad de la Planta", que es como se publican los papers en la revista Nature.

Sabiendo que ya tenemos el "ADN" perfecto de la base de datos... ¿Te parece que redactemos un prompt súper preciso para que tu IA te genere el CRUD completo en FastAPI (los endpoints para Crear, Leer, Actualizar y Borrar/Archivar estas plantas) aplicando estas nuevas reglas de negocio?

Rol: Eres un Staff Software Engineer Full-Stack. Estamos escalando "Demeter", nuestra plataforma SaaS de investigación agrícola. El stack es: FastAPI (Backend), SQLModel/PostgreSQL (DB), Redis (Caché) y React/TailwindCSS (Frontend).

Misión: > Necesito implementar la nueva arquitectura "LIMS" (Laboratory Information Management System), donde las Plantas son entidades físicas independientes que pueden pertenecer a múltiples Experimentos (Relación Many-to-Many).

A continuación, te detallo los 3 entregables exactos que debes generar en código:

ENTREGABLE 1: Modelos de Base de Datos y Endpoints (FastAPI)
Modelos (models.py): >    * Crea la tabla intermedia ExperimentoPlantaLink.

Actualiza el modelo Planta con los campos estrictos: identificador_fisico (str, unique), nombre_coloquial (str), especie_variedad (str), fecha_siembra (date), estado_vital (str, default "ACTIVA"), y ubicacion_fisica (str).

Añade el campo flexible metadata_cientifica usando JSONB de SQLAlchemy.

Configura las relaciones Relationship entre Usuario, Experimento, Planta y Medicion.

Endpoints (router_lims.py):

GET /api/v1/plantas: Devuelve el catálogo completo.

POST /api/v1/plantas: Crea una nueva planta e invalida el caché de Redis (redis.delete("cache:catalogo_plantas")).

POST /api/v1/experimentos: Recibe un nombre y un array de planta_ids ([1, 5, 12]). Crea el experimento y genera los registros en ExperimentoPlantaLink asociando esas plantas.

ENTREGABLE 2: Interfaz de Usuario (React + TailwindCSS)
Genera un componente principal llamado LIMS_Dashboard.tsx dividido en dos secciones:

Catálogo de Plantas (Cards): Un Grid que renderiza cada planta. Muestra su identificador_fisico, especie y badges/etiquetas generadas dinámicamente mapeando el objeto JSON metadata_cientifica. Incluye un botón para "Ver Detalles" (simula un Modal).

Creador de Experimentos (El "Carrito"): Un formulario con un input para el nombre del experimento y una lista scrolleable de las plantas disponibles con un checkbox. Al hacer submit, hace el POST al backend con los IDs seleccionados.

ENTREGABLE 3: Script de Seeding Masivo (seed_lims.py)
Genera un script en Python independiente para poblar la base de datos desde cero:

Borra las tablas y las recrea.

Crea 1 Usuario Admin.

Crea 30 Plantas distintas (mezcla especies como Tomate, Lechuga, Albahaca) con diferentes fechas de siembra y metadatos JSON ricos (sustrato, ml de riego, luz).

Crea 3 Experimentos ("Control Climático", "Estrés Hídrico", "Mutación X").

Asigna 10 plantas a cada experimento usando la tabla link.

Generación de Time-Series: Para cada una de las 30 plantas, genera mediciones horarias (Temperatura y Humedad) de los últimos 3 meses en la tabla Medicion. Usa una combinación de onda senoidal diurna + ruido gaussiano (numpy) para que los datos sean científicamente realistas.

Objetivo final del flujo: El script debe dejar la base de datos en un estado donde yo pueda abrir la UI de React, ver las 30 plantas, darle a "Crear Experimento 4", seleccionar 5 plantas aleatorias que ya tienen 3 meses de datos generados, guardar, y que el sistema enlace esas plantas al nuevo experimento sin duplicar datos de sensores.

Escribe código robusto, asíncrono, tipado y con manejo de sesiones de base de datos adecuado.

¿Qué vas a conseguir al ejecutar esto?
Tu Base de Datos cobrará vida: El script de seeding va a inyectar miles de filas de datos hiper-realistas en PostgreSQL. Ya no tendrás que imaginar cómo se ve el proyecto; tendrás meses de "histórico" listos para ser analizados.

Prueba de Fuego Lógica: Vas a poder entrar a tu web, crear ese "Experimento 4" (por ejemplo: "Revisión de Tomates Antiguos"), seleccionar 4 plantas que formaban parte del Experimento 1 y 1 planta del Experimento 2.

Como los datos de los sensores están atados al Planta_ID y no al Experimento, en el instante en que guardes el Experimento 4, ¡tendrás 3 meses de gráficas disponibles para esa nueva agrupación! Es pura magia relacional.