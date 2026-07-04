"""Unit tests for elaborate_match validators."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.resume_tailoring.types import ElaborateMatchConfig, ElaborateStructuredOutput
from src.resume_tailoring.validators import validate_elaborate_output


_SAMPLE_RESUME = (
    "Jane Doe | Data Engineer\n"
    "Python SQL AWS ETL pipelines cloud leadership analytics stakeholder"
)

_SAMPLE_JD = (
    "Looking for a Data Engineer with Python, SQL, ETL, AWS, and analytics skills. "
    "Leadership and stakeholder management experience required."
)


def _good_output() -> ElaborateStructuredOutput:
    bullet = (
        "- Designed and implemented ETL pipeline using Python and AWS Glue, "
        "improving data availability and reducing manual intervention across analytics team."
    )
    exp = "Data Engineer | Corp | 2020–Present\n" + "\n".join([bullet] * 5) + "\n"
    return ElaborateStructuredOutput(
        match_summary=["Strong Python and SQL alignment.", "Cloud experience.", "Leadership."],
        target_headline="Data Engineer | Python | AWS",
        target_summary="Experienced data engineer with Python and SQL background.",
        core_skills="Python, SQL, AWS, ETL",
        professional_experience=exp,
        selected_projects="Data platform migration.",
        education_certifications="BSc Computer Science",
        ats_keyword_coverage="Included: Python, SQL, ETL, AWS\nMissing: none",
        needs_confirmation=["Confirm tool versions."],
        final_resume_text=(
            "Data Engineer | Python | AWS\n"
            "Experienced data engineer with Python SQL AWS ETL analytics stakeholder leadership.\n"
            + exp
        ),
    )


class TestValidateElaborateOutput:
    def test_good_output_passes(self):
        output = _good_output()
        failures = validate_elaborate_output(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert failures == [], f"Unexpected failures: {failures}"

    def test_empty_final_resume_text_fails(self):
        output = _good_output()
        output.final_resume_text = ""
        failures = validate_elaborate_output(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert any("FINAL_RESUME_TEXT" in f for f in failures)

    def test_fabricated_number_fails(self):
        output = _good_output()
        output.final_resume_text += "\n- Cut costs by $2.5M within first quarter."
        config = ElaborateMatchConfig(allow_metric_inference=False)
        failures = validate_elaborate_output(output, _SAMPLE_JD, _SAMPLE_RESUME, config=config)
        assert any("fabricated" in f.lower() for f in failures)

    def test_metric_in_source_does_not_fail(self):
        resume_with_num = _SAMPLE_RESUME + " saved $2.5M in operational costs"
        output = _good_output()
        output.final_resume_text += "\n- Cut costs by $2.5M within first quarter."
        config = ElaborateMatchConfig(allow_metric_inference=False)
        failures = validate_elaborate_output(output, _SAMPLE_JD, resume_with_num, config=config)
        assert not any("fabricated" in f.lower() for f in failures)

    def test_missing_jd_keywords_fails(self):
        output = _good_output()
        output.final_resume_text = "Resume with no relevant words whatsoever."
        failures = validate_elaborate_output(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert any("keyword" in f.lower() for f in failures)

    def test_insufficient_bullets_fails(self):
        output = _good_output()
        # Replace experience with a single short bullet.
        output.professional_experience = (
            "Role | Company | 2020–Present\n"
            "- Did some work.\n"
        )
        config = ElaborateMatchConfig(min_bullets_per_recent_role=5, bullet_min_words=14)
        failures = validate_elaborate_output(
            output, _SAMPLE_JD, _SAMPLE_RESUME, config=config
        )
        assert any("bullet" in f.lower() for f in failures)

    def test_empty_needs_confirmation_triggers_warning(self):
        output = _good_output()
        output.needs_confirmation = []
        config = ElaborateMatchConfig(flag_uncertain_claims=True)
        failures = validate_elaborate_output(
            output, _SAMPLE_JD, _SAMPLE_RESUME, config=config
        )
        assert any("NEEDS_CONFIRMATION" in f for f in failures)

    def test_flag_uncertain_claims_false_skips_warning(self):
        output = _good_output()
        output.needs_confirmation = []
        config = ElaborateMatchConfig(flag_uncertain_claims=False)
        failures = validate_elaborate_output(
            output, _SAMPLE_JD, _SAMPLE_RESUME, config=config
        )
        assert not any("NEEDS_CONFIRMATION" in f for f in failures)
