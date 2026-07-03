# Operations Runbook

## Safe rollout sequence

1. Run discovery-only in dry mode.
2. Validate ranking outputs and rejection reasons.
3. Generate docs-only for sampled jobs.
4. Validate resume tailoring warnings and evidence coverage.
5. Enable single apply mode.
6. Enable batch apply with low daily cap.

## Incident handling

- If portal errors spike (429/403/5xx), trip circuit breaker and pause submissions.
- If unsupported resume claims are detected, block final artifact and require manual review.
- If duplicate applications are detected, inspect idempotency key generation and storage.

## Required telemetry fields

- run_id
- job_run_id
- job_url
- portal
- stage
- decision
- reason_code
- model_name
- timestamp

