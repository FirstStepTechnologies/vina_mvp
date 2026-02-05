"""
End-to-end pipeline test with realistic lesson data.
This is the full integration test for the hackathon demo.
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.video_pipeline import VideoPipeline, PipelineConfig


# Mock lesson data (realistic structure)
MOCK_LESSON = {
    "title": "Introduction to Large Language Models",
    "topic": "AI Fundamentals",
    "slides": [
        {
            "title": "What are Large Language Models?",
            "bullets": [
                "AI systems trained on vast amounts of text data",
                "Can understand context and generate human-like responses"
            ],
            "narration": "Large Language Models, or LLMs, are advanced AI systems that have been trained on massive amounts of text data from the internet. These models can understand context, generate human-like text, and perform a wide variety of language tasks.",
            "has_figure": True,
            "image_prompt": "A futuristic digital brain made of glowing neural networks and data streams, representing artificial intelligence and machine learning, modern tech aesthetic, vibrant blue and purple colors"
        },
        {
            "title": "How Do They Work?",
            "bullets": [
                "Use transformer architecture for parallel processing",
                "Learn patterns from billions of text examples",
                "Predict next words based on context",
                "Fine-tuned for specific tasks"
            ],
            "narration": "LLMs work using a transformer architecture that processes text in parallel rather than sequentially. They learn patterns from billions of examples during training, allowing them to predict what comes next in a sequence. These models can then be fine-tuned for specific applications.",
            "has_figure": False
        },
        {
            "title": "Real-World Applications",
            "bullets": [
                "Chatbots and virtual assistants",
                "Code generation and debugging"
            ],
            "narration": "Today, LLMs power many real-world applications. They're used in chatbots and virtual assistants that can have natural conversations with users. They also excel at code generation and debugging, helping developers write better software faster.",
            "has_figure": True,
            "image_prompt": "A modern workspace with holographic interfaces showing AI assistants helping with coding and communication, sleek futuristic design, warm lighting, professional atmosphere"
        }
    ]
}


async def test_end_to_end_pipeline():
    """Test the complete pipeline with realistic lesson data."""
    print("\n" + "="*60)
    print("🎬 End-to-End Video Pipeline Test")
    print("   Using realistic lesson data")
    print("="*60)
    
    lesson_data = MOCK_LESSON
    
    print(f"\n📚 Lesson: {lesson_data['title']}")
    print(f"   Topic: {lesson_data['topic']}")
    print(f"   Slides: {len(lesson_data['slides'])}")
    
    # Initialize pipeline
    config = PipelineConfig(
        cache_dir=Path("cache/end_to_end"),
        brand_name="VINA",
        course_label="AI Fundamentals"
    )
    
    pipeline = VideoPipeline(config)
    
    # Generate video
    output_path = Path("cache/final_videos") / "llm_intro_video.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🎥 Generating video...")
    print(f"   This will take a few minutes...")
    print(f"   Steps: Image Gen → TTS → Slide Composition → Video Rendering")
    
    try:
        video_path = await pipeline.generate_video_async(
            lesson_data=lesson_data,
            output_path=output_path,
            course_label="AI Fundamentals"
        )
        
        size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Video generated successfully!")
        print(f"   Path: {video_path}")
        print(f"   Size: {size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run end-to-end pipeline test."""
    success = asyncio.run(test_end_to_end_pipeline())
    
    if success:
        print("\n" + "="*60)
        print("✅ End-to-End Pipeline Test Passed!")
        print("="*60)
        print("\n🎉 Complete Video Generation Pipeline Working!")
        print("   • Image generation (Gemini)")
        print("   • Text-to-speech (ElevenLabs)")
        print("   • Professional slide composition")
        print("   • Video rendering (FFmpeg)")
        print("\n🚀 Ready for hackathon demo!")
    else:
        print("\n" + "="*60)
        print("❌ End-to-End Pipeline Test Failed")
        print("="*60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
