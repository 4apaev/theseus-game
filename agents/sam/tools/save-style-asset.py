import json
import shutil
import sys
from pathlib import Path
from PIL import Image

project = Path(__file__).resolve().parents[3]
task = json.loads(Path(sys.argv[1]).read_text())
folder = project / task['folder']
folder.mkdir(parents=True, exist_ok=True)
raw = project / 'agents/sam/scratch/style' / (task['id'] + '.png')
raw.parent.mkdir(parents=True, exist_ok=True)
source = Path(task['source'])
if not source.is_absolute():
    source = project / source
shutil.copy2(source, raw)
target = folder / task['file']
if target.exists():
    raise SystemExit('the target exists: ' + str(target.relative_to(project)))
with Image.open(raw) as image:
    sourceSize = list(image.size)
    image.convert('RGB').resize(task['size'], Image.Resampling.LANCZOS).save(target, 'WEBP', quality=94, method=6)
path = folder / 'prompts.json'
prompts = json.loads(path.read_text()) if path.exists() else {}
record = {
    'id': task['id'],
    'prompt': task['prompt'], 'anchor': task['anchor'],
    'tool': 'built-in imagegen', 'file': str(target.relative_to(project)),
    'source': str(raw.relative_to(project)), 'sourceSize': sourceSize,
    'w': task['size'][0], 'h': task['size'][1]
}
if isinstance(prompts, list):
    prompts.append(record)
else:
    prompts[task['id']] = record
path.write_text(json.dumps(prompts, indent=4) + '\n')
print(str(target.relative_to(project)))
