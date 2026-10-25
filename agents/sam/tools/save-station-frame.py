"""save a generated station frame and its prompt."""

import json
import subprocess
import sys
from pathlib import Path

name, source = sys.argv[1:3]
desk = Path(__file__).resolve().parents[1]
task = {
    'id': 'station-' + name,
    'folder': 'assets/concepts/toy/station',
    'file': 'station-' + name + '-meadow.webp',
    'source': source,
    'size': [2048, 1152],
    'prompt': (desk / 'scratch' / (name + '-prompt.txt')).read_text(),
    'anchor': ['sketches/direction-2026-10-06/starbirds-globe-station.webp']
}
path = desk / 'scratch' / (name + '-task.json')
path.write_text(json.dumps(task, indent=4) + '\n')
subprocess.run([sys.executable, str(desk / 'tools/save-style-asset.py'), str(path)], check=True)
