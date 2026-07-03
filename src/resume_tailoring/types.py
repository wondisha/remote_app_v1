from dataclasses import dataclass
from typing import List


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
