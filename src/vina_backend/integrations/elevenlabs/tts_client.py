"""
ElevenLabs Text-to-Speech client for generating professional audio narration.
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from elevenlabs.client import ElevenLabs
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from vina_backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TTSClient:
    """
    Client for ElevenLabs text-to-speech with async support and concurrency limiting.
    
    Features:
    - Async audio generation
    - Concurrency limiting (prevent rate limits)
    - Automatic retries with exponential backoff
    - Professional voice settings
    - MP3 output format
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        max_concurrent: int = 3,
        model: Optional[str] = None
    ):
        """
        Initialize TTS client.
        
        Args:
            api_key: ElevenLabs API key (defaults to settings)
            voice_id: Voice ID to use (defaults to settings)
            max_concurrent: Max parallel audio generation requests
            model: ElevenLabs model to use
        """
        self.api_key = api_key or settings.elevenlabs_api_key
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY must be set in .env")
        
        self.voice_id = voice_id or settings.elevenlabs_voice_id
        logger.info(f"Using ElevenLabs voice ID: {self.voice_id}")
        
        self.model = model or settings.elevenlabs_model
        logger.info(f"Using ElevenLabs model: {self.model}")
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)
        
        logger.info(f"TTS client initialized (voice_id={self.voice_id}, max_concurrent={max_concurrent})")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def generate_audio_async(
        self,
        text: str,
        output_path: Path,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Path:
        """
        Generate audio for a single text asynchronously with retry logic.
        
        Args:
            text: Text to convert to speech
            output_path: Where to save the generated MP3
            stability: Voice stability (0.0-1.0, higher = more consistent)
            similarity_boost: Voice similarity (0.0-1.0, higher = closer to original)
        
        Returns:
            Path to the generated audio file
        
        Raises:
            Exception: If API call fails after retries
        """
        async with self.semaphore:  # Limit concurrent requests
            # Preprocess text to increase pauses (experimental)
            # Adding an ellipsis after commas and periods to force ElevenLabs to pause longer
            processed_text = text.replace(",", ", ...").replace(".", ". ...")
            
            logger.info(f"Generating audio: {processed_text[:50]}... ({len(processed_text)} chars)")
            
            # Run ElevenLabs in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            audio_generator = await loop.run_in_executor(
                None,
                lambda: self.client.text_to_speech.convert(
                    voice_id=self.voice_id,
                    text=processed_text,
                    model_id=self.model,
                    voice_settings={
                        "stability": 0.65,  # Slightly higher for more deliberate speech
                        "similarity_boost": similarity_boost
                    }
                )
            )
            
            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                # audio_generator is an iterator of bytes
                for chunk in audio_generator:
                    f.write(chunk)
            
            file_size = output_path.stat().st_size
            logger.info(f"Audio saved to {output_path} ({file_size / 1024:.1f} KB)")
            return output_path
    
    def generate_audio(
        self,
        text: str,
        output_path: Path
    ) -> Path:
        """
        Synchronous wrapper for single audio generation.
        
        Args:
            text: Text to convert to speech
            output_path: Where to save the generated MP3
        
        Returns:
            Path to the generated audio file
        """
        return asyncio.run(self.generate_audio_async(text, output_path))
    
    async def generate_audio_batch(
        self,
        texts: List[str],
        output_dir: Path
    ) -> List[Optional[Path]]:
        """
        Generate audio for multiple texts in parallel (respecting concurrency limit).
        
        Args:
            texts: List of texts to convert to speech
            output_dir: Directory to save generated audio files
        
        Returns:
            List of paths to generated audio files (None for failures)
        """
        logger.info(f"Generating {len(texts)} audio files in parallel (max {self.max_concurrent} concurrent)")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        for i, text in enumerate(texts):
            output_path = output_dir / f"audio_{i:02d}.mp3"
            task = self.generate_audio_async(text, output_path)
            tasks.append(task)
        
        # Run all tasks in parallel (semaphore limits concurrency)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for errors
        audio_paths = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate audio {i}: {result}")
                audio_paths.append(None)
            else:
                audio_paths.append(result)
        
        successful = sum(1 for p in audio_paths if p is not None)
        logger.info(f"Generated {successful}/{len(texts)} audio files successfully")
        
        return audio_paths


def get_tts_client() -> TTSClient:
    """
    Get a singleton TTS client instance.
    
    Returns:
        Configured TTSClient
    """
    global _tts_client
    if '_tts_client' not in globals():
        _tts_client = TTSClient()
    return _tts_client

