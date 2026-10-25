"""place each model preview beside its concept at 512 pixels."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

root = Path(__file__).resolve().parents[3]
out = root / 'agents/sam/scratch/toy-detail'
out.mkdir(parents=True, exist_ok=True)


def frame(path, crop=None):
    image = Image.open(path).convert('RGBA')
    if crop:
        image = image.crop(crop)
    if image.getextrema()[3][0] == 0:
        image = image.crop(image.getbbox())
    image = ImageOps.contain(image, (512, 512))
    tile = Image.new('RGBA', (512, 512), '#143a2c')
    tile.alpha_composite(image, ((512 - image.width) // 2, (512 - image.height) // 2))
    return tile.convert('RGB')


for name in ('cargo', 'military', 'industrial', 'research', 'station',
        'tanker', 'liner', 'tug', 'police-cutter', 'raider', 'courier'):
    subject = 'station' if name == 'station' else 'ship-' + name
    preview = root / f'assets/blender/renders/toy/{subject}-preview.png'
    concept = root / ('assets/concepts/toy/station/station-world-meadow.webp'
        if name == 'station' else f'assets/concepts/toy/ships/{name}-flight.webp')
    kinds = ('cargo', 'military', 'industrial', 'research')
    sheet = Image.new('RGB', (1536 if name in kinds else 1024, 548), '#143a2c')
    sheet.paste(frame(preview), (0, 36))
    sheet.paste(frame(concept), (512, 36))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 12), name + ' model', fill='#f1eee4')
    draw.text((524, 12), name + ' concept', fill='#f1eee4')
    if name in kinds:
        left = kinds.index(name) * 512
        lineup = root / 'assets/concepts/toy/ships/ship-lineup-meadow.webp'
        sheet.paste(frame(lineup, (left, 245, left + 512, 850)), (1024, 36))
        draw.text((1036, 12), name + ' meadow concept', fill='#f1eee4')
    sheet.save(out / (subject + '.png'))
