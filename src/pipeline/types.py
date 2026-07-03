from dataclasses import dataclass
from typing import Literal, Optional


JobState = Literal[
    "discovered",
    "ranked",
    "docs_generated",
    "apply_started",
    "applied",
    "skipped",
    "failed",
]


@dataclass
class JobRunRecord:
    job_run_id: str
    job_url: str
    state: JobState
    reason: Optional[str] = None
