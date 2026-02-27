1. Hardware, Sistema Operativo y Bajo Nivel (El "Cuerpo")
Aquí es donde el software toca el mundo físico.

Tus conceptos: Raspberry PI, Hardware, Firmware, RAM, SSD, CPU, GPU, Aceleración por Hardware, Nucleos, Hilos, Permisos de Linux, Snap.

[NUEVO] GPIO (General Purpose Input/Output): Los pines físicos de la Raspberry Pi. Debes saber explicar que es por donde entran las señales eléctricas de los sensores SHT30 y por donde salen las órdenes a los relés.

[NUEVO] I2C / SPI / UART: Protocolos de comunicación física. El SHT30 usa I2C. Saber esto demuestra que no solo programas, sino que entiendes de electrónica básica.

2. Redes y Protocolos (Las "Venas")
Cómo viaja la información desde el invernadero hasta la nube.

Tus conceptos: Wifi, Ethernet, TCP, HTTP, HTTPS, Websocket, MQTT, Túnel de Cloudflare, SSH.

[NUEVO] Latencia vs. Ancho de Banda: Clave para explicar por qué no envías 50 megas de datos de golpe desde la Raspberry Pi, sino pequeños paquetes JSON en tiempo real.

[NUEVO] DNS / Dominios: Cómo el túnel de Cloudflare asocia tu servidor local con una dirección web legible (api.demeter.org).

3. Backend, Arquitectura y Concurrencia (El "Cerebro")
El núcleo duro de tu servidor.

Tus conceptos: Backend, Servidor, FastAPI, Pydantic, Schemas, Asincronía, Endpoints.

[NUEVO] REST API (Representational State Transfer): Debes saber explicar por qué tu API usa los verbos GET (pedir datos), POST (crear cosas) y no mezcla conceptos.

[NUEVO] Event Loop (Bucle de Eventos): Lo hablamos antes. Es vital para explicar por qué FastAPI no se bloquea esperando a la Raspberry Pi.

[NUEVO] ORM (Object-Relational Mapping): Es lo que hace SQLModel por debajo. Debes explicar que el ORM traduce tu código Python a consultas SQL automáticamente.

4. Bases de Datos y Estado (La "Memoria")
Donde vive la información para siempre (PostgreSQL) o temporalmente (Redis).

Tus conceptos: SQL, NoSQL, SQLModel, JSON, Redis, Colas RQ, Pub/Sub.

[NUEVO] Migraciones (Alembic): Si mañana añades la columna "Humedad del Suelo" a una tabla que ya tiene datos, ¿cómo lo haces sin borrar la base de datos? Las migraciones son la respuesta.

[NUEVO] Transacciones ACID: Saber explicar que en SQL, si una operación falla a la mitad (ej. crear usuario y crear experimento), se deshace entera para no dejar datos corruptos.

5. Frontend y Experiencia de Usuario (La "Cara")
Lo que ve y toca el investigador.

Tus conceptos: Frontend, React, JS, HTML, CSS, TUI (Text User Interface), GUI (Graphical User Interface).

[NUEVO] Estado (State) vs Propiedades (Props): El ABC de React. Cómo fluye la información en el panel de control.

[NUEVO] SPA (Single Page Application): React crea SPAs. La página web nunca se recarga en blanco, solo cambian los componentes inyectando JSONs de la API.

6. Ciencia de Datos y Analítica (El "Valor Real")
El motor que procesa la investigación.

Tus conceptos: Pandas, Numpy, Matplotlib, Seaborn, Dataframe, Curar resultados, Gráficas, Cálculos estadísticos.

[NUEVO] Interpolación y Manejo de NaNs (Nulls): Cómo limpiar los "agujeros" en los datos cuando un sensor se apaga un rato.

[NUEVO] ETL (Extract, Transform, Load): El nombre profesional de lo que hace tu Worker Pesado cada noche a las 3:00 AM.

7. Seguridad y Control de Acceso (El "Escudo")
Vital si manejas datos privados de universidades.

Tus conceptos: Autenticación, Autorización, Token, Claves API, Usuarios.

[NUEVO] CORS (Cross-Origin Resource Sharing): El dolor de cabeza de todo programador web. Es el mecanismo de seguridad que permite que tu web en demeter.com hable con tu API en api.demeter.com.

[NUEVO] Hashing (Bcrypt / SHA256): Explicar por qué NUNCA se guardan contraseñas ni API Keys en texto plano en la base de datos.

[NUEVO] JWT (JSON Web Tokens): El estándar de la industria para los tokens de inicio de sesión que usarás en tu API.

8. Infraestructura y DevOps (La "Fábrica")
Cómo llevas el código desde tu ordenador hasta el mundo real.

Tus conceptos: CI/CD, Docker/Imagen, Docker, Github, Github Actions, Github container, Nginx, PyPI, SDK, VM.

[NUEVO] Docker Compose: La herramienta que orquesta a todos tus contenedores (API, Worker, Secuenciador, Redis, DB) para que arranquen juntos y se hablen entre sí.

[NUEVO] Volúmenes (Docker Volumes): Crucial. Si borras un contenedor Docker, se borra todo su interior. Los volúmenes son la memoria externa que asegura que los datos de PostgreSQL no desaparezcan al actualizar la API.

[NUEVO] Reverse Proxy: Es el trabajo que hace Nginx o Cloudflare. Recibe la petición HTTP del investigador y decide a qué puerto interno del servidor enviarla.

9. Metodología
Tus conceptos: Tests, Desarrollo Agéntico.

[NUEVO] Unit Tests vs Integration Tests: Saber diferenciar entre probar una función matemática aislada (Unit) y probar si el Worker guarda bien el Excel en el disco duro (Integration).