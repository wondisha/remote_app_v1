from dataclasses import dataclass
from typing import Dict


@dataclass
class ScoreBreakdown:
    role_fit: float
    skills_overlap: float
    location_fit: float
    verification_confidence: float
    preference_alignment: float


def score_weighted(features: Dict[str, float]) -> tuple[float, ScoreBreakdown]:
    role_fit = max(0.0, min(30.0, features.get("role_fit", 0.0)))
    skills_overlap = max(0.0, min(30.0, features.get("skills_overlap", 0.0)))
    location_fit = max(0.0, min(15.0, features.get("location_fit", 0.0)))
    verification_confidence = max(0.0, min(15.0, features.get("verification_confidence", 0.0)))
    preference_alignment = max(0.0, min(10.0, features.get("preference_alignment", 0.0)))

    total = role_fit + skills_overlap + location_fit + verification_confidence + preference_alignment
    return total, ScoreBreakdown(
        role_fit=role_fit,
        skills_overlap=skills_overlap,
        location_fit=location_fit,
        verification_confidence=verification_confidence,
        preference_alignment=preference_alignment,
    )
