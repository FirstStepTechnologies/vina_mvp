"""
Lesson generation service with 3-agent pipeline (Generator → Reviewer → Rewriter).
Includes caching, validation, and retry logic.
"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
from json import JSONDecodeError
from jinja2 import Template
from pydantic import ValidationError

from vina_backend.domain.schemas.profile import UserProfileData
from vina_backend.domain.schemas.lesson import (
    LessonContent,
    ReviewResult,
    GeneratedLesson,
    GenerationMetadata
)
from vina_backend.services.course_loader import (
    load_course_config,
    get_lesson_config,
    get_difficulty_knobs,
    get_pedagogical_stage
)
from vina_backend.services.lesson_cache import LessonCacheService
from vina_backend.integrations.llm.client import get_llm_client

logger = logging.getLogger(__name__)

# Path to prompt templates
PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "lesson"


class LessonGenerator:
    """
    Service for generating personalized lessons using a 3-agent pipeline.
    """
    
    def __init__(self, cache_service: Optional[LessonCacheService] = None):
        """
        Initialize lesson generator.
        
        Args:
            cache_service: Optional caching service (if None, caching is disabled)
        """
        self.cache_service = cache_service
        self.llm_client = get_llm_client()
        
        # Load prompt templates
        self.generator_template = self._load_template("generator_prompt.md")
        self.reviewer_template = self._load_template("reviewer_prompt.md")
        self.rewriter_template = self._load_template("rewriter_prompt.md")
    
    @staticmethod
    def _load_template(filename: str) -> Template:
        """Load a Jinja2 template from the prompts directory."""
        template_path = PROMPTS_DIR / filename
        with open(template_path, 'r') as f:
            return Template(f.read())
    
    def generate_lesson(
        self,
        lesson_id: str,
        course_id: str,
        user_profile: UserProfileData,
        difficulty_level: int,
        adaptation_context: Optional[str] = None
    ) -> GeneratedLesson:
        """
        Generate a personalized lesson with caching, validation, and quality control.
        
        Args:
            lesson_id: Lesson identifier (e.g., "l01_what_llms_are")
            course_id: Course identifier (e.g., "c_llm_foundations")
            user_profile: User profile data
            difficulty_level: Difficulty level (1, 3, or 5)
            adaptation_context: Optional adaptation type ("simplify_this", "get_to_the_point", etc.)
        
        Returns:
            GeneratedLesson with content and metadata
        """
        start_time = time.time()
        
        # 1. Check cache (skip if adaptation requested)
        if self.cache_service and not adaptation_context:
            cached_lesson = self.cache_service.get(
                course_id, lesson_id, difficulty_level, user_profile
            )
            if cached_lesson:
                logger.info(f"Returning cached lesson for {lesson_id}")
                return GeneratedLesson(
                    lesson_id=lesson_id,
                    course_id=course_id,
                    difficulty_level=difficulty_level,
                    lesson_content=LessonContent(**cached_lesson),
                    generation_metadata=GenerationMetadata(cache_hit=True)
                )
        
        # 2. Load context
        logger.info(f"Generating lesson {lesson_id} for {user_profile.profession} at difficulty {difficulty_level}")
        
        course_config = load_course_config(course_id)
        lesson_spec = get_lesson_config(course_id, lesson_id)
        difficulty_knobs = get_difficulty_knobs(difficulty_level)
        pedagogical_stage = get_pedagogical_stage(course_id, lesson_id)
        
        # 3. Generate initial lesson
        lesson_json, generation_success = self._generate_with_retry(
            lesson_spec, user_profile, difficulty_level, difficulty_knobs, 
            pedagogical_stage, course_config
        )
        
        if not generation_success:
            logger.error(f"Failed to generate valid lesson for {lesson_id}")
            return self._fallback_lesson(lesson_id, course_id, difficulty_level)
        
        # 4. Review lesson
        review_result = self._review_lesson(
            lesson_json, lesson_spec, user_profile, difficulty_knobs, course_config
        )
        
        rewrite_count = 0
        
        # 5. Rewrite if needed (max 1 rewrite)
        if review_result.approval_status == "needs_revision" and rewrite_count < 1:
            logger.info(f"Lesson needs revision (quality score: {review_result.quality_score})")
            
            lesson_json = self._rewrite_lesson(
                lesson_json, review_result, lesson_spec, user_profile, 
                difficulty_knobs, course_config
            )
            rewrite_count += 1
            
            # Re-review
            review_result = self._review_lesson(
                lesson_json, lesson_spec, user_profile, difficulty_knobs, course_config
            )
        
        # 6. Validate final lesson
        try:
            lesson_content = LessonContent(**lesson_json)
        except ValidationError as e:
            logger.error(f"Final lesson validation failed: {e}")
            return self._fallback_lesson(lesson_id, course_id, difficulty_level)
        
        # 7. Cache if approved
        if self.cache_service and review_result.approval_status in ["approved", "approved_with_minor_fixes"]:
            self.cache_service.set(
                course_id, lesson_id, difficulty_level, user_profile, lesson_json
            )
        
        # 8. Return with metadata
        generation_time = time.time() - start_time
        
        return GeneratedLesson(
            lesson_id=lesson_id,
            course_id=course_id,
            difficulty_level=difficulty_level,
            lesson_content=lesson_content,
            generation_metadata=GenerationMetadata(
                cache_hit=False,
                llm_model=self.llm_client.model,
                generation_time_seconds=round(generation_time, 2),
                review_passed_first_time=(rewrite_count == 0),
                rewrite_count=rewrite_count,
                quality_score=review_result.quality_score
            )
        )
    
    def _generate_with_retry(
        self,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        pedagogical_stage: Optional[Dict],
        course_config: Dict,
        max_retries: int = 2
    ) -> tuple[Dict, bool]:
        """
        Generate lesson with retry logic for JSON parsing failures.
        
        Returns:
            (lesson_json, success)
        """
        generator_prompt = self._format_generator_prompt(
            lesson_spec, user_profile, difficulty_level, difficulty_knobs,
            pedagogical_stage, course_config
        )
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generation attempt {attempt + 1}/{max_retries}")
                lesson_json = self.llm_client.generate_json(
                    generator_prompt,
                    temperature=0.7  # Creative generation (auto-corrected to 1.0 for Gemini 3)
                )
                
                # Validate JSON structure
                LessonContent(**lesson_json)
                
                logger.info("Lesson generated and validated successfully")
                return lesson_json, True
                
            except (JSONDecodeError, ValidationError) as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} generation attempts failed")
                    return {}, False
                continue
        
        return {}, False
    
    def _review_lesson(
        self,
        lesson_json: Dict,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> ReviewResult:
        """Review generated lesson for quality."""
        reviewer_prompt = self._format_reviewer_prompt(
            lesson_json, lesson_spec, user_profile, difficulty_knobs, course_config
        )
        
        try:
            review_json = self.llm_client.generate_json(
                reviewer_prompt,
                temperature=0.3  # Consistent reviews (auto-corrected to 1.0 for Gemini 3)
            )
            review_result = ReviewResult(**review_json)
            
            logger.info(
                f"Review complete: {review_result.approval_status} "
                f"(score: {review_result.quality_score}/10)"
            )
            
            return review_result
            
        except (JSONDecodeError, ValidationError) as e:
            logger.error(f"Review failed: {e}. Defaulting to needs_revision")
            return ReviewResult(
                quality_score=5.0,
                approval_status="needs_revision",
                critical_issues=["Review agent failed to produce valid output"],
                minor_issues=[],
                suggested_fixes=["Regenerate the lesson"],
                strengths=[]
            )
    
    def _rewrite_lesson(
        self,
        lesson_json: Dict,
        review_result: ReviewResult,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> Dict:
        """Rewrite lesson based on review feedback."""
        rewriter_prompt = self._format_rewriter_prompt(
            lesson_json, review_result, lesson_spec, user_profile,
            difficulty_knobs, course_config
        )
        
        try:
            rewritten_json = self.llm_client.generate_json(
                rewriter_prompt,
                temperature=0.7  # Creative rewriting (auto-corrected to 1.0 for Gemini 3)
            )
            
            # Validate rewritten lesson
            LessonContent(**rewritten_json)
            
            logger.info("Lesson rewritten successfully")
            return rewritten_json
            
        except (JSONDecodeError, ValidationError) as e:
            logger.error(f"Rewrite failed: {e}. Returning original lesson")
            return lesson_json
    
    def _format_generator_prompt(
        self,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        pedagogical_stage: Optional[Dict],
        course_config: Dict
    ) -> str:
        """Format the generator prompt with all context."""
        # Extract difficulty metrics
        delivery_metrics = difficulty_knobs.get("delivery_metrics", {})
        
        # Prepare template variables
        context = {
            # Learner context
            "profession": user_profile.profession,
            "industry": user_profile.industry,
            "experience_level": user_profile.experience_level,
            "technical_comfort_level": user_profile.technical_comfort_level,
            "typical_outputs": user_profile.typical_outputs,
            "daily_responsibilities": user_profile.daily_responsibilities,
            "pain_points": user_profile.pain_points,
            "safety_priorities": user_profile.safety_priorities,
            "high_stakes_areas": user_profile.high_stakes_areas,
            
            # Lesson details
            "lesson_id": lesson_spec["lesson_id"],
            "lesson_name": lesson_spec["lesson_name"],
            "topic_group": lesson_spec["topic_group"],
            "estimated_duration_minutes": lesson_spec["estimated_duration_minutes"],
            "what_learners_will_understand": lesson_spec["what_learners_will_understand"],
            "misconceptions_to_address": lesson_spec["misconceptions_to_address"],
            
            # Difficulty level
            "difficulty_level": difficulty_level,
            "difficulty_label": difficulty_knobs.get("label", "Practical"),
            "slide_count": delivery_metrics.get("slide_count_for_3min_lesson", "4-5 slides").split()[0],  # Extract number
            "words_per_slide": delivery_metrics.get("words_per_slide", "50-70 words"),
            "analogies_per_concept": delivery_metrics.get("analogies_per_concept", "1"),
            "examples_per_concept": delivery_metrics.get("examples_per_concept", "1-2"),
            "jargon_density": delivery_metrics.get("jargon_density", "2-3 technical terms per slide"),
            "sentence_structure": delivery_metrics.get("sentence_structure", "Mix of short and medium sentences"),
            "content_scope": difficulty_knobs.get("content_scope", ""),
            "tone": difficulty_knobs.get("delivery_style", {}).get("tone", "Clear, professional"),
            
            # Pedagogical stage
            "stage_name": pedagogical_stage.get("stage_name", "N/A") if pedagogical_stage else "N/A",
            "teaching_approach": pedagogical_stage.get("teaching_approach", "") if pedagogical_stage else "",
            "stage_focus": pedagogical_stage.get("focus", "") if pedagogical_stage else "",
            "difficulty_guidance": pedagogical_stage.get("difficulty_guidance", "") if pedagogical_stage else "",
            
            # Course-specific safety
            "course_specific_safety_rules": course_config.get("course_specific_safety_rules", []),
            
            # Content constraints
            "content_constraints_avoid": lesson_spec.get("content_constraints", {}).get("avoid", []),
            "content_constraints_emphasize": lesson_spec.get("content_constraints", {}).get("emphasize", []),
            
            # References to previous lessons
            "references_previous_lessons": lesson_spec.get("references_previous_lessons", {})
        }
        
        return self.generator_template.render(**context)
    
    def _format_reviewer_prompt(
        self,
        lesson_json: Dict,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> str:
        """Format the reviewer prompt."""
        delivery_metrics = difficulty_knobs.get("delivery_metrics", {})
        
        context = {
            "generated_lesson_json": json.dumps(lesson_json, indent=2),
            "profession": user_profile.profession,
            "industry": user_profile.industry,
            "typical_outputs": user_profile.typical_outputs,
            "safety_priorities": user_profile.safety_priorities,
            "high_stakes_areas": user_profile.high_stakes_areas,
            "lesson_name": lesson_spec["lesson_name"],
            "what_learners_will_understand": lesson_spec["what_learners_will_understand"],
            "misconceptions_to_address": lesson_spec["misconceptions_to_address"],
            "difficulty_level": difficulty_knobs.get("label", "Practical"),
            "difficulty_label": difficulty_knobs.get("label", "Practical"),
            "slide_count": delivery_metrics.get("slide_count_for_3min_lesson", "4-5 slides").split()[0],
            "words_per_slide": delivery_metrics.get("words_per_slide", "50-70 words"),
            "analogies_per_concept": delivery_metrics.get("analogies_per_concept", "1"),
            "examples_per_concept": delivery_metrics.get("examples_per_concept", "1-2"),
            "jargon_density": delivery_metrics.get("jargon_density", "2-3 technical terms per slide"),
            "tone": difficulty_knobs.get("delivery_style", {}).get("tone", "Clear, professional"),
            "content_constraints_avoid": lesson_spec.get("content_constraints", {}).get("avoid", []),
            "content_constraints_emphasize": lesson_spec.get("content_constraints", {}).get("emphasize", []),
            "estimated_duration_minutes": lesson_spec["estimated_duration_minutes"]
        }
        
        return self.reviewer_template.render(**context)
    
    def _format_rewriter_prompt(
        self,
        lesson_json: Dict,
        review_result: ReviewResult,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> str:
        """Format the rewriter prompt."""
        delivery_metrics = difficulty_knobs.get("delivery_metrics", {})
        
        context = {
            "generated_lesson_json": json.dumps(lesson_json, indent=2),
            "quality_score": review_result.quality_score,
            "approval_status": review_result.approval_status,
            "critical_issues": review_result.critical_issues,
            "minor_issues": review_result.minor_issues,
            "suggested_fixes": review_result.suggested_fixes,
            "strengths": review_result.strengths,
            "profession": user_profile.profession,
            "industry": user_profile.industry,
            "typical_outputs": user_profile.typical_outputs,
            "safety_priorities": user_profile.safety_priorities,
            "high_stakes_areas": user_profile.high_stakes_areas,
            "difficulty_level": difficulty_knobs.get("label", "Practical"),
            "difficulty_label": difficulty_knobs.get("label", "Practical"),
            "slide_count": delivery_metrics.get("slide_count_for_3min_lesson", "4-5 slides").split()[0],
            "words_per_slide": delivery_metrics.get("words_per_slide", "50-70 words"),
            "analogies_per_concept": delivery_metrics.get("analogies_per_concept", "1"),
            "jargon_density": delivery_metrics.get("jargon_density", "2-3 technical terms per slide"),
            "tone": difficulty_knobs.get("delivery_style", {}).get("tone", "Clear, professional"),
            "what_learners_will_understand": lesson_spec["what_learners_will_understand"],
            "misconceptions_to_address": lesson_spec["misconceptions_to_address"],
            "content_constraints_avoid": lesson_spec.get("content_constraints", {}).get("avoid", []),
            "content_constraints_emphasize": lesson_spec.get("content_constraints", {}).get("emphasize", [])
        }
        
        return self.rewriter_template.render(**context)
    
    def _fallback_lesson(
        self,
        lesson_id: str,
        course_id: str,
        difficulty_level: int
    ) -> GeneratedLesson:
        """Return a generic fallback lesson when generation fails."""
        logger.warning(f"Returning fallback lesson for {lesson_id}")
        
        fallback_content = LessonContent(
            lesson_title="Lesson Temporarily Unavailable",
            slides=[
                {
                    "slide_number": 1,
                    "slide_type": "hook",
                    "heading": "We're Working on This Lesson",
                    "content": [
                        "This lesson is currently being generated",
                        "Please try again in a few moments",
                        "We apologize for the inconvenience"
                    ],
                    "speaker_notes": "We're currently generating this lesson content. Please refresh and try again."
                }
            ],
            references_to_previous_lessons=None
        )
        
        return GeneratedLesson(
            lesson_id=lesson_id,
            course_id=course_id,
            difficulty_level=difficulty_level,
            lesson_content=fallback_content,
            generation_metadata=GenerationMetadata(
                cache_hit=False,
                llm_model=None,
                generation_time_seconds=0,
                review_passed_first_time=False,
                rewrite_count=0,
                quality_score=0
            )
        )
