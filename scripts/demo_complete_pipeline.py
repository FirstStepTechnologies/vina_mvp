"""
COMPLETE END-TO-END DEMO SCRIPT
================================
Simulates the full VINA pipeline:
1. User inputs: profession, difficulty, lesson topic
2. LLM generates lesson content (simplified for demo)
3. Video pipeline creates professional video
4. Returns video path

This is the HACKATHON DEMO script!
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.services.video_pipeline import VideoPipeline, PipelineConfig


async def generate_lesson_with_llm(
    topic: str,
    profession: str,
    difficulty: str,
    num_slides: int = 3
) -> dict:
    """
    Generate lesson content using LLM (simplified for demo).
    
    Args:
        topic: Lesson topic
        profession: User's profession
        difficulty: Difficulty level
        num_slides: Number of slides to generate
    
    Returns:
        Lesson content dict with slides
    """
    llm_client = get_llm_client()
    
    # Create prompt for lesson generation
    prompt = f"""Generate a {num_slides}-slide educational lesson on "{topic}" for a {profession} at {difficulty} level.

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
    "title": "Lesson Title",
    "topic": "{topic}",
    "slides": [
        {{
            "title": "Slide Title",
            "bullets": ["Bullet point 1", "Bullet point 2"],
            "narration": "Full narration text for this slide (2-3 sentences)",
            "has_figure": true,
            "image_prompt": "Detailed image generation prompt"
        }}
    ]
}}

Requirements:
- Exactly {num_slides} slides
- Each slide must have 2-4 bullet points
- Narration should be 2-3 sentences (conversational, educational tone)
- For slides with has_figure=true, provide detailed image_prompt
- Alternate between slides with and without figures
- Make content relevant to {profession}
- Adjust complexity for {difficulty} level

Return ONLY the JSON, nothing else."""

    # Call LLM (run in thread pool since it's synchronous)
    import json
    loop = asyncio.get_event_loop()
    
    response = await loop.run_in_executor(
        None,
        lambda: llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000
        )
    )
    
    # Parse response
    content = response.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    lesson_data = json.loads(content)
    return lesson_data


async def generate_complete_lesson_video(
    profession: str,
    difficulty: str,
    lesson_topic: str,
    output_dir: Path = Path("cache/demo_videos")
):
    """
    Complete end-to-end pipeline: Generate lesson + Create video.
    
    Args:
        profession: User's profession (e.g., "Software Engineer")
        difficulty: Difficulty level ("beginner", "intermediate", "advanced")
        lesson_topic: Topic to teach (e.g., "Introduction to LLMs")
        output_dir: Where to save the final video
    
    Returns:
        Path to the generated video
    """
    print("\n" + "="*70)
    print("🎓 VINA - Complete Lesson Video Generation")
    print("="*70)
    
    print(f"\n📋 Input Parameters:")
    print(f"   Profession: {profession}")
    print(f"   Difficulty: {difficulty}")
    print(f"   Topic: {lesson_topic}")
    
    # ========================================
    # STEP 1: Generate Lesson Content with LLM
    # ========================================
    print("\n" + "="*70)
    print("STEP 1/2: Generating Lesson Content with LLM")
    print("="*70)
    
    print(f"\n🤖 Calling LLM to generate lesson...")
    print(f"   This may take 30-60 seconds...")
    
    try:
        lesson_content = await generate_lesson_with_llm(
            topic=lesson_topic,
            profession=profession,
            difficulty=difficulty,
            num_slides=3  # Keep it short for demo
        )
        
        print(f"\n✅ Lesson generated successfully!")
        print(f"   Title: {lesson_content.get('title', 'N/A')}")
        print(f"   Slides: {len(lesson_content.get('slides', []))}")
        
        # Show slide titles
        for i, slide in enumerate(lesson_content.get('slides', []), 1):
            has_img = "🖼️ " if slide.get('has_figure') else "📝 "
            print(f"   {has_img}Slide {i}: {slide.get('title', 'N/A')}")
        
    except Exception as e:
        print(f"\n❌ Lesson generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 2: Generate Video from Lesson
    # ========================================
    print("\n" + "="*70)
    print("STEP 2/2: Creating Professional Video")
    print("="*70)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = lesson_topic.lower().replace(" ", "_")[:30]
    video_filename = f"{safe_topic}_{difficulty}_{timestamp}.mp4"
    
    output_path = output_dir / video_filename
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize video pipeline
    pipeline_config = PipelineConfig(
        cache_dir=Path(f"cache/demo_pipeline_{timestamp}"),
        brand_name="VINA",
        course_label=f"{profession} - {difficulty.title()}"
    )
    
    pipeline = VideoPipeline(pipeline_config)
    
    print(f"\n🎬 Generating video...")
    print(f"   Steps: Image Gen → TTS → Slide Composition → Video Rendering")
    print(f"   This will take 2-5 minutes depending on slide count...")
    
    try:
        video_path = await pipeline.generate_video_async(
            lesson_data=lesson_content,
            output_path=output_path,
            course_label=f"{profession} - {difficulty.title()}"
        )
        
        size_mb = video_path.stat().st_size / (1024 * 1024)
        
        print(f"\n✅ Video created successfully!")
        print(f"   Path: {video_path}")
        print(f"   Size: {size_mb:.2f} MB")
        
        return video_path
        
    except Exception as e:
        print(f"\n❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def run_demo():
    """Run the complete demo with sample inputs."""
    
    # ========================================
    # Demo Scenarios
    # ========================================
    
    scenarios = [
        {
            "profession": "Software Engineer",
            "difficulty": "beginner",
            "topic": "Introduction to Large Language Models"
        },
        # Uncomment to test more scenarios:
        # {
        #     "profession": "Data Scientist",
        #     "difficulty": "intermediate",
        #     "topic": "Fine-tuning LLMs for Specific Tasks"
        # },
        # {
        #     "profession": "Product Manager",
        #     "difficulty": "beginner",
        #     "topic": "How AI Agents Work"
        # }
    ]
    
    print("\n" + "="*70)
    print("🚀 VINA HACKATHON DEMO")
    print("="*70)
    print(f"\nRunning {len(scenarios)} demo scenario(s)...")
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"Demo Scenario {i}/{len(scenarios)}")
        print(f"{'='*70}")
        
        video_path = await generate_complete_lesson_video(
            profession=scenario["profession"],
            difficulty=scenario["difficulty"],
            lesson_topic=scenario["topic"]
        )
        
        results.append({
            "scenario": scenario,
            "video_path": video_path,
            "success": video_path is not None
        })
    
    # ========================================
    # Summary
    # ========================================
    print("\n" + "="*70)
    print("📊 DEMO SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r["success"])
    
    print(f"\nCompleted: {successful}/{len(results)} scenarios")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        scenario = result["scenario"]
        print(f"\n{status} Scenario {i}:")
        print(f"   Topic: {scenario['topic']}")
        print(f"   Profession: {scenario['profession']}")
        print(f"   Difficulty: {scenario['difficulty']}")
        if result["video_path"]:
            print(f"   Video: {result['video_path']}")
    
    if successful == len(results):
        print("\n" + "="*70)
        print("🎉 ALL DEMOS SUCCESSFUL!")
        print("="*70)
        print("\n✨ Complete VINA Pipeline Working:")
        print("   1. ✅ User profiling (profession + difficulty)")
        print("   2. ✅ LLM-based lesson generation")
        print("   3. ✅ AI image generation (Gemini)")
        print("   4. ✅ Text-to-speech (ElevenLabs)")
        print("   5. ✅ Professional slide composition")
        print("   6. ✅ Video rendering (FFmpeg)")
        print("\n🚀 READY FOR HACKATHON PRESENTATION!")
        return True
    else:
        print("\n⚠️  Some demos failed. Check logs above.")
        return False


def main():
    """Main entry point."""
    success = asyncio.run(run_demo())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
