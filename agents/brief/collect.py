# the facts for the morning brief: what happened since the last one.
# writes brief/<date>.facts.json; the brief's words come from claude, the page from render.py.
import json, re, subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

here   = Path(__file__).resolve().parent
agents = here.parent
root   = agents.parent
REPOS  = { 'theseus': root, 'backend': root / 'backend', 'frontend': root / 'frontend' }
now    = datetime.now().replace(second=0, microsecond=0)


def git(repo, *args):
    return subprocess.run([ 'git', '-C', repo, *args ], capture_output=True, text=True).stdout.strip()


# the end of the last brief before today, or 24 hours ago
def since():
    last = [ p for p in sorted(here.glob('*.facts.json')) if not p.name.startswith(str(date.today())) ]
    return datetime.fromisoformat(json.loads(last[ -1 ].read_text())[ 'until' ]) if last else now - timedelta(hours=24)


def runs(t0):
    log = agents / 'log' / 'runs.jsonl'
    rows = [ json.loads(l) for l in log.read_text().splitlines() if l ] if log.exists() else []
    return [ r for r in rows if datetime.fromisoformat(r[ 'end' ]) > t0 ]


def commits(t0):
    out = []
    for name, repo in REPOS.items():
        for line in git(repo, 'log', f'--since={ t0.isoformat() }', '--format=%cI%x09%h%x09%s').splitlines():
            at, h, text = line.split('\t', 2)
            out.append({ 'repo': name, 'at': at[ :16 ], 'hash': h, 'text': text })
    return sorted(out, key=lambda c: c[ 'at' ])


def repos():
    return { name: {
        'branch'     : git(repo, 'branch', '--show-current'),
        'uncommitted': len(git(repo, 'status', '--porcelain').splitlines()),
        'unpushed'   : git(repo, 'rev-list', '--count', '@{u}..HEAD') or '?',
    } for name, repo in REPOS.items() }


def queue():
    jobs = re.findall(r'^\| *([a-z]+\d+) *\| *(\S+)[^|]*\| *([^|]+)', (agents / 'sam' / 'queue.md').read_text(), re.M)
    return { mark: [ j for j, s, _ in jobs if s.startswith(mark) ] for mark in ('❎', '♻️', '⛔') } | { 'total': len(jobs) }


# lanes and their open questions, from the board
def board():
    text = (agents / 'board.md').read_text()
    lanes = re.findall(r'^## (\S+) (\w+) · (\S+)', text, re.M)
    asks = [ a for a in re.findall(r'^- asks: (.+)$', text, re.M) if a.strip() != '-' ]
    return { 'lanes': [ { 'mark': m, 'lane': l, 'who': w } for m, l, w in lanes ], 'asks': asks }


def usage():
    out = subprocess.run([ 'python3', agents / 'usage.py' ], capture_output=True, text=True).stdout
    return [ l.split() for l in out.splitlines() if l ]


t0 = since()
facts = {
    'since'  : t0.isoformat(timespec='minutes'),
    'until'  : now.isoformat(timespec='minutes'),
    'runs'   : runs(t0),
    'commits': commits(t0),
    'repos'  : repos(),
    'queue'  : queue(),
    'board'  : board(),
    'usage'  : usage(),
}
(here / f'{ date.today() }.facts.json').write_text(json.dumps(facts, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(facts, indent=2, ensure_ascii=False))
