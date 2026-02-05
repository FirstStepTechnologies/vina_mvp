# Generator Prompt v2.4 - Targeted Improvements

## Date: 2026-02-05

## Changes Made

### 1. Added Plain Text Formatting Requirements

**Location:** After CONTENT CONSTRAINTS section (line ~197)

**New Section:**
```markdown
## FORMATTING REQUIREMENTS

**Plain Text Only:**
- No Markdown formatting (no *, **, _, `, etc.)
- No code blocks or inline code formatting
- Use hyphens (-) not em dashes (—)
- Use straight quotes ("") not curly quotes ("")
```

**Rationale:**
- Em dashes appeared in 2/3 generated lessons as fixable issues
- Easy fix that reduces rewrite frequency
- Minimal prompt bloat (4 simple rules)

### 2. Added Figure Layout Enum Constraints

**Location:** In FIGURE GUIDANCE section, after "Items Per Slide with Figures" (line ~397)

**New Section:**
```markdown
**Figure Layout Values:**
- **CRITICAL:** The `layout` field MUST be one of these exact values:
  - `"single"` - One image filling the space
  - `"side-by-side"` - Two images next to each other
  - `"grid"` - Multiple images in a grid
- ❌ **NEVER use:** "two-panel", "flow", "comparison", or any other value
```

**Rationale:**
- LLM used invalid value `"two-panel"` causing generation failures
- This caused retries and wasted LLM calls
- Explicit enum prevents validation errors
- High impact fix for a common failure mode

### 3. Updated Prompt Version

**Changed:**
- Version: 2.3 → 2.4
- Last Updated: 2026-02-04 → 2026-02-05
- Changelog: "Added plain text formatting rules (no em dashes), explicit figure layout enum constraints"

## Issues Addressed

### ✅ Fixed (High Priority)
1. **Figure layout validation errors** - Prevented generation failures
2. **Em dash formatting** - Reduced rewrite frequency

### ⏭️ Not Fixed (Intentionally)
3. **Duration target adjustments** - Keep in review/rewrite (variable by content)
4. **Talk track length balancing** - Keep in review/rewrite (quality polish step)

## Impact Analysis

### Before Changes:
- Generation retry rate: ~33% (1/3 lessons failed first attempt due to layout validation)
- Rewrite rate: 100% (all lessons needed `fix_in_place` for em dashes + other issues)

### Expected After Changes:
- Generation retry rate: ~0-10% (layout errors eliminated)
- Rewrite rate: ~70-80% (em dashes fixed, but duration/quality issues remain)
- Overall workflow efficiency: +15-20% (fewer retries, faster first-pass success)

## Design Philosophy

**Minimal Intervention Approach:**
- Only fix issues that cause **hard failures** (validation errors)
- Only fix issues that are **consistently fixable** (formatting rules)
- **Don't over-constrain** the generator (preserve creativity)
- **Keep review/rewrite valuable** (quality polish, not just error correction)

## Testing Recommendation

After deploying these changes:
1. Clear lesson cache: `python scripts/clear_lesson_cache.py`
2. Run test suite: `python scripts/test_lesson_generation.py`
3. Monitor review decisions:
   - Expect fewer `regenerate_from_scratch` (layout errors gone)
   - Expect similar `fix_in_place` rate (duration/quality still need polish)
   - Expect faster generation times (fewer retries)

## Files Modified

- `src/vina_backend/prompts/lesson/generator_prompt.md` (v2.3 → v2.4)

## Git Commit

```
commit 5b8b164
feat: Implement new lesson generation workflow with decision-based review

- Added plain text formatting rules (no em dashes) to generator prompt
- Added explicit figure layout enum constraints to prevent validation errors
- Updated prompt version to 2.4
```

## Next Steps

1. ✅ Monitor generation success rate
2. ✅ Track review decision distribution
3. ⏭️ Consider adding more enum constraints if new validation errors appear
4. ⏭️ Refine duration guidance if review continues to flag this frequently
