import fcntl
import json
import sys
from pathlib import Path
from PIL import Image

project = Path(__file__).resolve().parents[3]
task = json.loads(Path(sys.argv[1]).read_text())
folder = project / task['folder']
folder.mkdir(parents=True, exist_ok=True)
lockPath = project / 'agents/sam/scratch/toy/save.lock'
lockPath.parent.mkdir(parents=True, exist_ok=True)
lockFile = lockPath.open('w')
fcntl.flock(lockFile, fcntl.LOCK_EX)
target = folder / task['file']
if target.exists() and not task.get('replace', False):
    raise SystemExit('the target exists: ' + str(target.relative_to(project)))
source = Path(task['source'])
if not source.is_absolute():
    source = project / source
with Image.open(source) as image:
    image = image.convert('RGBA')
    alpha = image.getchannel('A')
    if alpha.getextrema()[0] == 255:
        raise SystemExit('the image has no transparent pixels')
    if task['size'] == 512:
        image = image.crop(alpha.getbbox())
        scale = 512 * .8 / max(image.size)
        image = image.resize(tuple(round(value * scale) for value in image.size), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (512, 512))
        canvas.paste(image, ((512 - image.width) // 2, (512 - image.height) // 2))
        canvas.save(target)
    else:
        image.resize((task['size'], task['size']), Image.Resampling.LANCZOS).save(target)
path = folder / 'prompts.json'
prompts = json.loads(path.read_text()) if path.exists() else {}
prompts[task['file']] = {
    'prompt': task['prompt'],
    'references': task['references'],
    'tool': 'built-in imagegen',
    'size': task['size'],
    'alphaFit': .8 if task['size'] == 512 else None
}
if 'derivedFrom' in task:
    prompts[task['file']]['derivedFrom'] = task['derivedFrom']
path.write_text(json.dumps(prompts, indent=4) + '\n')
print(target.relative_to(project))
