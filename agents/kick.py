# cron: start sam on his queue, then run the blender scripts he lists.
# no open job, or sam still running: exit.
# sam writes only in sam/ and assets/. this runner, blender.sb and the
# rules stay here, out of his reach: they run outside his sandbox.
import json, os, re, subprocess, sys, time
from datetime import date, datetime
from pathlib import Path
from usage import windows

here  = Path(__file__).resolve().parent
desk  = here / 'sam'
root  = here.parent
BUILD = re.compile(r'assets/blender/scripts/build-[a-z0-9-]+\.py')
env   = { **os.environ, 'PATH': '/opt/homebrew/bin:/usr/bin:/bin' }
lock  = here / 'lock'
todo  = desk / 'builds.txt'

(here / 'log').mkdir(exist_ok=True)
out = open(here / 'log' / f'{ date.today() }.log', 'a')


# one line per run in log/runs.jsonl, for the morning brief
def states():
    return dict(re.findall(r'^\| *([a-z]+\d+) *\| *(\S+)', (desk / 'queue.md').read_text(), re.M))


def journal(start, before, built):
    after = states()
    turned = lambda mark: [ j for j, s in after.items() if s.startswith(mark) and not before.get(j, '').startswith(mark) ]
    with open(here / 'log' / 'runs.jsonl', 'a') as f:
        f.write(json.dumps({ 'start': start, 'end': datetime.now().isoformat(timespec='minutes'), 'done': turned('✅'), 'failed': turned('⛔'), 'built': built }) + '\n')


def run(*cmd):
    return subprocess.run(cmd, cwd=desk, env=env, stdout=out, stderr=out).returncode


# sam's model and effort: one rung of a ladder. a window that burns faster
# than its clock moves the next run one rung down, a slow burn one rung up.
LADDER = [ ('gpt-6-astra', 'medium'), ('gpt-6-astra', 'low'), ('gpt-6.1-sol', 'low') ]
rung   = here / 'log' / 'rung'


# the share used against the share of the window gone. early in a window
# the gone share counts as 0.2 at least, so one big run does not read as a fire.
def pace():
    now = time.time()
    gone = lambda w: 1 - (w['resets'] - now) / (w['minutes'] * 60)
    return max((w['used'] / 100 / max(gone(w), .2) for w in windows() if gone(w) < 1), default=0)


def climb():
    i, p = int(rung.read_text()) if rung.exists() else 0, pace()
    i = min(len(LADDER) - 1, i + 1) if p > 1 else max(0, i - 1) if p < .6 else i
    rung.write_text(str(i))
    print(f'{ datetime.now():%H:%M} pace { p:.2f}, rung { i }: { LADDER[ i ] }', file=out, flush=True)
    return LADDER[ i ]


def sam(model, effort):
    run('codex', 'exec', '-m', model, '-c', f'model_reasoning_effort="{ effort }"',
        '-C', desk, '--add-dir', root / 'assets', '-s', 'workspace-write', '--color', 'never', 'work the queue')


# each script runs in blender here, outside codex: metal needs it.
# blender.sb lets it write only in assets/, with no network.
# without --python-exit-code a script error still exits 0.
def build():
    scripts = todo.read_text().split() if todo.exists() else []
    for s in scripts:
        note = ('refused: not a build script' if not BUILD.fullmatch(s)
            else 'missing' if not (root / s).exists()
            else f"exit { run('sandbox-exec', '-f', here / 'blender.sb', '-D', f'ROOT={ root }', '-D', f'HOME={ env['HOME'] }', 'blender', '-b', '--factory-startup', '--python-exit-code', '1', '-P', root / s) }")
        with open(desk / 'builds.log', 'a') as f:
            f.write(f"{ datetime.now():%H:%M:%S} { s } · { note }\n")
        built.append(f"{ Path(s).stem.removeprefix('build-') } · { note }")
    todo.write_text('')
    return bool(scripts)


# one sam at a time. a lock older than 6 hours is a dead run.
if not re.search(r'^\| *[a-z]+\d+ *\| *(❎|♻️)', (desk / 'queue.md').read_text(), re.M):
    sys.exit()
if lock.exists() and time.time() - lock.stat().st_mtime > 6 * 3600:
    lock.rmdir()
try:
    lock.mkdir()
except FileExistsError:
    sys.exit()
start, before, built = datetime.now().isoformat(timespec='minutes'), states(), []
try:
    build()
    rig = climb()
    sam(*rig)
    if build():
        sam(*rig)
finally:
    journal(start, before, built)
    lock.rmdir()
