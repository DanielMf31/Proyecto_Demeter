# JWT & OAuth2 Authentication Architecture

Este documento detalla el mecanismo de autenticación implementado en el backend de Demeter, usando JSON Web Tokens (JWT) y el flujo OAuth2 Password Bearer.

## 1. OAuth2 Password Bearer
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
```
Esta dependencia indica que la API está protegida por un sistema de Token "Bearer" (Portador).
- El cliente debe enviar una cabecera HTTP en cada petición: `Authorization: Bearer <TOKEN>`.
- `tokenUrl` informa a FastAPI y a Swagger UI dónde generar este token. En Swagger, esto habilita el botón "Authorize", permitiendo realizar peticiones autenticadas desde la interfaz.

## 2. JSON Web Tokens (JWT)
Un JWT tiene tres partes (Header, Payload, Signature).
- **Header:** Tipo de token y algoritmo de firma (`HS256`).
- **Payload:** Datos del usuario (por ejemplo `{"sub": "admin"}`) y fecha de expiración (`exp`).
- **Signature (Firma):** Se genera mediante una función criptográfica combinando el Header, Payload y un `SECRET_KEY` almacenado solo en el servidor.

**Seguridad del JWT:**
El JWT no está encriptado (se puede decodificar de Base64 fácilmente), pero está **firmado digitalmente**. Si un atacante altera el payload (ej. cambiando su rol a "superadmin"), la validación criptográfica en el servidor fallará porque la nueva combinación de datos no coincidirá con la firma generada por el `SECRET_KEY`.

## 3. Inyección de Dependencias y Validación (current_user)
Rutas protegidas inyectan dependencias como `Depends(get_current_active_user)`.
El ciclo de vida de la validación es:

1. **Interceptar Petición:** FastAPI detecta el encabezado `Authorization`. Si falta o es erróneo, devuelve automáticamente `401 Unauthorized`.
2. **Verificar el Token:** La librería decodifica el token usando el `SECRET_KEY`. Verifica de forma automática que la firma sea válida y que el token no haya caducado (fecha `exp`).
3. **Buscar al Usuario en Base de Datos:** Se extrae el `username` del token y se busca en PostgreSQL. Si no existe, se rechaza la petición.
4. **Verificación de Estado Activo:** `get_current_active_user` añade una verificación final para asegurarse de que el usuario tenga `is_active = True`, bloqueando accesos de usuarios dados de baja preventivamente.

## 4. Hashing de Contraseñas (Bcrypt)
Se emplea `bcrypt` para evitar guardar contraseñas en texto plano:
- **Al crear usuario:** `bcrypt` aplica un "salting" (basura aleatoria) y un hashing matemático en cascada que convierte la contraseña (ej. "hola123") en una cadena ilegible y unidireccional.
- **Al iniciar sesión:** Cuando el usuario envía de nuevo "hola123", se le vuelve a aplicar el algoritmo y se compara el hash resultante con el hash de la base de datos de manera segura contra ataques de sincronización (timing attacks) usando `bcrypt.checkpw`.

Este ciclo garantiza un pipeline estandarizado: **Criptografía (Bcrypt) -> Firma (JWT) -> Verdad Categórica (BD)**.
