<!-- 
Prompt: User Profile Generation
Version: 1.2
Last Updated: 2026-02-04
Changes: Added safety_priorities and high_stakes_areas fields for context-aware safety guidance in lesson generation
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
  ],
  "safety_priorities": [
    "First critical safety or ethical consideration for this role and industry",
    "Second critical safety or ethical consideration",
    "Third critical safety or ethical consideration"
  ],
  "high_stakes_areas": [
    "First area where errors could have serious consequences",
    "Second area where errors could have serious consequences",
    "Third area where errors could have serious consequences"
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
- **safety_priorities**: Identify the most critical safety, ethical, compliance, or risk considerations for this specific profession and industry. Think about: What regulations govern their work? What are the consequences of errors? What ethical standards must they uphold? Examples:
  * Clinical Researchers in Pharma: Patient safety, FDA/EMA compliance, data integrity
  * HR Managers in any industry: Bias mitigation, fair hiring laws, employee privacy
  * Marketing Managers: Brand reputation, factual accuracy in public claims, customer trust
  * Project Managers in Construction: Worker safety, building codes, liability
- **high_stakes_areas**: Specify the exact work outputs or decisions where mistakes would be catastrophic, legally problematic, or highly damaging. Be concrete about WHAT could go wrong, not just that it's "important." Examples:
  * Clinical Researchers: "Clinical trial protocols (errors could harm patients)", "Adverse event reporting (regulatory violations)", "Informed consent documents (ethical/legal issues)"
  * HR Managers: "Job descriptions and interview questions (discrimination lawsuits)", "Performance reviews (wrongful termination claims)", "Candidate screening decisions (bias and legal exposure)"
  * Marketing Managers: "Public-facing product claims (false advertising, brand damage)", "Customer data handling (privacy violations)", "Crisis communications (reputation risk)"

Return only the JSON object, nothing else.