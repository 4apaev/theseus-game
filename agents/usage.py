# sam's codex limits, read from the newest session log. costs no credits.
import glob, json, os, datetime as dt


# each window: its name, the share used, its length and its reset
def windows():
    log = max(glob.glob(os.path.expanduser('~/.codex/sessions/*/*/*/*.jsonl')), key=os.path.getmtime)
    last = {}
    for line in open(log):
        if '"rate_limits"' in line:
            e = json.loads(line)
            rl = e.get('payload', {}).get('rate_limits')
            if rl: last[ rl['limit_id'] ] = (rl, e['timestamp'])
    return [ { 'name': name, 'used': w['used_percent'], 'minutes': w['window_minutes'], 'resets': w['resets_at'],
               'seen': dt.datetime.fromisoformat(seen.replace('Z', '+00:00')).astimezone() }
             for name, (rl, seen) in last.items() for w in filter(None, (rl.get('primary'), rl.get('secondary'))) ]


if __name__ == '__main__':
    for w in windows():
        reset = dt.datetime.fromtimestamp(w['resets']).strftime('%a %H:%M')
        print(f"{w['name']:22} {w['used']:5.1f}%  of {w['minutes'] / 60:3.0f} h  resets {reset}  seen {w['seen']:%a %H:%M}")
