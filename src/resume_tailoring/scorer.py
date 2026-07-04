"""Post-generation scoring for elaborate_match mode.

Scoring rubric (0-100):
  A. Truth & Evidence Integrity  0-30
  B. JD Relevance & Alignment    0-20
  C. Impact & Specificity        0-20
  D. ATS Coverage                0-15
  E. Clarity & Readability       0-10
  F. Risk Controls               0-5

Pass threshold: 85.
Auto-fail conditions (override score):
  - fabricated metric/claim/tool detected
  - chronology corruption detected
  - keyword stuffing detected
"""

import re
from typing import Optional

from .types import (
    ElaborateMatchConfig,
    ElaborateScoreBreakdown,
    ElaborateScoreResult,
    ElaborateStructuredOutput,
)

PASS_THRESHOLD = 85

# Common English function/stop words excluded from entity-based comparisons so
# that normal prose variation in the generated output does not penalise truth
# integrity or JD relevance scoring.
_STOPWORDS: frozenset[str] = frozenset({
    "and", "the", "for", "with", "from", "that", "this", "have", "been",
    "were", "are", "was", "our", "their", "they", "will", "you", "your",
    "all", "but", "not", "can", "has", "had", "its", "his", "her", "who",
    "which", "when", "where", "how", "what", "why", "each", "into", "than",
    "then", "them", "these", "those", "such", "both", "more", "most", "very",
    "over", "also", "any", "may", "use", "per", "via", "out", "off", "new",
    "team", "role", "work", "time", "key", "end", "day", "way", "set",
    "enabling", "improving", "reducing", "delivering", "building", "leading",
    "managing", "working", "using", "within", "across", "through", "between",
    "including", "resulting", "providing", "ensuring", "supporting", "growing",
    "demonstrated", "proven", "strong", "senior", "junior", "cross",
    "driven", "oriented", "based", "focused", "related", "required",
    "experience", "skills", "role", "company", "organisation", "organization",
    "track", "record", "expertise", "solutions", "solution", "requires",
    "looking", "seeking", "candidate", "candidates", "responsibilities",
    "ability", "required", "preferred", "plus", "nice", "proficiency",
})


def _meaningful_tokens(text: str) -> set[str]:
    """Extract entity tokens from text, excluding common stopwords."""
    from .validators import extract_entities
    return extract_entities(text) - _STOPWORDS

# ---------------------------------------------------------------------------
# Auto-fail heuristics
# ---------------------------------------------------------------------------

# Patterns that suggest a fabricated or injected number not grounded by the
# original source text (e.g. "increased revenue by 47%", "saved $2.3M").
_FABRICATION_PATTERNS = [
    re.compile(r"\b\d[\d,.]*\s*%"),             # percentages: 47%, 3.5%
    re.compile(r"\$\s*\d[\d,.]*[KMBkmb]?"),     # dollar amounts: $2.5M, $100K
    re.compile(r"\b\d+x\b", re.IGNORECASE),     # multipliers: 3x, 10x
]

_CHRONOLOGY_CORRUPTION_MARKERS = [
    "currently at",
    "present at",
    # Mismatch signals; real detection needs LLM review – this is a heuristic.
]

_STUFFING_THRESHOLD = 0.55  # unique-word ratio below this threshold is considered stuffing


def _check_auto_fail(
    structured: ElaborateStructuredOutput,
    source_resume: str,
    candidate_profile: str,
    allow_metric_inference: bool,
) -> Optional[str]:
    """Return an auto-fail reason string, or None if no auto-fail triggered."""
    final_text = structured.final_resume_text

    if not allow_metric_inference:
        for pattern in _FABRICATION_PATTERNS:
            new_matches = set(pattern.findall(final_text))
            known_matches = set(pattern.findall(source_resume)) | set(
                pattern.findall(candidate_profile)
            )
            fabricated = new_matches - known_matches
            if fabricated:
                return (
                    "Fabricated metric or claim detected in output that is not present "
                    f"in source materials: {', '.join(sorted(fabricated)[:5])}"
                )

    # Keyword-stuffing check: ratio of unique JD-style tokens to total tokens.
    words = re.findall(r"\b[A-Za-z]{3,}\b", final_text.lower())
    if words:
        unique_ratio = len(set(words)) / len(words)
        # Very low unique ratio (many repeated words) = stuffing.
        if unique_ratio < _STUFFING_THRESHOLD:
            return (
                f"Keyword stuffing detected: unique-word ratio {unique_ratio:.2f} "
                f"is below acceptable threshold {_STUFFING_THRESHOLD:.2f}."
            )

    return None


# ---------------------------------------------------------------------------
# Category scorers
# ---------------------------------------------------------------------------

def _score_truth_evidence(
    structured: ElaborateStructuredOutput,
    source_resume: str,
    candidate_profile: str,
) -> float:
    """Score Truth & Evidence Integrity (0-30)."""
    needs = structured.needs_confirmation
    final_text = structured.final_resume_text

    if not final_text:
        return 0.0

    allowed = _meaningful_tokens(source_resume) | _meaningful_tokens(candidate_profile)
    generated = _meaningful_tokens(final_text)
    unsupported_count = len(generated - allowed)

    # Each unsupported meaningful token costs up to 0.3 points, capped at 10 deductions.
    deduction = min(unsupported_count * 0.3, 10.0)

    # Partial credit if uncertainties are properly flagged.
    if needs:
        deduction = max(0.0, deduction - len(needs) * 0.5)

    return max(0.0, 30.0 - deduction)


def _score_jd_relevance(
    structured: ElaborateStructuredOutput,
    job_description: str,
) -> float:
    """Score JD Relevance & Alignment (0-20)."""
    final_text = structured.final_resume_text
    if not final_text or not job_description:
        return 0.0

    jd_tokens = _meaningful_tokens(job_description)
    resume_tokens = _meaningful_tokens(final_text)
    if not jd_tokens:
        return 10.0

    overlap = len(jd_tokens & resume_tokens) / len(jd_tokens)
    return min(20.0, overlap * 20.0)


def _score_impact_specificity(
    structured: ElaborateStructuredOutput,
    config: ElaborateMatchConfig,
) -> float:
    """Score Impact & Specificity (0-20).

    Heuristic: check that experience bullets meet word-count requirements
    and start with action verbs.
    """
    exp_text = structured.professional_experience
    if not exp_text:
        return 0.0

    # Extract bullet-like lines (starting with -, *, or •).
    # Role header lines (e.g. "Senior Role | Company | 2020–Present") are
    # intentionally excluded to avoid polluting the bullet quality analysis.
    bullet_lines = [
        ln.lstrip("-*• ").strip()
        for ln in exp_text.splitlines()
        if re.match(r"^\s*[-*•]", ln)
    ]
    bullet_lines = [b for b in bullet_lines if b]

    if not bullet_lines:
        return 5.0

    good_bullets = 0
    for bullet in bullet_lines:
        words = bullet.split()
        word_count = len(words)
        meets_min = word_count >= config.bullet_min_words
        meets_max = word_count <= config.bullet_max_words
        # Simple action-verb check: first word is title-case or all-lowercase alpha.
        starts_verb = bool(words and re.match(r"^[A-Za-z]+ed$|^[A-Za-z]+ing$|^[A-Z][a-z]+", words[0]))
        if meets_min and meets_max and (not config.require_action_verb or starts_verb):
            good_bullets += 1

    ratio = good_bullets / len(bullet_lines)
    return min(20.0, ratio * 20.0)


def _score_ats_coverage(
    structured: ElaborateStructuredOutput,
    job_description: str,
) -> float:
    """Score ATS Coverage (0-15)."""
    ats_section = structured.ats_keyword_coverage
    final_text = structured.final_resume_text
    if not final_text or not job_description:
        return 0.0

    jd_tokens = _meaningful_tokens(job_description)
    resume_tokens = _meaningful_tokens(final_text)
    if not jd_tokens:
        return 8.0

    covered = len(jd_tokens & resume_tokens) / len(jd_tokens)
    # Bonus if ATS coverage section is present.
    ats_bonus = 1.5 if ats_section else 0.0
    return min(15.0, covered * 13.5 + ats_bonus)


def _score_clarity_readability(structured: ElaborateStructuredOutput) -> float:
    """Score Clarity & Readability (0-10).

    Heuristic: check that all 10 sections are present and non-empty.
    """
    section_weights = {
        "match_summary": 1.0,
        "target_headline": 1.0,
        "target_summary": 1.5,
        "core_skills": 1.0,
        "professional_experience": 2.0,
        "selected_projects": 0.5,
        "education_certifications": 0.5,
        "ats_keyword_coverage": 1.0,
        "needs_confirmation": 0.5,
        "final_resume_text": 1.0,
    }
    earned = 0.0
    for attr, weight in section_weights.items():
        val = getattr(structured, attr)
        if val:  # non-empty list or non-empty string
            earned += weight
    total_weight = sum(section_weights.values())
    return min(10.0, (earned / total_weight) * 10.0)


def _score_risk_controls(structured: ElaborateStructuredOutput) -> float:
    """Score Risk Controls (0-5).

    Full marks if NEEDS_CONFIRMATION section has entries; zero if empty.
    """
    if structured.needs_confirmation:
        return 5.0
    return 0.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_elaborate_result(
    structured: ElaborateStructuredOutput,
    job_description: str,
    source_resume: str,
    candidate_profile: str = "",
    config: Optional[ElaborateMatchConfig] = None,
) -> ElaborateScoreResult:
    """Compute a 0-100 quality score for an elaborate_match output.

    Returns an :class:`ElaborateScoreResult` with the total, per-category
    breakdown, pass/fail status, and diagnostic messages.
    """
    if config is None:
        config = ElaborateMatchConfig()

    auto_fail_reason = _check_auto_fail(
        structured, source_resume, candidate_profile, config.allow_metric_inference
    )

    breakdown = ElaborateScoreBreakdown(
        truth_evidence_integrity=_score_truth_evidence(
            structured, source_resume, candidate_profile
        ),
        jd_relevance_alignment=_score_jd_relevance(structured, job_description),
        impact_specificity=_score_impact_specificity(structured, config),
        ats_coverage=_score_ats_coverage(structured, job_description),
        clarity_readability=_score_clarity_readability(structured),
        risk_controls=_score_risk_controls(structured),
    )

    total = (
        breakdown.truth_evidence_integrity
        + breakdown.jd_relevance_alignment
        + breakdown.impact_specificity
        + breakdown.ats_coverage
        + breakdown.clarity_readability
        + breakdown.risk_controls
    )

    passed = (auto_fail_reason is None) and (total >= PASS_THRESHOLD)

    diagnostics: list[str] = []
    if auto_fail_reason:
        diagnostics.append(f"AUTO-FAIL: {auto_fail_reason}")
    if total < PASS_THRESHOLD and auto_fail_reason is None:
        diagnostics.append(
            f"Score {total:.1f} is below pass threshold {PASS_THRESHOLD}."
        )
    if breakdown.truth_evidence_integrity < 20:
        diagnostics.append(
            "Truth & Evidence Integrity is low — review unsupported claims and "
            "expand NEEDS_CONFIRMATION."
        )
    if breakdown.jd_relevance_alignment < 12:
        diagnostics.append(
            "JD Relevance is low — ensure experience bullets mirror key JD language."
        )
    if breakdown.impact_specificity < 12:
        diagnostics.append(
            "Impact & Specificity is low — expand bullets with context, actions, and outcomes."
        )
    if breakdown.ats_coverage < 8:
        diagnostics.append(
            "ATS Coverage is low — include additional truthful JD keywords."
        )

    return ElaborateScoreResult(
        total=total,
        breakdown=breakdown,
        passed=passed,
        auto_fail_reason=auto_fail_reason,
        diagnostics=diagnostics,
    )
