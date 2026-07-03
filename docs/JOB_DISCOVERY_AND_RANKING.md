# Job Discovery and Ranking (v1)

## Discovery design

Supported portal adapters should implement a common interface:

- `discover(query, location, max_results) -> list[JobPostingRef]`
- `fetch_context(url) -> JobContext`

Where:

- `JobPostingRef`: url, portal, external_id, discovered_at
- `JobContext`: title, company, location, description_excerpt, full_text_hash, verification_signals

## Ranking design

Score = weighted sum of:

1. Role keyword fit (0-30)
2. Skills overlap (0-30)
3. Location/work mode fit (0-15)
4. Verification confidence (0-15)
5. Candidate preference alignment (0-10)

Return:

- numeric score
- confidence
- reason codes
- top positive and negative factors

## Selection policy

- Filter out jobs below configurable minimum score.
- Filter out unverified companies when strict mode enabled.
- Select top N by score and confidence.

## Failure policy

- Adapter failures are non-fatal; continue with other portals.
- Mark failed contexts with typed reason code.
- Preserve retry metadata for operations diagnostics.

