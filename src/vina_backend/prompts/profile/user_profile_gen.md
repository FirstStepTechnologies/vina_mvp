<!-- 
Prompt: User Profile Generation
Version: 1.1
Last Updated: 2026-01-31
Changes: Added typical_outputs field to better personalize lesson examples
-->

You are an expert in understanding professional roles across different industries.

Your task is to generate a detailed, realistic user profile that captures someone's professional context independent of any specific course or learning topic.

USER INPUTS:
- Profession: {profession}
- Industry: {industry}
- Experience Level: {experience_level}

Generate a comprehensive profile that includes all of the following fields. Be specific and grounded in real-world knowledge of this profession and industry combination. Avoid generic statements.

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure. Do not include any markdown formatting, explanatory text, or preamble.

{{
  "profession": "{profession}",
  "industry": "{industry}",
  "experience_level": "{experience_level}",
  "daily_responsibilities": [
    "First specific responsibility",
    "Second specific responsibility",
    "Third specific responsibility"
  ],
  "pain_points": [
    "First genuine pain point this role experiences",
    "Second genuine pain point this role experiences",
    "Third genuine pain point this role experiences"
  ],
  "typical_outputs": [
    "First type of document/deliverable this person creates",
    "Second type of document/deliverable",
    "Third type of document/deliverable"
  ],
  "technical_comfort_level": "Low|Medium|High",
  "learning_style_notes": "A 1-2 sentence description of how someone in this role typically prefers to learn technical topics, including preferred example types and explanation styles.",
  "professional_goals": [
    "First career or skill development goal",
    "Second career or skill development goal"
  ]
}}

GUIDELINES:
- Make daily_responsibilities concrete and specific to this industry context, not generic to the profession
- Ensure pain_points are genuine challenges this person faces in their day-to-day work
- Make typical_outputs specific work products this person creates (e.g., "Clinical trial protocols", "Quarterly performance reviews", "Marketing campaign briefs")
- Set technical_comfort_level based on typical technical proficiency:
  * Clinical Researchers, HR Managers: typically "Low"
  * Project Managers: typically "Medium"
  * Marketing Managers: "Medium" to "High" depending on industry
- Write learning_style_notes that reflect how professionals in this field actually consume and apply knowledge
- Make professional_goals realistic aspirations for someone at this experience level

Return only the JSON object, nothing else.