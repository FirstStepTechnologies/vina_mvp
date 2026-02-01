from sqlmodel import create_engine, SQLModel
from vina_backend.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False}  # Required for SQLite
)

def init_db():
    """Create database tables."""
    # Importing models here ensures they are registered with SQLModel.metadata
    import vina_backend.integrations.db.models.user
    import vina_backend.integrations.db.models.profile
    import vina_backend.integrations.db.models.session
    import vina_backend.integrations.db.models.quiz_attempt
    
    SQLModel.metadata.create_all(engine)
