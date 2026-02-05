"""
End-to-end video generation pipeline.
Orchestrates the complete workflow from lesson JSON to final MP4 video.
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from vina_backend.integrations.imagen.client import ImagenClient
from vina_backend.integrations.elevenlabs.tts_client import TTSClient
from vina_backend.services.slide_composer import SlideComposer
from vina_backend.services.video_renderer import VideoRenderer

logger = logging.getLogger(__name__)


@dataclass
class SlideData:
    """Data for a single slide."""
    title: str
    bullets: List[str]
    narration: str
    image_prompt: Optional[str] = None
    has_figure: bool = False


@dataclass
class PipelineConfig:
    """Configuration for the video pipeline."""
    cache_dir: Path = Path("cache/pipeline")
    brand_name: str = "VINA"
    course_label: Optional[str] = None
    max_concurrent_images: int = 3
    max_concurrent_audio: int = 5


class VideoPipeline:
    """
    End-to-end video generation pipeline.
    
    Workflow:
    1. Parse lesson JSON
    2. Generate images (parallel)
    3. Generate audio (parallel)
    4. Compose slides
    5. Render video
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize video pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        
        # Initialize clients
        self.imagen_client = ImagenClient(max_concurrent=self.config.max_concurrent_images)
        self.tts_client = TTSClient(max_concurrent=self.config.max_concurrent_audio)
        self.slide_composer = SlideComposer(brand_name=self.config.brand_name)
        self.video_renderer = VideoRenderer()
        
        logger.info("Video pipeline initialized")
    
    async def generate_video_async(
        self,
        lesson_data: Dict[str, Any],
        output_path: Path,
        course_label: Optional[str] = None
    ) -> Path:
        """
        Generate a complete video from lesson data (async).
        
        Args:
            lesson_data: Lesson JSON with slides
            output_path: Where to save the final video
            course_label: Optional course label for slides
        
        Returns:
            Path to the generated video
        """
        logger.info(f"Starting video generation for lesson: {lesson_data.get('title', 'Unknown')}")
        
        # Parse lesson data
        slides = self._parse_lesson_data(lesson_data)
        
        if not slides:
            raise ValueError("No slides found in lesson data")
        
        logger.info(f"Parsed {len(slides)} slides")
        
        # Create working directories
        images_dir = self.config.cache_dir / "images"
        audio_dir = self.config.cache_dir / "audio"
        slides_dir = self.config.cache_dir / "slides"
        
        for dir_path in [images_dir, audio_dir, slides_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Generate images (parallel)
        logger.info("Step 1/4: Generating images...")
        image_paths = await self._generate_images(slides, images_dir)
        
        # Step 2: Generate audio (parallel)
        logger.info("Step 2/4: Generating audio...")
        audio_paths = await self._generate_audio(slides, audio_dir)
        
        # Step 3: Compose slides
        logger.info("Step 3/4: Composing slides...")
        slide_paths = self._compose_slides(
            slides, image_paths, slides_dir,
            course_label or self.config.course_label
        )
        
        # Step 4: Render video
        logger.info("Step 4/4: Rendering video...")
        video_path = self.video_renderer.render_video(
            slides=slide_paths,
            audio_files=audio_paths,
            output_path=output_path
        )
        
        logger.info(f"✅ Video generation complete: {video_path}")
        return video_path
    
    def generate_video(
        self,
        lesson_data: Dict[str, Any],
        output_path: Path,
        course_label: Optional[str] = None
    ) -> Path:
        """
        Generate a complete video from lesson data (sync wrapper).
        
        Args:
            lesson_data: Lesson JSON with slides
            output_path: Where to save the final video
            course_label: Optional course label for slides
        
        Returns:
            Path to the generated video
        """
        return asyncio.run(
            self.generate_video_async(lesson_data, output_path, course_label)
        )
    
    def _parse_lesson_data(self, lesson_data: Dict[str, Any]) -> List[SlideData]:
        """Parse lesson JSON into SlideData objects."""
        slides = []
        
        for i, slide_json in enumerate(lesson_data.get("slides", [])):
            # Extract slide data
            title = slide_json.get("title", f"Slide {i+1}")
            bullets = slide_json.get("bullets", [])
            narration = slide_json.get("narration", "")
            
            # Check for image
            has_figure = slide_json.get("has_figure", False)
            image_prompt = slide_json.get("image_prompt") if has_figure else None
            
            slides.append(SlideData(
                title=title,
                bullets=bullets,
                narration=narration,
                image_prompt=image_prompt,
                has_figure=has_figure
            ))
        
        return slides
    
    async def _generate_images(
        self,
        slides: List[SlideData],
        output_dir: Path
    ) -> List[Optional[Path]]:
        """Generate images for slides with figures."""
        image_paths = []
        
        for i, slide in enumerate(slides):
            if slide.has_figure and slide.image_prompt:
                output_path = output_dir / f"image_{i:03d}.png"
                image_paths.append(output_path)
            else:
                image_paths.append(None)
        
        # Generate all images in parallel
        tasks = []
        for i, (slide, image_path) in enumerate(zip(slides, image_paths)):
            if image_path:
                task = self.imagen_client.generate_image_async(
                    prompt=slide.image_prompt,
                    output_path=image_path,
                    style="professional"
                )
                tasks.append((i, task))
        
        # Wait for all images
        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (i, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate image for slide {i}: {result}")
                    image_paths[i] = None
        
        successful = sum(1 for p in image_paths if p is not None)
        logger.info(f"Generated {successful}/{len(tasks)} images")
        
        return image_paths
    
    async def _generate_audio(
        self,
        slides: List[SlideData],
        output_dir: Path
    ) -> List[Path]:
        """Generate audio for all slides."""
        audio_paths = []
        tasks = []
        
        for i, slide in enumerate(slides):
            output_path = output_dir / f"audio_{i:03d}.mp3"
            audio_paths.append(output_path)
            
            task = self.tts_client.generate_audio_async(
                text=slide.narration,
                output_path=output_path
            )
            tasks.append(task)
        
        # Wait for all audio
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate audio for slide {i}: {result}")
                raise result
        
        logger.info(f"Generated {len(audio_paths)} audio files")
        return audio_paths
    
    def _compose_slides(
        self,
        slides: List[SlideData],
        image_paths: List[Optional[Path]],
        output_dir: Path,
        course_label: Optional[str]
    ) -> List[Path]:
        """Compose all slides."""
        slide_paths = []
        
        for i, (slide, image_path) in enumerate(zip(slides, image_paths)):
            output_path = output_dir / f"slide_{i:03d}.png"
            
            self.slide_composer.compose_slide(
                title=slide.title,
                output_path=output_path,
                bullets=slide.bullets,
                image_path=image_path,
                slide_number=i + 1,
                total_slides=len(slides),
                course_label=course_label
            )
            
            slide_paths.append(output_path)
        
        logger.info(f"Composed {len(slide_paths)} slides")
        return slide_paths


def get_video_pipeline(config: Optional[PipelineConfig] = None) -> VideoPipeline:
    """
    Get a video pipeline instance.
    
    Args:
        config: Optional pipeline configuration
    
    Returns:
        Configured VideoPipeline
    """
    return VideoPipeline(config)
