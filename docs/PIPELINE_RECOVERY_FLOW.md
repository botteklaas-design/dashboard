# Pipeline Recovery Flow (v1.2b)

## Purpose
Guarantee publish continuity when one or more core stages fail validation, while clearly signaling degraded quality.

## Trigger
1. Run `scripts/validate_pipeline_outputs.py`.
2. If `validation-report.json` has `pass=false`, run `scripts/pipeline_auto_recovery.py`.
3. Recovery executes deterministic fallback synthesis for invalid/missing core stages.

## Recovery synthesis order and data priority
Source priority is fixed:
1. Existing stage 03 output (if partially usable)
2. Existing stage 02 output
3. Stage 01 forum scout ideas

Deterministic rules:
- If stage 02 is missing/invalid:
  - Build bounded `02-business-analysis.md` with scoring framework and final ranking.
  - Generate top 3 ideas from stage 01 using a fixed heuristic.
  - Mark output with `RECOVERY_DRAFT: true`.
- If stage 03 is missing/invalid:
  - Build `03-final-winner-summary.md` from top-ranked item in stage 02.
  - Include winner, feasibility, and next steps.
  - Mark output with `RECOVERY_DRAFT: true`.
- Never write empty artifacts.

## Recovery metadata + diagnostics
Recovery appends to `pipeline-results/latest/00-run-metadata.txt`:
- `recovery_mode: true`
- `recovery_reason_codes: <comma-separated validation codes>`

Recovery also appends diagnostics to:
- `pipeline-results/latest/pipeline-debug.log`
- with prefix `AUTO_RECOVERY`

## Revalidation and publish
After recovery:
1. Re-run `scripts/validate_pipeline_outputs.py`.
2. Run `scripts/generate_dashboard_state.py`.
3. Publish artifacts.

## Dashboard signaling
When recovery is used:
- `status = amber`
- `quality.freshness = fallback`
- `quality.errorCodes` includes recovery reason codes (merged with validation error codes)

This ensures consumers can distinguish a valid direct run from a recovered run.
