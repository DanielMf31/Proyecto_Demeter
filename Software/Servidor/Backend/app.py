import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Core.config import get_settings
from Core.logger import setup_logger

# ── Routers ───────────────────────────────────────────────────────────────────
from API.routers.system_router import router as system_router
from API.routers.ws_router import router as ws_router
from API.routers.command_router import router as command_router
from API.routers.discovery_router import router as discovery_router
from WS_Manager.dispatcher import start_redis_listener, start_activity_batch_flusher
from BD.init_db import init_tables

settings = get_settings()
logger = setup_logger("app")


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.on_event("startup")
    async def startup_event():
        logger.info("Application starting up…")
        
        # 1. Initialize Database Tables
        logger.info("Initializing database tables…")
        try:
            # Short sleep to let Postgres warm up in Docker
            await asyncio.sleep(2) 
            await init_tables()
        except Exception as e:
            logger.error(f"Database Initialization Error: {e}")
            # We don't exit here to allow the app to try to run, 
            # but functionality will be limited.

        # 2. Connect to Redis
        from Core.redis import redis_manager
        try:
            await redis_manager.connect()
        except Exception as e:
            logger.warning(f"Redis Connection Warning: {e}")

        # 3. Launch background tasks
        asyncio.create_task(start_redis_listener())
        asyncio.create_task(start_activity_batch_flusher())
        logger.info("Dispatcher and Batch Flusher tasks launched.")

    @application.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutting down…")
        from Core.redis import redis_manager
        await redis_manager.close()

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

    return application


app = create_application()


@app.get("/")
async def root():
    return {
        "message": "Welcome to Proyecto Demeter Backend",
        "docs": settings.API_PREFIX + "/docs",
    }
