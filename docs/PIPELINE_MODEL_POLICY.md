# Pipeline Model Policy (v1.2)

This file explains how to use `config/pipeline-model-policy.json` safely.

## Goals
- Keep **Stage 1 scout** cheap and resilient via local Ollama models.
- Keep **Stage 2 analyst** and **Stage 3 dev** stable using the current main model.
- Make model routing explicit so cron and manual runs stay aligned.

## Stage defaults
- **scout**
  - preferred: `ollama/qwen2.5:7b`
  - fallback: `ollama/llama3.2:latest`
- **analyst**
  - default: `openai-codex/gpt-5.3-codex` (current main model)
- **dev**
  - default: `openai-codex/gpt-5.3-codex` (current main model)

## Budget controls
- `localFirst: true` means always try local inference before expensive calls where possible.
- `maxExpensiveCallsPerDay` is intentionally a placeholder (`TODO_SET_LIMIT`) and should be set after observing real daily usage.

## How to apply in prompts/automation
1. Read `config/pipeline-model-policy.json` first.
2. For scout stage, explicitly mention preferred + fallback model in the run prompt.
3. For analyst/dev stages, only override model when there is a concrete quality incident.
4. If fallback was used, report it in `04-log-scan.txt` as recovery/fallback signal.

## Change management
- Update policy and this doc together.
- Bump `version` only when behavior changes, not for text edits.
- Validate downstream outputs with `scripts/validate_pipeline_outputs.py` after policy changes.
