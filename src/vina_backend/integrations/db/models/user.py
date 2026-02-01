from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """Database model for users."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, index=True)
    
    # Preferred professional info (to default new courses)
    profession: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
