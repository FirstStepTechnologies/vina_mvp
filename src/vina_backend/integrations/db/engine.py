from sqlmodel import create_engine, SQLModel, Session
from vina_backend.core.config import get_settings

settings = get_settings()

# Configure connection args based on database type
# SQLite needs check_same_thread=False for FastAPI async support
# PostgreSQL doesn't support this parameter
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL debugging
    connect_args=connect_args
)

def init_db():
    """Create database tables."""
    # Importing models here ensures they are registered with SQLModel.metadata
    import vina_backend.integrations.db.models.user
    import vina_backend.integrations.db.models.profile
    import vina_backend.integrations.db.models.session
    import vina_backend.integrations.db.models.quiz_attempt
    from vina_backend.services.lesson_cache import LessonCache  # Import cache model
    
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Get a database session with automatic cleanup.
    Use as a generator in a with statement or next().
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
