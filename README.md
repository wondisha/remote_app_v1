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
