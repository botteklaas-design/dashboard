#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
VALIDATION = BASE / 'validation-report.json'
SCOUT = BASE / '01-forum-scout.md'
ANALYST = BASE / '02-business-analysis.md'
DEV = BASE / '03-final-winner-summary.md'
META = BASE / '00-run-metadata.txt'
DEBUG_LOG = BASE / 'pipeline-debug.log'


def now_stamp() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log(msg: str) -> None:
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_LOG.open('a', encoding='utf-8') as f:
        f.write(f"[{now_stamp()}] AUTO_RECOVERY {msg}\n")


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''


def parse_validation() -> Dict:
    if not VALIDATION.exists():
        return {'pass': False, 'errorCodes': ['VALIDATION_REPORT_MISSING'], 'stages': {}}
    try:
        p = json.loads(read(VALIDATION))
        return {
            'pass': bool(p.get('pass', False)),
            'errorCodes': p.get('summary', {}).get('errorCodes', []) or [],
            'stages': p.get('stages', {}) or {},
        }
    except Exception:
        return {'pass': False, 'errorCodes': ['VALIDATION_REPORT_PARSE_FAILED'], 'stages': {}}


def parse_scout_ideas() -> List[Dict[str, str]]:
    txt = read(SCOUT)
    ideas = []
    pattern = re.compile(r'## Idee\s+(\d+):\s+([^\n]+)\n([\s\S]*?)(?=\n## Idee\s+\d+:|\Z)')
    for m in pattern.finditer(txt):
        idx, title, body = m.group(1), m.group(2).strip(), m.group(3)
        def field(name: str) -> str:
            fm = re.search(rf'\*\*{re.escape(name)}\*\*:\s*([^\n]+)', body)
            return fm.group(1).strip() if fm else ''
        ideas.append({
            'index': idx,
            'title': title,
            'description': field('Beschrijving'),
            'context': field('Context'),
            'urgency': field('Urgentie'),
            'sentiment': field('Sentiment'),
            'source': field('Bron'),
        })
    return ideas


def score_idea(idea: Dict[str, str]) -> Tuple[int, int, int, int, int]:
    text = f"{idea.get('title','')} {idea.get('description','')} {idea.get('context','')}".lower()
    urgency = (idea.get('urgency') or '').lower()
    sentiment = (idea.get('sentiment') or '').lower()

    value = 5
    viability = 5
    payment = 4
    repetition = 2

    money_terms = ['kosten', 'factuur', 'claim', 'garantie', 'boete', 'schade', 'vergoeding']
    ops_terms = ['vertraging', 'wifi', 'internet', 'beveilig', 'service', 'support']

    if any(t in text for t in money_terms):
        value += 2
        payment += 2
    if any(t in text for t in ops_terms):
        value += 1
        viability += 1
    if 'hoog' in urgency:
        value += 1
        repetition += 1
    if 'negatief' in sentiment:
        payment += 1

    value = max(1, min(10, value))
    viability = max(1, min(10, viability))
    payment = max(1, min(10, payment))
    repetition = max(1, min(5, repetition))
    total = value + viability + payment + repetition
    return value, viability, payment, repetition, total


def synthesize_02_from_01() -> str:
    ideas = parse_scout_ideas()
    if not ideas:
        ideas = [
            {'index': '1', 'title': 'Generieke klantfrictie-oplosser', 'description': 'Fallback idee bij ontbrekende stage-1 data', 'context': 'RECOVERY_DRAFT', 'urgency': 'Middel', 'sentiment': 'Negatief', 'source': 'unknown'}
        ]

    scored = []
    for idea in ideas:
        v, vi, p, r, t = score_idea(idea)
        scored.append((t, idea, v, vi, p, r))
    scored.sort(key=lambda x: (-x[0], int(x[1].get('index', '999') if str(x[1].get('index', '999')).isdigit() else 999)))
    top3 = scored[:3] if len(scored) >= 3 else scored

    lines = [
        '# Business Analysis Report (AUTO RECOVERY)',
        'RECOVERY_DRAFT: true',
        f'Datum: {datetime.now().strftime("%Y-%m-%d")}',
        'Run: AUTO_RECOVERY',
        f'Aantal ideeën geanalyseerd: {len(ideas)}',
        '',
        '## Scoringskader (/35)',
        '- Business Value (0–10)',
        '- Viability (0–10)',
        '- Payment Willingness (0–10)',
        '- Repetition Score (0–5)',
        '',
        '## Top 3 (deterministische fallback)',
    ]
    for rank, (t, idea, v, vi, p, r) in enumerate(top3, start=1):
        lines += [
            f"{rank}. Idee {idea.get('index','?')} — {idea.get('title','Onbekend')} — {t}/35",
            f"   - Business Value: {v}/10",
            f"   - Viability: {vi}/10",
            f"   - Payment Willingness: {p}/10",
            f"   - Repetition Score: {r}/5",
        ]

    lines += ['', '## Idea-by-idea (bounded)']
    for (_t, idea, v, vi, p, r) in scored[:10]:
        total = v + vi + p + r
        lines += [
            '',
            f"## Idee {idea.get('index','?')}: {idea.get('title','Onbekend')}",
            f"**Totaalscore**: **{total}/35**",
            f"- Business Value: {v}/10",
            f"- Viability: {vi}/10",
            f"- Payment Willingness: {p}/10",
            f"- Repetition Score: {r}/5",
        ]

    lines += ['', '## Final Ranking']
    if top3:
        for rank, (t, idea, *_rest) in enumerate(top3, start=1):
            lines.append(f"{rank}. Idee {idea.get('index','?')} — {idea.get('title','Onbekend')} — {t}/35")
    else:
        lines.append('1. Idee 1 — Generieke klantfrictie-oplosser — 15/35')

    return '\n'.join(lines).strip() + '\n'


def extract_top_rank_from_02() -> Tuple[str, str]:
    txt = read(ANALYST)
    m = re.search(r'\n1\.\s*(?:Idee\s*\d+\s*[—-]\s*)?([^\n—-]+?)(?:\s*[—-]\s*(\d+/35))?\s*$', txt, re.M)
    if m:
        return m.group(1).strip(), (m.group(2) or 'n/a')
    return 'Fallback winnaar uit recovery', 'n/a'


def synthesize_03_from_02() -> str:
    winner, score = extract_top_rank_from_02()
    return (
        '# Senior Developer Technical Assessment (AUTO RECOVERY)\n'
        'RECOVERY_DRAFT: true\n'
        f'Datum: {datetime.now().strftime("%Y-%m-%d")}\n'
        'Run: AUTO_RECOVERY\n\n'
        '## Combined Winner\n'
        f'**{winner}**\n\n'
        '## Feasibility\n'
        f'- Business score input: {score}\n'
        '- Tech Feasibility **7/10**\n'
        '- Implementatiecomplexiteit: Middel\n\n'
        '## Next Steps\n'
        '1. Valideer 5 gebruikersinterviews binnen 7 dagen.\n'
        '2. Bouw een smalle MVP met 1 kernworkflow.\n'
        '3. Definieer meetbare succes-KPI (activatie + retentie).\n'
    )


def stage_invalid(stage_name: str, stages: Dict) -> bool:
    return not bool(stages.get(stage_name, {}).get('pass', False))


def append_recovery_metadata(reason_codes: List[str]) -> None:
    META.parent.mkdir(parents=True, exist_ok=True)
    existing = read(META)
    block = (
        '\n# AUTO_RECOVERY\n'
        'recovery_mode: true\n'
        f"recovery_reason_codes: {','.join(sorted(set(reason_codes)))}\n"
        f"recovery_timestamp: {datetime.now().strftime('%Y-%m-%d-%H%M%S')}\n"
    )
    META.write_text((existing.rstrip() + '\n' + block).lstrip('\n'), encoding='utf-8')


def main() -> int:
    validation = parse_validation()
    if validation.get('pass') is True:
        log('validation passed; no-op')
        print(json.dumps({'recovery': False, 'reasonCodes': []}))
        return 0

    reason_codes = list(validation.get('errorCodes') or [])
    changed = []

    if stage_invalid('analyst', validation.get('stages', {})):
        content = synthesize_02_from_01()
        ANALYST.write_text(content if content.strip() else 'RECOVERY_DRAFT\n', encoding='utf-8')
        changed.append(ANALYST.name)

    analyst_text = read(ANALYST)
    if not analyst_text.strip():
        ANALYST.write_text('RECOVERY_DRAFT: true\n\n# Final Ranking\n1. Idee 1 — Fallback — 15/35\n', encoding='utf-8')
        changed.append(ANALYST.name)

    if stage_invalid('dev', validation.get('stages', {})):
        content = synthesize_03_from_02()
        DEV.write_text(content if content.strip() else 'RECOVERY_DRAFT\n', encoding='utf-8')
        changed.append(DEV.name)

    dev_text = read(DEV)
    if not dev_text.strip():
        DEV.write_text('RECOVERY_DRAFT: true\n\n## Combined Winner\n**Fallback winnaar**\n', encoding='utf-8')
        changed.append(DEV.name)

    append_recovery_metadata(reason_codes)
    log(f"triggered reason_codes={','.join(reason_codes) if reason_codes else 'unknown'} changed={','.join(sorted(set(changed)))}")

    print(json.dumps({'recovery': True, 'reasonCodes': reason_codes, 'changed': sorted(set(changed))}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
