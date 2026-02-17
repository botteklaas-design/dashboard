#!/usr/bin/env python3
"""Pipeline v2.0 state machine orchestrator with resume + event logging."""
import argparse
import json
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
STATE_PATH = BASE / 'state-machine.json'
EVENTS_PATH = BASE / 'run-events.jsonl'
RUN_HISTORY_PATH = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/history/run-history.jsonl')

STAGES = ['INIT', 'SCOUT', 'ANALYST', 'DEV', 'VALIDATE', 'RECOVER', 'REVALIDATE', 'PUBLISH']
TERMINAL = {'COMPLETE', 'FAILED'}


@dataclass
class StageResult:
    ok: bool
    fatal: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict] = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8', errors='ignore'))
    except Exception:
        return default


def append_event(event: Dict) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')


def save_state(state: Dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def run_cmd(command: List[str], stage: str) -> StageResult:
    try:
        proc = subprocess.run(command, capture_output=True, text=True)
        out = (proc.stdout or '').strip()
        err = (proc.stderr or '').strip()
        details = {'command': command, 'returncode': proc.returncode, 'stdout': out[-2000:], 'stderr': err[-2000:]}
        if proc.returncode != 0:
            return StageResult(ok=False, fatal=False, error_code=f'{stage}_CMD_FAILED', details=details)
        return StageResult(ok=True, details=details)
    except Exception as e:
        return StageResult(ok=False, fatal=True, error_code=f'{stage}_EXCEPTION', details={'error': str(e), 'command': command})


def check_file_nonempty(path: Path, code: str) -> StageResult:
    if not path.exists():
        return StageResult(ok=False, fatal=True, error_code=f'{code}_MISSING')
    if not path.read_text(encoding='utf-8', errors='ignore').strip():
        return StageResult(ok=False, fatal=True, error_code=f'{code}_EMPTY')
    return StageResult(ok=True)


def stage_action(stage: str) -> StageResult:
    if stage == 'INIT':
        return StageResult(ok=True)
    if stage == 'SCOUT':
        return check_file_nonempty(BASE / '01-forum-scout.md', 'SCOUT_ARTIFACT')
    if stage == 'ANALYST':
        return check_file_nonempty(BASE / '02-business-analysis.md', 'ANALYST_ARTIFACT')
    if stage == 'DEV':
        return check_file_nonempty(BASE / '03-final-winner-summary.md', 'DEV_ARTIFACT')
    if stage == 'VALIDATE':
        return run_cmd(['python3', '/Users/mcbot/.openclaw/workspace/scripts/validate_pipeline_outputs.py'], stage)
    if stage == 'RECOVER':
        return run_cmd(['python3', '/Users/mcbot/.openclaw/workspace/scripts/pipeline_auto_recovery.py'], stage)
    if stage == 'REVALIDATE':
        return run_cmd(['python3', '/Users/mcbot/.openclaw/workspace/scripts/validate_pipeline_outputs.py'], stage)
    if stage == 'PUBLISH':
        # Publish prep signal only; actual dashboard generation remains explicit in cron flow.
        return StageResult(ok=True, details={'note': 'publish-prep stage complete'})
    return StageResult(ok=False, fatal=True, error_code='UNKNOWN_STAGE')


def next_stage(stage: str, result: StageResult) -> str:
    if result.fatal:
        return 'FAILED'
    if stage == 'VALIDATE':
        return 'PUBLISH' if result.ok else 'RECOVER'
    if stage == 'RECOVER':
        return 'REVALIDATE' if result.ok else 'FAILED'
    if stage == 'REVALIDATE':
        return 'PUBLISH' if result.ok else 'FAILED'
    if stage == 'PUBLISH':
        return 'COMPLETE' if result.ok else 'FAILED'
    idx = STAGES.index(stage)
    return STAGES[idx + 1]


def find_resume_stage(state: Dict) -> str:
    cur = state.get('current_stage')
    if cur in STAGES:
        return cur
    for s in STAGES:
        info = state.get('stages', {}).get(s, {})
        if info.get('status') not in ('success',):
            return s
    return 'INIT'


def write_run_history(state: Dict) -> None:
    terminal = state.get('status')
    if terminal not in TERMINAL:
        return
    started = state.get('started_at')
    ended = state.get('ended_at') or now_iso()
    runtime_sec = None
    try:
        runtime_sec = int((datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()) if started else None
    except Exception:
        runtime_sec = None

    rec = {
        'run_id': state.get('run_id'),
        'started_at': started,
        'ended_at': ended,
        'status': terminal,
        'runtime_sec': runtime_sec,
        'fallback_used': bool(state.get('recovery_used', False)),
        'error_codes': state.get('error_codes', []),
        'winner': state.get('winner'),
    }
    RUN_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RUN_HISTORY_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def parse_winner() -> Optional[str]:
    p = BASE / '03-final-winner-summary.md'
    if not p.exists():
        return None
    txt = p.read_text(encoding='utf-8', errors='ignore')
    for line in txt.splitlines():
        if line.strip().startswith('**'):
            return line.strip('* ').strip()
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true', help='Resume from last non-terminal stage')
    args = parser.parse_args()

    prior = load_json(STATE_PATH, {})
    if args.resume and prior:
        run_id = prior.get('run_id') or str(uuid.uuid4())
        state = prior
        state['resumed_at'] = now_iso()
        start = find_resume_stage(state)
        state['current_stage'] = start
    else:
        run_id = str(uuid.uuid4())
        state = {
            'version': '2.0',
            'run_id': run_id,
            'status': 'RUNNING',
            'current_stage': 'INIT',
            'started_at': now_iso(),
            'ended_at': None,
            'stages': {},
            'error_codes': [],
            'recovery_used': False,
        }
        start = 'INIT'

    save_state(state)

    stage = start
    while stage in STAGES:
        started = now_iso()
        append_event({'ts': started, 'run_id': run_id, 'type': 'stage_start', 'stage': stage})
        result = stage_action(stage)
        ended = now_iso()

        state['stages'].setdefault(stage, {})
        state['stages'][stage].update({
            'status': 'success' if result.ok else 'failed',
            'started_at': started,
            'ended_at': ended,
            'error_code': result.error_code,
            'details': result.details or {},
        })
        state['current_stage'] = stage
        if stage == 'RECOVER' and result.ok:
            state['recovery_used'] = True
        if result.error_code:
            if result.error_code not in state['error_codes']:
                state['error_codes'].append(result.error_code)

        append_event({
            'ts': ended,
            'run_id': run_id,
            'type': 'stage_end',
            'stage': stage,
            'ok': result.ok,
            'fatal': result.fatal,
            'error_code': result.error_code,
        })
        save_state(state)

        nxt = next_stage(stage, result)
        if nxt in TERMINAL:
            state['status'] = nxt
            state['current_stage'] = nxt
            state['ended_at'] = now_iso()
            state['winner'] = parse_winner()
            save_state(state)
            append_event({'ts': state['ended_at'], 'run_id': run_id, 'type': 'run_terminal', 'status': nxt, 'recovery_used': state['recovery_used']})
            write_run_history(state)
            print(json.dumps({'run_id': run_id, 'status': nxt, 'recovery_used': state['recovery_used']}, ensure_ascii=False))
            return 0 if nxt == 'COMPLETE' else 1
        stage = nxt

    state['status'] = 'FAILED'
    state['ended_at'] = now_iso()
    save_state(state)
    append_event({'ts': now_iso(), 'run_id': run_id, 'type': 'run_terminal', 'status': 'FAILED', 'error_code': 'INVALID_TRANSITION'})
    write_run_history(state)
    print(json.dumps({'run_id': run_id, 'status': 'FAILED', 'error': 'invalid-transition'}, ensure_ascii=False))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
