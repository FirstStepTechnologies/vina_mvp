import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vina_backend.api.routers import (
    health, debug, onboarding, lesson_quizzes, practice, auth, profiles, courses, progress, lessons, assessment
)
from vina_backend.core.config import get_settings
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize database
init_db()

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
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"]) # Auth router has prefix /auth
app.include_router(profiles.router, prefix="/api/v1", tags=["user"]) # Profiles router has prefix /user/profile
app.include_router(courses.router, prefix="/api/v1", tags=["course"])
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
app.include_router(lessons.router, prefix="/api/v1/lessons", tags=["lessons"]) # Overlays with lesson_quizzes
app.include_router(assessment.router, prefix="/api/v1", tags=["assessment"])
app.include_router(lesson_quizzes.router, prefix="/api/v1/lessons", tags=["lessons"])
app.include_router(practice.router, prefix="/api/v1/practice", tags=["practice"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Vina API",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
