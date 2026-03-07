"""
app.py — Punto de entrada principal (Entrypoint) de la API Demeter Backend.

Orquesta la inicialización de FastAPI, configuración CORS, inicialización de 
Alembic/PostgreSQL, siembra de datos de prueba y registro de todos los 
routers (Endpoints). También dispara los listeners en background de Redis.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Core.config import get_settings
from Core.logger import setup_logger

# ── Routers ───────────────────────────────────────────────────────────────────
from API.routers.system_router import router as system_router
from API.routers.ws_router import router as ws_router
from API.routers.command_router import router as command_router
from API.routers.discovery_router import router as discovery_router
from API.routers.analysis_router import router as analysis_router
from API.routers.auth_router import router as auth_router
from API.routers.export_router import router as export_router
from API.routers.sdk_router import router as sdk_router
from API.routers.lims_router import router as lims_router
from WS_Manager.dispatcher import start_redis_listener, start_activity_batch_flusher
from BD.init_db import init_tables
from Core.startup import create_default_admin
from BD.seed_data import seed_historical_data

settings = get_settings()
logger = setup_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up…")
    
    # 1. Database is now managed by Alembic
    logger.info("Database schema is managed by Alembic. Waiting for warmup...")
    try:
        # Short sleep to let Postgres warm up in Docker
        await asyncio.sleep(2) 
        # await init_tables() # Disabled! Alembic manages this now
    except Exception as e:
        logger.error(f"Database Warmup Error: {e}")
        # We don't exit here to allow the app to try to run, 
        # but functionality will be limited.

    # 2. Add Default Admin User & Seed Test Data
    from Core.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as session:
            await create_default_admin(session)
            await seed_historical_data(session)
    except Exception as e:
        logger.error(f"Error creating default admin or seeding data: {e}")

    # 3. Connect to Redis
    from Core.redis import redis_manager
    try:
        await redis_manager.connect()
    except Exception as e:
        logger.warning(f"Redis Connection Warning: {e}")

    # 3. Launch background tasks
    asyncio.create_task(start_redis_listener())
    asyncio.create_task(start_activity_batch_flusher())
    logger.info("Dispatcher and Batch Flusher tasks launched.")

    yield

    logger.info("Application shutting down…")
    await redis_manager.close()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    # ── Register all routers ──────────────────────────────────────────────────
    application.include_router(
        system_router,
        prefix=f"{settings.API_PREFIX}/system",
        tags=["System"],
    )
    application.include_router(
        ws_router,
        tags=["WebSocket"],
    )
    application.include_router(
        command_router,
        prefix=f"{settings.API_PREFIX}",
        tags=["Commands"],
    )
    application.include_router(
        discovery_router,
        prefix=f"{settings.API_PREFIX}",
        tags=["Discovery"],
    )
    application.include_router(
        analysis_router,
        prefix=f"{settings.API_PREFIX}/analysis",
        tags=["Analytics"],
    )
    application.include_router(
        auth_router,
        prefix=f"{settings.API_PREFIX}",
    )
    application.include_router(
        export_router,
        prefix=f"{settings.API_PREFIX}",
    )
    
    from API.routers.history_router import router as history_router
    application.include_router(
        history_router,
        prefix=f"{settings.API_PREFIX}",
    )
    application.include_router(
        sdk_router,
        prefix=f"{settings.API_PREFIX}",
    )
    application.include_router(
        lims_router,
        prefix=f"{settings.API_PREFIX}",
    )

    return application


app = create_application()


@app.get("/")
async def root():
    return {
        "message": "Welcome to Proyecto Demeter Backend",
        "docs": settings.API_PREFIX + "/docs",
    }
