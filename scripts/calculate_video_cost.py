import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from vina_backend.core.config import get_settings
from vina_backend.utils.logging import setup_logging
from vina_backend.services.lesson_generator import LessonGenerator
from vina_backend.services.video_pipeline import VideoPipeline
from vina_backend.integrations.opik_tracker import OpikTracker, COST_RATES
from vina_backend.domain.schemas.profile import UserProfileData

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

logger = logging.getLogger("COST_CALC")

def print_cost_report():
    """Print detailed cost breakdown from Opik session data."""
    tracker = OpikTracker()
    costs = getattr(tracker, "session_costs", [])
    
    print("\n" + "="*80)
    print("💰 VIDEO GENERATION COST BREAKDOWN (Estimated)")
    print("="*80)
    
    total_cost = 0.0
    by_service = {}
    by_type = {"LLM": 0.0, "Audio": 0.0, "Visual": 0.0}
    
    # Header
    print(f"{'OPERATION':<35} | {'SERVICE':<15} | {'UNIT':<10} | {'AMOUNT':<8} | {'COST ($)':<10}")
    print("-" * 90)
    
    for item in costs:
        op = item.get("operation", "unknown")
        svc = item.get("service", "unknown")
        unit = item.get("unit", "units")
        amt = item.get("amount", 0)
        cost = item.get("cost", 0.0)
        
        total_cost += cost
        by_service[svc] = by_service.get(svc, 0.0) + cost
        
        if svc in ["gemini", "openai"]:
            by_type["LLM"] += cost
        elif svc == "eleven_labs":
            by_type["Audio"] += cost
        elif svc == "imagen":
            by_type["Visual"] += cost
            
        print(f"{op[:35]:<35} | {svc[:15]:<15} | {unit:<10} | {str(amt):<8} | ${cost:.6f}")
        
    print("-" * 90)
    print(f"{'TOTAL ESTIMATED COST':<76} | ${total_cost:.4f}")
    print("="*80)
    
    print("\n📊 SERVICE SUMMARY:")
    for svc, amount in by_service.items():
        pct = (amount / total_cost * 100) if total_cost > 0 else 0
        print(f"  - {svc:<15}: ${amount:.4f} ({pct:.1f}%)")
        
    print("\n📈 TYPE SUMMARY:")
    for typ, amount in by_type.items():
        pct = (amount / total_cost * 100) if total_cost > 0 else 0
        print(f"  - {typ:<15}: ${amount:.4f} ({pct:.1f}%)")

async def run_cost_analysis():
    """Run full pipeline and track costs."""
    setup_logging()
    
    # 1. Setup Data
    user_profile = UserProfileData(
        id="cost_test_user",
        name="Alex Cost",
        profession="HR Manager",
        industry="Technology",
        experience_level="Intermediate",
        professional_goals=["Conflict Management", "Team Building"],
        safety_priorities=["Employee Retention", "Compliance"],
        high_stakes_areas=["Performance Reviews", "Disciplinary Actions"],
        interests=["Leadership", "Management"]
    )
    
    lesson_id = "l01_what_llms_are"
    logger.info(f"🚀 Starting Cost Analysis for: {lesson_id} (HR Manager)")
    
    # Initialize Tracker (clears session costs)
    tracker = OpikTracker()
    if hasattr(tracker, "session_costs"):
        tracker.session_costs = []
    
    # 2. Generate Lesson (LLM Cost)
    logger.info("📝 Phase 1: Generating Lesson Content...")
    generator = LessonGenerator()
    try:
        lesson_content = generator.generate_lesson(
            lesson_id=lesson_id,
            course_id="c_llm_foundations",
            user_profile=user_profile,
            difficulty_level=1
        )
            
        if not lesson_content:
            logger.error("Failed to generate lesson")
            return

        # 3. Generate Video (Audio + Image + LLM for prompts if applicable)
        logger.info("🎬 Phase 2: Generating Video Assets (Audio/Video)...")
        video_pipeline = VideoPipeline()
        
        output_file = Path("output/cost_test_video.mp4")
        
        # Override config if needed, or just let it run
        # VideoPipeline logic:
        # 1. Image Generation (Parallel) -> Uses ImagenClient
        # 2. Audio Generation (Parallel) -> Uses TTSClient
        
        # We need to ensure VideoPipeline actually calls the instrumented clients.
        # It imports them, so it should be fine.
        
        # Note: VideoPipeline expects a Dict, not Pydantic model usually
        # But get_lesson returns dict based on my previous knowledge of LessonGenerator
        # Let's check type.
        
        # Convert to dict
        full_lesson_dict = lesson_content if isinstance(lesson_content, dict) else lesson_content.dict()
        
        # VideoPipeline expects the content dict (with title, slides), not the wrapper
        content_dict = full_lesson_dict.get("lesson_content", full_lesson_dict)
        
        result = await video_pipeline.generate_video_async(
            lesson_data=content_dict, 
            output_path=output_file
        )
        
        logger.info(f"✅ Video generated at: {result.video_path}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        # Build report anyway so user sees partial costs
    
    # 4. Report
    print_cost_report()

if __name__ == "__main__":
    asyncio.run(run_cost_analysis())
