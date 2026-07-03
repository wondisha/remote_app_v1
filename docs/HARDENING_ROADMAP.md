# Hardening Roadmap

## P0 (do first)

1. **Idempotent apply pipeline**
   - Create deterministic `job_run_id` from job URL + candidate + date window.
   - Prevent duplicate submit operations for same idempotency window.

2. **Network resilience for discovery/fetch**
   - Shared HTTP session client.
   - Exponential backoff + jitter.
   - Retry policy for 429/5xx and connect timeouts.
   - Circuit breaker per portal.

3. **Safety gate before submit**
   - Add dry-run mode default in non-production profile.
   - Hard guardrails when verification confidence is low.

## P1 (next)

1. **Ranking model v2**
   - Weighted factors: role fit, skills overlap, location fit, verification confidence, recency signals.
   - Return explicit reason codes and confidence score.

2. **Resume tailoring governance**
   - Evidence map for each bullet/claim.
   - Delta report from source resume.
   - Policy validator to block unsupported claims.

3. **Structured observability**
   - JSON logs with run_id/job_id/portal/model/event.
   - Artifact manifest with checksums and timestamps.

## P2 (after stabilization)

1. Queue-backed workers for discovery and document generation.
2. Concurrency control with per-portal limits.
3. Better semantic job matching using embeddings.
4. Admin dashboard for run health and rejection diagnostics.

