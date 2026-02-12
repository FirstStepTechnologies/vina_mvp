"""
Application configuration using environment variables.
"""
from functools import lru_cache
from typing import Literal, Optional, Tuple, Type
from pathlib import Path
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

# Calculate DB Path at module level
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_db_path = _project_root / "data" / "vina.db"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    env: str
    log_level: str
    
    # Database
    database_url: str = f"sqlite:///{_db_path}"
    
    # LLM Configuration
    llm_provider: Literal["anthropic", "openai", "gemini"]
    llm_model: str
    llm_reasoning_model: Optional[str] = None
    llm_max_tokens: int
    llm_temperature: float
    
    # Provider-specific API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Text-to-Speech (ElevenLabs)
    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    elevenlabs_model: str
    
    # Cloudinary (Video Storage)
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
    # Opik (Observability)
    opik_api_key: str
    opik_workspace: str
    
    # Auth
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
    
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