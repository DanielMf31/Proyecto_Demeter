import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from BD.models import User
from Core.auth import get_password_hash

logger = logging.getLogger("startup")

async def create_default_admin(db: AsyncSession):
    """
    Arranca en el on_startup() system. Comprueba si la BD está limpia (sin admins).
    Si está vacía, crea un superusuario "admin" predeterminado para permitir 
    los primeros arranques del Dashboard sin tener que lanzar comandos manuales shell.
    
    :param db: Sesión ASYNC inyectada en el arranque de la app.py.
    """
    try:
        result = await db.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            logger.info("Default admin user already exists.")
            return

        logger.info("Creating default admin user...")
        hashed_password = get_password_hash("admin")
        db_admin = User(
            username="admin",
            password_hash=hashed_password,
            role="admin",
            is_active=True
        )
        
        db.add(db_admin)
        await db.commit()
        logger.info("Default admin user created successfully.")
    except Exception as e:
        logger.error(f"Error creating default admin user: {e}")
        await db.rollback()
