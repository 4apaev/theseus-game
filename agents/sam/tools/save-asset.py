import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3] / 'assets'
task = json.loads(Path(sys.argv[1]).read_text()) if Path(sys.argv[1]).is_file() else json.loads(sys.argv[1])
folder = root / task['folder']
source = folder / 'sources' / (task['name'] + '.png')
source.parent.mkdir(parents=True, exist_ok=True)
if Path(task['source']) != source:
    shutil.copy2(task['source'], source)
width, height = struct.unpack('>II', source.read_bytes()[16:24])
if task['kind'] == 'part':
    scale = 2048 / max(width, height)
    w, h = round(width * scale), round(height * scale)
    target = folder / 'parts' / (task['name'] + '.webp')
elif task['kind'] == 'plate':
    w, h = 2048, 1152
    target = folder / 'plate.webp'
else:
    w, h = 2048, 1024
    target = folder / (task['name'] + '.webp')
target.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['cwebp', '-quiet', '-q', '94', '-alpha_q', '100', '-resize', str(w), str(h), str(source), '-o', str(target)], check=True)
promptsFile = folder / 'prompts.json'
prompts = json.loads(promptsFile.read_text()) if promptsFile.exists() else {}
prompts[task['name']] = {'prompt': task['prompt'], 'tool': 'built-in imagegen', 'source': str(source.relative_to(root)), 'file': str(target.relative_to(folder)), 'w': w, 'h': h}
promptsFile.write_text(json.dumps(prompts, indent=4) + '\n')
if task['kind'] == 'part':
    kitFile = folder / 'kit.json'
    kit = json.loads(kitFile.read_text()) if kitFile.exists() else {'kit': folder.name, 'stations': task['stations'], 'parts': []}
    kit['parts'] = [p for p in kit['parts'] if p['name'] != task['name']]
    kit['parts'].append({'name': task['name'], 'file': str(target.relative_to(folder)), 'w': w, 'h': h, 'foot': [round(w * task.get('footX', .5)), round(h * task.get('footY', .88))], 'layer': task.get('layer', 'back')})
    kitFile.write_text(json.dumps(kit, indent=4) + '\n')
print(json.dumps({'file': str(target), 'w': w, 'h': h}))
