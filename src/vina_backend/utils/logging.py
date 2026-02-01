import logging
import sys
from typing import Optional

from vina_backend.core.config import get_settings

def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure global logging settings for the application.
    
    Args:
        level: Optional log level override. Defaults to value in settings.
    """
    settings = get_settings()
    log_level = level or settings.log_level
    
    # Map string level to logging constants
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set levels for noisy libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized at level: {log_level}")
