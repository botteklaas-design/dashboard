#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
HISTORY = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/history')
STRATEGY = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/strategy')


def read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''


def load(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(read(p))
    except Exception:
        return default


def latest_strategy_text() -> str:
    if not STRATEGY.exists():
        return ''
    files = sorted(STRATEGY.glob('*.md'))
    return read(files[-1]) if files else ''


def extract_winner() -> str:
    rm = load(BASE / 'manifests/run-manifest.json', {})
    if rm.get('winner'):
        return rm['winner']
    txt = read(BASE / '03-final-winner-summary.md')
    m = re.search(r'\*\*([^\n*]+)\*\*', txt)
    return m.group(1).strip() if m else 'Onbekende winnaar'


def extract_score() -> float:
    txt = read(BASE / '02-business-analysis.md') + '\n' + read(BASE / '03-final-winner-summary.md')
    m = re.search(r'(\d+)\/(35|30|10)', txt)
    if not m:
        return 0.55
    num, den = int(m.group(1)), int(m.group(2))
    return max(0.3, min(0.95, num / den))


def build_decision():
    trend = load(BASE / 'manifests/trend-manifest.json', {'points': []}).get('points', [])
    ops = load(BASE / 'manifests/ops-manifest.json', {})
    winner = extract_winner()
    score_signal = extract_score()
    strat = latest_strategy_text().lower()

    repeat = 0
    if winner and trend:
        repeat = sum(1 for p in trend[-10:] if winner.lower()[:25] in str(p.get('winner', '')).lower())

    success30 = (ops.get('successRate', {}) or {}).get('last30')
    fallback30 = (ops.get('fallbackRate', {}) or {}).get('last30')

    confidence = score_signal
    if repeat >= 2:
        confidence += 0.1
    if isinstance(success30, (int, float)) and success30 >= 70:
        confidence += 0.05
    if isinstance(fallback30, (int, float)) and fallback30 > 30:
        confidence -= 0.08
    if 'reduce noise' in strat or 'concrete problem' in strat:
        confidence += 0.03
    confidence = round(max(0.35, min(0.92, confidence)), 2)

    bet = {
        'title': winner,
        'confidence': confidence,
        'rationale': [
            f'Latest validated winner remains: {winner}.',
            f'Trend repetition count (last 10): {repeat}.',
            f'Operational reliability context: success30={success30}, fallback30={fallback30}.',
            'Recommendation favors a narrow MVP with single painful workflow and payment trigger.',
        ],
        'killCriteria': [
            'If <10 qualified users complete core flow in 14 days, stop.',
            'If no clear willingness-to-pay signal (>=3 paid pilots/LOIs) in 21 days, stop.',
            'If support burden exceeds target (manual ops >2h/day) by week 3, pivot.',
        ],
    }

    payload = {
        'version': '2.0',
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'singleProductBet': bet,
    }
    return payload


def main() -> int:
    payload = build_decision()
    (BASE / 'weekly-decision.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    bet = payload['singleProductBet']
    md = [
        '# Weekly Product Bet (Latest)',
        f"Generated: {payload['generatedAt']}",
        '',
        f"## Single Product Bet: {bet['title']}",
        f"**Confidence:** {bet['confidence']}",
        '',
        '### Rationale',
    ]
    md += [f'- {r}' for r in bet['rationale']]
    md += ['', '### Kill Criteria']
    md += [f'- {k}' for k in bet['killCriteria']]
    (BASE / 'weekly-product-bet-latest.md').write_text('\n'.join(md).strip() + '\n', encoding='utf-8')

    print('generated weekly decision')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
