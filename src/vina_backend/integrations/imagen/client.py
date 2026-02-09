"""
Gemini 2.5 Flash Image generation client using native Google Gemini API.
Supports true 9:16 aspect ratio for vertical TikTok-style videos.
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from google import genai
from google.genai import types
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from vina_backend.core.config import get_settings
from vina_backend.integrations.opik_tracker import track_cost

logger = logging.getLogger(__name__)
settings = get_settings()


class ImagenClient:
    """
    Client for Gemini 2.5 Flash Image generation via native Google API.
    
    Features:
    - Async image generation using Google Gemini API
    - Concurrency limiting (prevent rate limits)
    - Automatic retries with exponential backoff
    - True 9:16 aspect ratio support (vertical TikTok format)
    - Professional style presets
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash-image",
        max_concurrent: int = 3,
        aspect_ratio: str = "1:1"  # Square images for card-based layouts
    ):
        """
        Initialize Imagen client.
        
        Args:
            api_key: Gemini API key (defaults to settings)
            model: Gemini model name (default: gemini-2.5-flash-image)
            max_concurrent: Max parallel image generation requests
            aspect_ratio: Image aspect ratio (default: 1:1 for square images)
                         Options: "1:1" (square), "9:16" (vertical), "16:9" (horizontal)
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in .env")
        
        self.model = model
        self.max_concurrent = max_concurrent
        self.aspect_ratio = aspect_ratio
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Initialize Google Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        logger.info(f"Imagen client initialized (model={model}, aspect_ratio={aspect_ratio}, max_concurrent={max_concurrent})")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    @track_cost("generate_image", "imagen")
    async def generate_image_async(
        self,
        prompt: str,
        output_path: Path,
        style: str = "professional"
    ) -> Path:
        """
        Generate a single image asynchronously with retry logic.
        
        Args:
            prompt: Image generation prompt
            output_path: Where to save the generated PNG
            style: Style preset ("professional", "minimalist", "vibrant")
        
        Returns:
            Path to the generated image
        
        Raises:
            Exception: If API call fails after retries
        """
        async with self.semaphore:  # Limit concurrent requests
            logger.info(f"Generating image: {prompt[:50]}...")
            
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Run Gemini API in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=[enhanced_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio=self.aspect_ratio,
                        ),
                    ),
                )
            )
            
            # Extract image from response
            image_found = False
            for part in response.parts:
                # Call as_image() on parts that have inline_data
                if getattr(part, "inline_data", None) is not None:
                    img = part.as_image()  # Returns a Pillow Image object
                    
                    # Save to file
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(output_path)
                    image_found = True
                    
                    # Get file size for logging
                    file_size = output_path.stat().st_size
                    logger.info(f"Image saved to {output_path} ({file_size / 1024:.1f} KB)")
                    return output_path
                
                # Log any text parts (usually empty for image generation)
                if getattr(part, "text", None):
                    logger.debug(f"Text part from model: {part.text}")
            
            if not image_found:
                raise ValueError("No image part returned by Gemini model")


    
    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        style: str = "professional"
    ) -> Path:
        """
        Synchronous wrapper for single image generation.
        
        Args:
            prompt: Image generation prompt
            output_path: Where to save the generated PNG
            style: Style preset
        
        Returns:
            Path to the generated image
        """
        return asyncio.run(self.generate_image_async(prompt, output_path, style))
    
    async def generate_images_batch(
        self,
        prompts: List[str],
        output_dir: Path,
        style: str = "professional"
    ) -> List[Optional[Path]]:
        """
        Generate multiple images in parallel (respecting concurrency limit).
        
        Args:
            prompts: List of image generation prompts
            output_dir: Directory to save generated images
            style: Style preset for all images
        
        Returns:
            List of paths to generated images (None for failures)
        """
        logger.info(f"Generating {len(prompts)} images in parallel (max {self.max_concurrent} concurrent)")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        for i, prompt in enumerate(prompts):
            output_path = output_dir / f"image_{i:02d}.png"
            task = self.generate_image_async(prompt, output_path, style)
            tasks.append(task)
        
        # Run all tasks in parallel (semaphore limits concurrency)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for errors
        image_paths = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate image {i}: {result}")
                image_paths.append(None)
            else:
                image_paths.append(result)
        
        successful = sum(1 for p in image_paths if p is not None)
        logger.info(f"Generated {successful}/{len(prompts)} images successfully")
        
        return image_paths
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """
        Enhance user prompt with style and quality modifiers.
        
        Args:
            prompt: Original prompt
            style: Style preset
        
        Returns:
            Enhanced prompt
        """
        style_modifiers = {
            "professional": "professional, clean, modern, high-quality, business-appropriate",
            "minimalist": "minimalist, simple, clean lines, uncluttered, modern",
            "vibrant": "vibrant colors, energetic, dynamic, eye-catching, modern"
        }
        
        modifier = style_modifiers.get(style, style_modifiers["professional"])
        
        # Add quality and format instructions
        enhanced = f"{prompt}, {modifier}, vertical format, high resolution"
        
        return enhanced


def get_imagen_client() -> ImagenClient:
    """
    Get a singleton Imagen client instance.
    
    Returns:
        Configured ImagenClient
    """
    global _imagen_client
    if '_imagen_client' not in globals():
        _imagen_client = ImagenClient()
    return _imagen_client

