from dataclasses import dataclass, field
from typing import List, Literal, Optional


TailoringMode = Literal["standard", "elaborate_match"]


@dataclass
class EvidenceItem:
    claim: str
    evidence: List[str]


@dataclass
class TailoringResult:
    tailored_summary: str
    tailored_bullets: List[str]
    evidence_map: List[EvidenceItem]
    warnings: List[str]


# ---------------------------------------------------------------------------
# elaborate_match mode
# ---------------------------------------------------------------------------

@dataclass
class ElaborateMatchConfig:
    """Generation policy knobs for elaborate_match mode."""

    bullet_min_words: int = 14
    bullet_max_words: int = 30
    min_bullets_per_recent_role: int = 5
    max_bullets_per_role: int = 7
    require_action_verb: bool = True
    require_outcome_phrase: bool = True
    allow_metric_inference: bool = False
    keyword_insertion_policy: str = "truth_only"
    flag_uncertain_claims: bool = True


@dataclass
class ElaborateStructuredOutput:
    """10-section structured output contract for elaborate_match."""

    match_summary: List[str] = field(default_factory=list)
    target_headline: str = ""
    target_summary: str = ""
    core_skills: str = ""
    professional_experience: str = ""
    selected_projects: str = ""
    education_certifications: str = ""
    ats_keyword_coverage: str = ""
    needs_confirmation: List[str] = field(default_factory=list)
    final_resume_text: str = ""


@dataclass
class ElaborateScoreBreakdown:
    """Score breakdown across the 6 rubric categories (total max = 100)."""

    truth_evidence_integrity: float = 0.0    # 0-30
    jd_relevance_alignment: float = 0.0      # 0-20
    impact_specificity: float = 0.0          # 0-20
    ats_coverage: float = 0.0                # 0-15
    clarity_readability: float = 0.0         # 0-10
    risk_controls: float = 0.0               # 0-5


@dataclass
class ElaborateScoreResult:
    """Post-generation scoring result."""

    total: float
    breakdown: ElaborateScoreBreakdown
    passed: bool
    auto_fail_reason: Optional[str]
    diagnostics: List[str] = field(default_factory=list)


@dataclass
class ElaborateMatchResult:
    """Full result for elaborate_match tailoring."""

    mode: TailoringMode
    structured_output: ElaborateStructuredOutput
    score: ElaborateScoreResult
    warnings: List[str] = field(default_factory=list)
