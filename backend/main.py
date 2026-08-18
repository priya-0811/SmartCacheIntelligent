import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.database import init_db
from backend.workers.background_manager import worker_manager

# API Routers
from backend.api.file import router as file_router
from backend.api.cache import router as cache_router
from backend.api.telemetry import router as telemetry_router
from backend.api.predictor import router as predictor_router
from backend.api.benchmark import router as benchmark_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smartcache.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing SmartCache Database Schema...")
    init_db()

    logger.info("Starting Background Workers (Telemetry, Preloader, Cleanup)...")
    worker_manager.start_all()

    yield

    # Shutdown tasks
    logger.info("Stopping SmartCache Background Workers...")
    worker_manager.stop_all()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="An Intelligent In-Memory Predictive Caching Layer with MySQL Metadata Tracking & Markov Preloading",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for Frontend React App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(file_router, prefix=settings.API_PREFIX)
app.include_router(cache_router, prefix=settings.API_PREFIX)
app.include_router(telemetry_router, prefix=settings.API_PREFIX)
app.include_router(predictor_router, prefix=settings.API_PREFIX)
app.include_router(benchmark_router, prefix=settings.API_PREFIX)

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "MySQL" if settings.USE_MYSQL else "SQLite (Fallback)",
        "cache_limit_mb": settings.MAX_CACHE_SIZE_MB,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
