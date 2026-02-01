"""
Quick test script for profile generation.
Run this to verify profile generation works with different LLM providers.
"""
import json
import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.profile_builder import get_or_create_user_profile
from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.utils.logging import setup_logging
from vina_backend.integrations.db.engine import init_db


def test_profile_generation(force: bool = False):
    """Test generating profiles for each profession/industry combination."""
    
    # Show which LLM provider we're using
    client = get_llm_client()
    info = client.get_info()
    
    print("=" * 80)
    print(f"🧪 Testing User Profile Generation")
    print(f"🤖 Provider: {info['provider']}")
    print(f"📦 Model: {info['model']}")
    print(f"🔑 API Key: {info['api_key_preview']}")
    print("=" * 80)
    
    test_cases = [
        ("Clinical Researcher", "Pharma/Biotech", "Intermediate"),
        ("HR Manager", "Tech Company", "Beginner"),
        ("Project Manager", "Software/Tech", "Intermediate"),
        ("Marketing Manager", "E-Commerce", "Intermediate"),
    ]

    test_cases = [
        # ("Clinical Researcher", "Pharma/Biotech", "Intermediate"),
        ("HR Manager", "Tech Company", "Beginner"),
        # ("Project Manager", "Software/Tech", "Intermediate"),
        # ("Marketing Manager", "E-Commerce", "Intermediate"),
    ]
    
    results = []
    
    for profession, industry, experience in test_cases:
        print(f"\n📋 Generating profile: {profession} in {industry} ({experience})")
        print("-" * 80)
        
        try:
            profile = get_or_create_user_profile(profession, industry, experience, force_refresh=force)
            
            print(f"✅ Success!")
            print(f"\nProfession: {profile.profession}")
            print(f"Industry: {profile.industry}")
            print(f"Technical Comfort: {profile.technical_comfort_level}")
            print(f"\nDaily Responsibilities ({len(profile.daily_responsibilities)}):")
            for resp in profile.daily_responsibilities:
                print(f"  - {resp}")
            print(f"\nPain Points ({len(profile.pain_points)}):")
            for pain in profile.pain_points:
                print(f"  - {pain}")
            print(f"\nTypical Outputs ({len(profile.typical_outputs)}):")
            for output in profile.typical_outputs:
                print(f"  - {output}")
            print(f"\nLearning Style: {profile.learning_style_notes}")
            
            results.append(("✅", profession, industry))
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            results.append(("❌", profession, industry))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary")
    print("=" * 80)
    for status, profession, industry in results:
        print(f"{status} {profession} in {industry}")
    
    success_count = sum(1 for status, _, _ in results if status == "✅")
    print(f"\n✅ {success_count}/{len(results)} profiles generated successfully")


def test_provider_switching():
    """
    Test switching between providers (if multiple API keys are configured).
    This is optional and only runs if you want to compare providers.
    """
    print("\n" + "=" * 80)
    print("🔄 Testing Provider Switching (Optional)")
    print("=" * 80)
    
    from vina_backend.core.config import get_settings
    from vina_backend.integrations.llm.client import LLMClient, reset_llm_client
    
    settings = get_settings()
    
    providers_to_test = []
    if settings.anthropic_api_key:
        providers_to_test.append(("anthropic", "claude-sonnet-4-20250514"))
    if settings.openai_api_key:
        providers_to_test.append(("openai", "gpt-4o-mini"))
    if settings.gemini_api_key:
        providers_to_test.append(("gemini", "gemini-3-flash"))
    
    if len(providers_to_test) < 2:
        print("⏭️  Skipping (only one provider configured)")
        return
    
    test_profession = "Clinical Researcher"
    test_industry = "Pharma/Biotech"
    test_experience = "Intermediate"
    
    for provider, model in providers_to_test:
        print(f"\n🔄 Testing with {provider}/{model}")
        print("-" * 80)
        
        try:
            # Create a new client with this provider
            client = LLMClient(provider=provider, model=model)
            
            # Generate a profile
            from vina_backend.services.profile_builder import generate_user_profile
            profile = generate_user_profile(
                test_profession, 
                test_industry, 
                test_experience
            )
            
            print(f"✅ Generated profile with {provider}")
            print(f"   Technical Comfort: {profile.technical_comfort_level}")
            print(f"   Responsibilities: {len(profile.daily_responsibilities)} items")
            
        except Exception as e:
            print(f"❌ Failed with {provider}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test profile generation")
    parser.add_argument("--force", action="store_true", help="Force regeneration of profiles")
    args = parser.parse_args()

    setup_logging()
    init_db()  # Initialize database tables
    test_profile_generation(force=args.force)
    
    # Uncomment to test provider switching
    # test_provider_switching()