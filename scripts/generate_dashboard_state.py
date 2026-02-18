#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime, timezone

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
HIST = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/history')


def read(name):
    p = BASE / name
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''


def parse_validation_report():
    p = BASE / 'validation-report.json'
    if not p.exists():
        return {
            'exists': False,
            'pass': None,
            'errorCodes': ['DASHBOARD_PARSE'],
        }
    try:
        payload = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
        codes = payload.get('summary', {}).get('errorCodes', []) or []
        return {
            'exists': True,
            'pass': bool(payload.get('pass', False)),
            'errorCodes': codes,
        }
    except Exception:
        return {
            'exists': True,
            'pass': False,
            'errorCodes': ['DASHBOARD_PARSE'],
        }


def classify_status(validation_pass, logscan_text, recovery_mode=False):
    scan_l = (logscan_text or '').lower()

    if recovery_mode:
        return 'amber'

    severe_terms = ['fatal', 'panic', 'hard fail', 'validation failed hard']
    if validation_pass is False:
        return 'red'
    if any(t in scan_l for t in severe_terms):
        return 'red'

    recovery_terms = ['recovery', 'fallback', 'partial', 'warning', 'pending']
    if any(t in scan_l for t in recovery_terms):
        return 'amber'

    return 'green'


def parse_recovery_metadata(meta):
    mode = bool(re.search(r'^recovery_mode:\s*true\s*$', meta or '', re.M | re.I))
    codes = []
    m = re.search(r'^recovery_reason_codes:\s*([^\n]+)\s*$', meta or '', re.M | re.I)
    if m:
        codes = [c.strip() for c in m.group(1).split(',') if c.strip()]
    return mode, codes


def freshness(meta, run_ts):
    src = f"{meta}\n{run_ts or ''}"
    m = re.search(r'(\d{4}-\d{2}-\d{2}-\d{6})', src)
    if not m:
        return {'label': 'unknown', 'minutes': None}

    try:
        ts = datetime.strptime(m.group(1), '%Y-%m-%d-%H%M%S').replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        mins = int((now - ts).total_seconds() // 60)
    except Exception:
        return {'label': 'unknown', 'minutes': None}

    if mins < 0:
        label = 'fresh'
    elif mins <= 300:
        label = 'fresh'
    elif mins <= 720:
        label = 'stale'
    else:
        label = 'old'

    return {'label': label, 'minutes': mins}


final = read('03-final-winner-summary.md')
biz = read('02-business-analysis.md')
logscan = read('04-log-scan.txt')
meta = read('00-run-metadata.txt')
state_machine = {}
try:
    state_machine = json.loads((BASE / 'state-machine.json').read_text(encoding='utf-8', errors='ignore')) if (BASE / 'state-machine.json').exists() else {}
except Exception:
    state_machine = {}

run_ts = None
for src in (meta, final):
    m = re.search(r'(\d{4}-\d{2}-\d{2}-\d{6})', src)
    if m:
        run_ts = m.group(1)
        break
if not run_ts:
    run_ts = datetime.now().strftime('%Y-%m-%d-%H%M%S')

winner_line = None
m = re.search(r'\n1\.\s*([^\n]+)', final)
if m:
    winner_line = m.group(1).strip()
winner = winner_line.split(' - ')[0] if winner_line else 'Onbekend'
score = None
ms = re.search(r'(\d+\/\d+)', winner_line or '')
if ms:
    score = ms.group(1)

ideas_count = None
m = re.search(r'Aantal ideeën geanalyseerd:\s*(\d+)', biz)
if m:
    ideas_count = int(m.group(1))

recommended = None
m = re.search(r'Aanbevolen voor verdere exploratie:\s*(\d+)', biz)
if m:
    recommended = int(m.group(1))

validation = parse_validation_report()
recovery_mode, recovery_codes = parse_recovery_metadata(meta)
status = classify_status(validation['pass'], logscan, recovery_mode=recovery_mode)
error_codes = sorted(list({*(validation['errorCodes'] or []), *recovery_codes}))
scout_source = state_machine.get('scout_source') or 'history_fallback'
quality = {
    'freshness': 'fallback' if recovery_mode else freshness(meta, run_ts),
    'validationPass': validation['pass'],
    'errorCodes': error_codes,
    'scoutSource': scout_source,
}

# Trend from history summaries
runs = []
for p in sorted(HIST.glob('03-final-winner-summary-*.md'))[-20:]:
    tsm = re.search(r'03-final-winner-summary-(\d{4}-\d{2}-\d{2}-\d{6})\.md$', p.name)
    if not tsm:
        continue
    t = tsm.group(1)
    txt = p.read_text(encoding='utf-8', errors='ignore')
    wm = re.search(r'\n1\.\s*([^\n]+)', txt)
    wl = wm.group(1).strip() if wm else '-'
    wname = wl.split(' - ')[0]
    sm = re.search(r'(\d+\/\d+)', wl)
    runs.append({'timestamp': t, 'winner': wname, 'score': sm.group(1) if sm else None})

payload = {
    'runTimestamp': run_ts,
    'winner': winner,
    'winnerScore': score,
    'ideasCount': ideas_count,
    'recommendedCount': recommended,
    'status': status,
    'quality': quality,
    'scoutFresh': bool(state_machine.get('scout_fresh', False)),
    'scoutSource': scout_source,
    'trend': runs[-8:],
    'generatedAt': datetime.now().isoformat(),
}

(BASE / 'dashboard-data.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
(BASE / 'run-state.json').write_text(json.dumps({
    'runTimestamp': run_ts,
    'status': status,
    'winner': winner,
    'winnerScore': score,
    'quality': quality,
    'scoutFresh': bool(state_machine.get('scout_fresh', False)),
    'scoutSource': scout_source,
    'updatedAt': datetime.now().isoformat(),
}, ensure_ascii=False, indent=2), encoding='utf-8')

print('generated dashboard-data.json and run-state.json')
