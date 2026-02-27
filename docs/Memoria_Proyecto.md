# Proyecto DEMETER

## Plataforma Integral de Monitorización y Gestión para Investigación Agrícola

**Autor:** Daniel Montero Fernández
**Fecha:** Febrero de 2026
**Estado:** Desarrollo activo

---

## 1. Motivación y Problema a Resolver

En la investigación agronómica actual existe una desconexión crítica entre el mundo físico —las plantas en el invernadero— y el mundo digital donde se analiza la ciencia. Los investigadores dependen de recolección manual de datos, hojas de cálculo aisladas y carecen de trazabilidad real cuando una misma planta es sujeto de múltiples estudios simultáneos. Esta situación produce pérdida de datos, errores humanos y resultados científicos difícilmente reproducibles.

**Demeter nace para resolver este problema.** Propone un ecosistema tecnológico completo que automatiza la recolección de variables ambientales mediante sensores, asegura la trazabilidad física de cada sujeto de prueba y facilita el análisis científico avanzado mediante herramientas modernas, accesibles y de bajo coste.

---

## 2. Objetivos del Proyecto

### 2.1 Objetivo General
Desarrollar una plataforma IoT integral que permita monitorizar, controlar y analizar entornos de cultivo, proporcionando trazabilidad científica completa de las plantas y los experimentos asociados.

### 2.2 Objetivos Específicos

**Automatización IoT:**
Desplegar una red de sensores de bajo coste y alta fiabilidad que recolecte variables ambientales (temperatura, humedad, humedad del suelo) de forma continua, sin intervención humana.

**Control Remoto:**
Permitir al investigador o administrador del laboratorio actuar sobre los elementos físicos del entorno (bombas de riego, electroválvulas, sistemas de ventilación) desde cualquier punto con acceso a internet.

**Trazabilidad LIMS:**
Implementar un sistema de gestión de información de laboratorio (LIMS) que mantenga un registro estructurado de cada planta física y los experimentos científicos en los que participa, con total integridad referencial.

**Análisis Científico Avanzado:**
Dotar a los investigadores de herramientas modernas (SDK, gráficas, informes exportables) para extraer y analizar los datos históricos de sus experimentos sin depender del equipo de soporte técnico.

---

## 3. Descripción del Sistema

El sistema Demeter se articula en cuatro módulos interconectados que cubren el ciclo completo desde la adquisición de datos hasta su interpretación científica.

### Módulo A — Capa de Campo (Hardware e IoT)

Es la capa que interactúa directamente con el entorno físico del invernadero.

Los **nodos sensores** son microcontroladores de bajo consumo desplegados en campo, equipados con sensores de temperatura, humedad ambiental y humedad del suelo. Operan de forma autónoma y transmiten sus lecturas a través de una red de radiofrecuencia local, sin necesidad de infraestructura Wi-Fi. Esto garantiza la resiliencia ante cortes de internet y elimina la dependencia de routers externos.

Los **nodos actuadores** reciben comandos desde el sistema central y controlan los elementos activos del invernadero: bombas hidráulicas, electroválvulas de riego y motores de apertura de ventanas.

La comunicación entre nodos y el servidor se realiza a través de un **Nodo Gateway**, que actúa como puente entre la red de radiofrecuencia local y la infraestructura de red del laboratorio, conectándose físicamente a la Raspberry Pi mediante un bus serial.

### Módulo B — Capa de Orquestación (Servidor Central)

Es el cerebro del sistema. Recibe, valida y organiza toda la información procedente del campo.

El **Gestor del Catálogo Biológico** mantiene un registro detallado de cada planta física: su identificador único en el laboratorio, especie y variedad, fecha de siembra, estado vital y cualquier metadato científico específico asociado. Cada planta es, a efectos del sistema, una entidad única e irrepetible.

El **Gestor de Experimentos** permite a los investigadores crear agrupaciones lógicas de plantas para un estudio concreto. Una misma planta puede participar en múltiples experimentos a lo largo de su vida, y el sistema mantiene la traza de cada uno de ellos.

La **Bóveda de Datos** combina una base de datos relacional (para asegurar la integridad de las relaciones entre plantas, experimentos y usuarios) con un sistema de caché de alta velocidad en memoria (para garantizar la disponibilidad inmediata de los datos más recientes).

### Módulo C — Capa Analítica (Herramientas para el Investigador)

Es donde los datos se convierten en ciencia.

El **Motor de Cálculos** es un servicio independiente que opera de forma desacoplada del servidor principal. Se activa periódicamente (típicamente de madrugada, cuando la carga es mínima) para procesar los datos del día anterior. Realiza un pipeline de tres fases: validación de integridad (detección de valores anómalos o perdidos), imputación estadística de datos corruptos y generación de gráficas e informes en formato Excel.

El **SDK Científico** es una librería Python que permite al investigador conectarse a la plataforma desde su entorno de trabajo habitual (Jupyter Notebook, scripts de análisis) y descargar el histórico completo de un experimento en segundos, gracias a un sistema de caché local que evita transferencias redundantes.

### Módulo D — Capa de Interfaz (Panel de Administración y Dashboard)

Es la ventana al sistema para el administrador del laboratorio y los investigadores.

El **Dashboard en Tiempo Real** muestra el estado actual de todos los nodos activos del invernadero, con actualización automática inferior a dos segundos. Las métricas se presentan mediante gráficas de series temporales y paneles de estado visuales.

El **Planificador de Secuencias** permite definir ciclos de riego complejos: qué dispositivos activar, en qué orden y durante cuánto tiempo. Las secuencias pueden guardarse, reutilizarse y ejecutarse bajo demanda o según una programación horaria.

El **LIMS Web** proporciona las interfaces de gestión del catálogo de plantas y los experimentos, incluyendo la exportación de informes a demanda.

---

## 4. Innovación y Valor Diferencial

A diferencia de las soluciones comerciales cerradas y de alto coste, Demeter propone una arquitectura completamente abierta y escalable construida sobre hardware asequible y software de nivel empresarial.

Su principal valor diferencial radica en la **convergencia de tres dominios** que habitualmente existen de forma aislada:
- El control físico del entorno (automatización IoT).
- La gestión formal del sujeto de estudio (LIMS).
- Las herramientas de análisis científico (SDK + Motor de Cálculos).

Además, su diseño modular está preparado para integraciones futuras sin necesidad de rediseñar la arquitectura base: incorporar cámaras con visión artificial para la detección temprana de enfermedades, añadir nuevos tipos de sensores o escalar la red a múltiples invernaderos son extensiones naturales del sistema tal y como está concebido hoy.

---

## 5. Estado Actual del Proyecto

| Módulo | Estado |
|--------|--------|
| Firmware (Nodos Sensor y Actuador) | ✅ Funcional |
| Nodo Gateway y comunicación serial | ✅ Funcional |
| Backend — API REST y WebSockets | ✅ Funcional |
| Base de datos y migraciones | ✅ Funcional |
| Dashboard en tiempo real | ✅ Funcional |
| Planificador de Secuencias | ✅ Funcional |
| LIMS (Plantas y Experimentos) | ✅ Funcional |
| Exportación de Datos (Worker) | 🔄 En desarrollo |
| SDK Científico | 🔄 En desarrollo |
| Motor de Cálculos (Nightly Batch) | 🔄 En desarrollo |

---

## 6. Conclusiones

Demeter es una propuesta técnica y científica que demuestra que es posible construir infraestructura de investigación de calidad profesional con recursos limitados y criterio de ingeniería. El proyecto integra disciplinas que van desde la programación de microcontroladores en C++ hasta el desarrollo de APIs web asíncronas y la gestión de datos científicos, ofreciendo una solución cohesionada donde cada pieza tiene un propósito claro dentro del conjunto.

La documentación técnica detallada de cada subsistema (arquitectura del firmware, diseño de la base de datos, especificación completa de la API) se recoge en los documentos anexos que acompañan a esta memoria.
