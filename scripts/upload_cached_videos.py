"""
Script to upload locally cached videos to Cloudinary and generate a manifest.
Run this once to migrate existing assets.
"""
import sys
import json
import logging
from pathlib import Path
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.cloudinary.client import CloudinaryClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache/global_assets/videos")
DEMO_DIR = Path("cache/demo_videos")
MANIFEST_FILE = Path("src/vina_backend/domain/constants/video_manifest.json")

def main():
    client = CloudinaryClient()
    
    # Load existing manifest if any
    manifest = {}
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, "r") as f:
                manifest = json.load(f)
        except Exception:
            pass
            
    # Collect all video files
    files_to_upload = []
    
    # 1. Global Cache (Content Hash based)
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.mp4"):
            files_to_upload.append(f)
            
    # 2. Demo Videos (Named)
    if DEMO_DIR.exists():
        for f in DEMO_DIR.glob("*.mp4"):
            files_to_upload.append(f)
            
    logger.info(f"Found {len(files_to_upload)} videos to process.")
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for file_path in tqdm(files_to_upload, desc="Uploading Videos"):
        # Use filename (without extension) as key
        key = file_path.stem
        
        # Skip if already in manifest
        if key in manifest:
            skipped_count += 1
            continue
            
        try:
            # Upload
            url = client.upload_video(file_path, public_id=key)
            manifest[key] = url
            updated_count += 1
        except Exception as e:
            logger.error(f"Failed to upload {file_path.name}: {e}")
            failed_count += 1
            
    # Save manifest
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
        
    logger.info(f"Migration Complete.")
    logger.info(f"  Uploaded: {updated_count}")
    logger.info(f"  Skipped: {skipped_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info(f"  Manifest saved to {MANIFEST_FILE}")

if __name__ == "__main__":
    main()
