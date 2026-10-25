import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[3]
name = sys.argv[1]
folder = root / 'assets/concepts/toy' / name
scratch = root / 'agents/sam/scratch' / name
scratch.mkdir(parents=True, exist_ok=True)
records = json.loads((folder / 'prompts.json').read_text())
paths = [root / record['file'] for record in records.values()]
anchors = [root / 'assets/icons/toy/modules/reactor-mk1.png', root / 'assets/concepts/toy/sprites/station-market.png'] if name == 'sky-reset' else [root / 'assets/concepts/toy/crew-creatures/little-robots-sheet.webp'] if name == 'crew-robots' else [root / 'sketches/direction-2026-10-06/starbirds-ship-exhaust.webp']
items = paths + anchors
cols = 4
sheet = Image.new('RGB', (cols * 256, ((len(items) + cols - 1) // cols) * 280), '#101b2d')
draw = ImageDraw.Draw(sheet)
checks = []
for i, path in enumerate(items):
    im = Image.open(path).convert('RGB')
    x, y = i % cols * 256, i // cols * 280
    thumb = ImageOps.contain(im, (256, 256))
    sheet.paste(thumb, (x, y + (256 - thumb.height) // 2))
    draw.text((x + 6, y + 260), path.stem, fill='white')
    if path not in paths:
        continue
    expected = (2048, 1152) if name == 'ships-redo' else (1024, 1024)
    assert im.size == expected, path
    checks.append({'file': str(path.relative_to(root)), 'size': list(im.size)})
    comparison = Image.new('RGB', ((1 + len(anchors)) * 512, 512), '#101b2d')
    for j, source in enumerate([path] + anchors):
        small = ImageOps.contain(Image.open(source).convert('RGB'), (512, 512))
        comparison.paste(small, (j * 512, (512 - small.height) // 2))
    comparison.save(scratch / (path.stem + '-comparison.png'))
sheet.save(scratch / 'review.png')
(scratch / 'validation.json').write_text(json.dumps(checks, indent=4) + '\n')
print(str((scratch / 'review.png').relative_to(root)))
