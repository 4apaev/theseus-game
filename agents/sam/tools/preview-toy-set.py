import sys
from pathlib import Path
from PIL import Image, ImageDraw

project = Path(__file__).resolve().parents[3]
folder = project / sys.argv[1]
size = int(sys.argv[2]) if len(sys.argv) > 2 else 128
files = sorted(folder.glob('*.png'))
columns = 5
width = max(size + 24, 180)
height = size + 48
sheet = Image.new('RGB', (columns * width, ((len(files) + columns - 1) // columns) * height), '#203d32')
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(files):
    x, y = index % columns * width, index // columns * height
    with Image.open(path) as source:
        sprite = source.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
        sheet.paste(sprite, (x + (width - size) // 2, y + 8), sprite)
    draw.text((x + 8, y + size + 18), path.stem, fill='#fff6e5')
target = project / 'agents/sam/scratch/toy' / (folder.name + '-' + str(size) + '.png')
target.parent.mkdir(parents=True, exist_ok=True)
sheet.save(target)
print(target.relative_to(project))
