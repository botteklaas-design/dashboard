#!/usr/bin/env python3
"""Fresh-first Scout stage runner with bounded retries and validation gates."""
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/mcbot/.openclaw/workspace')
BASE = WORKSPACE / 'pipeline-results/latest'
TASK_FILE = WORKSPACE / 'agent-tasks/forum-scout-task.md'
OUTPUT_MD = BASE / '01-forum-scout.md'
REPORT_JSON = BASE / 'scout-run-report.json'
DEBUG_LOG = BASE / 'pipeline-debug.log'

MIN_IDEAS = 5
PREFERRED_IDEAS = 8
FETCH_TIMEOUT_SEC = 15
FETCH_MAX_CHARS = 2800
PROMPT_BUDGET = 14000


@dataclass
class AttemptResult:
    step: str
    model: str
    chunked: bool
    ok: bool
    failure_code: Optional[str]
    ideas_count: int
    runtime_sec: int
    output_text: str
    note: str = ''


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] [SCOUT] {msg}'
    print(line, flush=True)
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def extract_urls(text: str) -> List[str]:
    urls = re.findall(r'https?://[^\s)]+', text or '')
    out, seen = [], set()
    for u in urls:
        u = u.rstrip('.,')
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def fetch_url(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 ScoutStage/2.0'})
    with urlopen(req, timeout=FETCH_TIMEOUT_SEC) as resp:
        raw = resp.read(FETCH_MAX_CHARS * 3)
    txt = raw.decode('utf-8', errors='ignore')
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt[:FETCH_MAX_CHARS]


def gather_sources() -> List[Dict[str, str]]:
    content = TASK_FILE.read_text(encoding='utf-8', errors='ignore') if TASK_FILE.exists() else ''
    urls = extract_urls(content)
    items = []
    for i, url in enumerate(urls, start=1):
        try:
            txt = fetch_url(url)
            items.append({'id': str(i), 'url': url, 'snippet': txt})
            log(f'source {i}/{len(urls)} ok {url}')
        except Exception as e:
            items.append({'id': str(i), 'url': url, 'snippet': f'FETCH_FAILED: {e}'})
            log(f'source {i}/{len(urls)} failed {url}: {e}')
    return items


def count_ideas(md: str) -> int:
    return len(re.findall(r'^##\s+Idee\s+\d+\s*:', md or '', re.M))


def failure_code_for(text: str, timed_out: bool) -> str:
    if timed_out:
        return 'SCOUT_TIMEOUT'
    if not (text or '').strip():
        return 'SCOUT_EMPTY'
    return 'SCOUT_TOO_FEW_IDEAS'


def build_prompt(source_block: str) -> str:
    today = datetime.now().strftime('%Y-%m-%d')
    return f"""Je bent Forum Scout voor Nederlandse marktproblemen. Gebruik ALLEEN de signalen hieronder.

Vereist outputformat (exact):
# Forum Scout Results
Datum: {today}
Focus: breed
Aantal ideeën: [X]

---

## Idee 1: [Titel]
**Beschrijving**: [1-2 zinnen]
**Bron**: [platform] - [URL]
**Context**: [waarom probleem urgent is]
**Sentiment**: [Positief/Negatief/Neutraal]
**Urgentie**: [kort]
**Quotes**: "[korte letterlijke quote of parafrase uit signalen]"

---

Minimaal 10 verschillende ideeën. Geen verzinsels, geen placeholders.

Signalen:
{source_block}
"""


def make_source_blocks(sources: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    lines = []
    for s in sources:
        lines.append(f"- URL: {s['url']}\\n  Snippet: {s['snippet'][:900]}")
    short = '\n'.join(lines)[:PROMPT_BUDGET]

    chunks, cur = [], ''
    for line in lines:
        if len(cur) + len(line) + 2 > PROMPT_BUDGET and cur:
            chunks.append(cur)
            cur = line
        else:
            cur = f'{cur}\n{line}' if cur else line
    if cur:
        chunks.append(cur)
    return short, chunks


def run_ollama(model: str, prompt: str, timeout_sec: int) -> Tuple[str, bool, str]:
    cmd = ['ollama', 'run', model]
    started = time.time()
    # Direct path first
    try:
        p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=timeout_sec)
        return (p.stdout or '') + ('\n' + p.stderr if p.stderr else ''), False, 'direct'
    except subprocess.TimeoutExpired as te:
        return (te.stdout or '') if isinstance(te.stdout, str) else '', True, 'direct-timeout'
    except Exception:
        pass

    # PTY-aware fallback path for environments where non-PTY ollama hangs
    script_cmd = f"script -q /dev/null ollama run {shlex.quote(model)}"
    try:
        p = subprocess.run(script_cmd, input=prompt, text=True, capture_output=True, timeout=timeout_sec, shell=True)
        return (p.stdout or '') + ('\n' + p.stderr if p.stderr else ''), False, 'script-pty'
    except subprocess.TimeoutExpired as te:
        return (te.stdout or '') if isinstance(te.stdout, str) else '', True, 'script-pty-timeout'
    except Exception as e:
        return f'EXCEPTION: {e}', False, 'script-pty-exception'
    finally:
        _ = int(time.time() - started)


def run_single_attempt(step: str, model: str, source_text: str, timeout_sec: int, chunked: bool) -> AttemptResult:
    t0 = time.time()
    if not chunked:
        log(f'{step} start model={model} chunked=false timeout={timeout_sec}s')
        out, timed_out, mode = run_ollama(model, build_prompt(source_text), timeout_sec)
        ideas = count_ideas(out)
        ok = ideas >= MIN_IDEAS
        code = None if ok else failure_code_for(out, timed_out)
        log(f'{step} end mode={mode} ideas={ideas} ok={ok}')
        return AttemptResult(step, model, False, ok, code, ideas, int(time.time() - t0), out, note=mode)

    log(f'{step} start model={model} chunked=true timeout={timeout_sec}s')
    parts = [p for p in source_text.split('\n\n@@CHUNK@@\n\n') if p.strip()]
    outputs = []
    timed_out_any = False
    for idx, part in enumerate(parts, start=1):
        log(f'{step} heartbeat chunk {idx}/{len(parts)}')
        out, timed_out, mode = run_ollama(model, build_prompt(part), timeout_sec)
        outputs.append(out)
        timed_out_any = timed_out_any or timed_out
    merged = '\n\n---\n\n'.join(outputs)
    ideas = count_ideas(merged)
    ok = ideas >= MIN_IDEAS
    code = None if ok else failure_code_for(merged, timed_out_any)
    log(f'{step} end ideas={ideas} ok={ok}')
    return AttemptResult(step, model, True, ok, code, ideas, int(time.time() - t0), merged, note='chunked')


def build_final_markdown(text: str, ideas_count: int) -> str:
    return text.strip() + f"\n\n---\n\n# Samenvatting\n- Scout runner ideas count: {ideas_count}\n"


def latest_history_scout() -> Optional[Path]:
    hist = WORKSPACE / 'pipeline-results/history'
    files = sorted(hist.glob('01-forum-scout-*.md'), reverse=True)
    for p in files:
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if count_ideas(txt) >= MIN_IDEAS:
            return p
    return None


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    started = now_iso()
    report: Dict = {
        'startedAt': started,
        'finishedAt': None,
        'status': 'failed',
        'scoutSource': 'fresh',
        'scoutFresh': False,
        'attempts': [],
        'selectedAttempt': None,
        'failureCode': None,
        'ideasCount': 0,
    }

    log('runner started')
    sources = gather_sources()
    short_block, chunks = make_source_blocks(sources)
    chunk_blob = '\n\n@@CHUNK@@\n\n'.join(chunks)

    ladder = [
        ('A_QWEN_SHORT', 'qwen2.5:7b', False, short_block, 220),
        ('B_QWEN_CHUNKED', 'qwen2.5:7b', True, chunk_blob, 180),
        ('C_LLAMA_SHORT', 'llama3.2', False, short_block, 220),
        ('D_LLAMA_CHUNKED', 'llama3.2', True, chunk_blob, 180),
    ]

    best: Optional[AttemptResult] = None
    for step, model, chunked, payload, timeout_sec in ladder:
        res = run_single_attempt(step, model, payload, timeout_sec, chunked)
        report['attempts'].append({
            'step': res.step,
            'model': res.model,
            'chunked': res.chunked,
            'ok': res.ok,
            'failureCode': res.failure_code,
            'ideasCount': res.ideas_count,
            'runtimeSec': res.runtime_sec,
            'note': res.note,
        })
        if best is None or res.ideas_count > best.ideas_count:
            best = res
        if res.ok and res.ideas_count >= PREFERRED_IDEAS:
            best = res
            break

    assert best is not None
    report['ideasCount'] = best.ideas_count
    report['selectedAttempt'] = best.step

    if best.ok:
        OUTPUT_MD.write_text(build_final_markdown(best.output_text, best.ideas_count), encoding='utf-8')
        report['status'] = 'success'
        report['failureCode'] = None
        report['scoutFresh'] = True
        report['scoutSource'] = 'fresh'
        log(f'runner success ideas={best.ideas_count} attempt={best.step}')
        code = 0
    else:
        report['status'] = 'failed'
        report['failureCode'] = best.failure_code or 'SCOUT_EMPTY'
        log(f'runner failed code={report["failureCode"]} bestIdeas={best.ideas_count}')
        code = 2 if report['failureCode'] == 'SCOUT_TIMEOUT' else 3

    report['finishedAt'] = now_iso()
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    if code == 0:
        print(json.dumps({'status': 'ok', 'ideas': best.ideas_count, 'artifact': str(OUTPUT_MD)}, ensure_ascii=False))
    else:
        print(json.dumps({'status': 'failed', 'failureCode': report['failureCode'], 'ideas': best.ideas_count}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
