"""Unit tests for elaborate_match end-to-end pipeline (tailor_resume_elaborate)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.resume_tailoring.tailor import tailor_resume_elaborate, tailor_resume_to_jd
from src.resume_tailoring.types import ElaborateMatchConfig, ElaborateMatchResult, TailoringResult


_SAMPLE_RESUME = (
    "Jane Doe | Senior Data Engineer\n"
    "Skills: Python, SQL, AWS, ETL, data pipelines, cloud, analytics, leadership, stakeholder management\n"
    "Experience: Led data platform migration at Acme Corp 2020-2024."
)

_SAMPLE_JD = (
    "We are hiring a Senior Data Engineer with Python, SQL, ETL pipeline design, "
    "and AWS cloud platform expertise. Strong leadership and stakeholder management skills required."
)


class TestTailorResumeElaborate:
    def test_returns_elaborate_match_result(self):
        result = tailor_resume_elaborate(
            source_resume_text=_SAMPLE_RESUME,
            job_title="Senior Data Engineer",
            job_description=_SAMPLE_JD,
        )
        assert isinstance(result, ElaborateMatchResult)
        assert result.mode == "elaborate_match"

    def test_structured_output_has_final_text(self):
        result = tailor_resume_elaborate(
            source_resume_text=_SAMPLE_RESUME,
            job_title="Senior Data Engineer",
            job_description=_SAMPLE_JD,
        )
        assert result.structured_output.final_resume_text.strip()

    def test_score_result_present(self):
        result = tailor_resume_elaborate(
            source_resume_text=_SAMPLE_RESUME,
            job_title="Senior Data Engineer",
            job_description=_SAMPLE_JD,
        )
        assert 0.0 <= result.score.total <= 100.0

    def test_optional_fields_accepted(self):
        result = tailor_resume_elaborate(
            source_resume_text=_SAMPLE_RESUME,
            job_title="Senior Data Engineer",
            job_description=_SAMPLE_JD,
            company_name="TechCorp",
            location_type="Remote, US",
            linkedin_text="Jane Doe on LinkedIn: data engineering expert.",
            extra_notes="Also worked on streaming data with Kafka.",
        )
        assert isinstance(result, ElaborateMatchResult)

    def test_custom_config_accepted(self):
        config = ElaborateMatchConfig(
            bullet_min_words=10,
            min_bullets_per_recent_role=3,
            allow_metric_inference=True,
        )
        result = tailor_resume_elaborate(
            source_resume_text=_SAMPLE_RESUME,
            job_title="Data Engineer",
            job_description=_SAMPLE_JD,
            config=config,
        )
        assert isinstance(result, ElaborateMatchResult)

    def test_warnings_is_list(self):
        result = tailor_resume_elaborate(
            source_resume_text=_SAMPLE_RESUME,
            job_title="Senior Data Engineer",
            job_description=_SAMPLE_JD,
        )
        assert isinstance(result.warnings, list)


class TestTailorResumeToJd:
    """Ensure the original standard tailoring function is unaffected."""

    def test_returns_tailoring_result(self):
        result = tailor_resume_to_jd(
            source_resume_text=_SAMPLE_RESUME,
            candidate_profile_text="",
            job_title="Data Engineer",
            job_description=_SAMPLE_JD,
        )
        assert isinstance(result, TailoringResult)
        assert result.tailored_summary
        assert len(result.tailored_bullets) > 0
        assert isinstance(result.warnings, list)
