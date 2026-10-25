"""save a toy crew portrait and its prompt."""

import json
import subprocess
import sys
from pathlib import Path

name, source = sys.argv[1:3]
desk = Path(__file__).resolve().parents[1]
task = {'id': 'crew-' + name, 'folder': 'assets/concepts/toy/crew',
    'file': name + '.webp', 'source': source, 'size': [1024, 1024],
    'prompt': (desk / 'scratch' / ('crew-' + name + '-prompt.txt')).read_text(),
    'anchor': ['sketches/direction-2026-10-06/starbirds-globe-station.webp',
        'sketches/crew/disco/halo-glasses.png']}
path = desk / 'scratch' / ('crew-' + name + '-task.json')
path.write_text(json.dumps(task, indent=4) + '\n')
subprocess.run([sys.executable, str(desk / 'tools/save-style-asset.py'), str(path)], check=True)
