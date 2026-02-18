#!/usr/bin/env python3
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
HISTORY = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/history')
MAN = BASE / 'manifests'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''


def load(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(read(path))
    except Exception:
        return default


def parse_ideas(md: str):
    out = []
    re_block = re.compile(r'## Idee\s+(\d+):\s+(.+)\n([\s\S]*?)(?=\n## Idee\s+\d+:|\n# Final Ranking|\Z)')
    def g(pat, body, default='-'):
        m = re.search(pat, body, re.I)
        return m.group(1).strip() if m else default
    for m in re_block.finditer(md or ''):
        body = m.group(3)
        out.append({
            'id': int(m.group(1)),
            'title': m.group(2).strip(),
            'score': g(r'\*\*Totaalscore\*\*:.*?(\d+/\d+)', body),
            'repetition': g(r'Repetition Score\*\*:?.*?([^\n]+)', body),
            'confidence': g(r'\*\*Confidence\*\*:?.*?([^\n]+)', body, 'medium'),
            'bmc': {
                'problem': g(r'\*\*Original Context\*\*: ([^\n]+)', body),
                'icp': g(r'\*\*Target segment\*\*: ([^\n]+)', body),
                'value': f"{m.group(2).strip()} — concrete probleemoplossing",
                'revenue': g(r'\*\*Revenue model\*\*: ([^\n]+)', body),
                'mvp': g(r'\*\*MVP scope\*\*: ([^\n]+)', body),
                'risk': g(r'⚠️\s*\*\*Risk 1\*\*: ([^\n]+)', body),
            }
        })
    return out


def parse_scout_ideas(md: str):
    out = []
    re_block = re.compile(r'## Idee\s+(\d+):\s+(.+)\n([\s\S]*?)(?=\n---\n\n## Idee\s+\d+:|\n# Samenvatting|\Z)')
    def g(pat, body, default='-'):
        m = re.search(pat, body, re.I)
        return m.group(1).strip() if m else default
    for m in re_block.finditer(md or ''):
        body = m.group(3)
        title = m.group(2).strip()
        out.append({
            'id': int(m.group(1)),
            'title': title,
            'score': '-',
            'repetition': '-',
            'confidence': 'scout-only',
            'bmc': {
                'problem': g(r'\*\*Context\*\*: ([^\n]+)', body),
                'icp': 'Consumenten/KB',
                'value': f"{title} — scout-signaal (nog niet volledig geanalyseerd)",
                'revenue': '-',
                'mvp': '-',
                'risk': '-',
            }
        })
    return out


def load_history_runs():
    hist = load(BASE / 'history-manifest.json', {'runs': []}).get('runs', [])
    return hist if isinstance(hist, list) else []


def load_run_history():
    path = HISTORY / 'run-history.jsonl'
    if not path.exists():
        return []
    rows = []
    for line in read(path).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def main() -> int:
    MAN.mkdir(parents=True, exist_ok=True)

    state_machine = load(BASE / 'state-machine.json', {})
    run_state = load(BASE / 'run-state.json', {})
    dash = load(BASE / 'dashboard-data.json', {})
    validation = load(BASE / 'validation-report.json', {})
    weekly = load(BASE / 'weekly-decision.json', {})

    analysis_md = read(BASE / '02-business-analysis.md')
    scout_md = read(BASE / '01-forum-scout.md')
    ideas = parse_ideas(analysis_md)
    analysis_is_recovery = 'RECOVERY_DRAFT: true' in analysis_md
    if analysis_is_recovery or len(ideas) <= 1:
        scout_ideas = parse_scout_ideas(scout_md)
        if len(scout_ideas) > len(ideas):
            ideas = scout_ideas
    trend = load_history_runs()
    run_hist = load_run_history()

    now = datetime.now(timezone.utc).isoformat()

    scout_source = state_machine.get('scout_source') or 'history_fallback'
    scout_fresh = bool(state_machine.get('scout_fresh', False))
    quality = dash.get('quality', {}) or {}
    quality['scoutSource'] = scout_source

    run_manifest = {
        'version': '2.0',
        'generatedAt': now,
        'runId': state_machine.get('run_id'),
        'status': state_machine.get('status') or run_state.get('status') or dash.get('status'),
        'currentStage': state_machine.get('current_stage'),
        'recoveryUsed': bool(state_machine.get('recovery_used', False)),
        'errorCodes': sorted(set((state_machine.get('error_codes') or []) + (validation.get('summary', {}).get('errorCodes', []) or []))),
        'winner': dash.get('winner') or run_state.get('winner'),
        'winnerScore': dash.get('winnerScore') or run_state.get('winnerScore'),
        'ideasCount': dash.get('ideasCount') if dash.get('ideasCount') is not None else len(ideas),
        'recommendedCount': dash.get('recommendedCount'),
        'quality': quality,
        'scoutFresh': scout_fresh,
        'scoutSource': scout_source,
        'weeklyDecision': weekly if weekly else None,
    }

    ideas_manifest = {
        'version': '2.0',
        'generatedAt': now,
        'count': len(ideas),
        'selectedIdeaId': ideas[0]['id'] if ideas else None,
        'ideas': ideas,
    }

    trend_manifest = {
        'version': '2.0',
        'generatedAt': now,
        'points': trend[-30:],
    }

    last7 = run_hist[-7:]
    last30 = run_hist[-30:]
    succ7 = sum(1 for r in last7 if r.get('status') == 'COMPLETE')
    succ30 = sum(1 for r in last30 if r.get('status') == 'COMPLETE')
    fallback30 = sum(1 for r in last30 if r.get('fallback_used'))
    runtime_points = [{'run_id': r.get('run_id'), 'runtime_sec': r.get('runtime_sec')} for r in run_hist[-20:]]

    blockers = Counter()
    for r in run_hist[-30:]:
        for c in (r.get('error_codes') or []):
            blockers[c] += 1

    ops_manifest = {
        'version': '2.0',
        'generatedAt': now,
        'runWindow': {'last7': len(last7), 'last30': len(last30)},
        'successRate': {
            'last7': round((succ7 / len(last7)) * 100, 1) if last7 else None,
            'last30': round((succ30 / len(last30)) * 100, 1) if last30 else None,
        },
        'fallbackRate': {
            'last30': round((fallback30 / len(last30)) * 100, 1) if last30 else None,
        },
        'runtimeTrend': runtime_points,
        'blockerHeatmap': [{'errorCode': k, 'count': v} for k, v in blockers.most_common(12)],
    }

    (MAN / 'run-manifest.json').write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (MAN / 'ideas-manifest.json').write_text(json.dumps(ideas_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (MAN / 'trend-manifest.json').write_text(json.dumps(trend_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (MAN / 'ops-manifest.json').write_text(json.dumps(ops_manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    print('generated manifests')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
