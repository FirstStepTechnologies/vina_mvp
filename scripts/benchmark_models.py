"""
LLM Model Benchmarking Script.

This script compares different LLM models for lesson generation and review.
It evaluates:
1. Latency (seconds)
2. Workflow Success (Success vs Fallback)
3. Quality (via LLM-as-a-Judge)
4. Cost Efficiency
"""
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.services.lesson_generator import LessonGenerator
from vina_backend.integrations.llm.client import LLMClient, get_llm_client
from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.integrations.db.engine import init_db
from vina_backend.services.profile_builder import get_or_create_user_profile

# Configuration
TEST_MODELS = [
    {"provider": "gemini", "model": "gemini-3-flash-preview", "name": "Gemini 3 Flash"},
    # {"provider": "gemini", "model": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
    {"provider": "openai", "model": "gpt-4o-mini", "name": "GPT-4o Mini"},
    # {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
]

JUDGE_MODEL = {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}

TEST_LESSONS = [
    {"course_id": "c_llm_foundations", "lesson_id": "l01_what_llms_are", "difficulty": 3},
]

TEST_PROFILES = [
    {"profession": "Clinical Researcher", "industry": "Pharma", "experience": "Intermediate"},
]

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("benchmark")

class ModelJudge:
    """Evaluates generated lessons using a high-quality model."""
    
    def __init__(self, provider: str, model: str):
        self.client = LLMClient(provider=provider, model=model)
        
    def evaluate(self, lesson_content: Dict[str, Any], user_profile: UserProfileData) -> Dict[str, Any]:
        """Judge a lesson content against criteria."""
        prompt = f"""
### TASK: ACT AS AN EXPERT INSTRUCTIONAL DESIGNER AND EVALUATE THIS AI-GENERATED MICRO-LESSON.

### TARGET LEARNER:
- Profession: {user_profile.profession}
- Industry: {user_profile.industry}
- Experience: {user_profile.experience_level}

### LESSON CONTENT:
{json.dumps(lesson_content, indent=2)}

### EVALUATION CRITERIA (Score 1-10 each):
1. **Persona Alignment**: Does it use relevant examples from the user's daily work?
2. **Pedagogical Flow**: Is there a clear hook -> concept -> application flow?
3. **Safety & Realism**: Are high-stakes areas handled with appropriate warnings?
4. **Tone & Style**: Is it professional yet engaging?
5. **JSON Quality**: Is the structure perfectly followed? (10 if perfect, 1 if broken)

### RETURN FORMAT:
Return ONLY a JSON object with:
{{
  "scores": {{
    "persona_alignment": 0,
    "pedagogical_flow": 0,
    "safety_realism": 0,
    "tone_style": 0,
    "json_quality": 0
  }},
  "average_score": 0.0,
  "justification": "Short explanation of the scores.",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."]
}}
"""
        try:
            result = self.client.generate_json(prompt, temperature=0.3)
            return result
        except Exception as e:
            logger.error(f"Judge evaluation failed: {e}")
            return {"error": str(e)}

def run_benchmark():
    """Main benchmarking loop."""
    print("\n" + "=" * 80)
    print("🚀 Vina LLM Benchmarking Report")
    print("=" * 80)
    
    init_db()
    judge = ModelJudge(**JUDGE_MODEL)
    
    results = []
    
    for profile_config in TEST_PROFILES:
        profile = get_or_create_user_profile(
            profession=profile_config["profession"],
            industry=profile_config["industry"],
            experience_level=profile_config["experience"]
        )
        
        for lesson_config in TEST_LESSONS:
            print(f"\n📊 Testing Lesson: {lesson_config['lesson_id']} for {profile.profession}")
            
            for model_info in TEST_MODELS:
                print(f"\n⏳ Model: {model_info['name']} ({model_info['model']})...")
                
                # Custom client for this specific model
                try:
                    client = LLMClient(
                        provider=model_info["provider"],
                        model=model_info["model"]
                    )
                    generator = LessonGenerator(llm_client=client)
                    
                    # Benchmark generation
                    start_time = time.time()
                    generated_lesson = generator.generate_lesson(
                        lesson_id=lesson_config["lesson_id"],
                        course_id=lesson_config["course_id"],
                        user_profile=profile,
                        difficulty_level=lesson_config["difficulty"],
                        bypass_cache=True # ALWAYS bypass cache for benchmark
                    )
                    end_time = time.time()
                    latency = end_time - start_time
                    
                    # Judge the result
                    print(f"   ⚖️  Judging quality...")
                    evaluation = judge.evaluate(
                        generated_lesson.lesson_content.model_dump(),
                        profile
                    )
                    
                    # Collect data
                    metadata = generated_lesson.generation_metadata
                    is_fallback = "Temporarily Unavailable" in generated_lesson.lesson_content.lesson_title or \
                                 generated_lesson.lesson_id != lesson_config["lesson_id"]
                    
                    res = {
                        "model_name": model_info["name"],
                        "model_id": model_info["model"],
                        "latency": round(latency, 2),
                        "success": not is_fallback,
                        "rewrites": metadata.rewrite_count,
                        "passed_first": metadata.review_passed_first_time,
                        "judge_score": evaluation.get("average_score", 0),
                        "judge_notes": evaluation.get("justification", "N/A"),
                        "judge_strengths": evaluation.get("strengths", []),
                        "judge_weaknesses": evaluation.get("weaknesses", [])
                    }
                    results.append(res)
                    
                    print(f"   ✅ Latency: {res['latency']}s | Judge Score: {res['judge_score']}/10")
                    if not res["success"]:
                        print(f"   ⚠️  MODE: FALLBACK TRIGGERED")
                        
                except Exception as e:
                    print(f"   ❌ Model execution failed: {e}")
                    results.append({
                        "model_name": model_info["name"],
                        "error": str(e)
                    })

    # Generate Markdown Report
    generate_report(results)

def generate_report(results: List[Dict]):
    """Creates a markdown report of the benchmark."""
    report_path = Path("BENCHMARK_REPORT.md")
    
    lines = [
        "# Vina LLM Benchmark Report",
        f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## Summary Table",
        "| Model | Success | Latency | Pass 1st | Rewrites | Judge Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for r in results:
        if "error" in r:
            lines.append(f"| {r['model_name']} | ❌ ERROR | - | - | - | - |")
            continue
            
        success_icon = "✅" if r["success"] else "⚠️ (Fallback)"
        pass_first = "✅" if r["passed_first"] else "❌"
        
        lines.append(
            f"| {r['model_name']} | {success_icon} | {r['latency']}s | {pass_first} | {r['rewrites']} | **{r['judge_score']}** |"
        )
    
    lines.append("\n## Detailed Analysis")
    for r in results:
        if "error" in r:
            lines.append(f"\n### {r['model_name']}\n- ❌ ERROR: {r['error']}")
            continue
            
        lines.append(f"\n### {r['model_name']}")
        lines.append(f"- **Final Model Used:** `{r['model_id']}`")
        lines.append(f"- **Judge Justification:** {r['judge_notes']}")
        
        if r["judge_strengths"]:
            lines.append("- **Strengths:**")
            for s in r["judge_strengths"]:
                lines.append(f"  - {s}")
                
        if r["judge_weaknesses"]:
            lines.append("- **Weaknesses:**")
            for w in r["judge_weaknesses"]:
                lines.append(f"  - {w}")
                
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    
    print("\n" + "=" * 80)
    print(f"✅ Benchmark Complete! Report saved to {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
