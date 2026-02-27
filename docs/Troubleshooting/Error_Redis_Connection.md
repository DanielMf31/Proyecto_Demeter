# Error de Conexión a Redis

## El Problema
El log muestra:
```
redis.exceptions.ConnectionError: Error -3 connecting to redis:6379. Temporary failure in name resolution.
```

## ¿Por qué ocurre?
1.  **Configuración:** El Backend está configurado para intentar conectarse a un servidor Redis (por defecto `redis://redis:6379`).
2.  **Docker:** En tu archivo `docker-compose.server.yml`, **comentamos** el servicio de Redis para simplificar el despliegue.
3.  **Resultado:** Al arrancar, el Backend intenta buscar el host llamado "redis", no lo encuentra en la red Docker, y falla con "name resolution failure".

## Solución
Como nuestro objetivo era usar el **Enrutamiento Directo** (sin depender de Redis obligatoriamente), debemos modificar el código del Backend para que la conexión a Redis sea **opcional**.

Si Redis falla al iniciar:
*   El sistema debe mostrar una advertencia (WARNING).
*   El sistema **debe continuar arrancando**.
*   Simplemente no funcionará el modo "Escalado", pero el modo "Directo" (Raspberry <-> Backend) funcionará perfectamente.

## Pasos para arreglarlo
Modificaré `Software/Servidor/Backend/Core/redis.py` para capturar la excepción de conexión y permitir que la aplicación arranque sin Redis.
