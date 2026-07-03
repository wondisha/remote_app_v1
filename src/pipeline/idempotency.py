import hashlib
from datetime import date


def build_job_run_id(job_url: str, candidate_id: str, run_date: date | None = None) -> str:
    d = run_date or date.today()
    raw = f"{job_url.strip()}|{candidate_id.strip()}|{d.isoformat()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
