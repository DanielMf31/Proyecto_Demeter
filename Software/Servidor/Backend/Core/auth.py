import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# We'll need the settings explicitly or just directly define
from Core.config import get_settings
from BD.models import User, Experiment
from Core.database import get_db

settings = get_settings()

SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7) # 7 days default

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña en plano contra el Hash almacenado en Base de Datos.
    Utiliza bcrypt.checkpw que prevé ataques de sincronización (timing-attacks).
    
    :param plain_password: La contraseña enviada por el usuario en el Login.
    :param hashed_password: El Hash cifrado guardado previamente.
    :return: True si coincide, False en caso contrario.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Aplica hashing robusto (Bcrypt con subsalting) a una contraseña limpia.
    
    :param password: Contraseña a encriptar.
    :return: String del hash en base64 listo para guardar en BBDD.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Genera un JSON Web Token (JWT) firmado de seguridad.
    
    :param data: El payload (típicamente {"sub": "username"}).
    :param expires_delta: Tiempo de validez del token en timedelta (default = 15m o ENV setting).
    :return: Token en formato string listo para enviarse al cliente vía Bearer.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Dependencia Core de FastAPI.
    Extrae el JWT Bearer de la petición HTTP, verifica la firma criptográfica, corrobora
    la expiración y luego busca el objeto User real en la Base de Datos.
    
    :param token: JWT Token inyectado por FastAPI vía Header.
    :param db: Sesión asíncrona inyectada a la BD para validar existencia del usuario.
    :raises HTTPException 401: Si el token está adulterado, caducado, o el usuario fue borrado.
    :return: Objeto usuario completo (BBDD Model).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Dependencia estricta de FastAPI que encapsula `get_current_user`.
    Añade una validación extra para impedir login de usuarios con estado is_active=False 
    (por ejemplo, ex-empleados dados de baja).
    
    :return: Objeto usuario verificado y activo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ── API Key Security for SDK ──────────────────────────────────────────────────
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key_or_403(
    experimento_id: int,
    api_key_header: str = Depends(api_key_header_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates that the provided X-API-Key header matches the given experimento_id.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Missing X-API-Key in headers required for SDK access."
        )
        
    result = await db.execute(select(Experiment).where(Experiment.id == experimento_id))
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    if experiment.api_key != api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid API Key for this experiment."
        )
        
    return experiment
