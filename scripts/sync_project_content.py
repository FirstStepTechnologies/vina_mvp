"""
Script to sync generated lesson content (video URLs, etc) between environments
WITHOUT overwriting user data.

Usage:
    # EXPORT mode (Local Machine):
    # Dumps 'lesson_cache' table to 'data/content_export.json'
    python scripts/sync_project_content.py export

    # IMPORT mode (Render Production):
    # Reads 'data/content_export.json' and upserts into local DB
    python scripts/sync_project_content.py import
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import Session, select, text
from vina_backend.integrations.db.engine import engine, init_db
from vina_backend.services.lesson_cache import LessonCache
from vina_backend.core.config import get_settings

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SYNC")

DATA_DIR = Path(__file__).parent.parent / "data"
EXPORT_FILE = DATA_DIR / "content_export.json"

def export_content():
    """Export lesson_cache table to JSON."""
    logger.info("🚀 Starting Content Export...")
    
    init_db()
    
    with Session(engine) as session:
        # Fetch all cached lessons that have a video_url (meaning they are completed assets)
        # We export EVERYTHING in cache to be safe, but focus on content-complete ones
        statement = select(LessonCache)
        results = session.exec(statement).all()
        
        logger.info(f"Found {len(results)} lesson cache entries.")
        
        export_data = []
        for entry in results:
            # Convert SQLModel to dict
            data = entry.model_dump()
            
            # Handle datetime serialization
            if data.get("created_at"):
                data["created_at"] = data["created_at"].isoformat()
            if data.get("accessed_at"):
                data["accessed_at"] = data["accessed_at"].isoformat()
                
            export_data.append(data)
            
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True)
        
        with open(EXPORT_FILE, "w") as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"✅ Exported {len(export_data)} entries to {EXPORT_FILE}")
        logger.info("👉 Check this file into git!")

def check_and_migrate_schema():
    """Ensure the database has all required columns before importing."""
    import sqlite3
    from urllib.parse import urlparse
    
    settings = get_settings()
    db_url = settings.database_url
    
    # Extract file path from sqlite:///
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        # Remove any leading fourth slash (common in Render paths)
        if db_path.startswith("/"):
             pass # Absolute path is fine
    else:
        logger.warning(f"Not a local SQLite DB, skipping auto-migration: {db_url}")
        return

    logger.info(f"Checking schema for {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(lesson_cache)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_migrations = [
            ("video_url", "TEXT"),
            ("adaptation_context", "TEXT")
        ]
        
        for col_name, col_type in required_migrations:
            if col_name not in columns:
                logger.info(f"➕ Adding missing column: {col_name}")
                cursor.execute(f"ALTER TABLE lesson_cache ADD COLUMN {col_name} {col_type}")
        
        conn.commit()
        conn.close()
        logger.info("✅ Schema check complete.")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")

def import_content():
    """Import content from JSON to DB (Upsert)."""
    logger.info("🚀 Starting Content Import...")
    
    # --- NEW: Auto-Migrate Schema ---
    check_and_migrate_schema()
    
    if not EXPORT_FILE.exists():
        logger.error(f"❌ Export file not found: {EXPORT_FILE}")
        return

    try:
        with open(EXPORT_FILE, "r") as f:
            import_data = json.load(f)
    except json.JSONDecodeError:
        logger.error(f"❌ Failed to parse {EXPORT_FILE}")
        return
        
    logger.info(f"Loaded {len(import_data)} entries from JSON.")
    
    init_db()
    
    with Session(engine) as session:
        upsert_count = 0
        new_count = 0
        
        for item in import_data:
            cache_key = item["cache_key"]
            
            # Check if exists
            try:
                statement = select(LessonCache).where(LessonCache.cache_key == cache_key)
                existing = session.exec(statement).first()
            except Exception as e:
                logger.error(f"❌ Error querying cache_key {cache_key}: {e}")
                continue
            
            # Convert ISO formatted strings back to datetime objects if needed
            # (SQLModel often handles this automatically, but explicitly safe)
            if "created_at" in item and isinstance(item["created_at"], str):
                 try: item["created_at"] = datetime.fromisoformat(item["created_at"])
                 except: pass
            if "accessed_at" in item and isinstance(item["accessed_at"], str):
                 try: item["accessed_at"] = datetime.fromisoformat(item["accessed_at"])
                 except: pass

            if existing:
                # Update logic: we generally trust the JSON export as source of truth for content
                # But we might want to preserve local access stats. 
                # For simplicity: We overwrite fields that matter for content.
                
                # Only update if the export has a video_url (valuable)
                if item.get("video_url"):
                    existing.video_url = item["video_url"]
                    existing.lesson_json = item["lesson_json"]
                    existing.adaptation_context = item.get("adaptation_context") # important for new schema
                    
                    # Update other fields as needed
                    session.add(existing)
                    upsert_count += 1
            else:
                # Insert new
                # Filter out 'id' to let DB auto-increment
                if "id" in item:
                    del item["id"]
                    
                new_entry = LessonCache(**item)
                session.add(new_entry)
                new_count += 1
        
        session.commit()
        logger.info(f"✅ Import Complete: {new_count} new, {upsert_count} updated.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/sync_project_content.py [export|import]")
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    
    if mode == "export":
        export_content()
    elif mode == "import":
        import_content()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
