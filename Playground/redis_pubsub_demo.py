"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              DEMO: Redis Pub/Sub Asíncrono - Contador de Pulsaciones        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Objetivo: Mostrar cómo funcionan Publish y Subscribe en Redis usando asyncio.

Arquitectura:
  ┌─────────────────────┐        Canal Redis         ┌──────────────────────┐
  │  PUBLISHER (tarea)  │ ──── "demo:contador" ────▶ │ SUBSCRIBER (tarea)   │
  │  Cada 2s publica:   │                            │ Escucha infinita.    │
  │  {counter, presses} │                            │ Imprime al recibir.  │
  └─────────────────────┘                            └──────────────────────┘

Cómo ejecutarlo:
    python redis_pubsub_demo.py

Requisitos:
    pip install redis asyncio

Nota: Asegúrate de tener Redis corriendo (docker o local):
    docker run -d -p 6379:6379 redis:alpine
    -- ó --
    redis-server
"""

import asyncio
import json
import signal
import sys
import redis.asyncio as aioredis

# ─────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────
REDIS_URL     = "redis://localhost:6379"
CANAL         = "demo:contador"          # Canal Pub/Sub
INTERVALO_SEG = 2.0                      # Cada cuántos segundos publica el publisher
MAX_PULSACIONES = 10                     # Simula pulsaciones aleatorias hasta este valor


# ─────────────────────────────────────────────
#  TAREA 1: PUBLISHER
#  Publica un mensaje JSON cada INTERVALO_SEG segundos.
# ─────────────────────────────────────────────
async def publisher(cliente: aioredis.Redis, stop_event: asyncio.Event):
    """
    Simula un productor que cada cierto tiempo publica en el canal Redis.
    El payload es un JSON con:
        - counter  : número de mensaje enviado (1, 2, 3, ...)
        - presses  : número acumulado de "pulsaciones" simuladas
    """
    counter = 0
    presses = 0

    print(f"\n[PUBLISHER] Iniciado. Publicando en canal '{CANAL}' cada {INTERVALO_SEG}s\n")

    while not stop_event.is_set():
        # Incrementar contador de ciclos y simular una pulsación de vez en cuando
        counter += 1

        # Simulamos que en algunos ciclos se "pulsa" un botón
        # En un sistema real esto vendría de tu hardware / endpoint HTTP
        if counter % 3 == 0:     # Cada 3 ciclos se suma una pulsación
            presses += 1

        # Construimos el payload como dict y lo serializamos a JSON string
        payload: dict = {
            "counter": counter,
            "presses": presses,
        }
        mensaje_json: str = json.dumps(payload)

        # ─── PUBLISH ───
        # redis.publish(canal, mensaje) envía el string al canal
        suscriptores = await cliente.publish(CANAL, mensaje_json)

        print(
            f"[PUBLISHER] Ciclo #{counter:>3} | "
            f"Pulsaciones: {presses} | "
            f"Suscriptores que recibieron: {suscriptores}"
        )

        await asyncio.sleep(INTERVALO_SEG)

    print("[PUBLISHER] Detenido.")


# ─────────────────────────────────────────────
#  TAREA 2: SUBSCRIBER
#  Escucha el canal indefinidamente y procesa cada mensaje.
# ─────────────────────────────────────────────
async def subscriber(cliente: aioredis.Redis, stop_event: asyncio.Event):
    """
    Escucha el canal Redis de forma continua.
    Cada vez que llega un mensaje lo deserializa de JSON y lo imprime.
    """

    # IMPORTANTE: El subscriber necesita su PROPIA conexión dedicada.
    # No puede compartir la misma conexión que el publisher porque
    # una conexión en modo SUBSCRIBE solo puede usarse para suscribirse.
    pubsub = cliente.pubsub()

    print(f"[SUBSCRIBER] Suscribiéndose al canal '{CANAL}'...")
    await pubsub.subscribe(CANAL)
    print(f"[SUBSCRIBER] Escuchando. Esperando mensajes...\n")
    print("─" * 60)

    try:
        # pubsub.listen() es un async generator que bloquea hasta recibir algo
        async for mensaje_raw in pubsub.listen():

            # Salir limpiamente si se pidió parar
            if stop_event.is_set():
                break

            # El primer mensaje que llega siempre es de tipo "subscribe" (confirmación)
            # Los mensajes reales son de tipo "message"
            if mensaje_raw["type"] != "message":
                continue

            # ─── DESERIALIZAR JSON ───
            # El dato viene como string; lo convertimos de vuelta a dict
            datos: dict = json.loads(mensaje_raw["data"])

            presses = datos["presses"]
            counter = datos["counter"]

            # Imprimimos lo que nos interesa
            print(
                f"[SUBSCRIBER] 📩 Mensaje recibido | "
                f"Ciclo: {counter} | "
                f"🔘 Número de pulsaciones: {presses}"
            )
            print("─" * 60)

    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(CANAL)
        print("[SUBSCRIBER] Detenido.")


# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────
async def main():
    print("╔══════════════════════════════════════╗")
    print("║  DEMO Redis Pub/Sub  |  Proyecto Demeter  ║")
    print("╚══════════════════════════════════════╝")
    print(f"  Redis URL : {REDIS_URL}")
    print(f"  Canal     : {CANAL}")
    print(f"  Intervalo : {INTERVALO_SEG}s")
    print()

    # Evento para señalizar parada limpia (Ctrl+C)
    stop_event = asyncio.Event()

    # ─── Conectar a Redis ───
    # Usamos dos clientes separados:
    #   - cli_pub: para publish (conexión normal)
    #   - cli_sub: para subscribe (conexión dedicada en modo pub/sub)
    cli_pub = aioredis.from_url(REDIS_URL, decode_responses=True)
    cli_sub = aioredis.from_url(REDIS_URL, decode_responses=True)

    try:
        # Verificar conexión
        await cli_pub.ping()
        print("✅ Conexión a Redis OK\n")
    except Exception as e:
        print(f"❌ No se pudo conectar a Redis: {e}")
        print("   Asegúrate de tener Redis corriendo: docker run -d -p 6379:6379 redis:alpine")
        sys.exit(1)

    # Manejar Ctrl+C para parada limpia
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT,  lambda: stop_event.set())
    loop.add_signal_handler(signal.SIGTERM, lambda: stop_event.set())

    # ─── Lanzar ambas tareas concurrentemente ───
    # asyncio.gather ejecuta publisher y subscriber "a la vez"
    # El subscriber escucha mientras el publisher va publicando
    tarea_pub = asyncio.create_task(publisher(cli_pub, stop_event), name="publisher")
    tarea_sub = asyncio.create_task(subscriber(cli_sub, stop_event), name="subscriber")

    # Esperar hasta que se pida parar (Ctrl+C)
    await stop_event.wait()

    print("\n\n[MAIN] Señal de parada recibida. Cancelando tareas...")

    tarea_pub.cancel()
    tarea_sub.cancel()

    await asyncio.gather(tarea_pub, tarea_sub, return_exceptions=True)

    # Cerrar conexiones
    await cli_pub.aclose()
    await cli_sub.aclose()

    print("[MAIN] Finalizado correctamente. ¡Hasta luego! 👋")


if __name__ == "__main__":
    asyncio.run(main())
