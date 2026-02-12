"""
Script to batch generate lesson content for all professions and lessons.
This automates the process of generating "More Examples" adaptations.
"""
import sys
import asyncio
import logging
import time
from pathlib import Path

# Add the project root to sys.path
# This allows us to import from 'src' and 'scripts'
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(root_path / "src"))

# Import the pipeline from the demo script
from scripts.demo_complete_pipeline import run_full_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BATCH_GEN")

# Configuration
LESSONS = [1, 2, 3, 4, 5]
PROFESSIONS = [
    ("HR Manager", "Tech Company", "Beginner"),
    ("Project Manager", "Software/Tech", "Beginner"),
    ("Marketing Manager", "E-Commerce", "Beginner"),
    ("Clinical Researcher", "Pharma/Biotech", "Beginner"),
]

async def generate_all():
    """Iterate through all combinations and generate content."""
    logger.info("🎬 Starting Batch Video Generation...")
    start_time = time.time()
    
    success_count = 0
    fail_count = 0
    
    for prof_data in PROFESSIONS:
        profession, industry, level = prof_data
        
        for lesson_num in LESSONS:
            logger.info(f"\n{'='*60}")
            logger.info(f"Targeting: {profession} - Lesson {lesson_num} (Adaptation: examples)")
            logger.info(f"{'='*60}")
            
            try:
                # We use difficulty 3 (Practical) as the default for examples
                await run_full_pipeline(
                    profession=profession,
                    industry=industry,
                    level_str=level,
                    difficulty_level=3,
                    lesson_idx=lesson_num,
                    adaptation_context="examples"
                )
                success_count += 1
                logger.info(f"✅ Successfully generated Lesson {lesson_num} for {profession}")
            except Exception as e:
                fail_count += 1
                logger.error(f"❌ Failed to generate Lesson {lesson_num} for {profession}: {e}")
            
            # Small cooldown between generations to avoid rate limits
            await asyncio.sleep(2)

    total_time = time.time() - start_time
    logger.info(f"\n{'#'*60}")
    logger.info(f"✨ BATCH GENERATION COMPLETE")
    logger.info(f"   Success: {success_count}")
    logger.info(f"   Failures: {fail_count}")
    logger.info(f"   Total Time: {total_time/60:.2f} minutes")
    logger.info(f"{'#'*60}")

if __name__ == "__main__":
    try:
        asyncio.run(generate_all())
    except KeyboardInterrupt:
        logger.info("\nStopped by user.")
    except Exception as e:
        logger.fatal(f"Fatal error: {e}")
