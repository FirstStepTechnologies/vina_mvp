"""
Test script for ElevenLabs TTS client.
Tests single and batch audio generation.
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.elevenlabs.tts_client import TTSClient


async def test_single_audio():
    """Test generating a single audio file."""
    print("\n" + "="*60)
    print("Test 1: Single Audio Generation")
    print("="*60)
    
    client = TTSClient(max_concurrent=3)
    
    text = "Welcome to this lesson on Large Language Models. In this video, we'll explore what LLMs are and how they work."
    output_path = Path("cache/test_audio/single_test.mp3")
    
    try:
        result = await client.generate_audio_async(
            text=text,
            output_path=output_path
        )
        
        print(f"✅ Audio generated successfully")
        print(f"   Path: {result}")
        print(f"   Size: {result.stat().st_size / 1024:.1f} KB")
        print(f"   Text length: {len(text)} characters")
        
        # Check if file exists and has content
        if result.stat().st_size > 0:
            print(f"   ✅ File has content")
            return True
        else:
            print(f"   ❌ File is empty")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_audio():
    """Test generating multiple audio files in parallel."""
    print("\n" + "="*60)
    print("Test 2: Batch Audio Generation (3 files)")
    print("="*60)
    
    client = TTSClient(max_concurrent=2)  # Test concurrency limiting
    
    texts = [
        "Large Language Models are AI systems trained on vast amounts of text data.",
        "They can understand context, generate human-like responses, and perform various language tasks.",
        "Popular examples include GPT-4, Claude, and Gemini."
    ]
    
    output_dir = Path("cache/test_audio/batch")
    
    try:
        import time
        start_time = time.time()
        
        results = await client.generate_audio_batch(
            texts=texts,
            output_dir=output_dir
        )
        
        elapsed = time.time() - start_time
        
        successful = sum(1 for r in results if r is not None)
        print(f"\n✅ Generated {successful}/{len(texts)} audio files in {elapsed:.1f}s")
        
        for i, path in enumerate(results):
            if path:
                size_kb = path.stat().st_size / 1024
                print(f"   Audio {i+1}: {path.name} ({size_kb:.1f} KB)")
            else:
                print(f"   Audio {i+1}: ❌ Failed")
        
        return successful == len(texts)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test retry logic with invalid API key."""
    print("\n" + "="*60)
    print("Test 3: Error Handling (Invalid API Key)")
    print("="*60)
    
    # Create client with invalid key
    client = TTSClient(api_key="invalid_key_for_testing", max_concurrent=1)
    
    text = "Test audio"
    output_path = Path("cache/test_audio/error_test.mp3")
    
    try:
        await client.generate_audio_async(text, output_path)
        print("❌ Should have failed with invalid key")
        return False
    except Exception as e:
        print(f"✅ Correctly caught error: {type(e).__name__}")
        print(f"   Message: {str(e)[:100]}...")
        return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 ElevenLabs TTS Client Test Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Single audio
    results.append(await test_single_audio())
    
    # Test 2: Batch audio
    results.append(await test_batch_audio())
    
    # Test 3: Error handling
    results.append(await test_error_handling())
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
