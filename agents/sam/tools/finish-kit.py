import json
import struct
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[3]
root = project / 'assets/stations'
folder = root / sys.argv[1]
kit = json.loads((folder / 'kit.json').read_text())
layers = []

def layer(file, x, y, width):
    w, h = struct.unpack('>II', file.read_bytes()[16:24])
    layers.append({'file': str(file.relative_to(project)), 'x': float(x), 'y': float(y), 'w': float(width), 'h': float(width * h / w)})

plate = folder / 'sources/plate.png'
if plate.exists():
    layers.append({'file': str(plate.relative_to(project)), 'x': 0.0, 'y': 0.0, 'w': 2048.0, 'h': 1152.0})
platform = root / 'outpost/sources/platform-01.png'
layer(platform, 120, 400, 1200)
if folder.name == 'outpost':
    layer(folder / 'sources/platform-02.png', 820, 600, 1150)
    layer(folder / 'sources/ship-pad.png', 1240, 650, 650)
    layer(folder / 'sources/structure-02.png', 640, 325, 330)
    layer(folder / 'sources/structure-01.png', 260, 385, 430)
    layer(folder / 'sources/cargo-02.png', 860, 705, 200)
    layer(folder / 'sources/cargo-01.png', 700, 775, 150)
else:
    reports = {r['file']: r for r in json.loads((project / 'agents/sam/scratch' / (folder.name + '-validation.json')).read_text())}
    for part, (footX, footY, width) in zip(kit['parts'], [(520, 800, 450), (830, 740, 400), (1050, 800, 330)]):
        bounds = reports[part['file']]['bounds']
        x = footX - width * (bounds[0] + bounds[2]) / (2 * part['w'])
        y = footY - width * part['foot'][1] / part['w']
        layer(folder / 'sources' / (part['name'] + '.png'), x, y, width)
spec = project / 'agents/sam/scratch' / (folder.name + '-preview-layout.json')
spec.parent.mkdir(exist_ok=True)
for item in layers:
    if item['file'] == str(plate.relative_to(project)):
        continue
    item['x'] = item['x'] * .75 + 100
    item['y'] = item['y'] * .75 + 50
    item['w'] *= .75
    item['h'] *= .75
spec.write_text(json.dumps({'w': 2048, 'h': 1152, 'layers': layers}, indent=4) + '\n')
subprocess.run(['swift', '-module-cache-path', str(spec.parent / 'swift-cache'), str(Path(__file__).with_name('compose.swift')), str(spec), str(folder / 'preview.png')], check=True)
(folder / 'readme.md').write_text('the kit contains ' + ', '.join(p['name'] for p in kit['parts']) + '.\nno requested parts are missing.\nthe painted camera and deck anchors need review in the client.\n')
print(str(folder / 'preview.png'))
