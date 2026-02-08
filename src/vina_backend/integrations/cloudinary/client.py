import logging
from pathlib import Path
from typing import Optional, Dict, Any
import cloudinary
import cloudinary.uploader
import cloudinary.api
from tenacity import retry, stop_after_attempt, wait_exponential

from vina_backend.core.config import get_settings

logger = logging.getLogger(__name__)

class CloudinaryClient:
    """
    Client for interacting with Cloudinary API for video hosting.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._configure()
        
    def _configure(self):
        """Configure Cloudinary using settings."""
        if not self.settings.cloudinary_cloud_name:
            logger.warning("Cloudinary not configured (missing CLOUDINARY_CLOUD_NAME)")
            return
            
        cloudinary.config(
            cloud_name=self.settings.cloudinary_cloud_name,
            api_key=self.settings.cloudinary_api_key,
            api_secret=self.settings.cloudinary_api_secret,
            secure=True
        )
        logger.info("Cloudinary client configured")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def upload_video(self, file_path: Path, public_id: Optional[str] = None, folder: str = "vina_lessons") -> str:
        """
        Upload a video file to Cloudinary.
        
        Args:
            file_path: Path to local video file
            public_id: Optional custom public ID (filename without extension)
            folder: Cloudinary folder to store video in
            
        Returns:
            Secure URL of the uploaded video
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")
            
        try:
            # Use filename as public_id if not provided
            if not public_id:
                public_id = file_path.stem
                
            logger.info(f"Uploading video to Cloudinary: {file_path.name} -> {folder}/{public_id}")
            
            response = cloudinary.uploader.upload(
                str(file_path),
                resource_type="video",
                public_id=public_id,
                folder=folder,
                overwrite=True,
                notification_url=None, 
                eager=[
                    {"streaming_profile": "hd", "format": "m3u8"}, # HLS for adaptive streaming
                    {"format": "mp4"} # Standard MP4 fallback
                ]
            )
            
            secure_url = response.get("secure_url")
            logger.info(f"Upload successful: {secure_url}")
            return secure_url
            
        except Exception as e:
            logger.error(f"Failed to upload video to Cloudinary: {e}")
            raise
