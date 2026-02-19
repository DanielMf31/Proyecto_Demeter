from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Core.database import get_db

router = APIRouter()

@router.get("/status")
async def get_system_status():
    return {"status": "operational", "service": "Proyecto Demeter API"}

@router.get("/db-check")
async def check_database(db: AsyncSession = Depends(get_db)):
    # Simple check to see if we can get a session
    return {"status": "connected", "database": "responsive"}
