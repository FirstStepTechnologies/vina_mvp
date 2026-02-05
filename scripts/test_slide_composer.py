"""
Test script for Professional Slide Composer.
Tests both Text+Image and Text-Only templates.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.slide_composer import SlideComposer


def test_professional_slides():
    """Test the professional slide composer with both templates."""
    print("\n" + "="*60)
    print("🎨 Professional Slide Composer Test")
    print("="*60)
    
    # Check for test images
    test_images_dir = Path("cache/test_images/batch")
    if not test_images_dir.exists():
        print("❌ No test images found. Run test_imagen_client.py first.")
        return False
    
    image_files = sorted(list(test_images_dir.glob("*.png")))
    if len(image_files) < 3:
        print(f"❌ Need at least 3 images, found {len(image_files)}")
        return False
    
    print(f"✅ Found {len(image_files)} test images")
    
    # Initialize composer
    composer = SlideComposer(brand_name="VINA")
    
    # Test data
    slides_data = [
        {
            "title": "What are Large Language Models?",
            "bullets": [
                "AI systems trained on vast amounts of text data",
                "Can understand context and generate human-like responses"
            ],
            "image": image_files[0],
            "course_label": "AI Fundamentals"
        },
        {
            "title": "Key Capabilities",
            "bullets": [
                "Natural language understanding and generation",
                "Context-aware responses across conversations",
                "Multi-task learning without specific training",
                "Transfer learning to new domains"
            ],
            "image": None,  # Text-only slide
            "course_label": "AI Fundamentals"
        },
        {
            "title": "Real-World Applications",
            "bullets": [
                "Chatbots and virtual assistants",
                "Code generation and debugging"
            ],
            "image": image_files[1],
            "course_label": "AI Fundamentals"
        }
    ]
    
    # Compose slides
    output_dir = Path("cache/professional_slides")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📝 Composing {len(slides_data)} professional slides...")
    print(f"   Template: Text+Image (slides with images)")
    print(f"   Template: Text-Only (slides without images)")
    
    for i, slide_data in enumerate(slides_data):
        output_path = output_dir / f"slide_{i:02d}.png"
        
        try:
            template_type = "Text+Image" if slide_data["image"] else "Text-Only"
            
            result = composer.compose_slide(
                title=slide_data["title"],
                output_path=output_path,
                bullets=slide_data["bullets"],
                image_path=slide_data["image"],
                slide_number=i + 1,
                total_slides=len(slides_data),
                course_label=slide_data["course_label"]
            )
            
            size_kb = result.stat().st_size / 1024
            print(f"   ✅ Slide {i+1} ({template_type}): {result.name} ({size_kb:.1f} KB)")
            
        except Exception as e:
            print(f"   ❌ Slide {i+1} failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n✅ All slides composed successfully!")
    print(f"   Output directory: {output_dir}")
    print(f"\n💡 Design System Features:")
    print(f"   • 1080×1920 canvas (9:16 vertical)")
    print(f"   • Card-based layouts with rounded corners")
    print(f"   • Consistent spacing and typography")
    print(f"   • Professional color palette")
    print(f"   • Progress indicators")
    print(f"   • Brand logo (text-based)")
    
    return True


def main():
    """Run professional slide composer test."""
    success = test_professional_slides()
    
    if success:
        print("\n" + "="*60)
        print("✅ Professional Slide Composer Test Passed!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Professional Slide Composer Test Failed")
        print("="*60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
