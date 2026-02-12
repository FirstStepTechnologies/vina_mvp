
import sqlite3
from pathlib import Path

DB_PATH = Path("data/vina.db")

def migrate():
    if not DB_PATH.exists():
        print(f"❌ DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("repare to add missing columns to 'lesson_cache'...")

    # Check existing columns
    cursor.execute("PRAGMA table_info(lesson_cache)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")

    # Add video_url if missing
    if "video_url" not in columns:
        print("➕ Adding 'video_url' column...")
        try:
            cursor.execute("ALTER TABLE lesson_cache ADD COLUMN video_url TEXT")
            print("   Done.")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("✅ 'video_url' already exists.")

    # Add adaptation_context if missing
    if "adaptation_context" not in columns:
        print("➕ Adding 'adaptation_context' column...")
        try:
            cursor.execute("ALTER TABLE lesson_cache ADD COLUMN adaptation_context TEXT")
            print("   Done.")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("✅ 'adaptation_context' already exists.")

    conn.commit()
    conn.close()
    print("🏁 Migration check complete.")

if __name__ == "__main__":
    migrate()
