"""build station models from the painted kits."""

import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

import paintkit as kit


def box(name, at, size, color, root):
    return kit.block(name, at, size, color, root, .18, 2)


def beam(name, a, b, radius, color, root):
    a, b = Vector(a), Vector(b)
    obj = kit.barrel(name, (a + b) / 2, radius, (b - a).length, color, root, 'Z', sides=8)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj


def deck(p, root, width=60, depth=48):
    group = kit.empty('deck', root)
    box('deck core', (0, 0, -2), (width, depth, 4), p['tealD'], group)
    box('walking surface', (0, 0, -.18), (width - 2, depth - 2, .36), p['dark'], group)
    for x in range(-int(width / 2) + 4, int(width / 2), 8):
        for sign in (-1, 1):
            box('cream edge panel', (x, sign * (depth / 2 - .5), -1), (7.5, 1.8, 3.2), p['cream'], group)
            box('panel inset', (x, sign * (depth / 2 + .42), -1.3), (4.8, .18, 1.2), p['teal'], group)
    for y in range(-int(depth / 2) + 4, int(depth / 2), 8):
        for sign in (-1, 1):
            box('end edge panel', (sign * (width / 2 - .5), y, -1), (1.8, 7.5, 3.2), p['cream'], group)
    for x in (-width / 2 + 1, width / 2 - 1):
        for y in (-depth / 2 + 1, depth / 2 - 1):
            box('corner cap', (x, y, 0), (3, 3, 2), p['cream'], group)
            box('nav deck lamp', (x, y, 1.1), (1.1, 1.1, .3), p['lamp'], group)
    for x in range(-int(width / 2) + 8, int(width / 2), 8):
        box('deck seam', (x, 0, .015), (.055, depth - 4, .025), p['black'], group)
    for sign in (-1, 1):
        kit.pipe('edge service pipe', [(-width / 2 + 3, sign * (depth / 2 + .5), -2),
            (width / 2 - 3, sign * (depth / 2 + .5), -2)], .28, p['mustard'], group)
    return group


def berth(p, root, edge=30):
    group = kit.empty('rig', root)
    box('berth bridge', (edge + 4, -8, -1), (10, 9, 2), p['teal'], group)
    pad = (edge + 15, -8, -.8)
    kit.barrel('octagonal berth', pad, 12, 1.6, p['tealD'], group, 'Z', sides=8, round_=.2)
    kit.barrel('pad surface', (pad[0], pad[1], .04), 11.3, .12, p['dark'], group, 'Z', sides=8)
    kit.ring('pad target', (pad[0], pad[1], .13), 4.5, .09, p['mustard'], group, 'Z')
    for i in range(8):
        a = i * math.tau / 8
        x, y = pad[0] + 11 * math.cos(a), pad[1] + 11 * math.sin(a)
        cap = box('berth edge', (x, y, .05), (7.4, 1.2, 1), p['cream'], group)
        cap.rotation_euler.z = a + math.pi / 2
        box('nav berth lamp', (x, y, .7), (.5, .5, .3), p['lamp'], group)
    kit.empty('berth', root, (pad[0], pad[1], .2))['forward'] = '+x'
    points = [(pad[0], pad[1], .2), (edge + 2, -8, .2), (edge - 5, -8, .2), (0, -8, .2), (-18, -8, .2)]
    for name, point in zip(('walk_a', 'walk_b', 'walk_c', 'walk_d', 'walk_e'), points):
        kit.empty(name, root, point)


def hall(p, root, name, at, size=(18, 12, 10)):
    group = kit.empty(name, root, at)
    w, d, h = size
    kit.chamfered('pressure hull', (0, 0, h / 2), size, p['teal'], group, 1, .18)
    for x in (-w / 2 + .7, w / 2 - .7):
        box('cream portal frame', (x, 0, h / 2), (1.4, d + .5, h + .4), p['cream'], group)
    box('roof plate', (0, 0, h + .1), (w - 2, d - 2, .6), p['cream'], group)
    box('entry recess', (0, -d / 2 - .1, 3), (5.5, .35, 6), p['black'], group)
    box('entry hatch', (0, -d / 2 - .35, 3), (4.5, .4, 5.4), p['tealD'], group)
    box('entry light', (0, -d / 2 - .6, 5), (2.8, .2, .3), p['lamp'], group)
    for x in (-w / 3, w / 3):
        kit.vent('wall vent', (x, -d / 2 - .25, 5.4), (2.5, .3, 3), '-y', p, group, 5)
        kit.pipe('service riser', [(x, d / 2 + .4, 1), (x, d / 2 + .4, h - 1),
            (x, d / 2 - 1, h + .6)], .25, p['mustard'], group)
    return group


def cargo(p, root, at, rows=2, cols=3):
    group = kit.empty('container stack', root, at)
    colors = ['teal', 'olive', 'rust', 'mustard']
    for row in range(rows):
        for col in range(cols - row):
            x, z = col * 4.3, 1.6 + row * 3.3
            box('shipping case', (x, 0, z), (4, 6.5, 3), p[colors[(row + col) % 4]], group)
            for sign in (-1, 1):
                box('cream case frame', (x, sign * 3.25, z), (4.1, .3, 3.1), p['cream'], group)
                box('case door', (x, sign * 3.43, z), (3.3, .12, 2.3), p['tealD'], group)
    return group


def mast(p, root, name, at, height):
    group = kit.empty(name, root, at)
    box('mast base', (0, 0, 1.5), (5, 5, 3), p['teal'], group)
    for x in (-1.3, 1.3):
        for y in (-1.3, 1.3):
            beam('mast leg', (x, y, 2), (x * .45, y * .45, height), .22, p['cream'], group)
    for z in range(4, int(height), 4):
        for y in (-1, 1):
            beam('mast brace', (-1.2, y, z), (1.2, y, z + 3), .13, p['mustard'], group)
    kit.barrel('beacon mast lamp', (0, 0, height + 1), .6, 1.8, p['lamp'], group, 'Z')
    return group


def dish(p, root, at, radius=4):
    group = kit.empty('spin relay dish', root, at)
    group['spin'] = True
    group.rotation_euler.y = math.radians(28)
    bm = bmesh.new()
    center = bm.verts.new((0, 0, 0))
    rings = []
    for r in (radius / 3, radius * 2 / 3, radius):
        rings.append([bm.verts.new((r * math.cos(i * math.tau / 24), r * math.sin(i * math.tau / 24), r * r / (radius * 3))) for i in range(24)])
    for i in range(24):
        j = (i + 1) % 24
        bm.faces.new((center, rings[0][i], rings[0][j]))
        for k in range(2):
            bm.faces.new((rings[k][i], rings[k + 1][i], rings[k + 1][j], rings[k][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    kit.link('dish bowl', bm, p['cream'], group)
    kit.ring('dish rim', (0, 0, radius / 3), radius, .18, p['teal'], group, 'Z')
    for i in range(3):
        a = i * math.tau / 3
        beam('feed strut', (radius * math.cos(a), radius * math.sin(a), radius / 3), (0, 0, radius * .8), .12, p['dark'], group)
    kit.barrel('dish receiver', (0, 0, radius * .8), .3, .7, p['mustard'], group, 'Z')
    return group


def tanks(p, root, at, count=2, length=16, radius=3):
    group = kit.empty('tank farm', root, at)
    for i in range(count):
        y = i * (radius * 2 + 1.5)
        box('tank skid', (0, y, .8), (length + 2, radius * 2 + 1, 1.6), p['tealD'], group)
        kit.barrel('insulated tank', (0, y, radius + 1.7), radius, length, p['cream'], group, 'X', round_=.3)
        for x in (-length / 2, length / 2):
            kit.barrel('tank end', (x, y, radius + 1.7), radius * .9, .5, p['teal'], group)
        for x in (-length / 3, length / 3):
            kit.ring('tank band', (x, y, radius + 1.7), radius, .18, p['shade'], group)
        kit.pipe('tank feed', [(length / 2 + .5, y, radius + 1.7), (length / 2 + 1.2, y, radius + 1.7),
            (length / 2 + 1.2, y, .6)], .25, p['mustard'], group)


def crane(p, root, at, span=24, height=22):
    group = kit.empty('gantry crane', root, at)
    for x in (-span / 2, span / 2):
        box('crane runner', (x, 0, .7), (4, 13, 1.4), p['teal'], group)
        box('cream crane leg', (x, 0, height / 2), (2.2, 3, height), p['cream'], group)
        beam('leg brace', (x, -5, 1), (x, 0, height * .65), .4, p['mustard'], group)
    box('teal crossbeam', (0, 0, height), (span + 4, 4, 3), p['teal'], group)
    box('hoist trolley', (0, -.5, height - 2), (5, 5, 2), p['mustard'], group)
    beam('hoist cable', (0, -.5, height - 3), (0, -.5, height / 2), .1, p['dark'], group)
    kit.pipe('empty hook', [(0, -.5, height / 2), (0, -.5, height / 2 - 2),
        (1, -.5, height / 2 - 2), (1, -.5, height / 2 - 1)], .25, p['mustard'], group)


def cradle(p, root, at):
    group = kit.empty('hull cradle', root, at)
    for y in (-4, 4):
        box('cradle rail', (0, y, .4), (18, 1, .8), p['tealD'], group)
    for x in (-5, 5):
        box('saddle base', (x, 0, 1.2), (2, 11, 1.6), p['cream'], group)
        for sign in (-1, 1):
            arm = box('saddle support', (x, sign * 4, 2.8), (2, 2, 4), p['teal'], group)
            arm.rotation_euler.x = sign * math.radians(25)
            box('saddle pad', (x, sign * 3.1, 4), (2.4, 2, .6), p['dark'], group)


def rack(p, root, at):
    group = kit.empty('module rack', root, at)
    for x in (-6, 6):
        box('rack upright', (x, 0, 5), (1, 6, 10), p['cream'], group)
    for z in (1, 5, 9):
        box('rack shelf', (0, 0, z), (13, 6, .6), p['mustard'], group)
        for x in (-3.5, 3.5):
            kit.barrel('stored drive module', (x, 0, z + 1.8), 1.3, 4, p['teal'], group, 'Y')


def arc(p, root, name, at, radius, start, end, vertical=False):
    group = kit.empty(name, root, at)
    count = max(6, round((end - start) / 12))
    for i in range(count):
        angle = math.radians(start + (end - start) * (i + .5) / count)
        length = radius * math.radians((end - start) / count) * 1.02
        if vertical:
            center = (radius * math.cos(angle), 0, radius * math.sin(angle))
            body = box('ring shell', center, (length, 4, 4), p['cream'], group)
            body.rotation_euler.y = math.pi / 2 - angle
            trim = box('ring inset', (center[0], -2.1, center[2]), (length * .8, .4, 2.5), p['teal'], group)
            trim.rotation_euler.y = body.rotation_euler.y
        else:
            center = (radius * math.cos(angle), radius * math.sin(angle), 3)
            body = box('habitat shell', center, (length, 5, 6), p['cream'], group)
            body.rotation_euler.z = angle + math.pi / 2
            trim = box('window band', (center[0], center[1], 4), (length * .85, 5.1, 1.1), p['teal'], group)
            trim.rotation_euler.z = body.rotation_euler.z
    return group


def outpost(p, root):
    hall(p, root, 'market', (-17, 14, 0))
    hall(p, root, 'comms', (6, 15, 0), (14, 12, 10))
    dish(p, root, (6, 15, 12), 4)
    kit.antenna('comms mast', (12, 18, 10), 8, p, root)
    cargo(p, root, (-19, -17, 0), 2, 2)
    box('pad bridge', (-1, -4, .04), (16, .3, .05), p['mustard'], root)


def yards(p, root):
    crane(p, root, (-14, 10, 0), 24, 24)
    cradle(p, root, (-14, 10, 0))
    rack(p, root, (17, 16, 0))
    hall(p, root, 'comms', (18, -17, 0), (14, 9, 7))


def hub(p, root):
    group = hall(p, root, 'market', (-9, 15, 0), (30, 13, 10))
    for x in (-10, 0, 10):
        box('service bay', (x, -6.9, 3.5), (7, .4, 6), p['black'], group)
        box('service counter', (x, -8, 1.5), (6, 2, 3), p['mustard'], group)
        box('bay lamp', (x, -7.2, 7), (5, .2, .3), p['lamp'], group)
    cargo(p, root, (-22, -17, 0), 3, 3)
    lift = kit.empty('cargo lift', root, (19, 15, 0))
    box('lift deck', (0, 0, 1), (12, 10, 2), p['teal'], lift)
    for x in (-5, 5):
        box('lift rail', (x, 3, 10), (1.5, 2, 20), p['cream'], lift)
    box('lift crossbar', (0, 3, 20), (12, 2, 2), p['mustard'], lift)


def lab(p, root):
    group = kit.empty('dome lab', root, (-14, 12, 0))
    kit.barrel('lab base', (0, 0, 3), 9, 6, p['cream'], group, 'Z')
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=8)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.001], context='VERTS')
    kit.link('teal dome', bm, p['teal'], group, at=(0, 0, 6))
    kit.ring('dome collar', (0, 0, 6), 8.1, .35, p['mustard'], group, 'Z')
    box('lab hatch', (0, -9, 2.5), (4, .5, 5), p['tealD'], group)
    tanks(p, root, (12, 11, 0), 2, 15, 2.5)
    mast(p, root, 'antenna array', (-18, -17, 0), 17)
    for x in (-22, -14):
        kit.antenna('array antenna', (x, -17, 0), 11, p, root)


def gate(p, root):
    arc(p, root, 'gate ring segment', (-15, 17, 0), 18, 15, 165, True)
    for x in (-32, 2):
        box('gate foundation', (x, 17, 2), (7, 8, 4), p['tealD'], root)
    mast(p, root, 'beacon tower', (20, 16, 0), 26)
    hall(p, root, 'customs booth', (-17, -18, 0), (16, 10, 7))


def dock(p, root):
    group = kit.empty('dry dock arm', root, (-17, 13, 0))
    box('dock arm base', (0, 0, 2), (14, 12, 4), p['teal'], group)
    box('dock support', (0, 0, 10), (5, 6, 16), p['cream'], group)
    box('dock cross arm', (8, 0, 18), (22, 5, 4), p['cream'], group)
    box('dock jaw', (17, 0, 14), (5, 8, 6), p['tealD'], group)
    kit.pipe('arm hydraulic', [(0, -3.5, 4), (0, -3.5, 17), (16, -3.5, 17)], .4, p['mustard'], group)
    hall(p, root, 'warehouse', (14, 15, 0), (22, 13, 11))
    fuel = mast(p, root, 'fuel mast', (-18, -17, 0), 16)
    kit.pipe('fuel hose', [(0, 0, 14), (4, 0, 14), (6, 0, 11), (6, 0, 4)], .45, p['mustard'], fuel)


def gas(p, root):
    tanks(p, root, (-14, 13, 0), 2, 20, 3)
    arc(p, root, 'habitat ring segment', (13, 10, 0), 12, -30, 160)
    group = kit.empty('skimmer', root, (-16, -17, 0))
    kit.chamfered('skimmer hull', (0, 0, 3), (20, 7, 5), p['cream'], group, 1, .2)
    kit.barrel('intake', (11, 0, 3), 3.5, 3, p['teal'], group)
    kit.barrel('intake throat', (12.6, 0, 3), 2.8, .1, p['black'], group)
    for y in (-5, 5):
        box('skimmer outrigger', (0, y, 1.5), (15, 2, 2), p['mustard'], group)


def mine(p, root):
    crusher = kit.empty('ore crusher', root, (-16, 12, 0))
    box('crusher frame', (0, 0, 4), (16, 12, 8), p['cream'], crusher)
    kit.barrel('hopper', (0, 0, 11), 6, 6, p['teal'], crusher, 'Z', top=8, sides=8)
    for x in (-4, 4):
        kit.barrel('crusher roller', (x, -6.5, 4), 2, 1, p['rust'], crusher, 'Y')
    shield = kit.empty('sun shield', root, (15, 17, 0))
    for x in (-8, 8):
        beam('shield support', (x, 0, 0), (x, 0, 13), .6, p['teal'], shield)
    plates = kit.empty('shield plates', shield, (0, 0, 15))
    plates.rotation_euler.x = math.radians(-28)
    box('shield back', (0, .3, 3), (25, 1, 16), p['rust'], plates)
    for x in (-8, 0, 8):
        for z in (-2, 3, 8):
            box('ceramic tile', (x, -.5, z), (7.7, 1, 4.7), p['cream'], plates)
    conveyor = kit.empty('conveyor', root, (-7, -18, 0))
    box('conveyor frame', (0, 0, 1.3), (30, 7, 2.6), p['teal'], conveyor)
    box('empty belt', (0, 0, 2.7), (29, 5, .3), p['black'], conveyor)
    for x in range(-12, 13, 4):
        kit.barrel('conveyor roller', (x, 0, 2.5), .55, 6, p['mustard'], conveyor, 'Y')


def relay(p, root):
    mast(p, root, 'relay mast', (-19, 15, 0), 28)
    dish(p, root, (-19, 15, 28), 4)
    tower = kit.empty('watch tower', root, (4, 16, 0))
    for x in (-4, 4):
        for y in (-4, 4):
            beam('tower leg', (x, y, 0), (x * .8, y * .8, 13), .65, p['cream'], tower)
    box('observation cabin', (0, 0, 15), (11, 11, 5), p['teal'], tower)
    box('window band', (0, 0, 15.5), (11.1, 11.1, 1.5), p['glass'], tower)
    box('cabin roof', (0, 0, 18), (12, 12, 1), p['cream'], tower)
    box('beacon watch lamp', (0, 0, 19), (1, 1, 1), p['lamp'], tower)
    hab = kit.empty('hab can', root, (20, 13, 0))
    kit.barrel('hab shell', (0, 0, 4), 4, 16, p['cream'], hab, 'Y', round_=.3)
    for y in (-8, 8):
        kit.barrel('hab end cap', (0, y, 4), 3.8, .5, p['olive'], hab, 'Y')
    box('hab hatch', (0, -8.4, 3.2), (3, .5, 5), p['teal'], hab)


BUILDERS = {name: fn for name, fn in (
    ('outpost', outpost), ('yards', yards), ('hub', hub), ('lab', lab),
    ('gate', gate), ('dock', dock), ('gas', gas), ('mine', mine), ('relay', relay))}


def preview(root, name, folder, size):
    kit.toonify(size)
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x, scene.render.resolution_y = 1536, 1024
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.04, .06, .1, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .5
    camera = bpy.data.objects.new('preview camera', bpy.data.cameras.new('preview camera'))
    scene.collection.objects.link(camera)
    camera.data.type, camera.data.ortho_scale = 'ORTHO', size
    scene.camera = camera
    for suffix, azimuth in (('preview', 42), ('reverse', 222)):
        previewView(camera, root, azimuth, scene, folder / f'{name}-{suffix}.png')


def previewView(camera, root, azimuth, scene, path):
    a, e = math.radians(azimuth), math.radians(29)
    direction = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
    center = Vector((0, 0, 0))
    camera.location = center + direction * 180
    camera.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    right = (-direction).cross(Vector((0, 0, 1))).normalized()
    up = right.cross(-direction)
    lights = []
    for name, ray, energy, color in (
        ('warm key', -right * .55 + up * .7 + direction * .45, 3.2, (1, .93, .82)),
        ('cool rim', right * .7 + up * .2 - direction * .2, 1.1, (.6, .75, 1))):
        data = bpy.data.lights.new(name, 'SUN')
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        data.energy, data.color = energy, color
        obj.rotation_euler = ray.normalized().to_track_quat('Z', 'Y').to_euler()
        lights.append(obj)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    for light in lights:
        bpy.data.objects.remove(light, do_unlink=True)


def build(name):
    assets = Path(__file__).resolve().parents[2]
    source = assets / 'blender/stations/painted' / name
    exports = assets / 'exports/painted/stations'
    renders = assets / 'blender/renders/stations' / name
    for folder in (source, exports, renders):
        folder.mkdir(parents=True, exist_ok=True)
    kit.reset()
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1
    root = kit.empty(name)
    root['units'], root['export_up_axis'] = 'metres', '+y'
    root['kit'] = f'assets/stations/{name}/kit.json'
    p = kit.palette()
    deck(p, root, 68 if name == 'gate' else 60)
    berth(p, root, 34 if name == 'gate' else 30)
    BUILDERS[name](p, root)
    centerOrigin(root)
    validate(root)
    bpy.ops.wm.save_as_mainfile(filepath=str(source / f'{name}.blend'))
    kit.consolidate_all(root)
    kit.export(root, exports / f'{name}.glb')
    info = {'kit': name, 'triangles': kit.stats(root), 'bytes': (exports / f'{name}.glb').stat().st_size,
        'source': f'assets/blender/stations/painted/{name}/{name}.blend',
        'export': f'assets/exports/painted/stations/{name}.glb',
        'berth': [next(child for child in root.children if child.name == 'berth').location[i] for i in range(3)],
        'coordinates': 'source z up; glb y up; berth bow +x', 'camera': {'azimuth': 42, 'elevation': 29}}
    (source / 'manifest.json').write_text(json.dumps(info, indent=4) + '\n')
    preview(root, name, renders, 120)


def centerOrigin(root):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(c) for obj in root.children_recursive if obj.type == 'MESH' for c in obj.bound_box]
    center = Vector([(min(p[i] for p in points) + max(p[i] for p in points)) / 2 for i in range(3)])
    for child in root.children:
        child.location -= center
    root['source_center_offset'] = list(center)


def validate(root):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(c) for obj in root.children_recursive if obj.type == 'MESH' for c in obj.bound_box]
    span = max(max(p[i] for p in points) - min(p[i] for p in points) for i in range(3))
    if not 60 <= span <= 150:
        raise ValueError(f'station span {span} is outside 60 to 150 metres')
    markers = {obj.name for obj in root.children_recursive if obj.type == 'EMPTY'}
    if not {'berth', 'walk_a', 'walk_b', 'walk_c', 'walk_d', 'walk_e'} <= markers:
        raise ValueError('station markers are missing')
    if any(abs(angle) > .001 for angle in next(child for child in root.children if child.name == 'berth').rotation_euler):
        raise ValueError('the berth bow does not point along +x')
