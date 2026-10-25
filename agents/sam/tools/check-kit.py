import json
import subprocess
import sys
from pathlib import Path

folder = Path(__file__).resolve().parents[3] / 'assets/stations' / sys.argv[1]
kit = json.loads((folder / 'kit.json').read_text())
reports = []
for part in kit['parts']:
    temp = Path(__file__).resolve().parents[1] / 'scratch' / ('sam-' + part['name'] + '.png')
    temp.parent.mkdir(exist_ok=True)
    subprocess.run(['dwebp', str(folder / part['file']), '-quiet', '-o', str(temp)], check=True)
    result = subprocess.run(['node', str(Path(__file__).with_name('check-foot.mjs')), str(temp)], check=True, capture_output=True, text=True)
    report = json.loads(result.stdout)
    assert max(report['width'], report['height']) == 2048
    assert [report['width'], report['height']] == [part['w'], part['h']]
    assert all(sample[-1] == 0 for sample in report['samples'][:4])
    report['file'] = part['file']
    if not part['name'].startswith('platform') and part['name'] != 'ship-pad':
        part['foot'] = report['foot']
    reports.append(report)
(temp.parent / (folder.name + '-validation.json')).write_text(json.dumps(reports, indent=4) + '\n')
(folder / 'kit.json').write_text(json.dumps(kit, indent=4) + '\n')
print(str(len(reports)) + ' sprites passed dimensions and alpha checks')
