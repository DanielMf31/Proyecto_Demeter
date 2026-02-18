from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Core.config import get_settings
from Core.logger import setup_logger

# Import Routers
from API.routers import system
from WS_Manager import router as ws_router

settings = get_settings()
logger = setup_logger("app")

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
    )

    # Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Adjust in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Data Base Events (Optional: Connect/Disconnect)
    @application.on_event("startup")
    async def startup_event():
        logger.info("Application starting up...")
        from Core.redis import redis_manager
        # Attempt connection, but don't block app startup on failure
        try:
            await redis_manager.connect()
        except Exception as e:
            logger.warning(f"Redis Connection Warning: {e}")

    @application.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutting down...")
        from Core.redis import redis_manager
        await redis_manager.close()

    # Include Routers
    application.include_router(system.router, prefix=f"{settings.API_PREFIX}/system", tags=["System"])
    application.include_router(ws_router.router, tags=["WebSocket"])

    return application

app = create_application()

@app.get("/")
async def root():
    return {"message": "Welcome to Proyecto Demeter Backend", "docs": settings.API_PREFIX + "/docs"}
