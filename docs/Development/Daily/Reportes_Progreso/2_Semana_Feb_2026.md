# Reporte de Progreso - [Fecha: 11/02/2026]

**Autor:** Daniel Montero Fernández
**Semana:** 2
**Estado General:** A tiempo

---

## 1. Resumen Ejecutivo

1. Inicio de etapa de Pruebas de Software y Firmware
    2. Diseño, Implementación y Pruebas de la Arquitectura de Software (Python/Raspberry Pi) y Firmware (ESP32)
    3. Pruebas unitarias funcionales
    4. Planificación de Despliegue en entorno de Pruebas (Aula de Asociaciones ETSI) para la próxima (3) semana.
2. Vuelta desarrollo conjunto del Proyecto
    1. Dirección organizada por parte de Dani
    2. Reparto de tareas
        1. Miguel Antonio (Riego)
        2. Dani (Software)
        3. Rod (Electrónica)
        4. Pablete/Chema (Eléctrica/Electrónica)
    3. Diseño de Cronograma oficial de Trabajo
        1. Febrero: Despliegue en entorno de Pruebas (Aula de Asociaciones ETSI)
        2. Marzo: Estudio Despliegue en entorno Real (Invernadero)
        3. Abril: NO PLANIFICADO
        4. Mayo: NO PLANIFICADO
        5. Junio: NO PLANIFICADO
---

## 2. Detalle por Categoría

### 1. Software
* **Actividades Realizadas:**
    * [ ] Arquitectura de Software (Python/Raspberry Pi)
        1. Diseño Protocolo Comunicación Binario Universal y Multiplataforma (ProtocoloDemeter)
        2. Módulo de comunicación UART asíncrono
        3. Módulo de serialización y deserialización de mensajes
        4. Módulo de gestión de estados y daemon orquestador
        5. Módulo de loggeo en terminal y en log propio
        6. Módulo de persistencia de datos en Base de Datos SQLite
        7. Módulo de interfaz gráfica para control de Hardware en Pantalla táctil
        8. Implementación de Test unitarios y de integración
        9. Integraciones de test entorno real con Mocks para verificar lógica dentro de Python sin depender de Hardware real

    * [ ] Arquitectura de Firmware (ESP32)
        1. Implementación de ProtocoloDemeter en ESP32
        2. Sistema de Actuador Hardware
        3. Sistema de Comunicación Hardware (ESP-Now/UART)
        4. Implementación de Interfaces de Clases
            1. Implementación de Interfaz de Comunicación
            2. Implementación de Interfaz de Actuador
            3. Implementación de Interfaz de Sensor
        5. Implementación de Nodos como Clases
            1. Nodo Actuador
            2. Nodo Sensor
            3. Nodo Gateway
        6. Implementación de tests unitarios
        7. Integraciones de test entorno real con Mocks para verificar lógica dentro de ESP32 sin depender de Hardware real
        8. Control de Firmware mediante comandos en monitor Serial.

    * [ ] DevOps
        1. Configuración de Entorno de Desarrollo
            1. Instalación de PlatformIO
            2. Verificación funcionamiento en sistemas reales
        2. Implementación CI/CD mediante Workflows de Github/Action
            1. Tests automáticos Backend Python
            2. Tests automáticos Firmware ESP32
            3. Workflow de despliegue mediante creación de Imágen de Docker
        3. Subida de código a Repositorio de Github
            1. Creación de ramas main/develop
            2. Ramas aisladas para desarrollo de funcionalidad
    
    * [ ] Documentación
        1. Creación de Documentación. Separada en
            1. Arquitecture: Arquitectura real del sistema ya implementada en desarrollo y verificada mediante pruebas unitarias, integración y prueba en hardware real.
            2. Design: Diseño de nuevas funcionalidades e ideas no implementadas al 100%
            3. Manuals: Manuales de usuario y técnicos
            4. Development: Documentación de trabajo de Desarrollo de Software, Gestión del proyecto y Planificación General.
            5. Knowledge: Preguntas de conceptos e imágenes para visualización de conceptos
        

* **Cambios Implementados:**
    * [ ] Ninguno
* **Proyecciones a Futuro:**
    * [ ] Continuación del Desarrollo siguiendo Prácticas Profesionales y buena Organización General
* **Planificación Temporal:**
    * [ ] **Despliegue en entorno de Pruebas:** Despliegue real en el Aula de Asociaciones para probar los sistemas por usuarios reales y ayudar a las pruebas de Riego - **Fecha Estimada:** 18/02/2026

### 2. Electrónica
* **Actividades Realizadas:**
    * [ ] POR PLANIFICAR
* **Cambios Implementados:**
    * [ ] [Modificaciones en esquemáticos o selección de componentes]
* **Proyecciones a Futuro:**
    * [ ] [Fabricación, compras o integración]
* **Planificación Temporal:**
    * [ ] **Hito:** [Descripción] - **Fecha Estimada:** [DD/MM]

### 3. Riego
* **Actividades Realizadas:**
    * [ ] LISTA DE TAREAS ENTREGADA A MIGUEL ANTONIO. SE AÑADIRÁ A LA DOCUMENTACIÓN OFICIAL EN BREVE
* **Proyecciones a Futuro:**
    * [ ] [Expansión de zonas o mantenimiento]
* **Planificación Temporal:**
    * [ ] **Hito:** [Descripción] - **Fecha Estimada:** [DD/MM]

### 4. Eléctrica
* **Actividades Realizadas:**
    * [ ] POR PLANIFICAR
* **Cambios Implementados:**
    * [ ] [Mejoras en seguridad o distribución de carga]
* **Proyecciones a Futuro:**
    * [ ] [Finalización de cuadros o certificaciones]
* **Planificación Temporal:**
    * [ ] **Hito:** [Descripción] - **Fecha Estimada:** [DD/MM]

### 5. Documentación
* **Actividades Realizadas:**
    * [ ] POR PLANIFICAR **Fecha Estimada:** [DD/MM]

### 6. Comunicación con la ETSIA
* **Actividades Realizadas:**
    * [ ] Aviso continuación de desarrollo a la ETSIA
    * [ ] Reunión con Alvarado para hablar de los últios desarrollos.
* **Cambios Implementados:**
    * [ ] [Acuerdos alcanzados o feedback incorporado]
* **Proyecciones a Futuro:**
    * [ ] [Próximas reuniones o hitos académicos]
* **Planificación Temporal:**
    * [ ] **Hito:** [Descripción] - **Fecha Estimada:** [DD/MM]

---

## 3. Bloqueos y Riesgos Identificados


## 4. Próximos Pasos Inmediatos (Para la siguiente semana)
1. [ ] Reunión Jueves/Viernes 2 Semana para discusión en detalle de la Organización del Trabajo

