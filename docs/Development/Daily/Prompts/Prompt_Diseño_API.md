Rol: Actúa como un Arquitecto de Software y Desarrollador Backend Senior experto en la creación de APIs mixtas (REST + WebSockets) orientadas a IoT.

Contexto del Proyecto:
Necesito diseñar y estructurar el backend para un sistema IoT. El actor principal es una Raspberry Pi que se conectará al servidor de forma persistente a través de un endpoint de WebSocket para enviar telemetría en tiempo real y recibir comandos. Además, necesito una API REST tradicional para gestionar el resto de requerimientos (usuarios, configuración, consultas de datos desde un frontend, etc.).

Stack Tecnológico preferido: [AQUÍ PON TU PREFERENCIA: Ej. Node.js con Express y Socket.io / Python con FastAPI / Go]

Requerimientos Core a diseñar:

Conexión WebSocket (Raspberry Pi):

Endpoint dedicado para la conexión de la Raspberry.

Sistema básico de autenticación/handshake al conectar el socket.

Gestión de desconexiones, reconexiones automáticas y "ping/pong" (keep-alive).

API REST:

Endpoints básicos de ejemplo para operaciones CRUD que interactúen con el mismo estado o base de datos que usa el WebSocket.

Estructura de Routing (Crucial):

Quiero una separación de responsabilidades estricta. Necesito ver cómo modularizar el enrutamiento (rutas REST separadas de los manejadores de eventos del WebSocket).

Uso de Controladores y Servicios (las rutas no deben contener lógica de negocio).

Entregables que necesito de ti:

Estructura de Directorios: Un árbol en formato texto explicando qué hace cada carpeta y archivo (rutas, controladores, servicios, sockets, middleware).

Código de Inicialización (App/Server): El archivo principal (ej. server.js o main.py) donde coexisten el servidor HTTP y el servidor WebSocket compartiendo el mismo puerto.

Ejemplo de Routing REST: Un archivo de ruta básico delegando a un controlador.

Ejemplo de Manejador WebSocket: Cómo aislar los eventos del socket en su propio archivo/módulo para que no ensucie el servidor principal.

Interacción: Un breve ejemplo de cómo un endpoint REST (ej. POST /api/comando) puede emitir un evento a través del WebSocket conectado hacia la Raspberry.

Por favor, escribe código limpio, comentado, modular y preparado para escalar.