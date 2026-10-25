import json
import shutil
import sys
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[3] / 'assets'
task = json.loads(Path(sys.argv[1]).read_text())
folder = root / task['folder']
folder.mkdir(parents=True, exist_ok=True)
source = folder / 'sources' / (task['name'] + '.png')
source.parent.mkdir(exist_ok=True)
shutil.copy2(task['source'], source)
image = Image.open(source).convert('RGBA')
size = task.get('size', [2048, 1152])
image = image.resize(size, Image.Resampling.LANCZOS)
target = folder / (task['name'] + '.webp')
image.save(target, 'WEBP', quality=94, method=6)
promptsFile = folder / 'prompts.json'
prompts = json.loads(promptsFile.read_text()) if promptsFile.exists() else {}
prompts[task['name']] = {'prompt': task['prompt'], 'tool': 'built-in imagegen', 'source': str(source.relative_to(root)), 'file': target.name, 'w': size[0], 'h': size[1]}
promptsFile.write_text(json.dumps(prompts, indent=4) + '\n')
print(str(target))
