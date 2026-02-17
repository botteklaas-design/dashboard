#!/usr/bin/env python3
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

BASE = Path('/Users/mcbot/.openclaw/workspace/pipeline-results/latest')
REPORT_PATH = BASE / 'validation-report.json'

SCOUT_FILE = BASE / '01-forum-scout.md'
ANALYST_FILE = BASE / '02-business-analysis.md'
DEV_FILE = BASE / '03-final-winner-summary.md'


@dataclass
class ValidationIssue:
    code: str
    severity: str
    stage: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''


def validate_scout(issues: List[ValidationIssue], stages: Dict[str, Dict]) -> None:
    stage = 'scout'
    if not SCOUT_FILE.exists():
        issues.append(ValidationIssue('SCOUT_MISSING_FILE', 'hard', stage, f'Missing file: {SCOUT_FILE.name}'))
        stages[stage] = {'pass': False, 'ideasCount': 0}
        return

    txt = read_text(SCOUT_FILE)
    if not txt.strip():
        issues.append(ValidationIssue('SCOUT_EMPTY', 'hard', stage, f'File is empty: {SCOUT_FILE.name}'))
        stages[stage] = {'pass': False, 'ideasCount': 0}
        return

    blocks = re.findall(r'## Idee\s+\d+:\s+[^\n]+\n([\s\S]*?)(?=\n## Idee\s+\d+:|\n#\s|$)', txt)
    ideas_count = len(blocks)
    if ideas_count < 5:
        issues.append(ValidationIssue('SCOUT_TOO_FEW_IDEAS', 'hard', stage, f'Expected >=5 ideas, found {ideas_count}'))

    required_fields = ['**Beschrijving**', '**Bron**', '**Context**', '**Sentiment**', '**Urgentie**']
    malformed = 0
    for block in blocks:
        if not all(field in block for field in required_fields):
            malformed += 1

    if malformed > 0:
        issues.append(ValidationIssue('SCOUT_SCHEMA_INVALID', 'hard', stage, f'{malformed} idea block(s) missing required fields'))

    stages[stage] = {
        'pass': ideas_count >= 5 and malformed == 0,
        'ideasCount': ideas_count,
        'malformedIdeas': malformed,
    }


def validate_analyst(issues: List[ValidationIssue], stages: Dict[str, Dict]) -> None:
    stage = 'analyst'
    if not ANALYST_FILE.exists():
        issues.append(ValidationIssue('ANALYST_MISSING_FILE', 'hard', stage, f'Missing file: {ANALYST_FILE.name}'))
        stages[stage] = {'pass': False}
        return

    txt = read_text(ANALYST_FILE)
    if not txt.strip():
        issues.append(ValidationIssue('ANALYST_EMPTY', 'hard', stage, f'File is empty: {ANALYST_FILE.name}'))
        stages[stage] = {'pass': False}
        return

    has_scores = bool(re.search(r'\*\*Totaalscore\*\*:\s*\*?\*?\d+\/\d+', txt))
    has_ranking = '# Final Ranking' in txt and bool(re.search(r'\n1\.\s+.+', txt))

    if not has_scores:
        issues.append(ValidationIssue('ANALYST_MISSING_SCORES', 'hard', stage, 'No idea score blocks found'))
    if not has_ranking:
        issues.append(ValidationIssue('ANALYST_MISSING_RANKING', 'hard', stage, 'Final ranking section missing or malformed'))

    stages[stage] = {'pass': has_scores and has_ranking}


def validate_dev(issues: List[ValidationIssue], stages: Dict[str, Dict]) -> None:
    stage = 'dev'
    if not DEV_FILE.exists():
        issues.append(ValidationIssue('DEV_MISSING_FILE', 'hard', stage, f'Missing file: {DEV_FILE.name}'))
        stages[stage] = {'pass': False}
        return

    txt = read_text(DEV_FILE)
    if not txt.strip():
        issues.append(ValidationIssue('DEV_EMPTY', 'hard', stage, f'File is empty: {DEV_FILE.name}'))
        stages[stage] = {'pass': False}
        return

    has_winner = bool(re.search(r'## Combined Winner\s*\n\*\*.+\*\*', txt)) or ('Combined Winner' in txt and '**' in txt)
    has_feasibility = bool(re.search(r'Tech Feasibility\s*\*\*\d+\/\d+\*\*', txt)) or ('Tech Feasibility' in txt)

    if not has_winner:
        issues.append(ValidationIssue('DEV_MISSING_WINNER', 'hard', stage, 'Combined winner not found'))
    if not has_feasibility:
        issues.append(ValidationIssue('DEV_MISSING_FEASIBILITY', 'hard', stage, 'Tech feasibility signal missing'))

    stages[stage] = {'pass': has_winner and has_feasibility}


def main() -> int:
    issues: List[ValidationIssue] = []
    stages: Dict[str, Dict] = {}

    validate_scout(issues, stages)
    validate_analyst(issues, stages)
    validate_dev(issues, stages)

    hard_errors = [i for i in issues if i.severity == 'hard']
    report = {
        'version': '1.2',
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'basePath': str(BASE),
        'pass': len(hard_errors) == 0,
        'summary': {
            'hardErrorCount': len(hard_errors),
            'errorCount': len(issues),
            'errorCodes': sorted(list({i.code for i in issues})),
        },
        'stages': stages,
        'errors': [
            {
                'code': i.code,
                'severity': i.severity,
                'stage': i.stage,
                'message': i.message,
            }
            for i in issues
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    print(json.dumps({'pass': report['pass'], 'errorCodes': report['summary']['errorCodes']}, ensure_ascii=False))
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
