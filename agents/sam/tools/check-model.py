import json
import struct
from pathlib import Path

assets = Path(__file__).resolve().parents[3] / 'assets'
scratch = Path(__file__).resolve().parents[1] / 'scratch'
scratch.mkdir(exist_ok=True)
p = assets / 'exports/painted/icarus/beam-emitter.glb'
data = p.read_bytes()
magic, version, length = struct.unpack_from('<4sII', data)
assert magic == b'glTF' and version == 2 and length == len(data)
chunkLength, kind = struct.unpack_from('<I4s', data, 12)
assert kind == b'JSON'
doc = json.loads(data[20:20 + chunkLength])
assert doc.get('meshes') and doc.get('materials')
assert not doc.get('cameras')
assert not doc.get('extensions', {}).get('KHR_lights_punctual')
assert any(node.get('name') == 'beam axis' for node in doc['nodes'])
triangles = 0
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        assert primitive.get('mode', 4) == 4
        triangles += doc['accessors'][primitive['indices']]['count'] // 3
report = {'file': str(p.relative_to(assets)), 'bytes': len(data), 'triangles': triangles, 'meshes': len(doc['meshes']), 'materials': len(doc['materials']), 'cameras': 0, 'lights': 0}
(scratch / 'icarus-validation.json').write_text(json.dumps(report, indent=4) + '\n')
print(json.dumps(report))
