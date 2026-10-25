import json
from pathlib import Path
from PIL import Image

project = Path(__file__).resolve().parents[3]
style = (project / 'agents/style.md').read_text().split('## the toy block\n\n')[1].split('\nafter the block')[0]
block = '\n'.join(line[4:] for line in style.strip('\n').splitlines())
groups = {'station': 'station-world', 'ships': 'ship-lineup', 'nav': 'sector-manifest',
    'orbit': 'burn-plan', 'combat': 'ship-fight'}
records = []
for group, subject in groups.items():
    folder = project / 'assets/concepts/toy' / group
    prompts = json.loads((folder / 'prompts.json').read_text())
    entries = prompts if isinstance(prompts, list) else list(prompts.values())
    for palette in ('meadow', 'lagoon'):
        path = folder / (subject + '-' + palette + '.webp')
        with Image.open(path) as image:
            assert image.size == (2048, 1152), path.name
        entry = next(e for e in entries if e.get('file') == str(path.relative_to(project)))
        assert entry['prompt'].startswith(block + '\n'), path.name
        width, height = entry['sourceSize']
        assert abs(width / height - 16 / 9) < .06, path.name + ': source ratio differs'
        records.append({'file': str(path.relative_to(project)), 'size': [2048, 1152]})
report = project / 'agents/sam/scratch/toy/variants-validation.json'
report.write_text(json.dumps(records, indent=4) + '\n')
print('ten frames passed')
