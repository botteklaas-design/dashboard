# Scout Reliability Hardening

This document defines the fresh-first reliability contract for Stage 1 (Scout).

## Runner
- Script: `scripts/run_scout_stage.py`
- Output report: `pipeline-results/latest/scout-run-report.json`
- Output artifact: `pipeline-results/latest/01-forum-scout.md` (written **only** on validation pass)

## Retry ladder (deterministic)
1. `qwen2.5:7b` short prompt
2. `qwen2.5:7b` chunked prompts
3. `llama3.2` short prompt
4. `llama3.2` chunked prompts

## Reliability controls
- Strict per-attempt timeout enforcement
- PTY-aware Ollama execution fallback path (`script` wrapper)
- Bounded prompt chunks (source groups split to prompt budget)
- Heartbeat/progress logging into `pipeline-debug.log`
- Sanity gates:
  - Preferred: `>= 8` ideas
  - Minimum pass: `>= 5` ideas

## Failure code semantics
- `SCOUT_TIMEOUT`: all usable output blocked by timeout behavior
- `SCOUT_TOO_FEW_IDEAS`: output exists but under minimum idea count
- `SCOUT_EMPTY`: empty/near-empty generated output

## Stage machine integration
- SCOUT stage runs `run_scout_stage.py` first (fresh-first)
- History fallback may be used **only after** fresh ladder failure
- State/events track source:
  - `scoutFresh: true|false`
  - `scoutSource: fresh|history_fallback`

## Manifest/dashboard signaling
- `manifests/run-manifest.json` includes:
  - `scoutFresh`
  - `scoutSource`
- Dashboard quality section shows: `Scout source: fresh|history_fallback`
