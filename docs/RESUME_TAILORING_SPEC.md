# Resume Tailoring Spec (Truth-Preserving)

## Objective

Generate job-targeted resume language without fabricating experience or credentials.

## Inputs

- Source resume text
- Candidate profile
- Job description / job context

## Outputs

1. Tailored summary
2. Tailored bullet suggestions
3. Evidence map (claim -> supporting source)
4. Delta report (what changed from source phrasing)

## Policy rules

1. No new employers, dates, certifications, or metrics unless present in source evidence.
2. No unsupported technology claims.
3. Every generated bullet must map to one or more source evidence snippets.
4. If evidence is weak, output a caution flag and conservative wording.

## Validation gates

- Entity whitelist gate (from source resume/profile/job title context).
- Number/metric gate (blocks newly introduced numerical claims unless supported).
- Evidence coverage threshold (100% of bullets must have evidence references).

## Recommended workflow

1. Parse JD into required/preferred skills.
2. Extract candidate evidence spans.
3. Generate constrained rewrite.
4. Run policy validators.
5. Emit final artifact + evidence JSON.

