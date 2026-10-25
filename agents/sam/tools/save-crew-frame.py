"""save a crew-flow concept frame and its prompt."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[3]
folder = project / 'assets/concepts/crew-flow'
name, source, prompt = sys.argv[1:]
target = folder / 'sources' / (name + '.png')
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, target)
subprocess.run(['cwebp', '-quiet', '-q', '94', '-resize', '2048', '1152', str(target),
    '-o', str(folder / (name + '.webp'))], check=True)
path = folder / 'prompts.json'
data = json.loads(path.read_text()) if path.exists() else {}
data[name] = {'prompt': prompt, 'tool': 'built-in imagegen',
    'source': str(target.relative_to(project)),
    'file': str((folder / (name + '.webp')).relative_to(project)), 'w': 2048, 'h': 1152}
path.write_text(json.dumps(data, indent=4) + '\n')
print(data[name]['file'])
