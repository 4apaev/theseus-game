import json
import struct
from pathlib import Path

project = Path(__file__).resolve().parents[3]
folder = project / 'assets/exports/toy'
roles = {'toy-red', 'toy-green', 'toy-butter', 'toy-milk', 'toy-dark', 'toy-glow'}
records = []
for path in sorted(folder.rglob('*.glb')):
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert (magic, version, length) == (b'glTF', 2, len(raw)), path.name
    count, kind = struct.unpack_from('<I4s', raw, 12)
    assert kind == b'JSON', path.name
    doc = json.loads(raw[20:20 + count])
    assert set(m['name'] for m in doc['materials']) <= roles, path.name
    assert not doc.get('textures'), path.name
    triangles = sum(doc['accessors'][p['indices']]['count'] // 3
        for mesh in doc['meshes'] for p in mesh['primitives'])
    limit = 60000 if path.stem in ('station-dry-dock', 'station-gas-station') else 80000 if path.stem.startswith('station') else 3000 if path.parent.name == 'modules' else 40000
    assert triangles <= limit, path.name
    nodes = {n['name']: n for n in doc['nodes'] if 'name' in n}
    if path.stem == 'station':
        for name in ('berth', 'berth_b', 'berth_c', 'berth_d',
                'spot_exchange', 'spot_rigging', 'spot_comms', 'spot_chart',
                'walk_a', 'walk_b', 'walk_c', 'walk_d'):
            assert name in nodes, name
        for name in ('berth_b', 'berth_c', 'berth_d'):
            assert nodes[name]['extras']['size'] > 0, name
    elif path.stem.startswith('station-'):
        assert 'berth' in nodes, path.name
        for key in ('exchange', 'rigging', 'comms', 'chart'):
            assert 'spot_' + key in nodes, path.name
    elif path.stem.startswith('ship-'):
        for family in ('power', 'cruise', 'maneuver', 'cargo', 'utility'):
            slot = family + '1'
            node = nodes['socket_' + slot]
            assert node['extras']['slot'] == slot, slot
            assert node['extras']['family'] == family, slot
        assert 'exhaust' in nodes, path.name
    records.append({'file': str(path.relative_to(project)), 'triangles': triangles, 'bytes': len(raw)})
expected = {'station', 'ship-cargo', 'ship-military', 'ship-industrial', 'ship-research',
    'ship-tanker', 'ship-liner', 'ship-tug', 'ship-police-cutter', 'ship-raider', 'ship-courier'}
assert expected <= {Path(record['file']).stem for record in records}, 'required exports are missing'
assert len(records) >= 16, 'baseline exports are missing'
report = project / 'agents/sam/scratch/toy/model-validation.json'
report.write_text(json.dumps(records, indent=4) + '\n')
print(str(len(records)) + ' model exports passed')
