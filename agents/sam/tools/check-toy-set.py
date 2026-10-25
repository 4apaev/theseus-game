import json
import sys
from pathlib import Path
from PIL import Image

project = Path(__file__).resolve().parents[3]
folder = project / sys.argv[1]
size = int(sys.argv[2])
expected = sys.argv[3:]
style = (project / 'agents/style.md').read_text().split('## the toy block\n\n')[1].split('\nafter the block')[0]
block = '\n'.join(line[4:] for line in style.strip('\n').splitlines())
prompts = json.loads((folder / 'prompts.json').read_text())
results = []
for name in expected:
    path = folder / (name + '.png')
    with Image.open(path) as image:
        assert image.size == (size, size), name
        assert image.mode == 'RGBA', name
        assert image.getchannel('A').getextrema()[0] == 0, name
        assert image.getchannel('A').getbbox(), name
    assert prompts[path.name]['prompt'].startswith(block + '\n'), name
    results.append({'file': str(path.relative_to(project)), 'size': size, 'alpha': True})
report = project / 'agents/sam/scratch/toy' / (folder.name + '-validation.json')
report.write_text(json.dumps(results, indent=4) + '\n')
print(str(len(results)) + ' files passed')
