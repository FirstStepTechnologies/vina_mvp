
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.llm.client import get_llm_client
from vina_backend.services.course_loader import load_course_config
from vina_backend.utils.logging import setup_logging

setup_logging("INFO")
logger = logging.getLogger("QUIZ_GEN")

COURSE_ID = "c_llm_foundations"
OUTPUT_FILE = Path(__file__).parent.parent / "src/vina_backend/domain/constants/onboarding_quizzes.json"

TARGET_PROFESSIONS = [
    "Clinical Researcher",
    "HR Manager",
    "Project Manager", 
    "Marketing Manager"
]

# --- Data Models ---
class QuizOption(BaseModel):
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    id: str
    text: str
    options: List[QuizOption]
    associated_stage: str # foundations, application, mastery
    complexity_level: int # 1-10
    rationale: str # Why this question fits this stage/profession

class ProfessionQuiz(BaseModel):
    profession: str
    questions: List[QuizQuestion]

# --- Educator Prompt ---
# Designed to force the LLM to act as a pedagogical expert.
PROMPT_TEMPLATE = """
You are a **Master Technical Educator** specifying a placement assessment for a new course: "LLM Foundations".

**Goal:** Create a 5-question placement quiz for a **{profession}**.
This quiz will determine where the learner starts in the curriculum.

**Curriculum Structure (The "Truth"):**
{course_structure}

**Design Principles:**
1.  **Strict Progression (5 Questions):**
    *   **Q1-Q2 (Foundations):** Test basic literacy. (Terms: Hallucinations, Tokens, Context).
    *   **Q3-Q4 (Application):** Test ability to identify high-ROI use cases and safety risks specific to **{profession}**.
    *   **Q5 (Mastery):** Test advanced prompting strategies or deployment (Cloud vs Local).
    
2.  **Profession-First Context:**
    *   DO NOT ask generic questions like "What is an LLM?".
    *   DO ask: "As a {profession}, you need to summarize candidate resumes. Which limitation should you be most aware of?"
    *   Use terminology relevant to {profession} (e.g., "protocols" for Researchers, "campaigns" for Marketers).

3.  **Distractor Design:**
    *   Wrong answers must be *plausible misconceptions* (e.g., "LLMs access a database of facts" is a common misconception).
    *   Avoid obvious throwaway answers.

**Output Format:**
Return valid JSON matching this schema:
{{
  "profession": "{profession}",
  "questions": [
    {{
      "id": "q1",
      "text": "Scenario-based question text...",
      "options": [
         {{ "text": "Option A", "is_correct": false }},
         {{ "text": "Correct Option", "is_correct": true }},
         ...
      ],
      "associated_stage": "foundations",
      "complexity_level": 1,
      "rationale": "Tests understanding of tokens using a resume summary example."
    }}
    ...
  ]
}}
"""

def generate_quizzes():
    logger.info("🎓 Vina Quiz Generator - Starting...")

    # 1. Load Curriculum "Truth"
    try:
        config = load_course_config(COURSE_ID)
        
        # Build a structured summary of the course to guide the LLM
        # Group by 'pedagogical_progression' usually, but here we iterate lessons
        # to ensure we capture the specific "what_learners_will_understand" points.
        
        stages = {
            "Foundations": [],
            "Application": [],
            "Mastery": []
        }
        
        for lesson in config["lessons"]:
            # Map lesson IDs to stages roughly based on number
            lnum = lesson["lesson_number"]
            l_info = f"- L{lnum}: {lesson['lesson_name']} (Key Concept: {lesson['what_learners_will_understand'][0]})"
            
            if lnum <= 3:
                stages["Foundations"].append(l_info)
            elif lnum <= 10:
                stages["Application"].append(l_info)
            else:
                stages["Mastery"].append(l_info)

        course_context = (
            "STAGE 1: FOUNDATIONS (Lessons 1-3)\n" + "\n".join(stages["Foundations"]) + "\n\n" +
            "STAGE 2: APPLICATION & RISKS (Lessons 4-10)\n" + "\n".join(stages["Application"]) + "\n\n" +
            "STAGE 3: MASTERY & STRATEGY (Lessons 11-17)\n" + "\n".join(stages["Mastery"])
        )
        
        logger.info(f"✅ Loaded Course Context ({len(config['lessons'])} lessons)")
        
    except Exception as e:
        logger.error(f"❌ Failed to load course config: {e}")
        return

    # 2. Generate for each profession
    llm = get_llm_client()
    final_output = {}

    for profession in TARGET_PROFESSIONS:
        logger.info(f"📝 Generating Quiz for: {profession}...")
        
        prompt = PROMPT_TEMPLATE.format(
            profession=profession,
            course_structure=course_context
        )
        
        try:
            # High temperature for creative scenario generation, 
            # but schema usage usually constrains it enough.
            response_json = llm.generate_json(prompt, temperature=0.7)
            
            # Pydantic Validation
            quiz = ProfessionQuiz(**response_json)
            final_output[profession] = quiz.dict()
            logger.info(f"   ✅ Success: Generated {len(quiz.questions)} questions.")
            
        except Exception as e:
            logger.error(f"   ❌ Failed generation for {profession}: {e}")
            continue

    # 3. Save Artifact
    try:
        # Create directory if it doesn't exist (it should, but safety first)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_output, f, indent=2)
        logger.info(f"\n🎉 Generation Complete! Quizzes saved to:\n   {OUTPUT_FILE}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save output file: {e}")

if __name__ == "__main__":
    generate_quizzes()
