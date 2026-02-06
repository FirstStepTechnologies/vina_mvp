"""
End-to-end video generation pipeline.
Orchestrates the complete workflow from lesson JSON to final MP4 video.
"""
import asyncio
import logging
import time
import json
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


@dataclass
class PipelineResult:
    """Result of the video pipeline execution."""
    video_path: Path
    assets_dir: Path
    metrics: Dict[str, float]


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
    ) -> PipelineResult:
        """
        Generate a complete video from lesson data (async).
        
        Args:
            lesson_data: Lesson JSON with slides
            output_path: Where to save the final video
            course_label: Optional course label for slides
        
        Returns:
            PipelineResult with path and detailed metrics
        """
        logger.info(f"Starting video generation for lesson: {lesson_data.get('title', 'Unknown')}")
        start_time = time.time()
        metrics = {}
        
        # Parse lesson data
        slides = self._parse_lesson_data(lesson_data)
        
        if not slides:
            raise ValueError("No slides found in lesson data")
        
        logger.info(f"Parsed {len(slides)} slides")

        # --- VIDEO CACHE CHECK ---
        import hashlib
        # Create a unique hash for the ENTIRE lesson content (narrations, bullets, prompts)
        content_json = json.dumps(lesson_data, sort_keys=True)
        content_hash = hashlib.md5(content_json.encode()).hexdigest()
        
        # We can store a master copy in the global cache
        video_cache_dir = Path("cache/global_assets/videos")
        video_cache_dir.mkdir(parents=True, exist_ok=True)
        cached_video_path = video_cache_dir / f"{content_hash}.mp4"

        if cached_video_path.exists():
            import shutil
            logger.info(f"🚀 CACHE HIT: Full video already exists for this content hash ({content_hash})")
            shutil.copy(cached_video_path, output_path)
            return PipelineResult(
                video_path=output_path,
                assets_dir=self.config.cache_dir,
                metrics={"total_duration": 0.0, "notes": "Retrieved from cache"}
            )
        # -------------------------
        
        # Create working directories
        images_dir = self.config.cache_dir / "images"
        audio_dir = self.config.cache_dir / "audio"
        slides_dir = self.config.cache_dir / "slides"
        
        for dir_path in [images_dir, audio_dir, slides_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Generate images (parallel)
        logger.info("Step 1/4: Generating images...")
        s1 = time.time()
        image_paths = await self._generate_images(slides, images_dir)
        metrics["image_generation"] = round(time.time() - s1, 2)
        
        # Step 2: Generate audio (parallel)
        logger.info("Step 2/4: Generating audio...")
        s2 = time.time()
        audio_paths = await self._generate_audio(slides, audio_dir)
        metrics["audio_generation"] = round(time.time() - s2, 2)
        
        # Step 3: Compose slides
        logger.info("Step 3/4: Composing slides...")
        s3 = time.time()
        slide_paths = self._compose_slides(
            slides, image_paths, slides_dir,
            course_label or self.config.course_label
        )
        metrics["slide_composition"] = round(time.time() - s3, 2)
        
        # Step 4: Render video
        logger.info("Step 4/4: Rendering video...")
        s4 = time.time()
        video_path = self.video_renderer.render_video(
            slides=slide_paths,
            audio_files=audio_paths,
            output_path=output_path
        )
        metrics["video_rendering"] = round(time.time() - s4, 2)
        
        # Save a master copy to the video cache
        import shutil
        shutil.copy(video_path, cached_video_path)
        logger.info(f"Saved master copy to video cache: {cached_video_path.name}")
        
        total_duration = time.time() - start_time
        metrics["total_duration"] = round(total_duration, 2)
        
        logger.info(f"✅ Video generation complete: {video_path}")
        return PipelineResult(
            video_path=video_path,
            assets_dir=self.config.cache_dir,
            metrics=metrics
        )
    
    def generate_video(
        self,
        lesson_data: Dict[str, Any],
        output_path: Path,
        course_label: Optional[str] = None
    ) -> PipelineResult:
        """
        Generate a complete video from lesson data (sync wrapper).
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
        """Generate images for slides with figures, using content-based caching."""
        import hashlib
        global_cache = Path("cache/global_assets/images")
        global_cache.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        
        # Step A: Check cache and prepare paths
        for i, slide in enumerate(slides):
            if slide.has_figure and slide.image_prompt:
                # Create a hash of the prompt to identify unique images
                prompt_hash = hashlib.md5(slide.image_prompt.encode()).hexdigest()
                cached_file = global_cache / f"{prompt_hash}.png"
                local_path = output_dir / f"image_{i:03d}.png"
                
                if cached_file.exists():
                    import shutil
                    shutil.copy(cached_file, local_path)
                    logger.info(f"Slide {i}: Using cached image (prompt hash match)")
                    image_paths.append(local_path)
                else:
                    # Mark for generation
                    image_paths.append((local_path, cached_file))
            else:
                image_paths.append(None)
        
        # Step B: Generate missing images in parallel
        tasks = []
        for i, entry in enumerate(image_paths):
            if isinstance(entry, tuple):
                local_path, cached_file = entry
                task = self.imagen_client.generate_image_async(
                    prompt=slides[i].image_prompt,
                    output_path=local_path,
                    style="professional"
                )
                tasks.append((i, task, cached_file, local_path))
        
        if tasks:
            results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
            
            for (i, _, cached_file, local_path), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate image for slide {i}: {result}")
                    image_paths[i] = None
                else:
                    # Backup to global cache for future reuse
                    import shutil
                    shutil.copy(local_path, cached_file)
                    image_paths[i] = local_path
        
        successful = sum(1 for p in image_paths if p is not None)
        logger.info(f"Final Assets: {successful}/{len(slides)} slides now have images")
        
        return image_paths
    
    async def _generate_audio(
        self,
        slides: List[SlideData],
        output_dir: Path
    ) -> List[Path]:
        """Generate audio for all slides, using content-based caching."""
        import hashlib
        global_cache = Path("cache/global_assets/audio")
        global_cache.mkdir(parents=True, exist_ok=True)
        
        audio_paths = [None] * len(slides)
        tasks = []
        
        # Step A: Check cache and prepare tasks
        for i, slide in enumerate(slides):
            # Create hash of narration + voice_id (since changing voice should invalidate cache)
            voice_id = getattr(self.tts_client, 'voice_id', 'default')
            content_hash = hashlib.md5(f"{slide.narration}_{voice_id}".encode()).hexdigest()
            cached_file = global_cache / f"{content_hash}.mp3"
            local_path = output_dir / f"audio_{i:03d}.mp3"
            
            if cached_file.exists():
                import shutil
                shutil.copy(cached_file, local_path)
                logger.info(f"Slide {i}: Using cached audio (content hash match)")
                audio_paths[i] = local_path
            else:
                # Mark for generation
                task = self.tts_client.generate_audio_async(
                    text=slide.narration,
                    output_path=local_path
                )
                tasks.append((i, task, cached_file, local_path))
        
        # Step B: Wait for new audio generations
        if tasks:
            results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
            
            for (i, _, cached_file, local_path), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate audio for slide {i}: {result}")
                    raise result
                else:
                    # Backup to global cache
                    import shutil
                    shutil.copy(local_path, cached_file)
                    audio_paths[i] = local_path
        
        logger.info(f"Final Assets: {len(audio_paths)} audio tracks ready (reused {len(slides) - len(tasks)})")
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
