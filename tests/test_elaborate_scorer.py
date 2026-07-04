"""Unit tests for elaborate_match scorer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.resume_tailoring.types import (
    ElaborateMatchConfig,
    ElaborateStructuredOutput,
)
from src.resume_tailoring.scorer import (
    PASS_THRESHOLD,
    score_elaborate_result,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_good_output() -> ElaborateStructuredOutput:
    """Return a well-formed output that should pass scoring."""
    # Bullets are deliberately ≥14 words and start with past-tense action verbs.
    bullet1 = (
        "Designed and implemented scalable ETL pipeline architecture using Python and AWS Glue "
        "enabling automated daily data ingestion for the analytics engineering team."
    )
    bullet2 = (
        "Led migration of legacy SQL workflows to cloud-native pipeline design on AWS, "
        "eliminating manual intervention and improving data availability for stakeholder reporting."
    )
    bullet3 = (
        "Partnered with analytics leadership and stakeholder management teams to build "
        "self-service reporting dashboards, accelerating data-driven decision-making across the organisation."
    )
    bullet4 = (
        "Established code-review governance and pipeline design standards adopted across the "
        "data engineering squad, improving deployment consistency and reducing integration defects."
    )
    bullet5 = (
        "Mentored junior engineers in Python, SQL, and AWS best practices, growing team "
        "capability and reducing onboarding time for new data pipeline contributors."
    )
    exp = (
        "Senior Data Engineer | Acme Corp | 2020 – Present\n"
        f"- {bullet1}\n"
        f"- {bullet2}\n"
        f"- {bullet3}\n"
        f"- {bullet4}\n"
        f"- {bullet5}\n"
    )
    final_text = (
        "Senior Data Engineer | Python | AWS | Analytics\n\n"
        "Experienced data engineer with deep expertise in Python, SQL, ETL pipeline design, "
        "and AWS cloud platforms. Demonstrated leadership and stakeholder management skills.\n\n"
        "CORE SKILLS\nPython, SQL, AWS, ETL pipeline design, data engineering, analytics, "
        "leadership, stakeholder management, cloud platforms\n\n"
        "PROFESSIONAL EXPERIENCE\n"
        "Senior Data Engineer | Acme Corp | 2020 – Present\n"
        f"- {bullet1}\n"
        f"- {bullet2}\n"
        f"- {bullet3}\n"
        f"- {bullet4}\n"
        f"- {bullet5}\n"
    )
    return ElaborateStructuredOutput(
        match_summary=[
            "Strong alignment with Python and ETL pipeline design requirements.",
            "Relevant AWS cloud platform experience demonstrated in previous data engineering roles.",
            "Proven leadership of cross-functional data and analytics teams.",
            "Track record of delivering pipeline optimisations and stakeholder management excellence.",
            "ATS-optimised language with full JD keyword coverage incorporated throughout.",
        ],
        target_headline="Senior Data Engineer | Python | AWS | Analytics Leadership",
        target_summary=(
            "Experienced data engineer with strong background in Python, SQL, and ETL pipeline design.\n"
            "Track record of building scalable data pipelines on AWS cloud platforms.\n"
            "Skilled in cross-functional analytics collaboration and stakeholder management.\n"
            "Committed to evidence-based data engineering decision-making."
        ),
        core_skills=(
            "Technical: Python, SQL, AWS, ETL pipeline design, data engineering, analytics\n"
            "Leadership: Stakeholder management, Team mentoring, Governance"
        ),
        professional_experience=exp,
        selected_projects=(
            "Data platform modernisation — migrated on-premise warehouse to AWS cloud "
            "using Python ETL pipelines, enabling analytics self-service."
        ),
        education_certifications="BSc Computer Science | 2015 | AWS Certified Data Analytics",
        ats_keyword_coverage=(
            "Included keywords: Python, SQL, ETL, AWS, data engineering, analytics, "
            "leadership, stakeholder management, pipeline design, cloud\n"
            "Missing keywords: (none identified as truth-safe additions)"
        ),
        needs_confirmation=[
            "Confirm exact throughput figures for pipeline optimisation bullet.",
            "Verify AWS service versions mentioned are current.",
        ],
        final_resume_text=final_text,
    )


_SAMPLE_RESUME = (
    "John Smith | Senior Data Engineer\n"
    "Python SQL AWS ETL pipeline design analytics data engineering leadership "
    "stakeholder management cloud platforms mentored governance cross-functional "
    "organisation implemented designed led collaborated established drove migrated "
    "scalable architecture automated scheduling cloud-native accelerating "
    "self-service reporting decision-making deployment integration contributors "
    "capability reducing onboarding consistency engineering squad standards "
    "governance reviewing code team Acme Corp 2020 Present best practices "
    "dashboards visualisation tooling workflows ingestion availability "
    "eliminating intervention improving delivering excellence certified "
)

_SAMPLE_JD = (
    "We are looking for a Senior Data Engineer with expertise in Python, SQL, "
    "ETL pipeline design, and cloud platforms such as AWS. "
    "The role requires leadership skills, stakeholder management experience, "
    "and a track record of delivering analytics data engineering solutions."
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestScoreElaborateResult:
    def test_good_output_passes(self):
        output = _make_good_output()
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert result.passed, (
            f"Expected pass but got score={result.total:.1f}, "
            f"diagnostics={result.diagnostics}"
        )
        assert result.total >= PASS_THRESHOLD

    def test_empty_output_fails(self):
        output = ElaborateStructuredOutput()
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert not result.passed
        assert result.total < PASS_THRESHOLD

    def test_auto_fail_on_fabricated_metric(self):
        """Fabricated percentage not in source should trigger auto-fail."""
        output = _make_good_output()
        output.final_resume_text += "\n- Increased revenue by 47% in first quarter."
        config = ElaborateMatchConfig(allow_metric_inference=False)
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME, config=config)
        assert not result.passed
        assert result.auto_fail_reason is not None
        assert "fabricated" in result.auto_fail_reason.lower() or "metric" in result.auto_fail_reason.lower()

    def test_auto_fail_not_triggered_when_metric_in_source(self):
        """A percentage that already appears in source resume must not auto-fail."""
        resume_with_number = _SAMPLE_RESUME + " improved pipeline throughput by 30%"
        output = _make_good_output()
        output.final_resume_text += "\n- Improved pipeline throughput by 30%."
        config = ElaborateMatchConfig(allow_metric_inference=False)
        result = score_elaborate_result(output, _SAMPLE_JD, resume_with_number, config=config)
        assert result.auto_fail_reason is None

    def test_allow_metric_inference_disables_fabrication_check(self):
        output = _make_good_output()
        output.final_resume_text += "\n- Increased efficiency by 47%."
        config = ElaborateMatchConfig(allow_metric_inference=True)
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME, config=config)
        assert result.auto_fail_reason is None

    def test_score_breakdown_categories_bounded(self):
        output = _make_good_output()
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME)
        bd = result.breakdown
        assert 0.0 <= bd.truth_evidence_integrity <= 30.0
        assert 0.0 <= bd.jd_relevance_alignment <= 20.0
        assert 0.0 <= bd.impact_specificity <= 20.0
        assert 0.0 <= bd.ats_coverage <= 15.0
        assert 0.0 <= bd.clarity_readability <= 10.0
        assert 0.0 <= bd.risk_controls <= 5.0

    def test_total_equals_sum_of_breakdown(self):
        output = _make_good_output()
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME)
        bd = result.breakdown
        expected_total = (
            bd.truth_evidence_integrity
            + bd.jd_relevance_alignment
            + bd.impact_specificity
            + bd.ats_coverage
            + bd.clarity_readability
            + bd.risk_controls
        )
        assert abs(result.total - expected_total) < 1e-9

    def test_missing_needs_confirmation_lowers_risk_score(self):
        output = _make_good_output()
        output.needs_confirmation = []
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert result.breakdown.risk_controls < 5.0

    def test_diagnostics_populated_on_low_score(self):
        output = ElaborateStructuredOutput(final_resume_text="minimal")
        result = score_elaborate_result(output, _SAMPLE_JD, _SAMPLE_RESUME)
        assert len(result.diagnostics) > 0
