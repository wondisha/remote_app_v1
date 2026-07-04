# remote_app_v1

Best-practice upgrade pack for `wondisha/remote_app` focused on reliability, safer automation, and truthful resume tailoring.

## Quick Start (Use This First)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .\.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
```

Then run (from your runtime repo where `apply_agent.py` exists):

```bash
python apply_agent.py --preflight --job-url "https://linkedin.com/jobs/view/123/" --resume resume.pdf
python apply_agent.py --discover-only --job-search-query "data engineer" --job-search-location "Texas" --resume resume.pdf
python apply_agent.py --job-search-query "data engineer" --job-search-location "Texas" --resume resume.pdf
```

## What this repository contains

- Full technical analysis of `remote_app`
- Prioritized hardening roadmap (P0/P1/P2)
- Job discovery and ranking design improvements
- Resume-to-job-description tailoring specification (truth-preserving)
- Code scaffolds for orchestration, scoring, and tailoring
- Operations runbook

## How to Execute the App (End-to-End)

> `remote_app_v1` is a blueprint/scaffold repo. Execute the full app from your runtime repo (`remote_app`) and use v1 docs/code to harden it.

### 1) Preflight first

```bash
python apply_agent.py --preflight --job-url "https://linkedin.com/jobs/view/123/" --resume resume.pdf
```

### 2) Safe mode: discover only

```bash
python apply_agent.py --discover-only --job-search-query "data engineer" --job-search-location "Texas" --resume resume.pdf
```

### 3) Generate docs only

```bash
python apply_agent.py --generate-docs-only --job-url "https://linkedin.com/jobs/view/123/" --resume resume.pdf
```

### 4) Apply to one posting

```bash
python apply_agent.py --job-url "https://linkedin.com/jobs/view/123/" --resume resume.pdf
```

### 5) Batch apply from file

```bash
python apply_agent.py --job-urls-file jobs.txt --resume resume.pdf
```

### 6) Discover and apply in one run

```bash
python apply_agent.py --job-search-query "senior data engineer python airflow dbt" --job-search-location "Dallas, TX" --resume resume.pdf
```

## Better Search Strategy (Higher Match Quality)

1. **Use role + stack keywords together**
   - Example: `"senior data engineer python airflow dbt"`
2. **Constrain location intentionally**
   - Start broad (`Texas`), then narrow (`Dallas, TX`) after preview.
3. **Tune in discover-only mode first**
   - Iterate query text before enabling apply mode.
4. **Keep verification strict by default**
   - Prefer verified companies and maintain allowlist carefully.
5. **Use focused batches**
   - Curate high-quality URLs in `jobs.txt`.

### Recommended search progression

Start broad preview:

```bash
python apply_agent.py --discover-only --job-search-query "data engineer" --job-search-location "Texas" --resume resume.pdf
```

Refine:

```bash
python apply_agent.py --discover-only --job-search-query "senior data engineer python airflow dbt" --job-search-location "Dallas, TX" --resume resume.pdf
```

Apply after relevance is good:

```bash
python apply_agent.py --job-search-query "senior data engineer python airflow dbt" --job-search-location "Dallas, TX" --resume resume.pdf
```

## Goals

1. Keep the original repo untouched.
2. Provide a production-ready blueprint for safer job automation.
3. Enforce evidence-based resume tailoring (no fabricated claims).

## Resume Tailoring: `elaborate_match` Mode

The `elaborate_match` tailoring mode produces richer, truth-preserving, JD-aligned resume output instead of over-compressed summaries.

### How to use `elaborate_match`

```python
from src.resume_tailoring.tailor import tailor_resume_elaborate
from src.resume_tailoring.types import ElaborateMatchConfig

result = tailor_resume_elaborate(
    source_resume_text="... your full resume text ...",
    job_title="Senior Data Engineer",
    job_description="... full JD text ...",
    # Optional inputs for richer output:
    company_name="Acme Corp",
    location_type="Remote, US",
    candidate_profile_text="... LinkedIn profile export or profile summary ...",
    linkedin_text="... LinkedIn profile text if separate ...",
    extra_notes="Also worked on streaming pipelines with Kafka.",
    # Optional policy config (defaults shown):
    config=ElaborateMatchConfig(
        bullet_min_words=14,
        bullet_max_words=30,
        min_bullets_per_recent_role=5,
        max_bullets_per_role=7,
        require_action_verb=True,
        require_outcome_phrase=True,
        allow_metric_inference=False,
        keyword_insertion_policy="truth_only",
        flag_uncertain_claims=True,
    ),
)

# Access structured sections
print(result.structured_output.final_resume_text)

# Check score
print(f"Score: {result.score.total:.1f}/100 — {'PASS' if result.score.passed else 'FAIL'}")
print(result.score.breakdown)

# Review warnings and flagged uncertainties
for w in result.warnings:
    print("Warning:", w)
for item in result.structured_output.needs_confirmation:
    print("Needs confirmation:", item)
```

### Expected inputs

| Input | Required | Description |
|---|---|---|
| `source_resume_text` | ✅ | Full base resume as plain text |
| `job_title` | ✅ | Target job title |
| `job_description` | ✅ | Full job description text |
| `candidate_profile_text` | Optional | LinkedIn export or profile summary |
| `linkedin_text` | Optional | LinkedIn profile text (if separate from profile) |
| `company_name` | Optional | Hiring company name (enriches prompt) |
| `location_type` | Optional | Work location / type (e.g. "Remote, US") |
| `extra_notes` | Optional | Additional experience context for the LLM |

### Output sections

The `structured_output` field contains all 10 structured sections:

| Section | Description |
|---|---|
| `match_summary` | 5–8 bullets summarising fit to the JD |
| `target_headline` | ATS-optimised professional headline |
| `target_summary` | 4–6 line professional summary |
| `core_skills` | Skills grouped by category |
| `professional_experience` | Role-by-role tailored bullets |
| `selected_projects` | 2–4 relevant projects (if applicable) |
| `education_certifications` | Education and certifications |
| `ats_keyword_coverage` | Included/missing JD keywords |
| `needs_confirmation` | Uncertain claims flagged for user review |
| `final_resume_text` | Clean copy-paste-ready resume text |

### Scoring threshold behaviour

Quality is scored 0–100 across 6 rubric categories:

| Category | Max | Description |
|---|---|---|
| Truth & Evidence Integrity | 30 | All claims grounded in source materials |
| JD Relevance & Alignment | 20 | Experience mirrors JD responsibilities and keywords |
| Impact & Specificity | 20 | Bullets are detailed, outcome-oriented, action-led |
| ATS Coverage | 15 | Critical JD keywords included truthfully |
| Clarity & Readability | 10 | All 10 sections present and well-structured |
| Risk Controls | 5 | Uncertainties captured in NEEDS_CONFIRMATION |

**Pass threshold: 85/100.**

Auto-fail conditions (override score regardless of total):
- Fabricated metric or claim not present in source materials
- Keyword stuffing detected (abnormally low unique-word ratio)

On failure, `result.score.passed` is `False` and `result.score.diagnostics` contains actionable messages explaining what to fix.

### LLM integration

The `_call_llm_elaborate` function in `src/resume_tailoring/tailor.py` is the integration seam. Replace its body with your preferred LLM client (OpenAI, Anthropic, Gemini). The pipeline — prompt building, section parsing, scoring, validation — is fully implemented around it.

```python
# Example: OpenAI integration
import openai

def _call_llm_elaborate(system_prompt: str, user_prompt: str) -> str:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
```


## Suggested next steps

1. Review `docs/ANALYSIS_REPORT.md` and `docs/HARDENING_ROADMAP.md`.
2. Implement adapters from this scaffold into your active runtime.
3. Add tests for ranking, idempotency, and tailoring guardrails.
4. Roll out in dry-run mode before enabling submit actions.

## Troubleshooting

- **`ModuleNotFoundError`**: Activate virtual environment and reinstall dependencies.
- **No jobs discovered**: Improve query specificity and widen/narrow location deliberately.
- **Too many low-quality hits**: Add stack/domain terms and run discover-only tuning.
- **Browser issues**: Confirm Chrome/Edge installation and local runtime permissions.
- **Slow generation**: Use bounded document limits and smaller test batches first.
