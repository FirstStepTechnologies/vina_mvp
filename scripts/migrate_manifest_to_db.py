#!/usr/bin/env python3
"""
Migrate video URLs from video_manifest.json to the database.

This script reads the static manifest file created by upload_cached_videos.py
and populates the video_url column in the lesson_cache table.

Usage:
    uv run scripts/migrate_manifest_to_db.py
"""

import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.db.engine import init_db, engine
from vina_backend.services.lesson_cache import LessonCache
from sqlmodel import Session, select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MANIFEST_FILE = Path("src/vina_backend/domain/constants/video_manifest.json")

def parse_filename(filename: str) -> dict:
    """
    Parse video filename to extract metadata.
    
    Examples:
    - hr_manager_tech_company_beginner_d3_gemini-3-pro-preview_c_llm_foundations_l01_what_llms_are
    - clinical_researcher_pharma_biotech_beginner_d1_gemini-3-pro-preview_c_llm_foundations_l01_what_llms_are
    """
    parts = filename.split("_")
    
    # Try to find difficulty level (d1, d3, d5)
    difficulty = None
    for i, part in enumerate(parts):
        if part.startswith("d") and part[1:].isdigit():
            difficulty = int(part[1:])
            break
    
    # Try to find course and lesson IDs
    course_id = None
    lesson_id = None
    
    # Look for c_llm_foundations pattern
    for i, part in enumerate(parts):
        if part.startswith("c_"):
            # Found course ID
            course_id = part
            # Lesson ID should be next parts until end
            if i + 1 < len(parts):
                lesson_id = "_".join(parts[i+1:])
            break
    
    return {
        "difficulty": difficulty,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "filename": filename
    }

def main():
    """Migrate manifest URLs to database."""
    init_db()
    
    if not MANIFEST_FILE.exists():
        logger.error(f"Manifest file not found: {MANIFEST_FILE}")
        return
    
    # Load manifest
    with open(MANIFEST_FILE, "r") as f:
        manifest = json.load(f)
    
    logger.info(f"Loaded {len(manifest)} entries from manifest")
    
    with Session(engine) as session:
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        
        for filename, url in manifest.items():
            # Parse filename
            metadata = parse_filename(filename)
            
            if not metadata["course_id"] or not metadata["lesson_id"]:
                logger.debug(f"Skipping {filename}: couldn't parse course/lesson ID")
                skipped_count += 1
                continue
            
            if not metadata["difficulty"]:
                logger.debug(f"Skipping {filename}: couldn't parse difficulty")
                skipped_count += 1
                continue
            
            # Find matching cache entries
            statement = select(LessonCache).where(
                LessonCache.course_id == metadata["course_id"],
                LessonCache.lesson_id == metadata["lesson_id"],
                LessonCache.difficulty_level == metadata["difficulty"]
            )
            
            entries = session.exec(statement).all()
            
            if not entries:
                logger.debug(f"No cache entry found for {filename}")
                failed_count += 1
                continue
            
            # Update all matching entries (there may be multiple profiles)
            for entry in entries:
                if not entry.video_url:  # Only update if not already set
                    entry.video_url = url
                    session.add(entry)
                    updated_count += 1
                    logger.info(f"✅ Updated {metadata['course_id']}/{metadata['lesson_id']} D{metadata['difficulty']}")
                else:
                    skipped_count += 1
        
        session.commit()
    
    logger.info("=" * 60)
    logger.info(f"Migration Complete!")
    logger.info(f"  ✅ Updated: {updated_count}")
    logger.info(f"  ⏭️  Skipped: {skipped_count}")
    logger.info(f"  ❌ Failed: {failed_count}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
