#!/usr/bin/env python3
"""
Diagnostic script to show all cached videos in the database.
Shows lesson, difficulty, adaptation context, and video URL status.

Usage:
    uv run scripts/check_video_cache.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.db.engine import init_db, engine
from vina_backend.services.lesson_cache import LessonCache
from sqlmodel import Session, select

def main():
    """Display all cached videos in a readable table format."""
    init_db()
    
    with Session(engine) as session:
        statement = select(LessonCache).order_by(
            LessonCache.course_id,
            LessonCache.lesson_id,
            LessonCache.difficulty_level,
            LessonCache.adaptation_context
        )
        entries = session.exec(statement).all()
        
        if not entries:
            print("📭 No cached lessons found in database.")
            return
        
        print("=" * 120)
        print(f"{'LESSON':<25} {'DIFF':<6} {'ADAPTATION':<20} {'VIDEO URL':<50} {'CREATED':<20}")
        print("=" * 120)
        
        for entry in entries:
            lesson_display = f"{entry.course_id}/{entry.lesson_id}"
            diff_display = f"D{entry.difficulty_level}"
            adaptation_display = entry.adaptation_context or "(none)"
            
            # Video URL status
            if entry.video_url:
                # Truncate long URLs
                url_display = entry.video_url[:47] + "..." if len(entry.video_url) > 50 else entry.video_url
                url_status = "✅ " + url_display
            else:
                url_status = "❌ No video"
            
            created_display = entry.created_at.strftime("%Y-%m-%d %H:%M") if entry.created_at else "N/A"
            
            print(f"{lesson_display:<25} {diff_display:<6} {adaptation_display:<20} {url_status:<50} {created_display:<20}")
        
        print("=" * 120)
        print(f"\n📊 Total cached entries: {len(entries)}")
        
        # Summary stats
        with_video = sum(1 for e in entries if e.video_url)
        without_video = len(entries) - with_video
        
        print(f"   ✅ With video URL: {with_video}")
        print(f"   ❌ Without video URL: {without_video}")
        
        # Adaptation breakdown
        adaptations = {}
        for entry in entries:
            ctx = entry.adaptation_context or "normal"
            adaptations[ctx] = adaptations.get(ctx, 0) + 1
        
        print(f"\n📈 By Adaptation Type:")
        for ctx, count in sorted(adaptations.items()):
            print(f"   - {ctx}: {count}")

if __name__ == "__main__":
    main()
