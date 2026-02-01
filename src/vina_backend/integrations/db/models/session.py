from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Session(SQLModel, table=True):
    """Database model for user learning sessions."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Selection used for this specific session
    profession: str
    industry: str
    experience_level: str
    
    current_topic_index: int = 0
    
    start_time: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
