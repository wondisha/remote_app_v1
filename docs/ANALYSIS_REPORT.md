# Analysis Report: remote_app

## Scope

Source analyzed: `wondisha/remote_app` (Python-first app for job discovery, ranking, prep, and browser-based application workflows).

## Architecture overview

Core modules observed:

- `apply_agent.py`: CLI orchestration and mode routing.
- `discovery.py`: multi-portal URL discovery.
- `documents.py`: job context extraction, ranking helpers, artifact generation, interview prep and tailored resume outputs.
- `config.py`: environment config and provider/runtime validation.
- `agent.py`, `storage.py`, `app_backend/*` referenced by orchestrator for execution, persistence, and API runtime.

## Strengths

1. Clear modular decomposition.
2. Useful CLI operational modes (`preflight`, `discover-only`, `generate-docs-only`, full apply).
3. Multi-source portal discovery support.
4. Good baseline safety prompting for resume tailoring ("do not invent facts").
5. Artifact persistence model for per-job outputs.

## Key risks / gaps

### 1) Reliability and network hardening

- Discovery and posting fetch rely on simple request calls.
- Missing robust retry policy, 429 handling, and portal-specific circuit breakers.
- Regex-only HTML extraction is brittle for frequently changing portal pages.

### 2) Execution safety and idempotency

- Batch apply paths need explicit idempotency tokens to prevent duplicate submissions.
- Failure classes are broad in places (`except Exception`).
- No explicit state-machine transitions persisted per job lifecycle.

### 3) Ranking quality

- Ranking is mostly keyword-hit based.
- Susceptible to false positives/negatives when wording differs semantically.
- Limited explainability schema for why a job was selected or rejected.

### 4) Resume tailoring governance

- Good prompt guardrails exist, but enforcement is still model-output dependent.
- Missing explicit evidence map tying each tailored claim to source resume/profile evidence.
- Needs deterministic checks for prohibited entities (new employers/metrics/dates).

### 5) Config/security posture

- Env-driven config is good.
- Personal fallback defaults for profile fields should be removed for production-like mode (fail closed if required profile fields absent).

## Recommendations summary

- Introduce resilient HTTP client wrappers with retries/backoff/jitter.
- Implement job lifecycle state machine + idempotency keys.
- Upgrade scoring to weighted, explainable multi-factor model.
- Add evidence-anchored resume tailoring validation and delta reports.
- Add structured telemetry and audit manifests for every run.

