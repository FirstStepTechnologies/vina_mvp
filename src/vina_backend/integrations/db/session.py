from typing import Generator
from sqlmodel import Session
from vina_backend.integrations.db.engine import engine

def get_session() -> Generator[Session, None, None]:
    """Provide a database session."""
    with Session(engine) as session:
        yield session
