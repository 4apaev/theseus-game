"""add work equipment to the clear service areas of each station."""

import math
import random

import bmesh
import bpy
from mathutils import Vector
import paintkit as kit


def box(name, at, size, color, root):
    return kit.block(name, at, size, color, root, .05, 1)


def bar(name, a, b, radius, color, root):
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    obj = kit.barrel(name, (a + b) / 2, radius, (b - a).length, color, root, 'Z', sides=6)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj


def cases(p, root, rng):
    for i in range(5):
        x, y = (i % 3 - 1) * 4.5 + rng.uniform(-.3, .3), (i // 3 * 2 - 1) * 2.5
        group = kit.empty('secured case bundle', root, (x, y, 0))
        group.rotation_euler.z = rng.uniform(-.7, .7)
        obj = box('strapped work case', (0, 0, .75), (1.8, 1.4, 1.4),
            p[rng.choice(('rust', 'olive', 'teal', 'mustard'))], group)
        if i == 0:
            obj.rotation_euler.x = .35
            obj.location.z = 1
        if i == 1:
            box('stacked case', (0, 0, 2.15), (1.8, 1.4, 1.4), p['cream'], group)
        height = 2.9 if i == 1 else 1.8
        for side in (-.55, .55):
            kit.pipe('case restraint', [(side, -1, .08), (side, -.75, height),
                (side, .75, height), (side, 1, .08)], .035, p['mustard'], group)


def drums(p, root, rng):
    for i in range(4):
        x, y = i * 1.4 - 2, rng.uniform(-1, 1)
        kit.barrel('service drum', (x, y, 1), .55, 1.8, p['rust' if i % 2 else 'olive'], root, 'Z', sides=10)
        for z in (.25, 1.7):
            kit.ring('drum band', (x, y, z), .56, .045, p['cream'], root, 'Z')
        kit.pipe('drum tie', [(x - .7, y, .05), (x, y, 2), (x + .7, y, .05)], .035, p['mustard'], root)


def plates(p, root, rng):
    for i in range(5):
        obj = box('spare hull plate', (0, 0, .16 + i * .2), (6, 3.6, .15),
            p[('cream', 'rust', 'teal', 'olive', 'cream')[i]], root)
        obj.rotation_euler.z = rng.uniform(-.2, .2)
    for x in (-2, 2):
        kit.pipe('plate bundle strap', [(x, -2.8, .03), (x, -2.8, 1.45), (x, 2.8, 1.45),
            (x, 2.8, .03)], .045, p['mustard'], root)


def cart(p, root):
    box('tool cart tray', (0, 0, .9), (2.4, 1.4, .25), p['rust'], root)
    box('tool cart cabinet', (0, 0, .5), (2, 1.2, .7), p['teal'], root)
    for x in (-.8, .8):
        for y in (-.85, .85):
            kit.barrel('cart wheel', (x, y, .2), .18, .15, p['black'], root, 'Y', sides=8)
    kit.pipe('cart handle', [(1, -.5, .55), (1, -.5, 1.5), (1, .5, 1.5), (1, .5, .55)], .05, p['cream'], root)
    for i in range(4):
        box('loose tool', (-.7 + i * .4, 0, 1.1), (.15, .6, .12), p['mustard'], root)
    kit.pipe('cart tether', [(1, 0, .5), (2, 1, .25), (3, 1, .08)], .035, p['mustard'], root)


def hose(p, root, rng):
    points = [(i * .5 - 7, math.sin(i * .45) * 1.4, .18) for i in range(29)]
    kit.pipe('deck service hose', points, .11, p['mustard' if rng.random() < .5 else 'black'], root)
    coil = kit.empty('hose reel', root, (6, 2, .7))
    for i in range(4):
        kit.ring('coiled hose', (0, 0, i * .19), .75, .095, p['tealD'], coil, 'Z')
    box('hose coupling', (-7, 0, .2), (.5, .4, .4), p['cream'], root)


def tarp(p, root, rng):
    box('covered spare', (0, 0, 1), (4.2, 3.2, 2), p['tealD'], root)
    bm = bmesh.new()
    rows = []
    for y in (-2.1, -1.5, 0, 1.5, 2.1):
        rows.append([bm.verts.new((x, y, .35 if abs(y) > 2 else 2.25 + rng.uniform(-.15, .15)))
            for x in (-2.5, -1.2, 0, 1.2, 2.5)])
    for i in range(4):
        for j in range(4):
            bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    kit.link('patched cloth tarp', bm, p['olive'], root)
    for x in (-2, 2):
        kit.pipe('tarp tie', [(x, -2.6, .06), (x, -1.6, 2.4), (x, 1.6, 2.4),
            (x, 2.6, .06)], .035, p['mustard'], root)
    box('tarp repair patch', (.5, 0, 2.665), (.8, .9, .03), p['rust'], root)


def lamp(p, root, at, welding=False):
    stand = kit.empty('work lamp stand', root, at)
    for angle in (0, 2.1, 4.2):
        bar('lamp tripod', (0, 0, 1), (math.cos(angle) * .65, math.sin(angle) * .65, .04), .035, p['cream'], stand)
    bar('lamp post', (0, 0, .2), (0, 0, 2.6), .045, p['mustard'], stand)
    box('lamp housing', (0, 0, 2.6), (.7, .4, .55), p['tealD'], stand)
    box('beacon welding lamp' if welding else 'work lamp lens', (0, -.475, 2.6), (.55, .05, .4), p['lamp'], stand)


def scaffold(p, root, at):
    group = kit.empty('repair scaffold', root, at)
    for x in (-4, 4):
        for y in (-1, 1):
            bar('scaffold upright', (x, y, 0), (x, y, 7), .065, p['cream'], group)
    for z in (2, 4, 6):
        box('scaffold plank', (0, 0, z), (8.4, 2.4, .16), p['olive'], group)
        bar('scaffold guard', (-4, -1, z + 1.1), (4, -1, z + 1.1), .045, p['mustard'], group)
        bar('scaffold cross brace', (-4, 1, z - 2), (4, 1, z), .045, p['cream'], group)
    for x in (3.2, 3.9):
        bar('ladder stile', (x, -1.3, 0), (x, -1.3, 6.2), .045, p['mustard'], group)
    for i in range(19):
        bar('ladder rung', (3.2, -1.3, i * .32), (3.9, -1.3, i * .32), .035, p['cream'], group)


def hullRepair(p, root):
    for x in (-6, 6):
        box('hull cradle skid', (x, 0, .5), (2, 13, .9), p['tealD'], root)
        for y in (-4, 4):
            bar('cradle support', (x, y, .9), (x, y * .65, 3), .25, p['cream'], root)
    for x in (-8, -4, 0, 4, 8):
        for i in range(8):
            a, b = i * math.pi / 8, (i + 1) * math.pi / 8
            bar('open hull rib', (x, 4 * math.cos(a), 3 + 4 * math.sin(a)),
                (x, 4 * math.cos(b), 3 + 4 * math.sin(b)), .13, p['cream'], root)
    for y in (-4, 4):
        bar('hull stringer', (-8, y, 3), (8, y, 3), .12, p['teal'], root)
    for x in (-6, -2):
        obj = box('unfinished hull skin', (x, 2.9, 5.2), (3.7, .2, 3.5), p['rust' if x == -6 else 'teal'], root)
        obj.rotation_euler.x = .55
    scaffold(p, root, (0, -6, 0))
    lamp(p, root, (-7, -4, 0), True)
    lamp(p, root, (7, 4, 0), True)


def specialty(p, root, name, rng):
    if name == 'yards':
        hullRepair(p, root)
    elif name in ('outpost', 'hub', 'gate'):
        cases(p, root, rng)
        if name == 'gate':
            box('inspection cage base', (0, 5, .15), (5, 3, .3), p['teal'], root)
            for x in (-2.4, 0, 2.4):
                bar('inspection cage rail', (x, 3.5, .3), (x, 3.5, 3.8), .07, p['mustard'], root)
            box('seal scanner', (3, 5, 1.4), (1, 1, 2.7), p['cream'], root)
    elif name in ('gas', 'dock'):
        hose(p, root, rng)
        for x in (-3, 0, 3):
            kit.barrel('spare pressure bottle', (x, 3, 1.8), .65, 3.2, p['cream'], root, 'Z', sides=10)
            kit.ring('valve wheel', (x, 3, 3.6), .4, .065, p['rust'], root, 'Z')
    elif name == 'mine':
        plates(p, root, rng)
        for i in range(7):
            kit.chamfered('ore sample', ((i % 4 - 1.5) * 2.2, 3 + (i // 4) * 2.2, .65),
                (1.2, 1, 1.2), p['rust' if i % 2 else 'shade'], root, .3, .04)
    elif name == 'lab':
        box('sample containment tray', (0, 0, .15), (7, 5, .3), p['tealD'], root)
        for x in (-2, 0, 2):
            for y in (-1, 1):
                kit.barrel('sample canister', (x, y, .9), .5, 1.4, p['cream'], root, 'Z', sides=8)
                kit.ring('sample seal', (x, y, 1.55), .5, .06, p['mustard'], root, 'Z')
        hose(p, root, rng)
    else:
        for x in (-3, 0, 3):
            kit.antenna('spare antenna cluster', (x, 0, 0), rng.uniform(4, 7), p, root)
        box('personal locker', (5, 2, 1.5), (2, 2, 3), p['rust'], root)
        kit.pipe('tethered lunch case', [(5, 2, 2), (7, 2, 3), (7.5, 3, 4)], .035, p['mustard'], root)
        box('lunch case', (7.5, 3, 4), (.8, .6, .6), p['olive'], root)


def wear(p, root, rng, extent=9):
    bpy.context.view_layer.update()
    inverse = root.matrix_world.inverted()
    bounds = []
    for obj in root.children_recursive:
        if obj.type != 'MESH':
            continue
        points = [inverse @ obj.matrix_world @ Vector(c) for c in obj.bound_box]
        bounds.append([(min(v[i] for v in points), max(v[i] for v in points)) for i in (0, 1)])
    count = 0
    for attempt in range(120):
        x, y = rng.uniform(-extent, extent), rng.uniform(-extent, extent)
        w, d = rng.uniform(1, 3), rng.uniform(.4, 1.4)
        radius = math.hypot(w, d) / 2 + .3
        if any(x + radius > a and x - radius < b and y + radius > c and y - radius < e
                for ((a, b), (c, e)) in bounds):
            continue
        obj = box('raised deck repair' if count % 2 else 'scorch mark', (x, y, .2675),
            (w, d, .035), p['rust' if count % 2 else 'black'], root)
        obj.rotation_euler.z = rng.uniform(-math.pi, math.pi)
        bounds.append([(x - radius, x + radius), (y - radius, y + radius)])
        count += 1
        if count == 5:
            break


def populate(p, root, name, places):
    rng = random.Random(310 + sum(map(ord, name)))
    for i, (x, y, large) in enumerate(places):
        group = kit.empty('crew work area', root, (x, y, .65))
        group.rotation_euler.z = rng.uniform(-.18, .18)
        group['work_area_size'] = [28, 32] if large else [16, 18]
        if not large:
            compact(p, group, rng, i)
            continue
        if name == 'yards' and i > 0:
            plates(p, group, rng)
        else:
            specialty(p, group, name, rng)
        service = kit.empty('service supplies', group, (0, -11, 0))
        (drums if i % 2 else plates)(p, service, rng)
        cart(p, kit.empty('tool cart', group, (8, -9, 0)))
        if i % 2 == 0 and name not in ('gas', 'dock', 'lab', 'yards'):
            hose(p, kit.empty('service cable', group, (0, -6, 0)), rng)
        lamp(p, group, (-8, -7, 0))
        if i % 3 == 0:
            tarp(p, kit.empty('covered equipment', group, (-5, 10, 0)), rng)
        if i % 3 == 1:
            kit.pipe('spare part tether', [(6, 6, .08), (8, 5, 2), (9, 6, 4)], .035, p['mustard'], group)
            spare = box('tethered spare fitting', (9, 6, 4), (1.2, .7, .8), p['teal'], group)
            spare.rotation_euler.y = .4
        if name != 'yards' and i % 4 == 0:
            scaffold(p, group, (0, 7, 0))
        wear(p, group, rng)


def compact(p, root, rng, index):
    (drums, plates, tarp)[index % 3](p, root, rng)
    if index % 2:
        cart(p, kit.empty('tool cart', root, (2, -4, 0)))
    else:
        lamp(p, root, (-4, -5, 0))
    wear(p, root, rng, 4)
