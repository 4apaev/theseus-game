"""build the close node and three net densities."""

import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
from paintedstations import beam, preview

ASSETS = Path(__file__).resolve().parents[2]
RADIUS = .05 * 149597870700
DENSITIES = {'sparse': 2, 'medium': 3, 'dense': 4}


def emitter(p, root):
    kit.chamfered('ceramic emitter', (0, 0, 0), (8, 8, 6), p['cream'], root, 1, .12)
    kit.barrel('beam collar', (0, 0, 3.5), 2.4, 1, p['teal'], root, 'Z', sides=12)
    kit.barrel('beam throat', (0, 0, 4.04), 1.7, .08, p['black'], root, 'Z')
    kit.barrel('emitter tip', (0, 0, 4.12), .65, .08, p['lamp'], root, 'Z')
    kit.empty('beam_axis', root, (0, 0, 4.2))['axis'] = '+z'
    for x in (-3, 3):
        kit.pipe('coolant loop', [(x, -4.3, -2), (x, -4.3, 2), (x, 0, 3.2)], .22, p['mustard'], root)
    for x in (-5, 5):
        for y in (-2.5, 0, 2.5):
            kit.block('radiator blade', (x, y, -2), (3, 1.8, .25), p['olive'], root, .04)


def strand(p, root, angle):
    along = Vector((math.cos(angle), math.sin(angle), 0))
    cross = Vector((-math.sin(angle), math.cos(angle), 0))
    for side in (-1, 1):
        beam('strand chord', along * 4 + cross * side * .7, along * 25 + cross * side * .7, .16, p['teal'], root)
    for i in range(4, 25, 3):
        beam('strand brace', along * i - cross * .7, along * min(i + 3, 25) + cross * .7, .10, p['cream'], root)
    beam('maintenance rail', along * 4 + Vector((0, 0, .7)), along * 25 + Vector((0, 0, .7)), .12, p['mustard'], root)


def crawler(p, root):
    robot = kit.empty('crawler', root, (15, 0, 1.5))
    robot['joint'] = True
    robot['path'] = ['walk_a', 'walk_b']
    kit.chamfered('crawler body', (0, 0, .3), (2.4, 1.6, 1), p['cream'], robot, .3)
    kit.block('crawler battery', (-.4, 0, 1), (1.2, 1.2, .5), p['teal'], robot)
    kit.block('eye crawler', (1.25, 0, .4), (.1, .6, .2), p['lamp'], robot)
    for x in (-.8, .8):
        for y in (-1, 1):
            foot = kit.empty(f'grip_{x}_{y}', robot, (x, y, -.2))
            foot['joint'] = True
            beam('grip arm', (0, 0, 0), (0, -y * .35, -.6), .14, p['mustard'], foot)
            kit.block('rail clamp', (0, -y * .35, -.65), (.5, .4, .3), p['dark'], foot)
    for name, x in (('walk_a', 6), ('walk_b', 23)):
        point = kit.empty(name, root, (x, 0, 1.5))
        point['forward'] = '+x'


def node():
    kit.reset()
    root = kit.empty('icarus net node')
    root['units'], root['export_up_axis'] = 'metres', '+y'
    p = kit.palette()
    emitter(p, root)
    for i in range(6):
        strand(p, root, i * math.tau / 6)
    crawler(p, root)
    deliver(root, 'net-node', 64)


def shell(density):
    kit.reset()
    p, root = kit.palette(), kit.empty(f'icarus net {density}')
    root['physicalRadiusMetres'], root['metresPerUnit'] = RADIUS, RADIUS / 1000
    root['units'], root['export_up_axis'] = 'far-view units', '+y'
    root['detailModel'] = 'assets/exports/painted/icarus/net-node.glb'
    root['strandWidthIsSchematic'] = True
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=DENSITIES[density], radius=1000)
    bm.verts.ensure_lookup_table()
    points = [v.co.copy() for v in bm.verts]
    edges = [(e.verts[0].co.copy(), e.verts[1].co.copy()) for e in bm.edges]
    root['nodes'], root['faces'] = len(points), len(bm.faces)
    bm.free()
    for a, b in edges:
        beam('net strand', a, b, .65, p['teal'], root)
    for i, point in enumerate(points):
        obj = kit.block('emitter node', point, (6, 6, 4), p['cream'], root, 0)
        obj.rotation_euler = point.to_track_quat('Z', 'Y').to_euler()
        lamp = kit.block('node aperture', point * 1.004, (2, 2, 1), p['mustard'], root, 0)
        lamp.rotation_euler = obj.rotation_euler
    deliver(root, f'net-{density}', 110)


def deliver(root, name, viewSize):
    source, exports, renders = [ASSETS / path for path in ('blender/icarus', 'exports/painted/icarus', 'blender/renders/icarus')]
    for folder in (source, exports, renders):
        folder.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.ops.wm.save_as_mainfile(filepath=str(source / f'{name}.blend'))
    kit.consolidate_all(root)
    kit.export(root, exports / f'{name}.glb')
    info = {'name': name, 'triangles': kit.stats(root), 'extras': dict(root.items()),
        'export': f'assets/exports/painted/icarus/{name}.glb'}
    (source / f'{name}.json').write_text(json.dumps(info, indent=4) + '\n')
    if name != 'net-node':
        root.scale = (.04, .04, .04)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=40 * 695700000 / RADIUS)
        kit.link('preview sun', bm, kit.palette()['lamp'], None)
    preview(root, name, renders, viewSize)


parser = argparse.ArgumentParser()
parser.add_argument('--density', choices=[*DENSITIES, 'all'], default='all')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
node()
for density in DENSITIES if args.density == 'all' else [args.density]:
    shell(density)
