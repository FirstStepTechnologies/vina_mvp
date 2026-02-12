
import sys
from pathlib import Path
sys.path.append("src")
from vina_backend.integrations.db.engine import init_db, engine
from vina_backend.core.config import get_settings

print(f"CWD: {Path.cwd()}")
print(f"DB URL: {get_settings().database_url}")
try:
    init_db()
    print("✅ init_db success")
except Exception as e:
    print(f"❌ init_db failed: {e}")
