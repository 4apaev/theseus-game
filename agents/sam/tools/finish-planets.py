import json
import re
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[3]
folder = project / 'assets/planets'
job = folder / sys.argv[1]
job.mkdir(exist_ok=True)
names = sys.argv[2:]
layers = []
for index, name in enumerate(names):
    result = subprocess.run(['webpinfo', str(folder / (name + '.webp'))], capture_output=True, text=True, check=True)
    assert re.search(r'Width: 2048\s+Height: 1024', result.stdout)
    assert 'No error detected.' in result.stdout
    layers.append({'file': str((folder / 'sources' / (name + '.png')).relative_to(project)), 'x': 0.0, 'y': float(index * 512), 'w': 1024.0, 'h': 512.0})
spec = project / 'agents/sam/scratch' / (job.name + '-preview-layout.json')
spec.parent.mkdir(exist_ok=True)
spec.write_text(json.dumps({'w': 1024, 'h': 512 * len(names), 'layers': layers}, indent=4) + '\n')
subprocess.run(['swift', '-module-cache-path', str(spec.parent / 'swift-cache'), str(Path(__file__).with_name('compose.swift')), str(spec), str(job / 'preview.png')], check=True)
(job / 'readme.md').write_text('the set contains ' + ', '.join(names) + ' maps at 2048 × 1024.\nno requested maps are missing.\nthe longitude seams and polar distortion need review in the disc shader.\n')
(spec.parent / (job.name + '-validation.json')).write_text(json.dumps({'maps': names, 'w': 2048, 'h': 1024, 'webpDecode': 'passed', 'shaderReview': 'pending'}, indent=4) + '\n')
print(str(len(names)) + ' maps passed size and webp checks')
