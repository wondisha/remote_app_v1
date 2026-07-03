from .types import TailoringResult, EvidenceItem
from .validators import validate_claims_supported


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
