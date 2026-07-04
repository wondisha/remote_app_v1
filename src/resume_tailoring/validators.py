import re
from typing import List

from .types import ElaborateMatchConfig, ElaborateStructuredOutput


def extract_entities(text: str) -> set[str]:
    # Simple token entity extractor placeholder.
    # Replace with robust NER if needed.
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{2,}", text)
    return {t.lower() for t in tokens}


def validate_claims_supported(generated_text: str, source_resume: str, candidate_profile: str, job_title: str) -> list[str]:
    allowed = extract_entities(source_resume) | extract_entities(candidate_profile) | extract_entities(job_title)
    generated = extract_entities(generated_text)
    unsupported = sorted(token for token in generated if token not in allowed)
    return unsupported


# ---------------------------------------------------------------------------
# elaborate_match validation
# ---------------------------------------------------------------------------

def validate_elaborate_output(
    structured: ElaborateStructuredOutput,
    job_description: str,
    source_resume: str,
    candidate_profile: str = "",
    config: "ElaborateMatchConfig | None" = None,
) -> List[str]:
    """Run pre-return validation checks for elaborate_match output.

    Returns a list of human-readable validation failure messages.
    An empty list means all checks passed.

    Checks performed:
    1. No fabricated numbers not present in source materials (when
       allow_metric_inference is False).
    2. Top JD keywords are represented in the final resume text.
    3. Recent relevant roles have substantive bullets (min per config).
    4. Uncertainties are listed in NEEDS_CONFIRMATION when flagging is on.
    5. Final resume text is non-empty.
    """
    if config is None:
        config = ElaborateMatchConfig()

    failures: List[str] = []
    final_text = structured.final_resume_text

    # Check 1 — no fabricated numbers/tools/projects
    if not config.allow_metric_inference:
        # Match only explicit metric forms: percentages, dollar amounts, and
        # multiplier expressions (e.g. 3x).  Plain integers like years (2020)
        # are excluded intentionally to avoid false positives on date ranges.
        number_pattern = re.compile(
            r"(?:"
            r"\$\s*\d+(?:[,.]\d+)*\s*[KMBkmb]?"   # dollar amounts: $2.5M, $100K, $0.5M
            r"|\b\d[\d,.]*\s*%"                    # percentages: 47%, 3.5%
            r"|\b\d+x\b"                           # multipliers: 3x, 10x
            r")"
        )
        new_numbers = set(number_pattern.findall(final_text))
        source_numbers = set(number_pattern.findall(source_resume)) | set(
            number_pattern.findall(candidate_profile)
        )
        fabricated_numbers = new_numbers - source_numbers
        if fabricated_numbers:
            failures.append(
                "Validation failed: fabricated numeric values detected that are not "
                f"in source materials: {', '.join(sorted(fabricated_numbers)[:5])}"
            )

    # Check 2 — top JD keywords represented truthfully
    jd_tokens = extract_entities(job_description)
    resume_tokens = extract_entities(final_text)
    if jd_tokens:
        missing_ratio = len(jd_tokens - resume_tokens) / len(jd_tokens)
        if missing_ratio > 0.5:
            sample_missing = sorted(jd_tokens - resume_tokens)[:8]
            failures.append(
                f"Validation failed: more than 50% of JD keywords are absent from "
                f"the tailored resume. Missing examples: {', '.join(sample_missing)}"
            )

    # Check 3 — professional experience has substantive bullets
    exp_text = structured.professional_experience
    if exp_text:
        bullet_lines = [
            ln.lstrip("-*• ").strip()
            for ln in exp_text.splitlines()
            if re.match(r"^\s*[-*•]", ln)
        ]
        substantive = [b for b in bullet_lines if len(b.split()) >= config.bullet_min_words]
        if bullet_lines and len(substantive) < config.min_bullets_per_recent_role:
            failures.append(
                f"Validation failed: fewer than {config.min_bullets_per_recent_role} "
                f"substantive bullets (≥{config.bullet_min_words} words) found in "
                f"PROFESSIONAL_EXPERIENCE. Found {len(substantive)}."
            )

    # Check 4 — uncertainties flagged in NEEDS_CONFIRMATION
    if config.flag_uncertain_claims and not structured.needs_confirmation:
        failures.append(
            "Validation warning: NEEDS_CONFIRMATION is empty. If any claims are "
            "uncertain or metrics are inferred, they must be listed here."
        )

    # Check 5 — final resume text exists
    if not final_text.strip():
        failures.append("Validation failed: FINAL_RESUME_TEXT is empty.")

    return failures
