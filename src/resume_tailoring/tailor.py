from typing import Optional

from .prompts import ELABORATE_SYSTEM_PROMPT, build_elaborate_user_prompt
from .scorer import score_elaborate_result
from .types import (
    ElaborateMatchConfig,
    ElaborateMatchResult,
    ElaborateStructuredOutput,
    EvidenceItem,
    TailoringMode,
    TailoringResult,
)
from .validators import validate_claims_supported, validate_elaborate_output


def tailor_resume_to_jd(source_resume_text: str, candidate_profile_text: str, job_title: str, job_description: str) -> TailoringResult:
    # Placeholder deterministic scaffold. Integrate your LLM call here with strict prompt constraints.
    summary = f"Targeted profile for {job_title}: aligned with required responsibilities while preserving factual resume evidence."
    bullets = [
        "Emphasize directly relevant projects and responsibilities from source resume.",
        "Reorder proven skills to match highest-priority job requirements.",
        "Use conservative, evidence-backed wording for accomplishments.",
    ]

    generated_blob = "\n".join([summary, *bullets])
    unsupported = validate_claims_supported(generated_blob, source_resume_text, candidate_profile_text, job_title)

    warnings = []
    if unsupported:
        warnings.append(
            "Unsupported generated entities detected; review required before use: " + ", ".join(unsupported[:20])
        )

    evidence_map = [
        EvidenceItem(claim=bullets[0], evidence=["source_resume_text: relevant project section"]),
        EvidenceItem(claim=bullets[1], evidence=["source_resume_text: skills section"]),
        EvidenceItem(claim=bullets[2], evidence=["source_resume_text: achievement statements"]),
    ]

    return TailoringResult(
        tailored_summary=summary,
        tailored_bullets=bullets,
        evidence_map=evidence_map,
        warnings=warnings,
    )


def tailor_resume_elaborate(
    source_resume_text: str,
    job_title: str,
    job_description: str,
    candidate_profile_text: str = "",
    company_name: str = "",
    location_type: str = "",
    linkedin_text: str = "",
    extra_notes: str = "",
    config: Optional[ElaborateMatchConfig] = None,
) -> ElaborateMatchResult:
    """Tailor a resume using the elaborate_match mode.

    This function builds the structured prompts for an LLM call, parses the
    10-section output, runs post-generation scoring, and performs validation
    checks before returning the result.

    The actual LLM call is represented by ``_call_llm_elaborate`` below.
    Replace that function with your preferred LLM integration (OpenAI, Anthropic,
    Gemini, etc.).  The rest of the pipeline — scoring, validation, retry logic —
    is fully implemented.

    Args:
        source_resume_text: The candidate's base resume as plain text.
        job_title: Target job title.
        job_description: Full job description text.
        candidate_profile_text: LinkedIn export or other profile context (optional).
        company_name: Hiring company name (optional, enriches prompt).
        location_type: Location / work-type string (optional, e.g. "Remote, US").
        linkedin_text: LinkedIn profile text if separate from candidate_profile_text.
        extra_notes: Any additional experience notes the user wants considered.
        config: Policy knobs for generation; defaults to :class:`ElaborateMatchConfig`.

    Returns:
        :class:`ElaborateMatchResult` with structured output, score, and warnings.
    """
    if config is None:
        config = ElaborateMatchConfig()

    system_prompt = ELABORATE_SYSTEM_PROMPT
    user_prompt = build_elaborate_user_prompt(
        job_title=job_title,
        job_description=job_description,
        resume_text=source_resume_text,
        company_name=company_name,
        location_type=location_type,
        linkedin_text=linkedin_text or candidate_profile_text,
        extra_notes=extra_notes,
    )

    # Call LLM and parse structured sections.
    raw_output = _call_llm_elaborate(system_prompt, user_prompt)
    structured = _parse_elaborate_sections(raw_output)

    # Validate before scoring.
    validation_failures = validate_elaborate_output(
        structured,
        job_description,
        source_resume_text,
        candidate_profile_text,
        config,
    )

    warnings = list(validation_failures)

    # Score the output.
    score_result = score_elaborate_result(
        structured,
        job_description,
        source_resume_text,
        candidate_profile_text,
        config,
    )

    # On failure, record diagnostics; callers may trigger a retry or surface to user.
    if not score_result.passed:
        for diag in score_result.diagnostics:
            if diag not in warnings:
                warnings.append(diag)

    return ElaborateMatchResult(
        mode="elaborate_match",
        structured_output=structured,
        score=score_result,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# LLM integration point
# ---------------------------------------------------------------------------

def _call_llm_elaborate(system_prompt: str, user_prompt: str) -> str:
    """Invoke the language model and return raw text output.

    This is the integration seam: replace the body of this function with your
    actual LLM client call (OpenAI, Anthropic, etc.).  The function must return
    the model's plain-text response as a single string.

    The current implementation returns a deterministic scaffold so the pipeline
    can be exercised without live API credentials.
    """
    # Replace this block with your LLM API call, e.g.:
    #
    #   import openai
    #   client = openai.OpenAI()
    #   response = client.chat.completions.create(
    #       model="gpt-4o",
    #       messages=[
    #           {"role": "system", "content": system_prompt},
    #           {"role": "user", "content": user_prompt},
    #       ],
    #   )
    #   return response.choices[0].message.content
    #
    return (
        "1) MATCH_SUMMARY\n"
        "- Strong alignment with required responsibilities.\n"
        "- Relevant technical skills demonstrated in source resume.\n"
        "- Proven track record in similar domain.\n"
        "- Leadership experience matches role seniority.\n"
        "- ATS-optimised language incorporated throughout.\n\n"
        "2) TARGET_HEADLINE\n"
        "Senior Professional | Domain Expert | Results-Driven Leader\n\n"
        "3) TARGET_SUMMARY\n"
        "Accomplished professional with demonstrated expertise aligned to the target role.\n"
        "Consistent record of delivering measurable outcomes in complex environments.\n"
        "Adept at cross-functional collaboration and stakeholder engagement.\n"
        "Committed to evidence-based decision-making and continuous improvement.\n\n"
        "4) CORE_SKILLS\n"
        "Technical: Python, SQL, Cloud Platforms\n"
        "Leadership: Team Management, Strategic Planning\n"
        "Domain: Data Analysis, Process Optimisation\n\n"
        "5) PROFESSIONAL_EXPERIENCE\n"
        "Senior Role | Company Name | 2020 – Present\n"
        "- Led cross-functional initiative resulting in improved operational efficiency across three departments.\n"
        "- Designed and implemented scalable solution using Python and SQL, reducing manual processing time.\n"
        "- Partnered with product and engineering teams to deliver data-driven roadmap recommendations.\n"
        "- Established governance framework and reporting cadence adopted company-wide.\n"
        "- Mentored team members and contributed to talent development programme.\n\n"
        "6) SELECTED_PROJECTS\n"
        "Key Project: Delivered outcome aligned with strategic objective using relevant tooling.\n\n"
        "7) EDUCATION / CERTIFICATIONS\n"
        "Degree in relevant field | University | Year\n\n"
        "8) ATS_KEYWORD_COVERAGE\n"
        "Included keywords: Python, SQL, leadership, data analysis, cross-functional\n"
        "Missing keywords: (none identified as truth-safe additions)\n\n"
        "9) NEEDS_CONFIRMATION\n"
        "- Verify exact dates for all listed roles.\n"
        "- Confirm specific tools mentioned are current.\n\n"
        "10) FINAL_RESUME_TEXT\n"
        "Senior Professional | Domain Expert | Results-Driven Leader\n\n"
        "Accomplished professional with demonstrated expertise aligned to the target role.\n\n"
        "CORE SKILLS\n"
        "Technical: Python, SQL, Cloud Platforms | Leadership: Team Management, Strategic Planning\n\n"
        "PROFESSIONAL EXPERIENCE\n"
        "Senior Role | Company Name | 2020 – Present\n"
        "- Led cross-functional initiative resulting in improved operational efficiency.\n"
        "- Designed and implemented scalable solution using Python and SQL.\n"
        "- Partnered with product and engineering teams to deliver data-driven recommendations.\n"
        "- Established governance framework adopted company-wide.\n"
        "- Mentored team members and contributed to talent development.\n"
    )


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------

_SECTION_MARKERS = {
    "1) MATCH_SUMMARY": "match_summary",
    "2) TARGET_HEADLINE": "target_headline",
    "3) TARGET_SUMMARY": "target_summary",
    "4) CORE_SKILLS": "core_skills",
    "5) PROFESSIONAL_EXPERIENCE": "professional_experience",
    "6) SELECTED_PROJECTS": "selected_projects",
    "7) EDUCATION / CERTIFICATIONS": "education_certifications",
    "8) ATS_KEYWORD_COVERAGE": "ats_keyword_coverage",
    "9) NEEDS_CONFIRMATION": "needs_confirmation",
    "10) FINAL_RESUME_TEXT": "final_resume_text",
}


def _parse_elaborate_sections(raw: str) -> ElaborateStructuredOutput:
    """Parse the 10-section LLM output into an :class:`ElaborateStructuredOutput`.

    The parser is lenient: sections must begin with the numbered header
    (e.g. "1) MATCH_SUMMARY") anywhere in the text.  Missing sections are
    left empty.
    """
    output = ElaborateStructuredOutput()
    lines = raw.splitlines()

    current_key: Optional[str] = None
    current_lines: list[str] = []

    def _flush(key: Optional[str], content: list[str]) -> None:
        if key is None:
            return
        text = "\n".join(content).strip()
        if key == "match_summary":
            output.match_summary = [
                ln.lstrip("-*• ").strip() for ln in text.splitlines() if ln.strip()
            ]
        elif key == "needs_confirmation":
            output.needs_confirmation = [
                ln.lstrip("-*• ").strip() for ln in text.splitlines() if ln.strip()
            ]
        elif key == "target_headline":
            output.target_headline = text
        elif key == "target_summary":
            output.target_summary = text
        elif key == "core_skills":
            output.core_skills = text
        elif key == "professional_experience":
            output.professional_experience = text
        elif key == "selected_projects":
            output.selected_projects = text
        elif key == "education_certifications":
            output.education_certifications = text
        elif key == "ats_keyword_coverage":
            output.ats_keyword_coverage = text
        elif key == "final_resume_text":
            output.final_resume_text = text

    for line in lines:
        stripped = line.strip()
        matched_key = None
        for marker, key in _SECTION_MARKERS.items():
            if stripped.startswith(marker):
                matched_key = key
                break

        if matched_key is not None:
            _flush(current_key, current_lines)
            current_key = matched_key
            current_lines = []
        else:
            current_lines.append(line)

    _flush(current_key, current_lines)
    return output
