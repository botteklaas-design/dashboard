#!/usr/bin/env python3
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
HIST = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/history')

def read(name):
    p = BASE / name
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''

final = read('03-final-winner-summary.md')
biz = read('02-business-analysis.md')
logscan = read('04-log-scan.txt')
meta = read('00-run-metadata.txt')

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

status = 'green'
scan_l = (logscan or '').lower()
if any(k in scan_l for k in ['error', 'failed', 'timeout', 'incomplete', 'fallback']):
    status = 'amber'

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
    'trend': runs[-8:],
    'generatedAt': datetime.now().isoformat()
}

(BASE / 'dashboard-data.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
(BASE / 'run-state.json').write_text(json.dumps({
    'runTimestamp': run_ts,
    'status': status,
    'winner': winner,
    'winnerScore': score,
    'updatedAt': datetime.now().isoformat()
}, ensure_ascii=False, indent=2), encoding='utf-8')

print('generated dashboard-data.json and run-state.json')
