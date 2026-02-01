"""
Application configuration using environment variables.
"""
from functools import lru_cache
from typing import Literal, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    env: str = "dev"
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite:///./data/vina.db"
    
    # LLM Configuration
    llm_provider: Literal["anthropic", "openai", "gemini"] = "gemini"
    llm_model: str = "gemini-3-flash"
    llm_reasoning_model: Optional[str] = None
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.3
    
    # Provider-specific API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Text-to-Speech (ElevenLabs)
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    
    # Cloudinary (Video Storage)
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    # Opik (Observability)
    opik_api_key: str = ""
    opik_workspace: str = "vina-hackathon"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
    
    def get_active_api_key(self) -> str:
        """
        Get the API key for the currently configured LLM provider.
        
        Returns:
            API key for active provider
        
        Raises:
            ValueError: If no API key is configured for the active provider
        """
        key_map = {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
        }
        
        api_key = key_map.get(self.llm_provider)
        
        if not api_key:
            raise ValueError(
                f"No API key configured for provider '{self.llm_provider}'. "
                f"Please set {self.llm_provider.upper()}_API_KEY in your .env file."
            )
        
        return api_key


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures we only load settings once.
    """
    return Settings()