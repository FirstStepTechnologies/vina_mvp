"""
Test script for Video Renderer.
Tests creating MP4 videos from slides and audio.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.video_renderer import VideoRenderer


def test_video_rendering():
    """Test rendering videos from slides and audio."""
    print("\n" + "="*60)
    print("🎬 Video Renderer Test")
    print("="*60)
    
    # Check for test slides
    slides_dir = Path("cache/professional_slides")
    if not slides_dir.exists():
        print("❌ No test slides found. Run test_slide_composer.py first.")
        return False
    
    slide_files = sorted(list(slides_dir.glob("*.png")))
    if len(slide_files) < 3:
        print(f"❌ Need at least 3 slides, found {len(slide_files)}")
        return False
    
    # Check for test audio
    audio_dir = Path("cache/test_audio/batch")
    if not audio_dir.exists():
        print("❌ No test audio found. Run test_tts_client.py first.")
        return False
    
    audio_files = sorted(list(audio_dir.glob("*.mp3")))
    if len(audio_files) < 3:
        print(f"❌ Need at least 3 audio files, found {len(audio_files)}")
        return False
    
    print(f"✅ Found {len(slide_files)} slides and {len(audio_files)} audio files")
    
    # Initialize renderer
    try:
        renderer = VideoRenderer()
    except RuntimeError as e:
        print(f"❌ {e}")
        return False
    
    # Test 1: Single slide video
    print("\n" + "="*60)
    print("Test 1: Single Slide Video")
    print("="*60)
    
    output_dir = Path("cache/test_videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        single_output = output_dir / "single_slide.mp4"
        renderer.render_video(
            slides=[slide_files[0]],
            audio_files=[audio_files[0]],
            output_path=single_output
        )
        
        size_mb = single_output.stat().st_size / (1024 * 1024)
        print(f"✅ Single slide video created: {single_output.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"❌ Single slide test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Multi-slide video with transitions
    print("\n" + "="*60)
    print("Test 2: Multi-Slide Video (3 slides with transitions)")
    print("="*60)
    
    try:
        multi_output = output_dir / "multi_slide.mp4"
        renderer.render_video(
            slides=slide_files[:3],
            audio_files=audio_files[:3],
            output_path=multi_output,
            transition_duration=0.3
        )
        
        size_mb = multi_output.stat().st_size / (1024 * 1024)
        print(f"✅ Multi-slide video created: {multi_output.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"❌ Multi-slide test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n✅ All videos rendered successfully!")
    print(f"   Output directory: {output_dir}")
    print(f"\n💡 Video Features:")
    print(f"   • 1080×1920 vertical format (TikTok-ready)")
    print(f"   • Synchronized audio and slides")
    print(f"   • Smooth crossfade transitions")
    print(f"   • High-quality H.264 encoding")
    print(f"   • AAC audio (192kbps)")
    
    return True


def main():
    """Run video renderer test."""
    success = test_video_rendering()
    
    if success:
        print("\n" + "="*60)
        print("✅ Video Renderer Test Passed!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Video Renderer Test Failed")
        print("="*60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
