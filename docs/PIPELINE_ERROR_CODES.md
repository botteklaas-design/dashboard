# Pipeline Error Codes (v1.2)

Normalized error codes for pipeline validation, dashboard quality signaling, and recovery workflows.

## Severity guide
- **hard**: pipeline output is invalid/incomplete; dashboard should become `red`.
- **soft**: recoverable degradation, fallback, or partial quality issue; dashboard usually `amber`.

## Code taxonomy

### Scout / Stage 1
- `SCOUT_TIMEOUT` (soft/hard depending on output completeness)
- `SCOUT_EMPTY` (hard)
- `SCOUT_MISSING_FILE` (hard)
- `SCOUT_SCHEMA_INVALID` (hard)
- `SCOUT_TOO_FEW_IDEAS` (hard)

### Analyst / Stage 2
- `ANALYST_TIMEOUT` (soft/hard depending on output completeness)
- `ANALYST_EMPTY` (hard)
- `ANALYST_MISSING_FILE` (hard)
- `ANALYST_SCHEMA_INVALID` (hard)
- `ANALYST_MISSING_SCORES` (hard)
- `ANALYST_MISSING_RANKING` (hard)

### Dev / Stage 3
- `DEV_TIMEOUT` (soft/hard depending on output completeness)
- `DEV_EMPTY` (hard)
- `DEV_MISSING_FILE` (hard)
- `DEV_SCHEMA_INVALID` (hard)
- `DEV_MISSING_WINNER` (hard)
- `DEV_MISSING_FEASIBILITY` (hard)

### Dashboard / Publish
- `DASHBOARD_PARSE` (soft)
- `PUBLISH_FAIL` (soft)

## Validator mapping (current)
`scripts/validate_pipeline_outputs.py` currently emits these codes directly:
- `SCOUT_MISSING_FILE`, `SCOUT_EMPTY`, `SCOUT_TOO_FEW_IDEAS`, `SCOUT_SCHEMA_INVALID`
- `ANALYST_MISSING_FILE`, `ANALYST_EMPTY`, `ANALYST_MISSING_SCORES`, `ANALYST_MISSING_RANKING`
- `DEV_MISSING_FILE`, `DEV_EMPTY`, `DEV_MISSING_WINNER`, `DEV_MISSING_FEASIBILITY`

Timeout/publish/dashboard parse codes can be appended by log-scanning/release steps and should share this taxonomy.
