"""check station exports after the external builds."""

import json
import struct
from pathlib import Path


assets = Path(__file__).resolve().parents[3] / 'assets'
scratch = Path(__file__).resolve().parents[1] / 'scratch'
scratch.mkdir(exist_ok=True)
reports = []
for name in ('outpost', 'yards', 'hub', 'lab', 'gate', 'dock', 'gas', 'mine', 'relay'):
    path = assets / 'exports/painted/stations' / (name + '.glb')
    data = path.read_bytes()
    magic, version, size = struct.unpack_from('<III', data)
    assert magic == 0x46546c67 and version == 2 and size == len(data), name
    length, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4e4f534a
    doc = json.loads(data[20:20 + length])
    nodes = {node['name']: node for node in doc['nodes']}
    revision = 'dk1' if name == 'outpost' else 'f4'
    assert nodes[name].get('extras', {}).get('station_revision') == revision, (name, 'stale export')
    if name == 'outpost':
        for marker, size in zip(('berth_b', 'berth_c', 'berth_d', 'berth_e'),
                ('small', 'medium', 'large', 'small')):
            extras = nodes[marker].get('extras', {})
            assert extras.get('size') == size and extras.get('forward') == '+x', marker
    halls = [tuple(node['extras']['hall_size']) for node in doc['nodes'] if 'hall_size' in node.get('extras', {})]
    assert len(halls) >= 11 and len(halls) == len(set(halls)), (name, 'hall sizes')
    workAreas = [node for node in doc['nodes'] if 'work_area_size' in node.get('extras', {})]
    assert len(workAreas) >= 10, (name, 'work areas')
    assert 'original station core' in nodes and 'service precinct' not in nodes, (name, 'repeated core')
    assert {'berth', 'walk_a', 'walk_b', 'walk_c', 'walk_d', 'walk_e'} <= nodes.keys(), name
    assert not doc.get('cameras'), name
    assert not doc.get('extensions', {}).get('KHR_lights_punctual'), name
    assert not doc.get('images'), name
    assert nodes['berth'].get('extras', {}).get('forward') == '+x', name
    assert (assets / 'blender/stations/painted' / name / (name + '.blend')).is_file(), name
    for suffix in ('preview', 'reverse'):
        render = assets / 'blender/renders/stations' / name / f'{name}-{suffix}.png'
        assert render.is_file(), name
        assert render.stat().st_mtime >= path.stat().st_mtime, (name, 'stale render')
    triangles = sum(doc['accessors'][primitive['indices']]['count'] // 3
        for mesh in doc['meshes'] for primitive in mesh['primitives'])
    reports.append({'kit': name, 'file': f'assets/exports/painted/stations/{name}.glb',
        'bytes': size, 'triangles': triangles, 'markers': 10 if name == 'outpost' else 6,
        'revision': revision, 'halls': len(halls), 'work_areas': len(workAreas)})
(scratch / 'station-validation.json').write_text(json.dumps(reports, indent=4) + '\n')
print(json.dumps(reports))
