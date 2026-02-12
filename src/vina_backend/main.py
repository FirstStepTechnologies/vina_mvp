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

# --- AUTO MIGRATION FOR PRODUCTION ---
def _ensure_schema_migrations():
    """
    Hack to ensure new columns exist in production SQLite without full Alembic setup.
    Runs on startup.
    """
    import sqlite3
    from vina_backend.core.config import get_settings
    
    settings = get_settings()
    db_url = settings.database_url
    
    if "sqlite" not in db_url:
        return
        
    try:
        # Extract path
        db_path = db_url.replace("sqlite:///", "")
        if db_path.startswith("/"):
             pass 
             
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check lesson_cache
        cursor.execute("PRAGMA table_info(lesson_cache)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations = [
            ("video_url", "TEXT"),
            ("adaptation_context", "TEXT")
        ]
        
        for col, col_type in migrations:
            if col not in columns:
                logger.info(f"Adding missing column to lesson_cache: {col}")
                cursor.execute(f"ALTER TABLE lesson_cache ADD COLUMN {col} {col_type}")
                
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Auto-migration failed (might be harmless if DB valid): {e}")

_ensure_schema_migrations()
# -------------------------------------

settings = get_settings()

app = FastAPI(
    title="Vina API",
    description="Backend API for Vina - Personalized Learning Platform",
    version="0.1.0",
)

# Set all CORS enabled origins
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for Hackathon/Demo to prevent any CORS issues
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
app.include_router(lesson_quizzes.router, prefix="/api/v1", tags=["lessons"])
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
