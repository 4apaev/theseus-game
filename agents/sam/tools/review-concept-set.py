import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[3]
name = sys.argv[1]
folder = root / 'assets/concepts/toy' / name
scratch = root / 'agents/sam/scratch/new-concepts'
records = json.loads((folder / 'prompts.json').read_text())
items = [item for record in records.values() for item in record['outputs']]
cols = 4
sheet = Image.new('RGB', (cols * 256, ((len(items) + cols - 1) // cols) * 280), '#10271f')
draw = ImageDraw.Draw(sheet)
checks = []
for i, item in enumerate(items):
    path = root / item['file']
    im = Image.open(path)
    assert im.size == (1024, 1024), path
    x, y = i % cols * 256, i // cols * 280
    sheet.paste(im.resize((256, 256), Image.Resampling.LANCZOS), (x, y))
    draw.text((x + 8, y + 260), path.stem, fill='white')
    checks.append({'file': item['file'], 'size': list(im.size), 'nativeSize': item['nativeSize']})
sheet.save(scratch / (name + '-review.png'))
reference = Image.open(root / 'sketches/direction-2026-10-06/starbirds-globe-station.webp').convert('RGB')
for key, record in records.items():
    comparison = Image.new('RGB', (1024, 512), '#10271f')
    im = Image.open(root / record['outputs'][0]['file']).convert('RGB')
    comparison.paste(im.resize((512, 512), Image.Resampling.LANCZOS), (0, 0))
    comparison.paste(ImageOps.contain(reference, (512, 512)), (512, 0))
    comparison.save(scratch / (key + '-reference.png'))
(scratch / (name + '-validation.json')).write_text(json.dumps(checks, indent=4) + '\n')
print(str((scratch / (name + '-review.png')).relative_to(root)))
