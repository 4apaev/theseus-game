"""build the clean comparison hull and its modules in metres."""

import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import surfacecheck

ASSETS = Path(__file__).resolve().parents[2]
SCALE = 7.2
BEVEL = .02
GAP = .04


def comparison():
    path = Path(__file__).with_name('build-far-treasure-b.py')
    spec = importlib.util.spec_from_file_location('comparison', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def block(name, at, size, color, parent):
    return kit.block(name, at, size, color, parent, BEVEL)


def shell(p, root):
    hull = kit.empty('hull', root)
    kit.chamfered('spine', (-.1, 0, -.12), (6.4, 1.6, 1.65), p['dark'], hull, .25, BEVEL)
    for name, x, length in (('aft hull', -1.75, 1.62), ('forward hull', 2.28, 1.42)):
        kit.chamfered(name, (x, 0, 0), (length, 2.2, 2.1), p['cream'], hull, .42, BEVEL)
        roofPlates(p, hull, name, x, length)
    kit.prism('cab', [(3.02, .04), (4.88, .04), (4.88, 1.10), (3.02, 1.10)],
        -1.04, 1.04, p['cream'], hull, BEVEL)
    kit.prism('chin', [(3.02, -1.05), (4.95, -1.05), (6, -.55),
        (5.95, -.32), (4.88, -.04), (3.02, -.04)], -.98, .98, p['teal'], hull, BEVEL)
    block('cab seam backing', (3.95, 0, 0), (1.82, 1.9, .15), p['dark'], hull)
    block('keel', (.18, 0, -1.12), (6.32, 1.1, .14), p['dark'], hull)
    kit.barrel('probe', (6.1, 0, -.50), .045, .64, p['dark'], hull, sides=8, round_=BEVEL)
    for side in (-1, 1):
        sidePanels(p, hull, side)
        windows(p, hull, side)
    return hull


def roofPlates(p, hull, name, x, length):
    step = length / 2
    for index in (-.5, .5):
        kit.surfacePanel(name + ' roof panel', (x + index * step, 0, 0),
            (step - GAP, 1.25, .04), p['shade'], hull, '+z', 1.05, BEVEL)


def sidePanels(p, hull, side):
    facing = '+y' if side > 0 else '-y'
    for name, x, color, length in (('aft', -1.75, 'olive', 1.26), ('forward', 2.28, 'teal', 1.06)):
        kit.surfacePanel(name + ' service panel', (x, 0, -.32),
            (length, .035, .44), p[color], hull, facing, side * 1.1, BEVEL)
    kit.surfacePanel('chin band', (3.98, 0, -.23), (.9, .035, .12),
        p['mustard'], hull, facing, side * .98, BEVEL)
    for x, surface in ((-1.75, 1.1), (2.28, 1.1), (3.98, 1.04)):
        kit.surfacePanel('porthole row backing', (x, 0, .42),
            (.96, .035, .32), p['tealD'], hull, facing, side * surface, BEVEL)
    kit.lamp('nav port' if side > 0 else 'nav starboard', (3.09, side * 1.08, .82),
        (.09, .035, .05), facing, {**p, 'lamp': p['red' if side > 0 else 'green']}, hull)


def windows(p, hull, side):
    facing = '+y' if side > 0 else '-y'
    for row, z in enumerate((.30, .55)):
        group = kit.empty(f'porthole_{"port" if side > 0 else "starboard"}_{row + 1}', hull)
        for center, surface in ((-1.75, 1.1), (2.28, 1.1), (3.98, 1.04)):
            for index in range(6):
                x = center + (index - 2.5) * .15
                kit.surfacePanel('porthole pane', (x, 0, z), (.0694, .025, .0694),
                    p['lamp'], group, facing, side * (surface + .035 + .1 / SCALE), BEVEL)
        kit.consolidate(group)


def uniformBevel(root):
    for obj in root.children_recursive:
        for modifier in obj.modifiers:
            if modifier.type == 'BEVEL':
                modifier.width = BEVEL
                modifier.segments = 2


def bakeMetres(root):
    for obj in root.children_recursive:
        if obj.type == 'MESH':
            for modifier in list(obj.modifiers):
                with bpy.context.temp_override(object=obj, active_object=obj):
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
            obj.data.transform(Matrix.Scale(SCALE, 4))
        obj.location *= SCALE
        obj.matrix_parent_inverse.translation *= SCALE
        if 'radius' in obj:
            obj['radius'] *= SCALE
    root['units'], root['metres_per_unit'], root['surface_clearance'] = 'metres', 1, .1
    bpy.context.view_layer.update()


def bounds(root):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(c) for obj in root.children_recursive
        if obj.type == 'MESH' for c in obj.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def validateHull(root, fleet):
    extent = bounds(root)
    if not 69 <= extent[0][1] - extent[0][0] <= 71:
        raise ValueError('the bare hull must measure about 70 metres')
    for slot, at in fleet['FAR_SOCKETS'].items():
        obj = next(o for o in root.children if o.name == 'socket_' + slot)
        if (obj.location - Vector(at) * SCALE).length > .00001:
            raise ValueError('a socket position changed')
        if obj['slot'] != slot or obj['family'] != slot.rstrip('1'):
            raise ValueError('a socket contract changed')
    surfacecheck.validate(root)
    return extent


def preserveOriginal():
    folder = ASSETS / 'exports/painted'
    backup = folder / 'far-treasure-a.glb'
    if not backup.exists():
        shutil.copy2(folder / 'far-treasure.glb', backup)
    source = ASSETS / 'blender/painted'
    if not (source / 'far-treasure-a.blend').exists():
        shutil.copy2(source / 'far-treasure.blend', source / 'far-treasure-a.blend')


def moduleBuilds(fleet, exports, source):
    records = []
    for name, (slot, make) in fleet['MODULES'].items():
        kit.reset()
        root, p = kit.empty(name.replace('.', '_')), kit.palette()
        root['module'], root['slot'], root['family'] = name, slot, slot.rstrip('1')
        root['planned'] = name in fleet['PLANNED']
        make(p, root)
        uniformBevel(root)
        bakeMetres(root)
        extent = bounds(root)
        if any(not math.isfinite(v) for axis in extent for v in axis):
            raise ValueError('a module has invalid bounds')
        stem = name.replace('.', '-')
        bpy.ops.wm.save_as_mainfile(filepath=str(source / 'modules' / (stem + '.blend')))
        kit.consolidate_all(root)
        kit.export(root, exports / 'modules' / (stem + '.glb'))
        records.append({'name': name, 'slot': slot, 'bounds': extent, 'triangles': kit.stats(root)})
    return records


def build():
    compare = comparison()
    fleet = compare.fleetParts()
    source = ASSETS / 'blender/painted'
    exports = ASSETS / 'exports/painted'
    renders = ASSETS / 'blender/renders/painted'
    for folder in (source / 'modules', exports / 'modules', renders):
        folder.mkdir(parents=True, exist_ok=True)
    preserveOriginal()
    # stage all exports until the hull and every module build succeed.
    stage = ASSETS / 'blender/staging/sh1'
    (stage / 'modules').mkdir(parents=True, exist_ok=True)
    modules = moduleBuilds(fleet, stage, source)
    kit.reset()
    p, root = kit.palette(), kit.empty('far_treasure')
    root['category'], root['forward_axis'], root['export_up_axis'] = 'painted', '+x', '+y'
    root['revision'] = 'sh1'
    hull = shell(p, root)
    compare.gunnerNose(p, hull)
    hoops = [obj for obj in hull.children if obj.name.startswith('capsule hoop frame')]
    hoops[-1].location.x += .04
    for slot, at in fleet['FAR_SOCKETS'].items():
        kit.socket(root, slot, slot.rstrip('1'), at)
    uniformBevel(root)
    bakeMetres(root)
    extent = validateHull(root, fleet)
    bpy.ops.wm.save_as_mainfile(filepath=str(stage / 'far-treasure.blend'))
    kit.KEEP += ('porthole',)
    kit.consolidate_all(root)
    kit.export(root, stage / 'far-treasure.glb')
    info = {'revision': 'sh1', 'units': 'metres', 'bounds': extent,
        'triangles': kit.stats(root), 'modules': modules, 'bevel': BEVEL * SCALE, 'panel_gap': GAP * SCALE}
    (stage / 'far-treasure-metres.json').write_text(json.dumps(info, indent=4) + '\n')
    for slot, name in fleet['STARTER'].items():
        sock = next(o for o in root.children if o.name == 'socket_' + slot)
        group = kit.empty('preview module ' + name, root)
        fleet['MODULES'][name][1](p, group)
        uniformBevel(group)
        bakeMetres(group)
        group.location = sock.location
    root.scale = (1 / SCALE,) * 3
    kit.toonify(14)
    kit.render(root, 'far-treasure-metres', 14, renders)
    shutil.copy2(stage / 'far-treasure.blend', source / 'far-treasure.blend')
    shutil.copy2(stage / 'far-treasure-metres.json', source / 'far-treasure-metres.json')
    for path in stage.rglob('*.glb'):
        shutil.copy2(path, exports / path.relative_to(stage))


if __name__ == '__main__':
    build()
