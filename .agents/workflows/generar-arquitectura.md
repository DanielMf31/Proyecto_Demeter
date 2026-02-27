---
description: Pipeline de Documentación Automática (Compila todos los diagramas fuente -> SVG)
---
Este flujo de trabajo se encarga de recorrer la carpeta de Arquitectura y generar versiones SVG de alta calidad en base a los archivos fuente declarativos, estandarizando la visualización para el sistema documental.

// turbo-all

1. Compila el Entidad-Relación de BD (DBML) descargando temporalmente el motor via NodeJS.
`npx --yes @softwaretechnik/dbml-renderer -i docs/Architecture/diagrama_bd.dbml -o docs/Architecture/diagrama_bd.svg`

2. Compila el diagrama Arquitectónico de Contexto C4 (Nivel 1).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_context.d2 docs/Architecture/c4_context.svg`

3. Compila el diagrama Arquitectónico de Contenedores C4 (Nivel 2).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_containers.d2 docs/Architecture/c4_containers.svg`

4. Compila el diagrama Arquitectónico de Componentes C4 (Nivel 3).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_components.d2 docs/Architecture/c4_components.svg`

5. Compila el diagrama Arquitectónico de Componentes C4 de Raspberry Pi (Nivel 3).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_components_rpi.d2 docs/Architecture/c4_components_rpi.svg`

6. Compila el diagrama Arquitectónico de Contenedores de Nodos ESP32 (Nivel 2).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_containers_esp32.d2 docs/Architecture/c4_containers_esp32.svg`

7. Compila el diagrama Arquitectónico de Componentes C4 de Gateway ESP32 (Nivel 3).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_components_esp32_gateway.d2 docs/Architecture/c4_components_esp32_gateway.svg`

8. Compila el diagrama Arquitectónico de Componentes C4 de Nodo Sensor ESP32 (Nivel 3).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_components_esp32_sensor.d2 docs/Architecture/c4_components_esp32_sensor.svg`

9. Compila el diagrama Arquitectónico de Componentes C4 de Nodo Actuador ESP32 (Nivel 3).
`~/.local/bin/d2 --theme 3 docs/Architecture/c4_components_esp32_actuator.d2 docs/Architecture/c4_components_esp32_actuator.svg`
