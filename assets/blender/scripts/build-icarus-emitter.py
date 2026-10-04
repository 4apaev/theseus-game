"""build one beam emitter dish for the icarus array."""
import json
import math
import sys
from pathlib import Path
import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit

assets = Path(__file__).resolve().parents[2]
source = assets / 'blender/icarus'
exports = assets / 'exports/painted/icarus'
renders = assets / 'blender/renders/icarus'
for folder in (source, exports, renders):
    folder.mkdir(parents=True, exist_ok=True)
kit.reset()
p = kit.palette()
root = kit.empty('icarus emitter')
root['role'] = 'beam emitter dish'
root['units'] = 'metres'
kit.block('mount', (0, 0, .3), (3.4, 3.4, .6), p['teal'], root)
kit.barrel('azimuth bearing', (0, 0, .8), 1.2, .4, p['dark'], root, 'Z')
kit.barrel('pedestal', (0, 0, 1.5), .65, 1.3, p['cream'], root, 'Z')
dish = kit.empty('dish', root, (0, 0, 2))
dish['joint'] = True
dish.rotation_euler.y = math.radians(20)


def bowl():
    bm = bmesh.new()
    rings = []
    for i in range(9):
        radius = .08 + i * .49
        z = radius * radius / 10
        rings.append([bm.verts.new((radius * math.cos(a), radius * math.sin(a), z)) for a in (k * math.tau / 48 for k in range(48))])
    bm.faces.new(list(reversed(rings[0])))
    for i in range(8):
        for k in range(48):
            bm.faces.new([rings[i][k], rings[i + 1][k], rings[i + 1][(k + 1) % 48], rings[i][(k + 1) % 48]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.link('reflector', bm, p['cream'], dish)
    wall = obj.modifiers.new('dish thickness', 'SOLIDIFY')
    wall.thickness = .08


bowl()
kit.ring('rim', (0, 0, 1.59), 4, .13, p['teal'], dish, 'Z')
kit.barrel('receiver', (0, 0, 2.15), .24, .7, p['mustard'], dish, 'Z')
kit.barrel('emitter tip', (0, 0, 2.55), .16, .12, p['lamp'], dish, 'Z')
for i in range(4):
    a = i * math.tau / 4
    edge = (3.8 * math.cos(a), 3.8 * math.sin(a), 1.45)
    kit.pipe('feed support', [edge, (.32 * math.cos(a), .32 * math.sin(a), 2.4)], .075, p['dark'], dish)
for i in range(12):
    a = i * math.tau / 12
    kit.pipe('back rib', [(.7 * math.cos(a), .7 * math.sin(a), -.12), (2.4 * math.cos(a), 2.4 * math.sin(a), .43), (3.9 * math.cos(a), 3.9 * math.sin(a), 1.42)], .06, p['tealD'], dish)
for sign in (-1, 1):
    kit.block('coolant manifold', (sign * 1.5, 0, .75), (.5, 2.2, .35), p['rust'], root)
    kit.pipe('coolant line', [(sign * 1.5, 0, .9), (sign * 1.5, 0, 1.7), (sign * .6, 0, 2)], .1, p['mustard'], root)
kit.empty('beam axis', dish, (0, 0, 2.7))['axis'] = '+z'
bpy.ops.wm.save_as_mainfile(filepath=str(source / 'beam-emitter.blend'))
kit.consolidate_all(root)
kit.export(root, exports / 'beam-emitter.glb')
info = {'triangles': kit.stats(root), 'bytes': (exports / 'beam-emitter.glb').stat().st_size}
(source / 'manifest.json').write_text(json.dumps(info, indent=4) + '\n')
(source / 'readme.md').write_text('the dish scale and beam axis need review in the client.\n')
kit.toonify(12)
kit.render(root, 'beam-emitter', 12, renders)
