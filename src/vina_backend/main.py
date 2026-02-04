import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vina_backend.api.routers import health, debug
from vina_backend.core.config import get_settings
from vina_backend.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Vina API",
    description="Backend API for Vina - Personalized Learning Platform",
    version="0.1.0",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["General"])
app.include_router(debug.router, prefix="/api/v1/debug", tags=["Debug"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Vina API",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
