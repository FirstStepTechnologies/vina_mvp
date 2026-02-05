# Lesson Generation Workflow Update - Summary

## Date: 2026-02-05

## Changes Made

### 1. Updated Review Schema (`lesson.py`)

**New Classes Added:**
- `IssueDetail`: Detailed issue information with type, severity, description, location, and rewrite instructions
- `DurationAnalysis`: Duration analysis with estimated vs target seconds
- `PreserveElement`: Elements to preserve during rewrite

**Updated `ReviewResult` class:**
- Changed from `approval_status` (approved/approved_with_minor_fixes/needs_revision) to `decision` (approved/fix_in_place/regenerate_from_scratch)
- Changed from `quality_score` to structured issue lists
- Added `rewrite_strategy`: none/targeted_fixes/complete_regeneration
- Added `blocking_issues`: List[IssueDetail]
- Added `fixable_issues`: List[IssueDetail]
- Added `preserve_elements`: List[PreserveElement]
- Added `duration_analysis`: DurationAnalysis
- Added `summary`: str

### 2. Updated Generation Flow (`lesson_generator.py`)

**New Workflow:**
```
1. Generate lesson
2. Review lesson
3. If decision == "approved": return lesson
4. If decision == "fix_in_place": rewrite and return lesson
5. If decision == "regenerate_from_scratch": return fallback (for hackathon speed)
```

**Key Changes:**
- Removed re-review after rewrite (single rewrite attempt)
- Simplified decision logic based on `review_result.decision`
- Return fallback immediately for `regenerate_from_scratch` cases (no retry)
- Updated logging to show decision and issue counts

### 3. Updated `_review_lesson()` Method

**Changes:**
- Added `difficulty_level` parameter
- Updated logging to show blocking/fixable issue counts
- Updated fallback ReviewResult to use new schema structure
- Fallback now returns `regenerate_from_scratch` decision

### 4. Updated `_format_reviewer_prompt()` Method

**New Variables Passed:**
- `lesson_id`: Lesson identifier
- `technical_comfort_level`: User's technical comfort
- `difficulty_level`: Numeric difficulty (1, 3, or 5)
- `target_slide_count`: Target number of slides
- `min_slides`: Minimum allowed slides
- `max_slides`: Maximum allowed slides

**Removed Variables:**
- `safety_priorities` (not in new prompt)
- `words_per_slide`, `examples_per_concept`, `tone`, `content_constraints_*` (not in new prompt)

### 5. Updated `_format_rewriter_prompt()` Method

**Simplified to pass only:**
- `generated_lesson_json`: The original lesson JSON
- `review_json`: The complete review result as JSON

**Removed:**
- All individual review fields (quality_score, approval_status, etc.)
- All user profile and difficulty context (rewriter prompt doesn't need them)

### 6. Updated Metadata

**GenerationMetadata:**
- `quality_score` now set to `None` (new review format doesn't have numeric score)
- Still tracks `review_passed_first_time` and `rewrite_count`

## Prompt Files Updated by User

1. **generator_prompt.md** (v2.3)
   - Added version header and metadata
   - Updated to new slide structure with `items` array
   - Added figure support
   - Added duration constraints
   - Added concrete examples by difficulty

2. **reviewer_prompt.md** (v3.1)
   - Complete rewrite for agent-optimized workflow
   - Added decision logic (approved/fix_in_place/regenerate_from_scratch)
   - Added blocking vs fixable issue categorization
   - Added preservation rules
   - Added duration analysis
   - Removed code fences around lesson JSON

3. **rewriter_prompt.md** (v1.1)
   - Simplified to agent-optimized approach
   - Takes lesson JSON + review JSON only
   - Applies targeted fixes based on review instructions
   - No longer needs full context (user profile, difficulty, etc.)

## Testing Next Steps

1. Clear the lesson cache (old lessons won't match new schema)
2. Test generation with a simple lesson
3. Verify review produces correct decision structure
4. Test fix_in_place path with rewrite
5. Test regenerate_from_scratch path (should return fallback)

## Files Modified

- `/src/vina_backend/domain/schemas/lesson.py`
- `/src/vina_backend/services/lesson_generator.py`

## Files Updated by User (Prompts)

- `/src/vina_backend/prompts/lesson/generator_prompt.md`
- `/src/vina_backend/prompts/lesson/reviewer_prompt.md`
- `/src/vina_backend/prompts/lesson/rewriter_prompt.md`

## Files Deleted

- `/src/vina_backend/prompts/lesson/lesson_generate.md` (empty placeholder)
- `/src/vina_backend/prompts/lesson/lesson_review.md` (empty placeholder)
- `/src/vina_backend/prompts/lesson/lesson_rewrite.md` (empty placeholder)
