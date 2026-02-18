# PRD: Planificador de Secuencias Web (Demeter v0.4)

## 1. Visión General
El Planificador de Secuencias permite a los usuarios definir una serie de acciones (encendido/apagado de pines) con duraciones específicas para automatizar procesos complejos (ej: riego por zonas con tiempos diferenciados).

## 2. Objetivos
- Proporcionar una interfaz intuitiva para construir secuencias de hasta 10 pasos.
- Garantizar transiciones seguras entre estados (apagado de 1ms entre pasos).
- Permitir el guardado y la ejecución rápida de configuraciones frecuentes.

## 3. Requisitos Funcionales

### 3.1 Navegación
- Barra de navegación superior con diseño moderno.
- Secciones: **Control Directo** (Dashboard actual) y **Planificador**.

### 3.2 Constructor de Secuencias
- **Selector de Pin**: Lista desplegable con los pines disponibles (4, 5, 6, 7).
- **Acción**: ON/OFF.
- **Duración**: Campo numérico en milisegundos o segundos.
- **Botón "+ Paso"**: Añadir un nuevo eslabón a la cadena (Límite: 10).

### 3.3 Lógica de Seguridad y Delays
- **Acciones OFF por defecto**: Cada vez que se defina una acción de `OFF`, el sistema asignará automáticamente una duración de `1ms` como valor base. Esto actúa como un pequeño delay de seguridad antes de pasar al siguiente paso de la secuencia, a menos que el usuario especifique manualmente un tiempo mayor.

### 3.4 Persistencia
- Botón **Guardar**: Almacena la secuencia con un nombre personalizado (inicialmente en LocalStorage para rapidez, escalable a DB).
- Sección **Secuencias Registradas**: Lista de tarjetas con el nombre de la secuencia y un botón de "Ejecutar".

## 4. Requisitos Técnicos
- **Frontend**: HTML5, CSS3 (Glassmorphism/Modern), Vanilla JS.
- **Protocolo**: Enviar el objeto `SequenceCommand` mediante la API existente.
- **Arquitectura**: Simulación de Single Page Application (SPA) ocultando/mostrando contenedores mediante JS.

## 5. User Stories
1. **Como Agrónomo**, quiero programar que el Pin 4 esté ON 10s y luego el Pin 5 esté ON 5s para regar dos parcelas sin intervención manual.
2. **Como Usuario**, quiero guardar mi "Riego de Mañana" para no tener que configurar los tiempos cada día.
3. **Como Desarrollador**, quiero que el sistema apague los pines brevemente entre pasos para proteger los relés.
