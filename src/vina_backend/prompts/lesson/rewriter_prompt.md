You are an expert instructional designer fixing a lesson based on quality review feedback.

## ORIGINAL LESSON

```json
{{ generated_lesson_json }}
```

---

## REVIEWER FEEDBACK

**Quality Score:** {{ quality_score }}/10

**Approval Status:** {{ approval_status }}

### Critical Issues (MUST FIX):
{% if critical_issues %}
{% for issue in critical_issues %}
{{ loop.index }}. {{ issue }}
{% endfor %}
{% else %}
None
{% endif %}

### Minor Issues (fix if possible):
{% if minor_issues %}
{% for issue in minor_issues %}
{{ loop.index }}. {{ issue }}
{% endfor %}
{% else %}
None
{% endif %}

### Suggested Fixes:
{% if suggested_fixes %}
{% for fix in suggested_fixes %}
{{ loop.index }}. {{ fix }}
{% endfor %}
{% else %}
None provided
{% endif %}

### Strengths (preserve these):
{% if strengths %}
{% for strength in strengths %}
- {{ strength }}
{% endfor %}
{% else %}
None identified
{% endif %}

---

## ORIGINAL CONSTRAINTS (DO NOT VIOLATE THESE)

**Learner Context:**
- Profession: {{ profession }}
- Industry: {{ industry }}
- Typical Outputs: {{ typical_outputs | join(', ') }}
- Safety Priorities: {{ safety_priorities | join(', ') }}
- High-Stakes Areas: {{ high_stakes_areas | join(', ') }}

**Difficulty Requirements:**
- Difficulty Level: {{ difficulty_level }} ({{ difficulty_label }})
- Target Slide Count: {{ slide_count }} slides (EXACT, not approximate)
- Words Per Slide: {{ words_per_slide }}
- Analogies Per Concept: {{ analogies_per_concept }}
- Jargon Density: {{ jargon_density }}
- Tone: {{ tone }}

**Learning Objectives (ALL must be covered):**
{% for objective in what_learners_will_understand %}
- {{ objective }}
{% endfor %}

**Misconceptions to Address (ALL must be corrected):**
{% for misconception in misconceptions_to_address %}
- {{ misconception }}
{% endfor %}

**Content Constraints:**
- MUST AVOID: {{ content_constraints_avoid | join('; ') }}
- MUST EMPHASIZE: {{ content_constraints_emphasize | join('; ') }}

---

## INSTRUCTIONS

### Priority 1: Fix ALL Critical Issues
{% if critical_issues %}
Address each critical issue listed above. These are blocking issues that prevent approval.
{% else %}
No critical issues to fix.
{% endif %}

### Priority 2: Fix Minor Issues (if possible)
{% if minor_issues %}
Address minor issues if you can do so without violating any constraints or removing strengths.
{% else %}
No minor issues to fix.
{% endif %}

### Priority 3: Preserve Strengths
{% if strengths %}
The reviewer identified these strengths. Keep them in the revised lesson:
{% for strength in strengths %}
- {{ strength }}
{% endfor %}
{% else %}
No specific strengths identified, but preserve anything that works well.
{% endif %}

### Priority 4: Maintain Constraints
**CRITICAL:** While fixing issues, you MUST NOT:
- Change the slide count (must remain {{ slide_count }} slides)
- Violate content constraints (avoid/emphasize lists)
- Drop any learning objectives
- Ignore any misconceptions
- Remove safety warnings for high-stakes areas
- Change the difficulty level inappropriately

---

## REWRITING STRATEGY

1. **Identify the root cause** of each critical issue
2. **Make targeted fixes** - don't rewrite everything, just fix what's broken
3. **Verify constraints** - after each fix, check you haven't violated constraints
4. **Preserve what works** - keep good slides/content intact
5. **Maintain coherence** - ensure slides still flow logically after changes

---

## OUTPUT FORMAT

Return the corrected lesson in the SAME JSON format as the original:

```json
{
  "lesson_title": "...",
  "slides": [
    {
      "slide_number": 1,
      "slide_type": "hook|concept|example|connection",
      "heading": "...",
      "content": ["...", "...", "..."],
      "speaker_notes": "..."
    }
  ],
  "references_to_previous_lessons": "..." 
}
```

---

## QUALITY CHECKLIST

Before submitting the revised lesson, verify:

- [ ] ALL critical issues fixed
- [ ] Minor issues fixed (if possible without violating constraints)
- [ ] Strengths preserved
- [ ] Exactly {{ slide_count }} slides (count them!)
- [ ] All {{ what_learners_will_understand | length }} learning objectives covered
- [ ] All {{ misconceptions_to_address | length }} misconceptions addressed
- [ ] Examples still reference {{ profession }} and {{ typical_outputs }}
- [ ] Difficulty level still matches {{ difficulty_level }} ({{ difficulty_label }})
- [ ] Content constraints still followed (avoid/emphasize)
- [ ] Safety priorities still respected
- [ ] High-stakes areas still have human oversight warnings
- [ ] Slides still flow logically (hook → concept → example → connection)

Generate the corrected lesson now as valid JSON.
