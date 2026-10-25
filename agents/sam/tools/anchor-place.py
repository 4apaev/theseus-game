import json
import sys
from pathlib import Path
from PIL import Image

folder = Path(__file__).resolve().parents[3] / 'assets' / sys.argv[1]
p = folder / 'kit.json'
kit = json.loads(p.read_text())
for part in kit['parts']:
    image = Image.open(folder / part['file']).convert('RGBA')
    box = image.getchannel('A').point(lambda a: 255 if a > 200 else 0).getbbox()
    part['foot'] = [round((box[0] + box[2]) / 2), box[3] - 6]
p.write_text(json.dumps(kit, indent=4) + '\n')
