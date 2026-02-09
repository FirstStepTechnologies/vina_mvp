"""
VINA RENDER PIPELINE: CLOUD-NATIVE DEMO GENERATION
================================================
This script is deeply specialized for the Render environment.
It extends the local demo functionality with:
1.  Cloudinary Uploads: Assets are moved off ephemeral storage immediately.
2.  Database Persistence: Video URLs are saved to the persistent SQLite DB.
3.  Production Logging: Formatted for Render's log streams.

Usage on Render:
uv run scripts/render_demo_pipeline.py --prof "HR Manager" --adaptation "more_examples"
"""

import sys
import asyncio
import time
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Domains & Schemas
from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.domain.schemas.lesson import GeneratedLesson

# Services
from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.services.lesson_generator import LessonGenerator
from vina_backend.services.video_pipeline import VideoPipeline, PipelineConfig
from vina_backend.services.lesson_cache import LessonCacheService
from vina_backend.services.course_loader import load_course_config
from vina_backend.integrations.cloudinary.client import CloudinaryClient

# Core
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db, engine
from sqlmodel import Session

# Setup logging
setup_logging("INFO")
logger = logging.getLogger("VINA_RENDER")

# Constants
COURSE_ID = "c_llm_foundations"
DEFAULT_LESSON_ID = "l01_what_llms_are"

TEST_CASES = [
    # Format: (Profession, Industry, Experience_Level_String, Difficulty_Int)
    ("HR Manager", "Tech Company", "Beginner", 3),
    ("Project Manager", "Software/Tech", "Beginner", 3),
    ("Marketing Manager", "E-Commerce", "Beginner", 3),
    ("Clinical Researcher", "Pharma/Biotech", "Beginner", 3),
]

async def run_render_pipeline(profession: str, industry: str, level_str: str, difficulty_level: int, lesson_idx: int = 1, skip_media: bool = False, output_override: Optional[Path] = None, adaptation_context: Optional[str] = None):
    """Run the pipeline with Cloudinary integration for Render."""
    
    # Ensure database is initialized
    # On Render, this uses DATABASE_URL pointing to the persistent disk
    init_db()
    
    # Initialize Cloudinary Client
    try:
        cloudinary_client = CloudinaryClient()
    except Exception as e:
        logger.error(f"❌ Cloudinary configuration failed: {e}")
        return

    # Determine Lesson ID dynamically
    try:
        config = load_course_config(COURSE_ID)
        lessons = config.get("lessons", [])
        if 1 <= lesson_idx <= len(lessons):
            target_lesson = lessons[lesson_idx - 1]
            lesson_id = target_lesson["lesson_id"]
        else:
            target_lesson = lessons[0]
            lesson_id = target_lesson["lesson_id"]
    except Exception as e:
        logger.warning(f"⚠️ Error loading course config: {e}. Using default.")
        lesson_id = DEFAULT_LESSON_ID
    
    logger.info("="*80)
    logger.info(f"🚀 STARTING RENDER PIPELINE FOR: {profession}")
    logger.info("="*80)
    
    metrics = {}
    master_start = time.time()

    # --- PHASE 1: IDENTITY ---
    logger.info("[PHASE 1] Identity & Profile...")
    s1 = time.time()
    try:
        user_profile = get_or_create_user_profile(
            profession=profession,
            industry=industry,
            experience_level=level_str
        )
        metrics["1. Identity"] = time.time() - s1
        logger.info(f"✅ Identity Verified: {user_profile.profession}")
    except Exception as e:
        logger.error(f"❌ Identity Phase failed: {e}")
        return

    # --- PHASE 2: LESSON GENERATION ---
    logger.info("[PHASE 2] IP & Lesson Generation...")
    s2 = time.time()
    try:
        with Session(engine) as session:
            cache_service = LessonCacheService(db_session=session)
            lesson_generator = LessonGenerator(cache_service=cache_service)
            
            generated_lesson = await asyncio.to_thread(
                lesson_generator.generate_lesson,
                lesson_id=lesson_id,
                course_id=COURSE_ID,
                user_profile=user_profile,
                difficulty_level=difficulty_level,
                adaptation_context=adaptation_context,
                bypass_cache=False
            )
            
        metrics["2. Lesson Gen"] = time.time() - s2
        logger.info(f"✅ Lesson Generated: \"{generated_lesson.lesson_content.lesson_title}\"")
        
        if adaptation_context:
            logger.info(f"   Context: {adaptation_context}")
            
    except Exception as e:
        logger.error(f"❌ Lesson Phase failed: {e}")
        import traceback
        traceback.print_exc()
        return

    if skip_media:
        logger.info("⏩ Skipping Media Generation")
        return

    # --- PHASE 3: ASSET GENERATION & UPLOAD ---
    logger.info("[PHASE 3] Video Generation & Cloud Upload...")
    s3 = time.time()
    try:
        # Prepare deterministic filename
        model_name = "unknown"
        if generated_lesson.generation_metadata.llm_model:
            model_name = generated_lesson.generation_metadata.llm_model.split("/")[-1]
        
        slug = f"{profession}_{industry}_{level_str}_d{difficulty_level}_{model_name}_{COURSE_ID}_{lesson_id}".lower().replace(' ', '_').replace('/', '_')
        if adaptation_context:
            slug += f"_{adaptation_context}"
            
        # Use simple cache dir for temp storage
        temp_dir = Path("cache/render_temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        output_video_path = temp_dir / f"{slug}.mp4"
        
        # Configure Pipeline
        config = PipelineConfig(
            cache_dir=Path(f"cache/runs/{slug}"),
            brand_name="VINA",
            course_label=f"{profession} Masterclass"
        )
        
        pipeline = VideoPipeline(config)
        
        # Prepare Data
        # (Simplified slide extraction logic)
        slides_adapted = []
        for s in generated_lesson.lesson_content.slides:
            bullets = [item.bullet for item in s.items]
            narration = " ".join([item.talk for item in s.items])
            image_prompt = None
            has_figure = False
            for item in s.items:
                if item.type == "figure" and item.figure:
                    image_prompt = item.figure.image_prompt
                    has_figure = True
                    break
            
            slides_adapted.append({
                "title": s.title,
                "bullets": bullets,
                "narration": narration,
                "has_figure": has_figure,
                "image_prompt": image_prompt
            })

        lesson_data = {
            "title": generated_lesson.lesson_content.lesson_title,
            "topic": generated_lesson.lesson_content.lesson_id or "General Knowledge",
            "slides": slides_adapted
        }
        
        # Generate Video
        pipeline_result = await pipeline.generate_video_async(
            lesson_data=lesson_data,
            output_path=output_video_path,
            course_label=generated_lesson.lesson_content.lesson_title
        )
        
        logger.info(f"✅ Video Generated Locally: {output_video_path}")
        
        # --- UPLOAD TO CLOUDINARY ---
        logger.info("☁️ Uploading to Cloudinary...")
        upload_start = time.time()
        
        public_id = f"vina_render_{slug}"
        video_url = cloudinary_client.upload_video(
            file_path=output_video_path,
            public_id=public_id,
            folder="vina_demo_assets"
        )
        
        metrics["3b. Cloud Upload"] = time.time() - upload_start
        logger.info(f"🎉 Upload Complete! URL: {video_url}")
        
        # --- UPDATE DATABASE ---
        logger.info("💾 Updating Database with Video URL...")
        with Session(engine) as session:
            cache_service = LessonCacheService(db_session=session)
            updated = cache_service.update_video_url(
                course_id=COURSE_ID,
                lesson_id=lesson_id,
                difficulty_level=difficulty_level,
                user_profile=user_profile,
                llm_model=generated_lesson.generation_metadata.llm_model or "unknown",
                video_url=video_url,
                adaptation_context=adaptation_context
            )
            
            if updated:
                logger.info("✅ Database updated successfully")
            else:
                logger.warning("⚠️ Failed to update database record (Entry not found?)")

        metrics["3. Total Asset Phase"] = time.time() - s3
        
    except Exception as e:
        logger.error(f"❌ Media Phase failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- FINAL REPORT ---
    master_end = time.time()
    logger.info("="*80)
    logger.info("📋 RENDER EXECUTION REPORT")
    logger.info(f"   Total Time: {master_end - master_start:.2f}s")
    for k, v in metrics.items():
        logger.info(f"   - {k}: {v:.2f}s")
    logger.info("="*80)

async def main():
    """Entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="VINA Render Pipeline")
    parser.add_argument("--prof", type=str, help="Target profession")
    parser.add_argument("--adaptation", type=str, help="Adaptation context (e.g., 'more_examples')")
    parser.add_argument("--lesson-num", type=int, default=1, help="Lesson number")
    
    args = parser.parse_args()
    
    target_prof = args.prof
    adaptation_context = args.adaptation
    
    if not target_prof:
        print("Please provide --prof (e.g. 'HR Manager')")
        return

    # Find test case settings
    case = next((c for c in TEST_CASES if c[0].lower() == target_prof.lower()), None)
    if not case:
        # Default fallback
        case = (target_prof, "General", "Beginner", 3)
    
    # Unpack
    profession, industry, level, difficulty = case
    
    # Adaptation Override
    if adaptation_context == "more_examples":
        logger.info("⚡ Adaptation Override: Forcing Difficulty 3")
        difficulty = 3
        
    await run_render_pipeline(
        profession, industry, level, difficulty, 
        lesson_idx=args.lesson_num, 
        adaptation_context=adaptation_context
    )

if __name__ == "__main__":
    asyncio.run(main())
