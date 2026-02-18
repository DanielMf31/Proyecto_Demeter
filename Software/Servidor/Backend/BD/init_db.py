import asyncio
from Core.database import engine, Base
from BD.models import User, Device, Sequence, SequenceStep, ActivityLog

async def init_tables():
    async with engine.begin() as conn:
        # Check if tables exist or just create all
        # In production use Alembic, but for dev this is fine
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_tables())
