# Arquitectura de Enrutamiento: Redis vs. Directo

Este documento explica cómo fluyen los mensajes en el sistema Demeter, diferenciando entre el método estandar (Redis) y el método optimizado (Directo).

## 1. Enrutamiento Estándar con Redis (Pub/Sub)

En una arquitectura de microservicios escalable, es común tener múltiples instancias del Backend ejecutándose para soportar miles de conexiones. En este escenario, el Frontend podría estar conectado a la `Instancia A` y la Raspberry Pi a la `Instancia B`.

Sin un intermediario, la `Instancia A` no tendría forma de enviar un mensaje a la Raspberry Pi conectada a la `B`. Aquí entra **Redis Pub/Sub**.

### Flujo de Datos:
1.  **Frontend** envía comando a `Backend (Instancia A)`.
2.  `Backend A` no sabe dónde está la Raspberry.
3.  `Backend A` **publica** el mensaje en un canal de Redis (ej: `demeter:commands`).
4.  **Todas** las instancias del Backend (`A`, `B`, `C`...) están suscritas a este canal.
5.  `Backend B` recibe el mensaje desde Redis.
6.  `Backend B` verifica: "¿Tengo yo a la Raspberry Pi conectada?".
7.  **SÍ**: `Backend B` envía el mensaje por WebSocket a la Raspberry.
8.  **NO**: `Backend B` ignora el mensaje.

![Redis Flow](https://mermaid.ink/img/pako:eNpVkMtqwzAQRX9FzKqF_IAdsyl0Uyi0XSmdtBcjS4wlbAlJMnZK_r1yHCSB3szcO3NnHsgqM8hYsq_K1sFp9aM8W8n_PC_WvF6_ijVn81d2WvJqKw8H9gR2-wN7eX0lT_cf5AO_wA-QIAFJoAE0aAEdWkCHEMghARUkIQNlkIICSkghgwoyqKGCGlLIoYYaGmihgx4G6GGAAUYYoYcxJphhhgVmmGGBAxbfYIMdDjjhhDMcd8IVrnjDEx6xxzu-4skC3y8XfLvcyM/Llev1ym_LhR_XG_m93Miv6538ut7J7-uD_Hk9yJ83kF8_Qf4CxcxWQA?type=png)

> **Ventaja 1:** Permite escalar a infinitos servidores.
> **Ventaja 2:** Desacopla completamente los servicios.

---

## 2. Enrutamiento Directo (Local Bridge)

Para despliegues simplificados (como el actual en un solo Docker o servidor), el Frontend y la Raspberry Pi se conectan a la **misma instancia** del Backend. Redis es innecesario aquí.

### Flujo Actual (Optimizado):
1.  **Frontend** envía comando a `Backend`.
2.  `Backend` verifica en su propia memoria (`manager.active_connections`).
3.  Busca el cliente con ID estandarizado `raspberry_gateway`.
4.  **Si lo encuentra**: Le envía el mensaje directamente (`await websocket.send_json`).
5.  **Si NO lo encuentra**: Intenta usar Redis (fallback) o devuelve error.

Este método es el que hemos activado para asegurar que tu sistema funcione sin depender de contenedores adicionales si no deseas usar Redis aún.
