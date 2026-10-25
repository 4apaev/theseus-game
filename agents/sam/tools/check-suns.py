import json
from pathlib import Path
from PIL import Image

folder = Path(__file__).resolve().parents[3] / 'assets/suns'
scratch = Path(__file__).resolve().parents[1] / 'scratch'
scratch.mkdir(exist_ok=True)
reports = []
for path in sorted(folder.glob('*.webp')):
    image = Image.open(path).convert('RGBA')
    alpha = image.getchannel('A')
    assert image.size == (1024, 1024)
    assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 250
    edges = [alpha.crop((0, 0, 1024, 1)), alpha.crop((0, 1023, 1024, 1024)), alpha.crop((0, 0, 1, 1024)), alpha.crop((1023, 0, 1024, 1024))]
    assert max(edge.getextrema()[1] for edge in edges) <= 5
    reports.append({'file': path.name, 'size': list(image.size), 'alpha': list(alpha.getextrema()), 'bounds': alpha.getbbox()})
(scratch / (folder.name + '-validation.json')).write_text(json.dumps(reports, indent=4) + '\n')
print(json.dumps(reports))
