import json
import shutil
import sys
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[3]
task = json.loads(Path(sys.argv[1]).read_text())
folder = root / 'assets/concepts/toy' / task['folder']
scratch = root / 'agents/sam/scratch/new-concepts'
folder.mkdir(parents=True, exist_ok=True)
scratch.mkdir(parents=True, exist_ok=True)
raw = scratch / (task['id'] + '-raw.png')
shutil.copy2(task['source'], raw)
im = Image.open(raw).convert('RGB')
records = []
names = task.get('names', [task['id']])
for i, name in enumerate(names):
    tile = im
    if task.get('boxes'):
        tile = im.crop(task['boxes'][i])
    elif len(names) == 4:
        x, y = i % 2, i // 2
        tile = im.crop((x * im.width // 2, y * im.height // 2,
                       (x + 1) * im.width // 2, (y + 1) * im.height // 2))
    target = folder / (name + '.webp')
    if target.exists():
        raise SystemExit('the target exists: ' + str(target))
    tile.resize((1024, 1024), Image.Resampling.LANCZOS).save(target, quality=95)
    records.append({'file': str(target.relative_to(root)), 'nativeSize': list(tile.size), 'size': [1024, 1024]})
if len(names) == 4:
    im.resize((2048, 2048), Image.Resampling.LANCZOS).save(folder / (task['id'] + '-sheet.webp'), quality=95)
p = folder / 'prompts.json'
data = json.loads(p.read_text()) if p.exists() else {}
data[task['id']] = {'prompt': task['prompt'], 'reference': task['reference'],
                    'tool': 'built-in imagegen', 'source': str(raw.relative_to(root)), 'outputs': records}
p.write_text(json.dumps(data, indent=4) + '\n')
print(json.dumps(records))
