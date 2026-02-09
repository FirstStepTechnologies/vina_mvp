"""
Lesson generation service with 3-agent pipeline (Generator → Reviewer → Rewriter).
Includes caching, validation, and retry logic.
"""
import json
import logging
import time
from datetime import datetime
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
    GenerationMetadata,
    AuditTrail
)
from vina_backend.services.course_loader import (
    load_course_config,
    get_lesson_config,
    get_difficulty_knobs,
    get_pedagogical_stage
)
from vina_backend.services.lesson_cache import LessonCacheService
from vina_backend.integrations.llm.client import get_llm_client, LLMClient
from vina_backend.integrations.opik_tracker import track_llm_call

logger = logging.getLogger(__name__)

# Path to prompt templates
PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "lesson"


class LessonGenerator:
    """
    Service for generating personalized lessons using a 3-agent pipeline.
    """
    
    def __init__(
        self, 
        cache_service: Optional[LessonCacheService] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize lesson generator.
        
        Args:
            cache_service: Optional caching service (if None, caching is disabled)
            llm_client: Optional custom LLM client
        """
        self.cache_service = cache_service
        self.llm_client = llm_client or get_llm_client()
        
        # Load prompt templates
        self.generator_template = self._load_template("lesson_generator_prompt.md")
        self.reviewer_template = self._load_template("lesson_reviewer_prompt.md")
        self.rewriter_template = self._load_template("lesson_rewriter_prompt.md")
        self.fallback_template = self._load_template("fallback_generator.md")
    
    @staticmethod
    def _load_template(filename: str) -> Template:
        """Load a Jinja2 template from the prompts directory."""
        template_path = PROMPTS_DIR / filename
        with open(template_path, 'r') as f:
            return Template(f.read())
    
    @track_llm_call("generate_lesson", "gemini-2.0-flash-exp")
    def generate_lesson(
        self,
        lesson_id: str,
        course_id: str,
        user_profile: UserProfileData,
        difficulty_level: int,
        adaptation_context: Optional[str] = None,
        bypass_cache: bool = False
    ) -> GeneratedLesson:
        """
        Generate a personalized lesson with caching, validation, and quality control.
        
        Workflow:
        1. Generate lesson
        2. Review lesson
        3. If approved: return lesson
        4. If fix_in_place: rewrite and return lesson
        5. If regenerate_from_scratch: return fallback (for hackathon speed)
        
        Args:
            lesson_id: Lesson identifier (e.g., "l01_what_llms_are")
            course_id: Course identifier (e.g., "c_llm_foundations")
            user_profile: User profile data
            difficulty_level: Difficulty level (1, 3, or 5)
            adaptation_context: Optional adaptation type ("simplify_this", "get_to_the_point", etc.)
            bypass_cache: If True, force regeneration even if cached
        
        Returns:
            GeneratedLesson with content and metadata
        """
        start_time = time.time()
        
        # 1. Check cache (skip if bypass_cache is True)
        model_name = self.llm_client.model if self.llm_client else "unknown"
        if self.cache_service and not bypass_cache:
            cached_lesson = self.cache_service.get(
                course_id, lesson_id, difficulty_level, user_profile, model_name, adaptation_context
            )
            if cached_lesson:
                logger.info(f"Returning CACHED lesson for {lesson_id} (Model: {model_name})")
                return GeneratedLesson(
                    lesson_id=lesson_id,
                    course_id=course_id,
                    difficulty_level=difficulty_level,
                    lesson_content=LessonContent(**cached_lesson["lesson_content"]),
                    generation_metadata=GenerationMetadata(cache_hit=True, llm_model=model_name),
                    audit_trail=AuditTrail(**cached_lesson["audit_trail"])
                )
        
        # 2. Load context
        logger.info(f"Generating lesson {lesson_id} for {user_profile.profession} at difficulty {difficulty_level}")
        
        course_config = load_course_config(course_id)
        lesson_spec = get_lesson_config(course_id, lesson_id)
        difficulty_knobs = get_difficulty_knobs(difficulty_level)
        pedagogical_stage = get_pedagogical_stage(course_id, lesson_id)
        
        # 3. Generate initial lesson
        gen_start = time.time()
        lesson_json, generation_success, generator_prompt = self._generate_with_retry(
            lesson_spec, user_profile, difficulty_level, difficulty_knobs, 
            pedagogical_stage, course_config, adaptation_context
        )
        gen_duration = time.time() - gen_start
        
        if not generation_success:
            logger.error(f"Failed to generate valid lesson for {lesson_id}")
            return self._fallback_lesson(
                lesson_id, course_id, difficulty_level,
                lesson_spec, user_profile, difficulty_knobs, course_config
            )
        
        # 4. Review lesson
        rev_start = time.time()
        review_result, reviewer_prompt = self._review_lesson(
            lesson_json, lesson_spec, user_profile, difficulty_level, difficulty_knobs, course_config
        )
        rev_duration = time.time() - rev_start
        
        initial_lesson = lesson_json.copy()  # Snapshot for QA
        review_snapshot = review_result.model_dump() # Snapshot for QA
        
        rewriter_prompt = None
        
        logger.info(f"Review decision: {review_result.decision} - {review_result.summary}")
        
        rewrite_count = 0
        rewrite_duration = 0.0
        
        # 5. Handle review decision
        if review_result.decision == "approved":
            # Lesson is good to go
            logger.info("Lesson approved on first attempt")
            
        elif review_result.decision == "fix_in_place":
            # Apply targeted fixes
            logger.info(f"Applying targeted fixes ({len(review_result.fixable_issues)} issues)")
            
            rew_start = time.time()
            lesson_json, rewriter_prompt = self._rewrite_lesson(
                lesson_json, review_result, lesson_spec, user_profile, 
                difficulty_knobs, course_config
            )
            rewrite_duration = time.time() - rew_start
            rewrite_count = 1
            
        elif review_result.decision == "regenerate_from_scratch":
            # Use fallback generator for fast, safe lesson
            logger.warning(f"Lesson needs regeneration ({len(review_result.blocking_issues)} blocking issues). Using fallback generator.")
            return self._fallback_lesson(
                lesson_id, course_id, difficulty_level,
                lesson_spec, user_profile, difficulty_knobs, course_config
            )
        
        # 6. Validate final lesson
        try:
            lesson_content = LessonContent(**lesson_json)
        except ValidationError as e:
            logger.error(f"Final lesson validation failed: {e}")
            return self._fallback_lesson(
                lesson_id, course_id, difficulty_level,
                lesson_spec, user_profile, difficulty_knobs, course_config
            )
        
        # 7. Cache if approved or fixed (including QA snapshots)
        if self.cache_service and review_result.decision in ["approved", "fix_in_place"]:
            self.cache_service.set(
                course_id=course_id,
                lesson_id=lesson_id,
                difficulty_level=difficulty_level,
                user_profile=user_profile,
                llm_model=model_name,
                lesson_content=lesson_json,
                adaptation_context=adaptation_context,
                initial_lesson=initial_lesson,
                review_result=review_snapshot,
                gen_prompt=generator_prompt,
                rev_prompt=reviewer_prompt,
                rew_prompt=rewriter_prompt
            )
        
        # 8. Return with metadata
        total_time = time.time() - start_time
        
        return GeneratedLesson(
            lesson_id=lesson_id,
            course_id=course_id,
            difficulty_level=difficulty_level,
            lesson_content=lesson_content,
            generation_metadata=GenerationMetadata(
                cache_hit=False,
                llm_model=self.llm_client.model if self.llm_client else "unknown",
                generation_time_seconds=round(total_time, 2),
                phase_durations={
                    "generation": round(gen_duration, 2),
                    "review": round(rev_duration, 2),
                    "rewrite": round(rewrite_duration, 2)
                },
                review_passed_first_time=(rewrite_count == 0),
                rewrite_count=rewrite_count,
                quality_score=None
            ),
            audit_trail=AuditTrail(
                gen_prompt=generator_prompt,
                gen_output=initial_lesson,
                rev_prompt=reviewer_prompt,
                rev_output=review_snapshot,
                rew_prompt=rewriter_prompt,
                rew_output=lesson_json if rewrite_count > 0 else None
            )
        )
    
    @track_llm_call("generate_draft", "gemini-2.0-flash-exp")
    def _generate_with_retry(
        self,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        pedagogical_stage: Optional[Dict],
        course_config: Dict,
        adaptation_context: Optional[str] = None,
        max_retries: int = 2
    ) -> tuple[Dict, bool, str]:
        """
        Generate lesson with retry logic for JSON parsing failures.
        
        Returns:
            (lesson_json, success, prompt_used)
        """
        generator_prompt = self._format_generator_prompt(
            lesson_spec, user_profile, difficulty_level, difficulty_knobs,
            pedagogical_stage, course_config, adaptation_context
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
                return lesson_json, True, generator_prompt
                
            except (JSONDecodeError, ValidationError) as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} generation attempts failed")
                    return {}, False, generator_prompt
                continue
        
        return {}, False, generator_prompt
    
    @track_llm_call("review_draft", "gemini-2.0-flash-exp")
    def _review_lesson(
        self,
        lesson_json: Dict,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> tuple[ReviewResult, str]:
        """Review generated lesson for quality."""
        reviewer_prompt = self._format_reviewer_prompt(
            lesson_json, lesson_spec, user_profile, difficulty_level, difficulty_knobs, course_config
        )
        
        try:
            review_json = self.llm_client.generate_json(
                reviewer_prompt,
                temperature=0.3  # Consistent reviews (auto-corrected to 1.0 for Gemini 3)
            )
            review_result = ReviewResult(**review_json)
            
            logger.info(
                f"Review complete: {review_result.decision} "
                f"({len(review_result.blocking_issues)} blocking, {len(review_result.fixable_issues)} fixable issues)"
            )
            
            return review_result, reviewer_prompt
            
        except (JSONDecodeError, ValidationError) as e:
            logger.error(f"Review failed: {e}. Defaulting to regenerate_from_scratch")
            # Return a fallback review result that triggers regeneration
            return ReviewResult(
                decision="regenerate_from_scratch",
                rewrite_strategy="complete_regeneration",
                blocking_issues=[
                    {
                        "type": "json_error",
                        "severity": "critical",
                        "description": "Review agent failed to produce valid output",
                        "action_required": "Regenerate the lesson"
                    }
                ],
                fixable_issues=[],
                preserve_elements=[],
                duration_analysis={
                    "total_estimated_seconds": 0,
                    "target_seconds": lesson_spec.get("estimated_duration_minutes", 3) * 60,
                    "status": "on_target",
                    "slides_over_target": []
                },
                summary="Review agent error - regeneration required"
            ), reviewer_prompt
    
    @track_llm_call("refine_draft", "gemini-2.0-flash-exp")
    def _rewrite_lesson(
        self,
        lesson_json: Dict,
        review_result: ReviewResult,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> tuple[Dict, str]:
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
            return rewritten_json, rewriter_prompt
            
        except (JSONDecodeError, ValidationError) as e:
            logger.error(f"Rewrite failed: {e}. Returning original lesson")
            return lesson_json, rewriter_prompt
    
    def _format_generator_prompt(
        self,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        pedagogical_stage: Optional[Dict],
        course_config: Dict,
        adaptation_context: Optional[str] = None
    ) -> str:
        """Format the generator prompt with all context."""
        # Extract difficulty metrics
        delivery_metrics = difficulty_knobs.get("delivery_metrics", {})
        
        # Parse slide count range
        slide_count_str = delivery_metrics.get("slide_count_for_3min_lesson", "4-5 slides")
        if "-" in slide_count_str:
            parts = slide_count_str.split()[0].split("-")
            min_slides = int(parts[0])
            max_slides = int(parts[1])
            target_slide_count = min_slides
        else:
            target_slide_count = int(slide_count_str.split()[0])
            min_slides = target_slide_count
            max_slides = target_slide_count
        
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
            "target_slide_count": target_slide_count,
            "min_slides": min_slides,
            "max_slides": max_slides,
            "words_per_slide": delivery_metrics.get("words_per_slide", "50-70 words"),
            "analogies_per_concept": delivery_metrics.get("analogies_per_concept", "1"),
            "examples_per_concept": delivery_metrics.get("examples_per_concept", "1-2"),
            "jargon_density": delivery_metrics.get("jargon_density", "2-3 technical terms per slide"),
            "sentence_structure": delivery_metrics.get("sentence_structure", "Mix of short and medium sentences"),
            "content_scope": difficulty_knobs.get("content_scope", ""),
            "tone": difficulty_knobs.get("delivery_style", {}).get("tone", "Clear, professional"),
            "tone_description": difficulty_knobs.get("delivery_style", {}).get("tone", "Clear, professional"),
            
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
            "references_previous_lessons": lesson_spec.get("references_previous_lessons", {}),
            
            # Adaptation context (for regeneration with user feedback)
            "adaptation_context": adaptation_context
        }
        
        return self.generator_template.render(**context)
    
    def _format_reviewer_prompt(
        self,
        lesson_json: Dict,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> str:
        """Format the reviewer prompt."""
        delivery_metrics = difficulty_knobs.get("delivery_metrics", {})
        
        # Extract slide count info
        slide_count_str = delivery_metrics.get("slide_count_for_3min_lesson", "4-5 slides")
        # Parse "4-5 slides" -> target=4, min=4, max=5
        if "-" in slide_count_str:
            parts = slide_count_str.split()[0].split("-")
            min_slides = int(parts[0])
            max_slides = int(parts[1])
            target_slide_count = min_slides
        else:
            target_slide_count = int(slide_count_str.split()[0])
            min_slides = target_slide_count
            max_slides = target_slide_count
        
        context = {
            "generated_lesson_json": json.dumps(lesson_json, indent=2),
            
            # Learner context
            "profession": user_profile.profession,
            "industry": user_profile.industry,
            "technical_comfort_level": user_profile.technical_comfort_level,
            "typical_outputs": user_profile.typical_outputs,
            "high_stakes_areas": user_profile.high_stakes_areas,
            
            # Lesson details
            "lesson_id": lesson_spec["lesson_id"],
            "lesson_name": lesson_spec["lesson_name"],
            "what_learners_will_understand": lesson_spec["what_learners_will_understand"],
            "misconceptions_to_address": lesson_spec["misconceptions_to_address"],
            "estimated_duration_minutes": lesson_spec["estimated_duration_minutes"],
            
            # Difficulty requirements
            "difficulty_level": difficulty_level,
            "difficulty_label": difficulty_knobs.get("label", "Practical"),
            "target_slide_count": target_slide_count,
            "min_slides": min_slides,
            "max_slides": max_slides,
            "analogies_per_concept": delivery_metrics.get("analogies_per_concept", "1"),
            "jargon_density": delivery_metrics.get("jargon_density", "2-3 technical terms per slide"),
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
        # Convert review_result to dict for the template
        review_json_dict = review_result.model_dump()
        
        context = {
            "generated_lesson_json": json.dumps(lesson_json, indent=2),
            "review_json": json.dumps(review_json_dict, indent=2)
        }
        
        return self.rewriter_template.render(**context)
    
    def _fallback_lesson(
        self,
        lesson_id: str,
        course_id: str,
        difficulty_level: int,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> GeneratedLesson:
        """
        Generate a simple, safe fallback lesson using LLM with strict constraints.
        
        This is called when:
        - Primary generation fails validation
        - Review returns 'regenerate_from_scratch'
        - Final validation fails
        
        The fallback generator uses a simplified prompt with:
        - No figures (text-only)
        - Adaptive slide count based on difficulty
        - Guaranteed to pass validation
        - Personalized to user profile
        """
        logger.warning(f"Generating fallback lesson for {lesson_id} using LLM")
        
        try:
            # Format fallback prompt
            fallback_prompt = self._format_fallback_prompt(
                lesson_spec, user_profile, difficulty_level, difficulty_knobs, course_config
            )
            
            # Generate with LLM (single attempt, no retry)
            lesson_json = self.llm_client.generate_json(
                fallback_prompt,
                temperature=0.7  # Balanced creativity for fallback
            )
            
            # Validate
            lesson_content = LessonContent(**lesson_json)
            
            logger.info(f"Fallback lesson generated successfully with {len(lesson_content.slides)} slides")
            
            return GeneratedLesson(
                lesson_id=lesson_id,
                course_id=course_id,
                difficulty_level=difficulty_level,
                lesson_content=lesson_content,
                generation_metadata=GenerationMetadata(
                    cache_hit=False,
                    llm_model=self.llm_client.model,
                    generation_time_seconds=0,  # Not tracked for fallback
                    review_passed_first_time=None,  # Fallback skips review
                    rewrite_count=0,
                    quality_score=None
                )
            )
            
        except Exception as e:
            # If even fallback generation fails, return minimal hardcoded lesson
            logger.error(f"Fallback generation failed: {e}. Returning minimal hardcoded lesson.")
            return self._minimal_hardcoded_lesson(lesson_id, course_id, difficulty_level)
    
    def _minimal_hardcoded_lesson(
        self,
        lesson_id: str,
        course_id: str,
        difficulty_level: int
    ) -> GeneratedLesson:
        """
        Last resort: Return a minimal hardcoded lesson when even LLM fallback fails.
        This should rarely be needed.
        """
        logger.warning(f"Returning minimal hardcoded lesson for {lesson_id}")
        
        fallback_content = LessonContent(
            lesson_id=lesson_id,
            course_id=course_id,
            difficulty_level=difficulty_level,
            lesson_title="Lesson Temporarily Unavailable",
            total_slides=3,
            estimated_duration_minutes=1,
            slides=[
                {
                    "slide_number": 1,
                    "slide_type": "hook",
                    "title": "We're Working on This Lesson",
                    "items": [
                        {
                            "type": "text",
                            "bullet": "This lesson is currently being generated",
                            "talk": "We're currently generating this lesson content for you. This should only take a moment."
                        }
                    ],
                    "duration_seconds": None
                },
                {
                    "slide_number": 2,
                    "slide_type": "concept",
                    "title": "Please Try Again",
                    "items": [
                        {
                            "type": "text",
                            "bullet": "Refresh and try again in a few moments",
                            "talk": "Please refresh your browser and try accessing this lesson again. The generation process should complete shortly."
                        }
                    ],
                    "duration_seconds": None
                },
                {
                    "slide_number": 3,
                    "slide_type": "connection",
                    "title": "Thank You for Your Patience",
                    "items": [
                        {
                            "type": "text",
                            "bullet": "We apologize for the inconvenience",
                            "talk": "Thank you for your patience. We're working to provide you with high-quality, personalized lesson content."
                        }
                    ],
                    "duration_seconds": None
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
                review_passed_first_time=None,
                rewrite_count=0,
                quality_score=None
            )
        )

    def _format_fallback_prompt(
        self,
        lesson_spec: Dict,
        user_profile: UserProfileData,
        difficulty_level: int,
        difficulty_knobs: Dict,
        course_config: Dict
    ) -> str:
        """Format the fallback generator prompt with all context."""
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
            "course_id": lesson_spec.get("course_id", "unknown"),
            "lesson_name": lesson_spec["lesson_name"],
            "topic_group": lesson_spec["topic_group"],
            "estimated_duration_minutes": lesson_spec["estimated_duration_minutes"],
            "what_learners_will_understand": lesson_spec["what_learners_will_understand"],
            "misconceptions_to_address": lesson_spec["misconceptions_to_address"],
            
            # Difficulty level
            "difficulty_level": difficulty_level,
        }
        
        return self.fallback_template.render(**context)

    def export_generation_report(self, lesson: GeneratedLesson, output_dir: Path, user_profile: UserProfileData):
        """
        Exports a comprehensive Audit Folder for this generation run.
        Includes prompts, intermediate outputs, and the final report.
        """
        # Create a unique slug for this run
        prof_slug = user_profile.profession.lower().replace(' ', '_').replace('/', '_')
        diff_label = f"d{lesson.difficulty_level}"
        model_name = lesson.generation_metadata.llm_model or "unknown"
        
        # Ensure model name is safe for path
        model_safe = model_name.replace("/", "_")
        
        folder_name = f"{lesson.course_id}_{lesson.lesson_id}_{prof_slug}_{diff_label}_{model_safe}"
        report_dir = output_dir / folder_name
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Export Audit Trail (Prompts and Stage Outputs)
        if lesson.audit_trail:
            audit = lesson.audit_trail
            
            # Generator
            if audit.gen_prompt:
                with open(report_dir / "01_generator_prompt.md", "w") as f:
                    f.write(audit.gen_prompt)
            if audit.gen_output:
                with open(report_dir / "01_generator_output.json", "w") as f:
                    json.dump(audit.gen_output, f, indent=2)
            
            # Reviewer
            if audit.rev_prompt:
                with open(report_dir / "02_reviewer_prompt.md", "w") as f:
                    f.write(audit.rev_prompt)
            if audit.rev_output:
                with open(report_dir / "02_reviewer_output.json", "w") as f:
                    json.dump(audit.rev_output, f, indent=2)
            
            # Rewriter
            if audit.rew_prompt:
                with open(report_dir / "03_rewriter_prompt.md", "w") as f:
                    f.write(audit.rew_prompt)
            if audit.rew_output:
                with open(report_dir / "03_rewriter_output.json", "w") as f:
                    json.dump(audit.rew_output, f, indent=2)
                    
        # 2. Export Final Lesson Content
        with open(report_dir / "final_lesson.json", "w") as f:
            f.write(lesson.lesson_content.model_dump_json(indent=2))
            
        # 3. Export Summary Markdown Report
        summary_path = report_dir / "summary_report.md"
        with open(summary_path, "w") as f:
            f.write(f"# VINA Lesson Generation Report\n")
            f.write(f"**Target Audience:** {user_profile.profession} ({user_profile.experience_level})\n")
            f.write(f"**Course/Lesson:** {lesson.course_id} / {lesson.lesson_id}\n")
            f.write(f"**Difficulty:** {lesson.difficulty_level} ({diff_label})\n")
            f.write(f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {model_name}\n")
            f.write(f"**Total Generation Time:** {lesson.generation_metadata.generation_time_seconds}s\n")
            f.write(f"**Phase Durations:** {lesson.generation_metadata.phase_durations}\n")
            f.write(f"**Cache Hit:** {lesson.generation_metadata.cache_hit}\n\n")
            
            f.write(f"## 📋 Final Lesson Content\n")
            f.write(f"### Title: {lesson.lesson_content.lesson_title}\n\n")
            
            for i, slide in enumerate(lesson.lesson_content.slides):
                f.write(f"--- \n")
                f.write(f"### 🛝 Slide {i+1}: {slide.title}\n")
                f.write(f"**Type:** {slide.slide_type}\n\n")
                
                for j, item in enumerate(slide.items):
                    item_type = item.type.upper()
                    if item_type == "FIGURE" and item.figure:
                        f.write(f"**[{item_type}]** Prompt: *\"{item.figure.image_prompt}\"*\n")
                        f.write(f"**Talk Track:** {item.talk}\n\n")
                    else:
                        f.write(f"**[TEXT]** Bullet: \"{item.bullet}\"\n")
                        f.write(f"**Talk Track:** {item.talk}\n\n")
            
            f.write(f"\n--- \n")
            f.write(f"**End of Report**\n")
            
        return report_dir

from datetime import datetime
