import json
from pathlib import Path
from PIL import Image

assets = Path(__file__).resolve().parents[3] / 'assets'
scratch = Path(__file__).resolve().parents[1] / 'scratch'
scratch.mkdir(exist_ok=True)
places = ['places/exchange/outpost', 'places/rigging/outpost', 'places/comms/outpost', 'places/hold/far-treasure']
reports = []
for name in places:
    folder = assets / name
    kit = json.loads((folder / 'kit.json').read_text())
    prompts = json.loads((folder / 'prompts.json').read_text())
    for file in ['plate.webp', 'preview.png']:
        assert Image.open(folder / file).size == (2048, 1152)
    assert kit['parts'] and kit['spots']
    for part in kit['parts']:
        image = Image.open(folder / part['file'])
        assert image.size == (part['w'], part['h'])
        assert max(image.size) == 2048
        assert part['layer'] in ['back', 'front']
        assert part['name'] in prompts
    for entry in prompts.values():
        assert (assets / entry['source']).is_file()
        assert (folder / entry['file']).is_file()
    assert len((folder / 'readme.md').read_text().splitlines()) == 3
    reports.append({'folder': name, 'parts': len(kit['parts']), 'spots': len(kit['spots'])})
for name in ['icarus', 'beam']:
    folder = assets / 'concepts' / name
    prompts = json.loads((folder / 'prompts.json').read_text())
    assert len(prompts) == 2
    for entry in prompts.values():
        assert Image.open(folder / entry['file']).size == (2048, 1152)
        assert (assets / entry['source']).is_file()
    assert len((folder / 'readme.md').read_text().splitlines()) == 3
    reports.append({'folder': 'concepts/' + name, 'frames': 2})
(scratch / 'delivery-validation.json').write_text(json.dumps(reports, indent=4) + '\n')
print(json.dumps(reports))
