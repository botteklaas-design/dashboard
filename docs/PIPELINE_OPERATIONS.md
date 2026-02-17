# Pipeline Operations (v2.0)

## Standard runbook
1. `python3 scripts/pipeline_state_machine.py`
2. `python3 scripts/generate_manifests.py`
3. `python3 scripts/weekly_decision_engine.py`
4. `python3 scripts/generate_dashboard_state.py` (backward compatibility)

## Resume / recovery runbook
If run is interrupted or failed:
1. Inspect `pipeline-results/latest/state-machine.json` and `run-events.jsonl`.
2. Resume with `python3 scripts/pipeline_state_machine.py --resume`.
3. Re-run manifests + weekly decision steps.

## Health and diagnostics
- Terminal state: `COMPLETE` or `FAILED` in `state-machine.json`.
- Recovery usage: `recovery_used` in state file and run history.
- Blockers: error code frequencies in `manifests/ops-manifest.json` (`blockerHeatmap`).

## Common checks
- Validate files exist and are non-empty:
  - `01-forum-scout.md`
  - `02-business-analysis.md`
  - `03-final-winner-summary.md`
- Confirm UI data source is manifests only:
  - `index.html` should fetch from `manifests/*.json`.

## Cron integration (4-hour job)
Cron job `4206fae5-7c38-488b-a0f7-37b6f50a57cd` must execute, in order:
1. `pipeline_state_machine.py`
2. `generate_manifests.py`
3. `weekly_decision_engine.py`
4. `generate_dashboard_state.py`
