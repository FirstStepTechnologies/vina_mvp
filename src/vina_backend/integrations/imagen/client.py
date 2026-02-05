"""
Gemini 2.5 Flash Image generation client using litellm.
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional
import litellm
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from vina_backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ImagenClient:
    """
    Client for Gemini 2.5 Flash Image generation via litellm.
    
    Features:
    - Async image generation using litellm
    - Concurrency limiting (prevent rate limits)
    - Automatic retries with exponential backoff
    - 9:16 aspect ratio support (vertical TikTok format)
    - Professional style presets
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini/gemini-2.5-flash-image",
        max_concurrent: int = 3,
        aspect_ratio: str = "9:16"
    ):
        """
        Initialize Imagen client.
        
        Args:
            api_key: Gemini API key (defaults to settings)
            model: litellm model name (default: gemini/gemini-2.5-flash-image)
            max_concurrent: Max parallel image generation requests
            aspect_ratio: Image aspect ratio (default: 9:16 for vertical video)
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in .env")
        
        self.model = model
        self.max_concurrent = max_concurrent
        self.aspect_ratio = aspect_ratio
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        logger.info(f"Imagen client initialized (model={model}, max_concurrent={max_concurrent})")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def generate_image_async(
        self,
        prompt: str,
        output_path: Path,
        style: str = "professional",
        size: str = "1080x1920"  # Vertical format
    ) -> Path:
        """
        Generate a single image asynchronously with retry logic.
        
        Args:
            prompt: Image generation prompt
            output_path: Where to save the generated PNG
            style: Style preset ("professional", "minimalist", "vibrant")
            size: Image size (default: 1080x1920 for 9:16 vertical)
        
        Returns:
            Path to the generated image
        
        Raises:
            Exception: If API call fails after retries
        """
        async with self.semaphore:  # Limit concurrent requests
            logger.info(f"Generating image: {prompt[:50]}...")
            
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Run litellm in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: litellm.image_generation(
                    model=self.model,
                    prompt=enhanced_prompt,
                    api_key=self.api_key
                    # Note: Gemini doesn't support size parameter
                    # It generates images based on the prompt
                )
            )
            
            # Extract image from response
            # Response format: {"data": [{"b64_json": "base64_encoded_image"}]}
            if not response or "data" not in response or not response["data"]:
                raise ValueError(f"No image generated. Response: {response}")
            
            item = response["data"][0]
            if not item.get("b64_json"):
                raise ValueError(f"No b64_json in response: {item}")
            
            # Decode base64 image
            import base64
            image_bytes = base64.b64decode(item["b64_json"])
            
            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"Image saved to {output_path} ({len(image_bytes)} bytes)")
            return output_path
    
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
