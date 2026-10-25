"""build the fleet in metres with clear module mounts."""

import ast
import importlib.util
import json
import math
import random
import shutil
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit

ASSETS = Path(__file__).resolve().parents[2]
LENGTHS = {'hauler': 130, 'nobody': 60, 'patrol-cutter': 40, 'tug': 30,
    'hangar/freighter': 140, 'hangar/tanker': 150, 'hangar/liner': 170,
    'hangar/transport': 90, 'hangar/colony': 200, 'hangar/research': 110,
    'hangar/corvette': 60, 'hangar/frigate': 120, 'hangar/battleship': 260,
    'hangar/prison': 150, 'hangar/yacht': 40, 'hangar/tug': 35,
    'hangar/police-light': 45, 'hangar/police-heavy': 90}


def definitions(filename):
    path = Path(__file__).with_name(filename)
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) or
        isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id.isupper()
            for target in n.targets for t in (target.elts if isinstance(target, ast.Tuple) else [target]))]
    scope = dict(vars(kit), math=math, random=random, bmesh=bmesh, Vector=Vector, Matrix=Matrix)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)
    return scope


def bounds(root):
    bpy.context.view_layer.update()
    points = [o.matrix_world @ Vector(c) for o in root.children_recursive
        if o.type == 'MESH' for c in o.bound_box]
    return [[min(v[i] for v in points), max(v[i] for v in points)] for i in range(3)]


def scaleHull(root, factor):
    for obj in root.children_recursive:
        if obj.type == 'MESH':
            obj.data = obj.data.copy()
            for mod in list(obj.modifiers):
                with bpy.context.temp_override(object=obj, active_object=obj):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
            obj.data.transform(Matrix.Scale(factor, 4))
        obj.location *= factor
        obj.matrix_parent_inverse.translation *= factor
        if 'radius' in obj:
            obj['radius'] *= factor
    bpy.context.view_layer.update()


def envelopes():
    records = json.loads((ASSETS / 'blender/painted/far-treasure-metres.json').read_text())['modules']
    result = {}
    for family in ('cruise', 'cargo', 'maneuver', 'power', 'utility'):
        rows = [r['bounds'] for r in records if r['slot'] == family + '1']
        result[family] = [[min(r[i][0] for r in rows), max(r[i][1] for r in rows)] for i in range(3)]
    return result


def layout(extent, shapes):
    width = extent[0][1] - extent[0][0] - 1
    rows, row, used = [], [], 0
    for family, shape in shapes.items():
        span = shape[0][1] - shape[0][0]
        if row and used + span + 1 > width:
            rows.append(row)
            row, used = [], 0
        row.append((family, shape, used))
        used += span + 1
    rows.append(row)
    depths = [max(s[1][1] - s[1][0] for _, s, _ in row) for row in rows]
    y = -(sum(depths) + len(rows) - 1) / 2
    result = {}
    for row, depth in zip(rows, depths):
        span = row[-1][2] + row[-1][1][0][1] - row[-1][1][0][0]
        start = sum(extent[0]) / 2 - span / 2
        for family, shape, offset in row:
            result[family] = [start + offset - shape[0][0], y - shape[1][0], 0]
        y += depth + 1
    return result


def mounts(root, p, shapes, extent):
    positions = layout(extent, shapes)
    meshes = [o for o in root.children_recursive if o.type == 'MESH']
    boxes = [[o.matrix_world @ Vector(c) for c in o.bound_box] for o in meshes]
    boxes = [[[min(v[i] for v in pts), max(v[i] for v in pts)] for i in range(3)] for pts in boxes]
    for family, at in positions.items():
        shape = shapes[family]
        footprint = [[at[i] + shape[i][0], at[i] + shape[i][1]] for i in range(2)]
        roof = max((b[2][1] for b in boxes if all(footprint[i][0] < b[i][1]
            and footprint[i][1] > b[i][0] for i in range(2))), default=extent[2][1])
        floor = roof + .5
        at[2] = floor - shape[2][0]
        cx, cy = [sum(axis) / 2 for axis in footprint]
        base = sum(extent[2]) / 2
        kit.block(f'{family} cross arm', (cx, cy / 2, base), (1, abs(cy) + 1, .7), p['dark'], root, .12)
        kit.block(f'{family} pylon', (cx, cy, (base + floor) / 2), (1, 1, floor - base), p['teal'], root, .12)
        kit.block(f'{family} mount', (cx, cy, floor - .2),
            (shape[0][1] - shape[0][0], shape[1][1] - shape[1][0], .4), p['dark'], root, .12)
        kit.socket(root, family + '1', family, at)
    return positions


def fitPreview(root, positions, fleet):
    for family, at in positions.items():
        name = {'power': 'reactor.mk2', 'cruise': 'cruise.mk2', 'maneuver': 'maneuver.mk2',
            'cargo': 'cargo.mk2', 'utility': 'driver.mk1'}[family]
        group = kit.empty('preview ' + name, root)
        fleet['MODULES'][name][1](kit.palette(), group)
        scaleHull(group, 7.2)
        group.location = at


def buildOne(name, length, makers, fleet, shapes):
    kit.reset()
    p, root = kit.palette(), kit.empty(name.replace('/', '_'))
    root['units'], root['metres_per_unit'], root['revision'] = 'metres', 1, 'fl1'
    root['forward_axis'], root['export_up_axis'] = '+x', '+y'
    key = name.split('/')[-1].replace('-', '_')
    if name == 'patrol-cutter':
        key = 'cutter'
    makers[key](p, root)
    extent = bounds(root)
    scaleHull(root, length / (extent[0][1] - extent[0][0]))
    extent = bounds(root)
    positions = mounts(root, p, shapes, extent)
    result = bounds(root)
    if abs(result[0][1] - result[0][0] - length) > .01:
        raise ValueError('mounts changed the specified hull length')
    source = ASSETS / 'blender/painted/fleet-metres' / (name + '.blend')
    target = ASSETS / 'blender/staging/fl1' / (name + '.glb')
    renders = ASSETS / 'blender/renders/fleet-metres' / name
    for folder in (source.parent, target.parent, renders):
        folder.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    kit.consolidate_all(root)
    kit.export(root, target)
    record = {'name': name, 'length': length, 'bounds': result, 'sockets': positions, 'triangles': kit.stats(root)}
    fitPreview(root, positions, fleet)
    previewBounds = bounds(root)
    span = max(a[1] - a[0] for a in previewBounds)
    root.scale = (12 / span,) * 3
    kit.toonify(18)
    kit.render(root, 'fitted', 18, renders)
    final = ASSETS / 'exports/painted' / (name + '.glb')
    final.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, final)
    return record


def build():
    fleet = definitions('build-painted-fleet.py')
    hangar = definitions('build-hangar.py')
    shapes = envelopes()
    records = []
    for name, length in LENGTHS.items():
        records.append(buildOne(name, length, hangar if '/' in name else fleet, fleet, shapes))
    path = ASSETS / 'blender/painted/fleet-metres.json'
    path.write_text(json.dumps(records, indent=4) + '\n')


if __name__ == '__main__':
    build()
