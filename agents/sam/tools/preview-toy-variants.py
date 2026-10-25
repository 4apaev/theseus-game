import sys
from pathlib import Path
from PIL import Image, ImageDraw

project = Path(__file__).resolve().parents[3]
group, subject, reference = sys.argv[1:]
folder = project / 'assets/concepts/toy' / group
sheet = Image.new('RGB', (1024, 1024), '#203d32')
draw = ImageDraw.Draw(sheet)
for row, palette in enumerate(('meadow', 'lagoon')):
    for column, path in enumerate((folder / (subject + '-' + palette + '.webp'), project / reference)):
        with Image.open(path) as source:
            source = source.convert('RGB')
            source.thumbnail((512, 512), Image.Resampling.LANCZOS)
            sheet.paste(source, (column * 512 + (512 - source.width) // 2,
                row * 512 + (512 - source.height) // 2))
    draw.text((8, row * 512 + 8), palette, fill='white')
target = project / 'agents/sam/scratch/toy' / (group + '-variants-check.png')
sheet.save(target)
print(target.relative_to(project))
