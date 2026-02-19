import asyncio
from Core.database import engine, Base
# Import all models so they are registered in Base.metadata
from BD.models import (
    User, Device, Sequence, SequenceStep, ActivityLog,
    TelemetryTH, PinHistory, SystemHistory
)

async def init_tables():
    async with engine.begin() as conn:
        # Create all tables that don't exist
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_tables())
