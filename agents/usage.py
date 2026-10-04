# sam's codex limits, read from the newest session log. costs no credits.
import glob, json, os, datetime as dt

log = max(glob.glob(os.path.expanduser('~/.codex/sessions/*/*/*/*.jsonl')), key=os.path.getmtime)
last = {}
for line in open(log):
    if '"rate_limits"' in line:
        e = json.loads(line)
        rl = e.get('payload', {}).get('rate_limits')
        if rl: last[ rl['limit_id'] ] = (rl, e['timestamp'])

for name, (rl, seen) in last.items():
    seen = dt.datetime.fromisoformat(seen.replace('Z', '+00:00')).astimezone().strftime('%a %H:%M')
    for w in filter(None, (rl.get('primary'), rl.get('secondary'))):
        reset = dt.datetime.fromtimestamp(w['resets_at']).strftime('%a %H:%M')
        print(f"{name:22} {w['used_percent']:5.1f}%  of {w['window_minutes'] / 60:3.0f} h  resets {reset}  seen {seen}")
