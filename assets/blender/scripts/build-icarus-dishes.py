"""build the dish array from the existing emitter source."""

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
from paintedstations import beam, preview

ASSETS = Path(__file__).resolve().parents[2]


def loadEmitter():
    path = ASSETS / 'blender/icarus/beam-emitter.blend'
    with bpy.data.libraries.load(str(path), link=False) as (source, target):
        target.objects = source.objects
    objects = [obj for obj in target.objects if obj is not None]
    for obj in objects:
        bpy.context.scene.collection.objects.link(obj)
    return next(obj for obj in objects if obj.name == 'icarus emitter')


def copyEmitter(source, parent, at, angle):
    objects = [source] + list(source.children_recursive)
    copies = {obj: obj.copy() for obj in objects}
    for obj, clone in copies.items():
        if obj.type == 'MESH':
            clone.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(clone)
        clone.parent = copies.get(obj.parent, parent)
    root = copies[source]
    root.name = 'array emitter'
    root.location, root.scale = at, (3, 3, 3)
    root.rotation_euler = (0, math.pi / 2, angle)


def ring(p, root, radius=780, count=128):
    for i in range(count):
        a, b = i * math.tau / count, (i + 1) * math.tau / count
        for radial, z in ((-6, -6), (6, -6), (0, 6)):
            r = radius + radial
            beam('truss chord', (r * math.cos(a), r * math.sin(a), z),
                (r * math.cos(b), r * math.sin(b), z), 1, p['teal'], root)
        beam('truss diagonal', ((radius - 6) * math.cos(a), (radius - 6) * math.sin(a), -6),
            (radius * math.cos(b), radius * math.sin(b), 6), .65, p['mustard'], root)


def panels(p, root, angle, radius):
    group = kit.empty('thermal panels', root, (radius * math.cos(angle), radius * math.sin(angle), 0))
    group.rotation_euler.z = angle
    for z in (-35, 35):
        kit.block('radiator', (0, 0, z), (4, 22, 44), p['olive'], group, .15)
        beam('radiator spine', (0, 0, 0), (0, 0, z), .8, p['mustard'], group)
    kit.block('sunshield backing', (-16, 0, 0), (2, 30, 25), p['rust'], group, .15)
    for y in (-10, 0, 10):
        kit.block('ceramic sunshield', (-17.2, y, 0), (.3, 9.6, 24), p['cream'], group, .05)


def build():
    kit.reset()
    bpy.context.scene.unit_settings.system = 'METRIC'
    root, p = kit.empty('icarus dishes'), kit.palette()
    root['units'], root['export_up_axis'] = 'metres', '+y'
    root['orbitRadiusMetres'], root['diameterMetres'] = .05 * 149597870700, 1600
    root['orbitPlacement'] = 'the client places the array at 0.05 au'
    ring(p, root)
    source = loadEmitter()
    for i in range(128):
        angle = i * math.tau / 128
        copyEmitter(source, root, (780 * math.cos(angle), 780 * math.sin(angle), 8), angle)
        panels(p, root, angle, 780)
    for obj in reversed([source] + list(source.children_recursive)):
        bpy.data.objects.remove(obj, do_unlink=True)
    sourceFolder, exports, renders = [ASSETS / path for path in ('blender/icarus', 'exports/painted/icarus', 'blender/renders/icarus')]
    for folder in (sourceFolder, exports, renders):
        folder.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(sourceFolder / 'dishes.blend'))
    kit.consolidate_all(root)
    kit.export(root, exports / 'dishes.glb')
    info = {'emitters': 128, 'triangles': kit.stats(root), 'diameterMetres': 1600,
        'emitterSource': 'assets/blender/icarus/beam-emitter.blend'}
    (sourceFolder / 'dishes.json').write_text(json.dumps(info, indent=4) + '\n')
    root.scale = (.05, .05, .05)
    preview(root, 'dishes', renders, 100)


build()
