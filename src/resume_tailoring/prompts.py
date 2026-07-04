"""Prompt construction for the elaborate_match tailoring mode."""

ELABORATE_SYSTEM_PROMPT = """\
You are an expert executive resume strategist and ATS optimization writer.

MISSION
Rewrite and tailor a candidate's resume for a specific job description so it is:
1) truth-preserving,
2) impact-rich,
3) ATS-aligned,
4) detailed enough to "speak for the candidate,"
without unnecessary compression.

NON-NEGOTIABLE RULES
- Never invent employers, titles, dates, tools, projects, certifications, or metrics.
- Only use claims supported by provided sources:
  a) Base resume
  b) LinkedIn/profile text
  c) User-provided experience notes
  d) Portfolio/project evidence
- If a useful metric is missing, do NOT fabricate. Use strong but non-numeric phrasing
  and add it to "NEEDS_CONFIRMATION".
- Keep chronology consistent unless user asks otherwise.
- Preserve factual seniority and scope.
- Optimize for both ATS and human readability.

STYLE RULES
- Prefer achievement-expansion over compression.
- Bullets should be specific, context-aware, and outcome-oriented.
- Use CAR/STAR structure implicitly:
  Context/Challenge → Action → Result/Impact.
- Keep verbs strong and varied.
- Mirror critical job-description language naturally (no keyword stuffing).
- Include domain/tool keywords where truthful.
- Avoid vague bullets like "Responsible for…".

OUTPUT OBJECTIVE
Produce a role-targeted resume that improves relevance and clarity while staying
faithful to source truth.
"""

_USER_PROMPT_TEMPLATE = """\
TASK
Tailor the candidate resume for the target job using elaborate_match mode.

TARGET ROLE
{job_title}
{company_name}
{location_type}

JOB DESCRIPTION
{job_description}

CANDIDATE BASE RESUME
{resume_text}

LINKEDIN / PROFILE CONTEXT (optional but recommended)
{linkedin_text}

ADDITIONAL EXPERIENCE NOTES (optional)
{extra_notes}

CONSTRAINTS
- Keep claims truthful and source-grounded.
- Do not over-compress bullets.
- Prioritize achievements most relevant to this JD.
- Keep final resume concise but substantive (typically 1-2 pages depending on seniority).
- If uncertain about any claim/metric, include it in NEEDS_CONFIRMATION.

OUTPUT FORMAT (STRICT — include all 10 section headers exactly as shown)
1) MATCH_SUMMARY (5-8 bullets)
2) TARGET_HEADLINE
3) TARGET_SUMMARY (4-6 lines)
4) CORE_SKILLS (grouped by category, ATS-friendly)
5) PROFESSIONAL_EXPERIENCE
   - For each role:
     - role header
     - 4-7 tailored bullets (more for most relevant recent roles)
6) SELECTED_PROJECTS (if applicable, 2-4)
7) EDUCATION / CERTIFICATIONS
8) ATS_KEYWORD_COVERAGE
   - Included keywords
   - Missing keywords (truth-safe only)
9) NEEDS_CONFIRMATION
   - Any assumptions, missing metrics, unclear tools, date/title ambiguity
10) FINAL_RESUME_TEXT
   - Clean copy-paste version
"""


def build_elaborate_user_prompt(
    job_title: str,
    job_description: str,
    resume_text: str,
    company_name: str = "",
    location_type: str = "",
    linkedin_text: str = "",
    extra_notes: str = "",
) -> str:
    """Return the filled user-prompt string for elaborate_match mode.

    All positional fields are required; optional context fields default to
    empty strings so callers need not pass them when unavailable.
    """
    return _USER_PROMPT_TEMPLATE.format(
        job_title=job_title,
        company_name=company_name or "(not specified)",
        location_type=location_type or "(not specified)",
        job_description=job_description,
        resume_text=resume_text,
        linkedin_text=linkedin_text or "(not provided)",
        extra_notes=extra_notes or "(not provided)",
    )
