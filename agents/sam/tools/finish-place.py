import json
import sys
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[3] / 'assets'
scratch = Path(__file__).resolve().parents[1] / 'scratch'
scratch.mkdir(exist_ok=True)
folder = root / sys.argv[1]
spec = json.loads(Path(sys.argv[2]).read_text())
kitFile = folder / 'kit.json'
kit = json.loads(kitFile.read_text()) if kitFile.exists() else {'kit': folder.name, 'stations': spec.get('stations', []), 'parts': []}
kit['plate'] = 'plate.webp'
kit['spots'] = spec['spots']
kit['place'] = spec['place']
kit['placements'] = spec.get('placements', [])
kitFile.write_text(json.dumps(kit, indent=4) + '\n')
preview = Image.open(folder / 'plate.webp').convert('RGBA')
for item in kit['placements']:
    part = next(p for p in kit['parts'] if p['name'] == item['name'])
    sprite = Image.open(folder / part['file']).convert('RGBA')
    scale = item['width'] / sprite.width
    sprite = sprite.resize((item['width'], round(sprite.height * scale)), Image.Resampling.LANCZOS)
    x = round(item['x'] - part['foot'][0] * scale)
    y = round(item['y'] - part['foot'][1] * scale)
    preview.alpha_composite(sprite, (x, y))
preview.save(folder / 'preview.png')
(folder / 'readme.md').write_text(spec['readme'] + '\n')
reports = []
for part in kit['parts']:
    image = Image.open(folder / part['file']).convert('RGBA')
    alpha = image.getchannel('A')
    assert max(image.size) == 2048
    assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
    assert all(0 <= v < limit for v, limit in zip(part['foot'], image.size))
    reports.append({'file': part['file'], 'size': list(image.size), 'alpha': list(alpha.getextrema()), 'bounds': alpha.getbbox()})
assert preview.size == (2048, 1152)
assert all(0 <= s['x'] < 2048 and 0 <= s['y'] < 1152 for s in kit['spots'])
(scratch / (folder.name + '-validation.json')).write_text(json.dumps(reports, indent=4) + '\n')
print(str(folder / 'preview.png'))
