import re
import sys
from datetime import datetime
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'queue.md'
state = sys.argv[2]
if state == '♻️':
    state += ' ' + datetime.now().astimezone().strftime('%H:%M')
p.write_text(re.sub(r'(?m)^(\| ' + sys.argv[1] + r'\s*\|)[^|]*', lambda m: m[1] + ' ' + state + ' |'.removesuffix('|'), p.read_text()))
