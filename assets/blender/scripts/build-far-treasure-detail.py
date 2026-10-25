"""add human-scale details to the metre hull."""

import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import surfacecheck

ASSETS = Path(__file__).resolve().parents[2]


def loadBase():
    path = Path(__file__).with_name('build-far-treasure-metres.py')
    spec = importlib.util.spec_from_file_location('metreHull', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def panePoint(theta, phi):
    return Vector((35.286 + 7.344 * math.cos(theta),
        6.768 * math.sin(theta) * math.cos(phi),
        4.464 + 4.608 * math.sin(theta) * math.sin(phi)))


def closedFrame(name, points, radius, material, parent):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions, curve.bevel_depth, curve.bevel_resolution = '3D', radius, 0
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, position in zip(spline.points, points):
        point.co = (*position, 1)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    curve.materials.append(material)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')


def nose(p, hull):
    bm = bmesh.new()
    rows, columns = 20, 72
    for row in range(rows):
        for col in range(columns):
            angles = [(row, col), (row + 1, col), (row + 1, col + 1), (row, col + 1)]
            points = [panePoint(r * math.pi / (2 * rows), c * math.tau / columns) for r, c in angles]
            bm.faces.new([bm.verts.new(v) for v in (points[:3] if row == 0 else points)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    kit.link('gunner capsule panes', bm, p['glass'], hull)
    for col in range(columns):
        kit.pipe('capsule meridian frame', [panePoint(.04 + i * (math.pi / 2 - .04) / 40, col * math.tau / columns)
            for i in range(41)], .035, p['cream'], hull, .01, 6)
    for row in range(1, rows + 1):
        closedFrame('capsule hoop frame', [panePoint(row * math.pi / (2 * rows), i * math.tau / 144)
            for i in range(144)], .04, p['tealD'], hull)


def windows(p, hull):
    for side in (-1, 1):
        facing = '+y' if side > 0 else '-y'
        for row, z in enumerate((-1.4, 1.4, 4.2)):
            group = kit.empty(f'porthole_{side}_{row}', hull)
            for center, wall in ((-12.6, 7.92), (16.416, 7.92), (28.656, 7.488)):
                if center > 25 and z < 0:
                    continue
                for index in range(8):
                    x = center + (index - 3.5) * .8
                    if abs(x + 12.6) < 1.2 or abs(x - 29.5) < 1.2:
                        continue
                    kit.surfacePanel('porthole frame', (x, 0, z), (.62, .12, .62), p['tealD'],
                        group, facing, side * wall, .04)
                    kit.surfacePanel('porthole pane', (x, 0, z), (.46, .06, .46), p['lamp'],
                        group, facing, side * (wall + .28), .035)
            kit.consolidate(group)


def airlock(p, hull, x, side, z, wall):
    facing = '+y' if side > 0 else '-y'
    kit.surfacePanel('airlock surround', (x, 0, z), (1.8, .16, 2.6), p['mustard'], hull,
        facing, side * wall, .08)
    kit.surfacePanel('airlock door', (x, 0, z), (1.35, .12, 2.2), p['tealD'], hull,
        facing, side * (wall + .26), .08)
    for dz in (-1.12, 1.12):
        for dx in (-.65, -.2, .25, .7):
            kit.surfacePanel('hazard mark', (x + dx, 0, z + dz), (.2, .03, .14), p['black'], hull,
                facing, side * (wall + .26), .01)
    kit.lamp('airlock flood light', (x, side * (wall + .4), z + 1.65), (.8, .1, .16), facing, p, hull)
    y = side * (wall + .55)
    for height in (z - 3.2, z - 1.6, z + 1.5):
        for dx in (-.65, .65):
            kit.pipe('ladder bracket', [(x + dx, side * (wall - 1), height),
                (x + dx, y, height)], .05, p['dark'], hull)
    kit.pipe('airlock grab rail', [(x + 1.1, y, z - 1), (x + 1.1, y, z + 1)], .05, p['mustard'], hull)
    for dx in (-.65, .65):
        kit.pipe('ladder rail', [(x + dx, y, z - 3.4), (x + dx, y, z - 1.4)], .045, p['dark'], hull)
    for index in range(7):
        height = z - 3.3 + index * .3
        kit.pipe('ladder rung', [(x - .65, y, height), (x + .65, y, height)], .04, p['mustard'], hull)


def label(text, at, side, size, p, hull):
    curve = bpy.data.curves.new('registry lettering', 'FONT')
    curve.body, curve.size, curve.extrude = text, size, 0
    curve.align_x = 'CENTER'
    obj = bpy.data.objects.new('hull lettering', curve)
    bpy.context.collection.objects.link(obj)
    obj.parent, obj.location = hull, at
    obj.rotation_euler = (math.pi / 2, 0, math.pi if side > 0 else 0)
    curve.materials.append(p['mustard'])
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')


def equipment(p, hull):
    for side in (-1, 1):
        airlock(p, hull, 29.5, side, 1.8, 7.488)
        label('far treasure', (28.3, side * 7.8, 6.4), side, .62, p, hull)
        label('ft-070', (16.4, side * 8.18, -3.8), side, .6, p, hull)
        for x in (25, 31):
            kit.block('rcs quad mount', (x, side * 7.3, -4.7), (1.5, 1.4, 1.4), p['teal'], hull, .12)
            for dx in (-.4, .4):
                for dz in (-.4, .4):
                    kit.barrel('rcs nozzle', (x + dx, side * 8.12, -4.7 + dz), .18, .32,
                        p['dark'], hull, 'Y', sides=12, round_=.04)
        kit.block('radiator manifold', (-17.85, side * 6.8, -.5), (4.7, 3.4, .65), p['dark'], hull, .1)
        for index in range(7):
            kit.block('radiator fin', (-19.8 + index * .65, side * 8.4, -.5),
                (.18, 2, 3.6), p['tealD'], hull, .04)
        kit.vent('service vent', (21.1, side * 8.15, -2.4), (1.4, .2, 1.6),
            '+y' if side > 0 else '-y', p, hull, 6)
    airlock(p, hull, -12.6, 1, -2.2, 7.92)
    kit.surfacePanel('roof hatch', (28.8, -4.5, 0), (1.2, 1.4, .15), p['tealD'], hull, '+z', 7.92, .06)
    for y, height in ((-1.3, 2.4), (0, 3.6), (1.3, 1.8)):
        kit.antenna('comms mast', (34.3, y, 7.7), height, p, hull)


def figure(p, root):
    group = kit.empty('preview scale figure 1.8m', root, (30, -11, -7.56))
    kit.block('scale torso', (0, 0, 1.05), (.4, .23, .6), p['mustard'], group, .07)
    kit.barrel('scale helmet', (0, 0, 1.64), .16, .32, p['cream'], group, 'Z', sides=12)
    for side in (-1, 1):
        kit.block('scale leg', (side * .13, 0, .4), (.16, .2, .8), p['dark'], group, .05)
        kit.block('scale arm', (side * .28, 0, 1.06), (.14, .18, .62), p['cream'], group, .04)


def build():
    base = loadBase()
    source = ASSETS / 'blender/painted/far-treasure.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects['far_treasure']
    hull = next(o for o in root.children if o.name == 'hull')
    for obj in list(hull.children_recursive):
        if obj.name.startswith(('capsule', 'gunner capsule', 'porthole', 'aft service panel', 'forward service panel')):
            bpy.data.objects.remove(obj, do_unlink=True)
    root['revision'], root['surface_clearance'] = 'sh2', .12
    p = kit.palette()
    nose(p, hull)
    windows(p, hull)
    equipment(p, hull)
    fleet = base.comparison().fleetParts()
    extent = base.validateHull(root, fleet)
    stage = ASSETS / 'blender/staging/sh2'
    renders = ASSETS / 'blender/renders/painted'
    stage.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(stage / 'far-treasure.blend'))
    kit.KEEP += ('porthole',)
    kit.consolidate_all(root)
    kit.export(root, stage / 'far-treasure.glb')
    info = {'revision': 'sh2', 'bounds': extent, 'triangles': kit.stats(root),
        'deck_pitch': 2.8, 'airlock_height': 2.2, 'figure_height': 1.8}
    for slot, name in fleet['STARTER'].items():
        sock = next(o for o in root.children if o.name == 'socket_' + slot)
        group = kit.empty('preview module ' + name, root)
        fleet['MODULES'][name][1](p, group)
        base.uniformBevel(group)
        base.bakeMetres(group)
        group.location = sock.location
    figure(p, root)
    root.scale = (1 / 7.2,) * 3
    kit.toonify(14)
    kit.render(root, 'far-treasure-detail', 14, renders)
    shutil.copy2(stage / 'far-treasure.blend', source)
    shutil.copy2(stage / 'far-treasure.glb', ASSETS / 'exports/painted/far-treasure.glb')
    (ASSETS / 'blender/painted/far-treasure-detail.json').write_text(json.dumps(info, indent=4) + '\n')


if __name__ == '__main__':
    build()
