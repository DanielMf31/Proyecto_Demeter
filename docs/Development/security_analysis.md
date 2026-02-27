# Análisis de Seguridad y Plan de Implementación (Proyecto Demeter)

Este documento detalla el estado actual de la seguridad en el Backend del Proyecto Demeter, identifica vulnerabilidades críticas y traza un **Plan de Implementación** para proteger uniformemente las comunicaciones y los comandos enviados al Hardware.

## 1. Estado Actual del Sistema de Autenticación

Actualmente, Demeter implementa un sistema robusto de Autenticación y Autorización basado en tokens **JWT (JSON Web Tokens)** y cifrado de contraseñas mediante **Bcrypt**, alojado íntegramente en `Software/Servidor/Backend/Core/auth.py`.

### 1.1 Entidades y Protocolo
- **Usuarios BD (`BD/models.py`)**: Clase `User` con campos `username`, `password_hash`, `role` (ej: admin, viewer) y `is_active`.
- **Login / Token Exchange (`auth_router.py`)**: El endpoint `POST /api/auth/login` acepta solicitudes formato `OAuth2PasswordRequestForm` estándar y devuelve un `access_token` JWT firmado con codificación `HS256`.
- **Autorización por API Key (`auth.py`)**: Para el SDK de terceros, se dispone del esquema `APIKeyHeader(name="X-API-Key")` que autoriza descargas masivas vinculadas a un `experimento_id`.

## 2. Análisis de Vulnerabilidades Actuales

A través de una auditoría exhaustiva en la capa de Routers de FastAPI (`API/routers/*.py`), he descubierto el siguiente mapa de protección:

| Router | Endpoint Analizado | Nivel de Protección | Riesgo Crítico |
| :--- | :--- | :--- | :--- |
| **History** | `GET /api/history/...` | 🟢 **Protegido** (Usa `get_current_active_user`) | Bajo. Datos históricos solo visibles con token. |
| **Export** | `POST /api/export` | 🟢 **Protegido** (Usa `get_current_active_user`) | Bajo. |
| **Auth** | `GET /api/auth/me` | 🟢 **Protegido** (Valida firma de Token) | Bajo. |
| **System** | `GET /api/system/status` | 🔴 **Público** | Bajo. Información genérica de uptime. |
| **Discovery** | `GET /api/discovery/devices`| 🔴 **Público** | Medio. Permite a cualquiera consultar nombres y pines del Hardware. |
| **Analysis** | `GET /api/analysis/...` | 🔴 **Público** | Medio. Exposición de métricas y cálculos biológicos a terceros. |
| **WS (WebSocket)** | `ws://.../ws/frontend` | 🔴 **Público** | Alto. Un atacante podría suscribirse al bus de eventos y esnifar el tráfico MQTT sin credenciales. |
| **Command** | `POST /api/command` | 🔴 **Público** | **CRÍTICO**. Cualquier cliente HTTP puede encender/apagar una bomba de agua enviando JSON, ya que *no inyecta la Dependencia de OAuth*. |

> [!WARNING]
> La vulnerabilidad más crítica radica en `command_router.py`. Al no tener inyectado `Depends(get_current_active_user)`, **cualquier atacante anónimo** que alcance la IP de la Raspberry puede detonar un actuador (riego, calefactor) puenteando totalmente la pantalla de login del frontend.

---

## 3. Mejoras Recomendadas

### 3.1 Protección Universal de la API (Capa 7 - HTTP)
- Inyectar el requerimiento estricto `Depends(get_current_active_user)` en todos los endpoints HTTP que modifiquen el estado real del mundo (actuadores) o fuguen topología del hardware (`command_router.py`, `discovery_router.py`, `analysis_router.py`, `lims_router.py`).
- Implementar **Role-Based Access Control (RBAC)** en Comandos. A los usuarios con `role="viewer"` se les debería lanzar un HTTP 403 Forbidden si intentan realizar un POST en `/api/command`.

### 3.2 Seguridad en WebSockets de Frontend (`ws_router.py`)
- Los WebSockets no soportan cabeceras de "Autorización" HTTP clásicas en la conexión inicial vía API de Javascript en navegadores modernos. 
- **Mejora:** Exigir que el primer mensaje que envíe el cliente al conectarse al Socket sea un evento tipo `{"action": "authenticate", "token": "JWT_AQUI"}`. Si el backend no recibe esto en menos de X segundos o el JWT caducó, se cierra forzosamente la conexión.

### 3.3 Seguridad en WebSockets de Hardware (`ws://raspberry/ws/gateway`)
- Si hay una Raspberry externa conectándose al servidor de backend, aplicar un token JWT de larga duración estático configurado por variable de entorno (`.env`), evitando depender de que un atacante suplante a la Raspberry Pi subiendo datos falsos.

---

## 4. Plan de Implementación de Seguridad (+ Docstrings)

### Fase 1: Enfortecimiento de Rutas Críticas
- **Paso 1.1:** Modificar `command_router.py`, inyectando `current_user: User = Depends(get_current_active_user)` en la función de control manual de relés.
- **Paso 1.2:** Modificar `discovery_router.py`, inyectando token en la extracción de dispositivos descubiertos.
- **Paso 1.3:** Modificar `analysis_router.py` y `lims_router.py` de igual modo para cerrar brechas de privacidad de los datos agrológicos.

### Fase 2: Control de Roles en Comandos (Opcional pero Recomendado)
- **Paso 2.1:** Extender el código dentro de `post_command()` añadiendo:
  ```python
  if current_user.role != "admin":
      raise HTTPException(status_code=403, detail="Not enough privileges")
  ```

### Fase 3: Securización de WebSockets (WSS)
- **Paso 3.1:** Actualizar código de `ws_router.py`. Validar que el token enviado coincida en la firma.

### Fase 4: Refactorización y Auto-Documentación (Docstrings)
- **Paso 4.1:** Iterar por cada archivo `.py` en `Software/Servidor/Backend/API/routers` y `Software/Servidor/Backend/Core` añadiendo Docstrings estilo PEP-257 completos y unificados a cada clase y función de negocio.
- **Paso 4.2:** Asegurarse de que en `main.py` de Secuenciador y en la subcarpeta `Analisis_datos/` contengan explicaciones completas de su complejidad (especialmente scripts matemáticos de cálculo de VDP y GDD).
