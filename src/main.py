from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.cache import get_redis_pool, close_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Initialize Redis pool
    await get_redis_pool()
    print("Redis connection pool initialized")

    yield

    # Shutdown: Close Redis pool
    await close_redis_pool()
    print("Redis connection pool closed")


app = FastAPI(
    title="SciSciNet Backend API",
    description="Data visualization API for SciSciNet POC",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "SciSciNet Backend API"}
