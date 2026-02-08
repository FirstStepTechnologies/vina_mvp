"""
VINA HACKATHON: FULL END-TO-END SYSTEM DEMO
==========================================
This script simulates the entire VINA stack as built:
1.  IDENTITY: Load/Create the User Profile (Persists to SQLite Database).
2.  CURRICULUM: Load global and course-specific configurations.
3.  INTELLECTUAL PROPERTY: Generate a reviewed, personalized lesson (multi-agent Generator/Reviewer/Refiner).
4.  AUDIO/VISUAL: Orchestrate AI image generation (Gemini) and TTS (ElevenLabs).
5.  ASSEMBLY: Render professional vertical video for TikTok/Instagram format.

Features:
- Full timing breakdown per phase.
- Deep personalization based on professional challenges and safety priorities.
- Real-world personas: Clinical Researcher, HR Manager, Project Manager, Marketing Manager.

Usage Example:
python scripts/demo_complete_pipeline.py --prof "HR Manager" --diff 3 --lesson-num 1
"""

import sys
import asyncio
import time
import logging
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

# Core
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db, engine
from sqlmodel import Session

# Setup basic logging to see the pipeline's progress
setup_logging("INFO")
logger = logging.getLogger("VINA_DEMO")

# Constants
COURSE_ID = "c_llm_foundations"
DEFAULT_LESSON_ID = "l01_what_llms_are"
# Difficulty mapping is now explicit in TEST_CASES or via --diff flag

TEST_CASES = [
    # Format: (Profession, Industry, Experience_Level_String, Difficulty_Int)
    ("HR Manager", "Tech Company", "Beginner", 3),
    ("Project Manager", "Software/Tech", "Beginner", 3),
    ("Marketing Manager", "E-Commerce", "Beginner", 3),
    ("Clinical Researcher", "Pharma/Biotech", "Beginner", 3),
]

async def run_full_pipeline(profession: str, industry: str, level_str: str, difficulty_level: int, lesson_idx: int = 1, skip_media: bool = False, output_override: Optional[Path] = None, adaptation_context: Optional[str] = None):
    """Run every single module of the VINA platform."""
    # Ensure database is initialized before any phase starts
    init_db()
    
    # HACKATHON MIGRATION: Add adaptation_context to cache table if missing
    try:
        from sqlalchemy import text
        with Session(engine) as session:
            try:
                # Check if column exists
                session.exec(text("SELECT adaptation_context FROM lesson_cache LIMIT 1"))
            except Exception:
                # Column doesn't exist, add it
                print("⚡ MIGRATION: Adding 'adaptation_context' column to lesson_cache table...")
                session.exec(text("ALTER TABLE lesson_cache ADD COLUMN adaptation_context VARCHAR"))
                session.commit()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
    
    # Determine Lesson ID dynamically
    lesson_name = "Unknown Lesson"
    try:
        config = load_course_config(COURSE_ID)
        lessons = config.get("lessons", [])
        if 1 <= lesson_idx <= len(lessons):
            target_lesson = lessons[lesson_idx - 1]
            lesson_id = target_lesson["lesson_id"]
            lesson_name = target_lesson.get("lesson_name", "Unknown")
            print(f"📚 Selected Lesson {lesson_idx}: {lesson_name} ({lesson_id})")
        else:
            print(f"⚠️ Invalid lesson index {lesson_idx}, defaulting to Lesson 1")
            target_lesson = lessons[0]
            lesson_id = target_lesson["lesson_id"]
            lesson_name = target_lesson.get("lesson_name", "Unknown")
    except Exception as e:
        print(f"⚠️ Error loading course config: {e}. Using default.")
        lesson_id = DEFAULT_LESSON_ID
    
    print("\n" + "#"*80)
    print(f"🎬 STARTING VINA PIPELINE FOR: {profession} ({level_str})")
    print("#"*80)
    
    metrics = {}
    master_start = time.time()

    # --- PHASE 1: IDENTITY (User Profiling) ---
    print("\n[PHASE 1: IDENTITY] Fetching or Generating Persona...")
    s1 = time.time()
    try:
        user_profile = get_or_create_user_profile(
            profession=profession,
            industry=industry,
            experience_level=level_str
        )
        e1 = time.time()
        metrics["1. Identity (DB/LLM)"] = e1 - s1
        print(f"✅ Persona Created: {user_profile.profession}")
        print(f"   Key Goal: {user_profile.professional_goals[0]}")
    except Exception as e:
        print(f"❌ Identity Phase failed: {e}")
        return

    # --- PHASE 2: INTELLECTUAL PROPERTY (Lesson Content) ---
    print("\n[PHASE 2: INTELLECTUAL PROPERTY] Multi-Agent Lesson Generation...")
    s2 = time.time()
    try:
        with Session(engine) as session:
            # Initialize Cache Service & Generator
            cache_service = LessonCacheService(db_session=session)
            lesson_generator = LessonGenerator(cache_service=cache_service)
            
            # generate_lesson handles the Generator -> Reviewer -> Refiner loop
            generated_lesson = await asyncio.to_thread(
                lesson_generator.generate_lesson,
                lesson_id=lesson_id,
                course_id=COURSE_ID,
                user_profile=user_profile,
                difficulty_level=difficulty_level,
                adaptation_context=adaptation_context,
                bypass_cache=False
            )
        
        e2 = time.time()
        metrics["2. Lesson Gen (3-Agent)"] = e2 - s2
        print(f"✅ Lesson Refined: \"{generated_lesson.lesson_content.lesson_title}\"")
        if adaptation_context:
            print(f"   Adaptation: {adaptation_context}")
        print(f"   Metadata: Cached={generated_lesson.generation_metadata.cache_hit}, Model={generated_lesson.generation_metadata.llm_model}")
        
        # Expert Systems Engineer Utility: Export Audit Trail
        report_path = lesson_generator.export_generation_report(
            generated_lesson, 
            Path("cache/reports"),
            user_profile
        )
        print(f"📄 Audit Report saved: {report_path}")
    except Exception as e:
        print(f"❌ IP Phase failed: {e}")
        import traceback
        traceback.print_exc()
        return

    if skip_media:
        print("\n" + "="*80)
        print("⏩ SKIPPING AUDIO/VIDEO GENERATION (--text-only flag detected)")
        print(f"   Review the report at: {report_path}")
        print("="*80 + "\n")
        return

    # --- PHASE 3: AUDIO/VISUAL ORCHESTRATION ---
    print("\n[PHASE 3: AUDIO/VISUAL] Generating AI Image Prompts & TTS...")
    s3 = time.time()
    try:
        # Prepare Deterministic Pipeline ID
        # Format: profession_industry_difficulty_lessonid (safe for filenames)
        # Start by getting the model name (and sanitizing it)
        model_name = "unknown"
        if generated_lesson.generation_metadata.llm_model:
            model_name = generated_lesson.generation_metadata.llm_model.split("/")[-1] # Take last part if slash exists
        
        slug = f"{profession}_{industry}_{level_str}_d{difficulty_level}_{model_name}_{COURSE_ID}_{lesson_id}".lower().replace(' ', '_').replace('/', '_')
        run_name = slug
        
        config = PipelineConfig(
            cache_dir=Path(f"cache/runs/{run_name}"),
            brand_name="VINA",
            course_label=f"{profession} Masterclass"
        )
        
        pipeline = VideoPipeline(config)
        
        # Convert LessonContent to Dict
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
        
        output_video_path = output_override or Path(f"cache/demo_videos/{run_name}.mp4")
        output_video_path.parent.mkdir(parents=True, exist_ok=True)

        pipeline_result = await pipeline.generate_video_async(
            lesson_data=lesson_data,
            output_path=output_video_path,
            course_label=lesson_name
        )
        
        e3 = time.time()
        metrics["3. Asset Generation & Assembly"] = e3 - s3
        
        # Add detailed sub-metrics
        # Lesson Gen sub-metrics
        ldm = generated_lesson.generation_metadata.phase_durations
        metrics["   ↳ LLM Generation"] = ldm.get("generation", 0)
        metrics["   ↳ LLM Review"] = ldm.get("review", 0)
        metrics["   ↳ LLM Rewrite/Fix"] = ldm.get("rewrite", 0)
        
        # Video Pipeline sub-metrics
        vpm = pipeline_result.metrics
        metrics["   ↳ Image Generation"] = vpm.get("image_generation", 0)
        metrics["   ↳ Audio (TTS)"] = vpm.get("audio_generation", 0)
        metrics["   ↳ Slide Composition"] = vpm.get("slide_composition", 0)
        metrics["   ↳ Video Rendering"] = vpm.get("video_rendering", 0)

        print(f"✅ Video Assembled: {pipeline_result.video_path}")
        print(f"   File Size: {pipeline_result.video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"❌ Video Phase failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- FINAL REPORT ---
    master_end = time.time()
    print("\n" + "="*80)
    print("📋 PERFORMANCE ANALYSIS REPORT")
    print("="*80)
    for step, duration in metrics.items():
        if "↳" in step:
            print(f"     {step:<25} {duration:>8.2f} seconds")
        else:
            print(f"   • {step:<25} {duration:>8.2f} seconds")
    print("-" * 80)
    print(f"   TOTAL PROCESSING TIME:      {master_end - master_start:>8.2f} seconds")
    print("="*80 + "\n")

async def main():
    """Run all demo test cases."""
    print("VINA End-to-End Pipeline Demo Starting...")
    
    # Check for CLI flags
    skip_media = "--text-only" in sys.argv
    override_diff = None
    target_prof = None
    target_lesson_idx = 1
    output_override = None
    adaptation_context = None
    
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--diff="):
            try:
                override_diff = int(arg.split("=")[1])
            except ValueError:
                print(f"⚠️ Invalid difficulty override: {arg}")
        elif arg == "--diff" and i + 1 < len(sys.argv):
             try:
                override_diff = int(sys.argv[i + 1])
             except ValueError: pass
        elif arg == "--prof" and i + 1 < len(sys.argv):
            target_prof = sys.argv[i + 1]
        elif arg == "--lesson-num" and i + 1 < len(sys.argv):
            try:
                target_lesson_idx = int(sys.argv[i + 1])
            except ValueError: pass
        elif (arg == "--output" or arg == "--outputs") and i + 1 < len(sys.argv):
            output_override = Path(sys.argv[i + 1])
        elif arg == "--adaptation" and i + 1 < len(sys.argv):
            adaptation_context = sys.argv[i + 1]

    # Filter out flags from args for positional parsing
    args = [arg for arg in sys.argv if not arg.startswith("--")]

    # Parse parameters
    target_indices = range(len(TEST_CASES))
    
    if target_prof:
        target_indices = [i for i, case in enumerate(TEST_CASES) if case[0].lower() == target_prof.lower()]
        if not target_indices:
            print(f"⚠️ No test case found for profession: {target_prof}")
            return
    elif len(args) > 1:
        try:
            val = args[1]
            if val.lower() == "all":
                target_indices = range(len(TEST_CASES))
            else:
                target_indices = [int(val)]
        except ValueError:
            pass

    for i in target_indices:
        case = list(TEST_CASES[i])
        # If difficulty override is provided via CLI, use it
        if override_diff is not None:
            case[3] = override_diff
        
        # HACKATHON OVERRIDE: If generating "more_examples", FORCE difficulty to 3 (Practical)
        # This prevents generating separate example videos for every difficulty level.
        if adaptation_context == "more_examples":
            print("⚡ OVERRIDE: Forcing Difficulty to 3 for 'more_examples' variant")
            case[3] = 3
            
        await run_full_pipeline(*case, lesson_idx=target_lesson_idx, skip_media=skip_media, output_override=output_override, adaptation_context=adaptation_context)
        # Short pause between demos
        if len(target_indices) > 1:
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
