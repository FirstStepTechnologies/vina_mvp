"""
Test cross-provider fallback behavior.

This script demonstrates how the LLM client automatically falls back
across providers when one is unavailable.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.llm.client import LLMClient, FALLBACK_MODELS
from vina_backend.core.config import get_settings

def test_fallback_configuration():
    """Test that fallback models are properly configured."""
    
    print("=" * 80)
    print("🔧 Cross-Provider Fallback Configuration")
    print("=" * 80)
    
    for provider, fallbacks in FALLBACK_MODELS.items():
        print(f"\n📊 {provider.upper()} Fallback Chain:")
        print(f"   Primary: {provider}/<configured_model>")
        
        for i, (fallback_provider, fallback_model) in enumerate(fallbacks, 1):
            cross_provider = "🔀" if fallback_provider != provider else "↪️"
            print(f"   {cross_provider} Fallback {i}: {fallback_provider}/{fallback_model}")
    
    print("\n" + "=" * 80)
    print("✅ Fallback configuration loaded successfully!")
    print("=" * 80)


def test_api_key_availability():
    """Check which API keys are available for fallback."""
    
    print("\n" + "=" * 80)
    print("🔑 API Key Availability Check")
    print("=" * 80)
    
    settings = get_settings()
    
    providers = {
        "anthropic": settings.anthropic_api_key,
        "openai": settings.openai_api_key,
        "gemini": settings.gemini_api_key,
    }
    
    available_count = 0
    for provider, api_key in providers.items():
        if api_key:
            print(f"   ✅ {provider.upper()}: Available ({api_key[:8]}...)")
            available_count += 1
        else:
            print(f"   ❌ {provider.upper()}: Not configured")
    
    print(f"\n📊 Summary: {available_count}/3 providers configured")
    
    if available_count >= 2:
        print("   ✅ Cross-provider fallback is possible!")
    elif available_count == 1:
        print("   ⚠️  Only one provider configured - fallback limited")
    else:
        print("   ❌ No providers configured - fallback will fail")
    
    print("=" * 80)
    
    return available_count


def test_simple_generation():
    """Test a simple generation to verify fallback works."""
    
    print("\n" + "=" * 80)
    print("🧪 Testing Simple Generation with Fallback")
    print("=" * 80)
    
    try:
        client = LLMClient()
        
        print(f"\n📋 Initial Configuration:")
        info = client.get_info()
        print(f"   Provider: {info['provider']}")
        print(f"   Model: {info['model']}")
        print(f"   API Key: {info['api_key_preview']}")
        
        print(f"\n⏳ Generating response...")
        
        response = client.generate(
            prompt="Say 'Hello from AI' in exactly 3 words.",
            max_tokens=50,
            temperature=0.3
        )
        
        print(f"\n✅ Generation Successful!")
        print(f"   Response: {response}")
        
        # Check if provider/model changed (fallback occurred)
        final_info = client.get_info()
        if final_info['provider'] != info['provider'] or final_info['model'] != info['model']:
            print(f"\n🔀 Fallback Occurred!")
            print(f"   Original: {info['provider']}/{info['model']}")
            print(f"   Final: {final_info['provider']}/{final_info['model']}")
        else:
            print(f"\n✅ No fallback needed - primary model worked")
        
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ Generation Failed: {e}")
        print("=" * 80)
        return False


def show_fallback_example():
    """Show an example of what happens during fallback."""
    
    print("\n" + "=" * 80)
    print("📖 How Cross-Provider Fallback Works")
    print("=" * 80)
    
    print("""
When gemini-3-flash-preview fails with 503 (overloaded):

1️⃣  Primary: gemini/gemini-3-flash-preview
    ❌ 503 Error: Model overloaded
    
2️⃣  Fallback 1: gemini/gemini-2.5-flash (same provider)
    ⏳ Trying with same API key...
    ❌ Still overloaded or returns invalid JSON
    
3️⃣  Fallback 2: openai/gpt-4o-mini (cross-provider) 🔀
    ⏳ Switching to OpenAI API key...
    ✅ Success! Response received
    
4️⃣  Client state updated:
    - provider: gemini → openai
    - model: gemini-3-flash-preview → gpt-4o-mini
    - api_key: <gemini_key> → <openai_key>
    
5️⃣  Next call uses openai/gpt-4o-mini automatically

Benefits:
✅ Automatic failover across providers
✅ No code changes needed
✅ Uses fast, cheap models for fallback
✅ Graceful degradation
    """)
    
    print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Cross-Provider Fallback Test Suite\n")
    
    # Test 1: Show configuration
    test_fallback_configuration()
    
    # Test 2: Check API keys
    available = test_api_key_availability()
    
    # Test 3: Show how it works
    show_fallback_example()
    
    # Test 4: Try actual generation (only if keys available)
    if available > 0:
        success = test_simple_generation()
    else:
        print("\n⚠️  Skipping generation test - no API keys configured")
        success = None
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary:")
    print(f"   Configuration: ✅ Loaded")
    print(f"   API Keys: {available}/3 providers")
    if success is True:
        print(f"   Generation: ✅ Passed")
    elif success is False:
        print(f"   Generation: ❌ Failed")
    else:
        print(f"   Generation: ⏭️  Skipped")
    
    print("\n💡 Tip: Set ANTHROPIC_API_KEY, OPENAI_API_KEY, and GEMINI_API_KEY")
    print("   in your .env file to enable full cross-provider fallback!")
    print("=" * 80)
