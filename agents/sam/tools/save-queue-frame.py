"""save a generated ship frame and its prompt."""

import json
import subprocess
import sys
from pathlib import Path

name, source = sys.argv[1:3]
desk = Path(__file__).resolve().parents[1]
task = {
    'id': 'ship-' + name,
    'folder': 'assets/concepts/toy/ships',
    'file': 'ship-' + name + '-meadow.webp',
    'source': source,
    'size': [2048, 1152],
    'prompt': (desk / 'scratch' / (name + '-prompt.txt')).read_text(),
    'anchor': ['sketches/direction-2026-10-06/starbirds-ship-exhaust.webp']
}
path = desk / 'scratch' / (name + '-task.json')
path.write_text(json.dumps(task, indent=4) + '\n')
subprocess.run([sys.executable, str(desk / 'tools/save-style-asset.py'), str(path)], check=True)
