"""build the far treasure comparison hull without command arguments."""

import ast
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit


def fleetParts():
    path = Path(__file__).with_name('build-painted-fleet.py')
    tree = ast.parse(path.read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) or
        isinstance(node, ast.Assign) and all(isinstance(name, ast.Name) and
        name.id.isupper() for target in node.targets for name in
        (target.elts if isinstance(target, ast.Tuple) else [target]))]
    scope = dict(vars(kit), math=math, bmesh=bmesh, Vector=Vector)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)
    return scope


def nosePoint(theta, phi):
    return Vector((4.88 + 1.02 * math.cos(theta),
        .94 * math.sin(theta) * math.cos(phi),
        .62 + .64 * math.sin(theta) * math.sin(phi)))


def gunnerNose(p, hull):
    bm = bmesh.new()
    for row in range(5):
        for col in range(12):
            angles = [(row * math.pi / 10, col * math.tau / 12),
                ((row + 1) * math.pi / 10, col * math.tau / 12),
                ((row + 1) * math.pi / 10, (col + 1) * math.tau / 12),
                (row * math.pi / 10, (col + 1) * math.tau / 12)]
            points = [nosePoint(*angle) for angle in angles]
            if row == 0:
                points = points[:3]
            bm.faces.new([bm.verts.new(point) for point in points])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    kit.link('gunner capsule panes', bm, p['glass'], hull)
    for col in range(12):
        phi = col * math.tau / 12
        kit.pipe('capsule meridian frame', [nosePoint(i * math.pi / 40, phi)
            for i in range(21)], .014, p['cream'], hull, .006)
    for row in range(1, 6):
        kit.pipe('capsule hoop frame', [nosePoint(row * math.pi / 10, i * math.tau / 48)
            for i in range(49)], .016, p['tealD'], hull, .006)
    kit.block('gunner seat', (5.28, 0, .53), (.18, .26, .32), p['olive'], hull, .02)


def illuminators(p, hull):
    positions = [(-2.42 + i * .14) for i in range(10)]
    positions += [(1.66 + i * .14) for i in range(9)]
    positions += [(3.18 + i * .14) for i in range(11)]
    for side in (-1, 1):
        for row, z in enumerate((-.56, .02, .61)):
            parts = []
            for x in positions:
                parts.append(kit.block('illuminator frame', (x, side * 1.175, z),
                    (.1, .026, .1), p['dark'], hull, .009))
                parts.append(kit.block('illuminator pane', (x, side * 1.194, z),
                    (.07, .012, .07), p['lamp'], hull, .007))
            bpy.ops.object.select_all(action='DESELECT')
            for obj in parts:
                obj.select_set(True)
                with bpy.context.temp_override(object=obj, active_object=obj):
                    for modifier in list(obj.modifiers):
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.context.view_layer.objects.active = parts[0]
            bpy.ops.object.join()
            parts[0].name = f'porthole_{"port" if side > 0 else "starboard"}_{row + 1}'


def validate(root, fleet):
    sockets = {obj.name: obj for obj in root.children if obj.name.startswith('socket_')}
    if len(sockets) != 5:
        raise ValueError('the hull needs five sockets')
    for slot, at in fleet['FAR_SOCKETS'].items():
        if (sockets['socket_' + slot].location - Vector(at)).length > .00001:
            raise ValueError('a socket changed position')
    rows = [obj for obj in root.children_recursive if obj.name.startswith('porthole')]
    if len(rows) != 6 or any(obj.type != 'MESH' for obj in rows):
        raise ValueError('the hull needs six illuminator meshes')
    if any('windscreen' in obj.name or 'side window' in obj.name for obj in root.children_recursive):
        raise ValueError('the original windows remain')


def build():
    assets = Path(__file__).resolve().parents[2]
    source, exports, renders = [assets / path for path in
        ('blender/painted', 'exports/painted', 'blender/renders/painted')]
    for folder in (source, exports, renders):
        folder.mkdir(parents=True, exist_ok=True)
    fleet = fleetParts()
    kit.reset()
    p, root = kit.palette(), kit.empty('far_treasure_b')
    root['category'], root['forward_axis'], root['export_up_axis'] = 'painted', '+x', '+y'
    root['metres_per_unit'] = 7.2
    hull = fleet['far_treasure'](p, root)
    for obj in list(hull.children):
        if 'windscreen' in obj.name or 'side window' in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
    gunnerNose(p, hull)
    illuminators(p, hull)
    for slot, at in fleet['FAR_SOCKETS'].items():
        kit.socket(root, slot, slot.rstrip('1'), at)
    validate(root, fleet)
    bpy.ops.wm.save_as_mainfile(filepath=str(source / 'far-treasure-b.blend'))
    kit.KEEP += ('porthole',)
    kit.consolidate_all(root)
    validate(root, fleet)
    kit.export(root, exports / 'far-treasure-b.glb')
    info = {'name': 'far-treasure-b', 'triangles': kit.stats(root),
        'metres_per_unit': 7.2, 'illuminator_rows': 6,
        'source': 'assets/blender/painted/far-treasure-b.blend',
        'export': 'assets/exports/painted/far-treasure-b.glb'}
    (source / 'far-treasure-b.json').write_text(json.dumps(info, indent=4) + '\n')
    fleet['fit'](fleet['STARTER'])(p, root)
    kit.toonify(14)
    kit.render(root, 'far-treasure-b', 14, renders)


build()
