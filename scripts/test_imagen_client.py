"""
Test script for Imagen client.
Tests single and batch image generation.
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.imagen.client import ImagenClient


async def test_single_image():
    """Test generating a single image."""
    print("\n" + "="*60)
    print("Test 1: Single Image Generation")
    print("="*60)
    
    client = ImagenClient(max_concurrent=3)
    
    prompt = "A modern professional office with large windows, natural lighting, clean desk with laptop"
    output_path = Path("cache/test_images/single_test.png")
    
    try:
        result = await client.generate_image_async(
            prompt=prompt,
            output_path=output_path,
            style="professional"
        )
        
        print(f"✅ Image generated successfully")
        print(f"   Path: {result}")
        print(f"   Size: {result.stat().st_size / 1024:.1f} KB")
        
        # Verify it's a valid PNG
        from PIL import Image
        img = Image.open(result)
        print(f"   Dimensions: {img.size[0]}x{img.size[1]}")
        print(f"   Expected: 1080x1920 (9:16 vertical)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_batch_images():
    """Test generating multiple images in parallel."""
    print("\n" + "="*60)
    print("Test 2: Batch Image Generation (3 images)")
    print("="*60)
    
    client = ImagenClient(max_concurrent=2)  # Test concurrency limiting
    
    prompts = [
        "Abstract technology background with circuit patterns, blue and purple gradient",
        "Professional business meeting room with modern furniture",
        "Data visualization dashboard with charts and graphs, clean modern design"
    ]
    
    output_dir = Path("cache/test_images/batch")
    
    try:
        import time
        start_time = time.time()
        
        results = await client.generate_images_batch(
            prompts=prompts,
            output_dir=output_dir,
            style="professional"
        )
        
        elapsed = time.time() - start_time
        
        successful = sum(1 for r in results if r is not None)
        print(f"\n✅ Generated {successful}/{len(prompts)} images in {elapsed:.1f}s")
        
        for i, path in enumerate(results):
            if path:
                size_kb = path.stat().st_size / 1024
                print(f"   Image {i+1}: {path.name} ({size_kb:.1f} KB)")
            else:
                print(f"   Image {i+1}: ❌ Failed")
        
        return successful == len(prompts)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_error_handling():
    """Test retry logic with invalid prompt."""
    print("\n" + "="*60)
    print("Test 3: Error Handling (Invalid API Key)")
    print("="*60)
    
    # Create client with invalid key
    client = ImagenClient(api_key="invalid_key_for_testing", max_concurrent=1)
    
    prompt = "Test image"
    output_path = Path("cache/test_images/error_test.png")
    
    try:
        await client.generate_image_async(prompt, output_path)
        print("❌ Should have failed with invalid key")
        return False
    except Exception as e:
        print(f"✅ Correctly caught error: {type(e).__name__}")
        print(f"   Message: {str(e)[:100]}...")
        return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 Imagen Client Test Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Single image
    results.append(await test_single_image())
    
    # Test 2: Batch images
    results.append(await test_batch_images())
    
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
