#!/usr/bin/env python3
"""
Database migration script to add video_url column to lesson_cache table.

This migration is needed because the video_url field was added to the LessonCache
model after some databases were already created.

Usage:
    uv run scripts/migrate_add_video_url.py
"""

import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.core.config import get_settings

def main():
    """Add video_url column to lesson_cache table if it doesn't exist."""
    settings = get_settings()
    
    # Extract database path from DATABASE_URL
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        print(f"❌ Unsupported database URL format: {db_url}")
        return
    
    print(f"🔍 Checking database: {db_path}")
    
    if not Path(db_path).exists():
        print(f"⚠️  Database file not found. It will be created on first use.")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(lesson_cache)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "video_url" in columns:
            print("✅ Column 'video_url' already exists. No migration needed.")
            return
        
        # Add the column
        print("🔧 Adding 'video_url' column to lesson_cache table...")
        cursor.execute("""
            ALTER TABLE lesson_cache 
            ADD COLUMN video_url TEXT DEFAULT NULL
        """)
        
        conn.commit()
        print("✅ Migration successful! Column 'video_url' added.")
        
        # Verify
        cursor.execute("PRAGMA table_info(lesson_cache)")
        columns = [row[1] for row in cursor.fetchall()]
        if "video_url" in columns:
            print("✅ Verification passed.")
        else:
            print("❌ Verification failed. Column not found after migration.")
            
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
