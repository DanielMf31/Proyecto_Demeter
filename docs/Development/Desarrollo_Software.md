Desarrollo de Software

1. CI/CD hecho
2. Sensores en Grafana
3. Firmware de sensores reales
    1. Comprar sensores reales y probarlos en ESP32
    2. Enviar datos reales a Gateway y Raspberry Pi
    3. Mostrarlos en Grafana
4. Control de las ventanas
    1. Firmware de control (HECHO)
    2. Planificación de control (Relé Estado Sólido + ESP32)
    3. Documentación y propuesta de implementación real. 

0. Preparar documentación actual de todos los sistemas y asegurarse de que coincide con la realidad. 
1. Diseñar el firmware de un Nodo y sensores de forma modular para poder añadir nuevos sensores cada vez, y poder configurar los sensores que están conectados
    1. Sensor de Humedad Capacitiva
    2. Sensor de Humedad ambiental + temperatura
    3. Sensor de temperatura en tierra
    4. Calidad del aire + CO2.
2. Simular datos y enviarlos por ESP-Now al Gateway y luego a la Raspberry. 
    1. Simular varios sensores con varios datos distintos
    2. Enviarlos por ESP-Now
    3. Recibirlos en la Raspberry Pi y meterlos en base de datos
    4. Organizar datos y logs + Grafana para mostrar varios tipos de sensores
    5. Crear estructura espejo en Python para soportar estos sistemas
3. Controlar la apertura de las ventanas
    1. Activar la apertura de ventanas basado en la humedad y temperatura simulada
    2. Mostrar estado de sensores y de ventanas con Grafana
    3. Pushear códigos y crear versión estable e instalable