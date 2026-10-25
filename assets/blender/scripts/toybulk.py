"""build liquid, container and ore freighters."""

import math

import bmesh

import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic
import toytowing


def valve(root, p, at):
    x, y, z = at
    traffic.drum('valve stem', at, .6, 4, p['milk'], root, 'Z')
    kit.ring('valve wheel', (x, y, z + 2.5), 2.5, .45, p['butter'], root, 'Z')
    for angle in (0, math.pi / 2):
        spoke = toy.box('valve spoke', (x, y, z + 2.5), (4.8, .6, .6), p['butter'], root)
        spoke.rotation_euler.z = angle


def liquidTanker(root, p):
    toy.box('tank service spine', (0, 0, 5), (110, 8, 6), p['red'], root)
    for i, y in enumerate((-18, 18)):
        traffic.drum('long pressure tank', (0, y, 0), 14, 96, p['green'], root)
        for x in (-32, 0, 32):
            kit.ring('tank retaining band', (x, y, 0), 14.1, .9, p['milk'], root)
            valve(root, p, (x, y, 16))
        for side in (-1, 1):
            kit.pipe('tank lower service pipe', [(-44, y + side * 13, -2),
                (-36, y + side * 16, -4), (38, y + side * 16, -4),
                (46, y + side * 13, -2)], .7, p['red'], root, corner=2, sides=10)
            for x in (-21, 21):
                traffic.window((x, y + side * 14.3, 2), 1.4, p, root, side)
        traffic.engine(root, p, (-58, y, 0), 16, 15, 'red', i)
    kit.pipe('front liquid manifold', [(46, -18, 0), (58, -18, 0),
        (61, 0, 0), (58, 18, 0), (46, 18, 0)], 4, p['red'], root, corner=7, sides=16)
    toy.box('liquid bridge hanger', (57, 0, -10), (5, 8, 17), p['butter'], root)
    toy.box('liquid bridge', (57, 0, -20), (12, 13, 12), p['milk'], root)
    for side in (-1, 1):
        traffic.window((57, side * 7, -19), 2.7, p, root, side)
    return ((-30, 0, 9), (-58, 0, 4), (40, 0, -8), (3, -33, 0), (28, 0, 9))


def containerShip(root, p):
    toy.box('container keel', (0, 0, -6), (110, 26, 11), p['milk'], root)
    for col, (x, count) in enumerate(((-30, 3), (2, 2), (34, 1))):
        for level in range(count):
            z = 8 + level * 17
            role = ('red', 'green', 'butter')[(col + level) % 3]
            case = toy.box('freight container', (x, 0, z), (28, 27, 15), p[role], root)
            detail.seam('container door seam', case, [(0, (x + 8,))], .3)
            for side in (-1, 1):
                for dx in (-11, 11):
                    for dz in (-5, 5):
                        toy.box('container corner lock', (x + dx, side * 14, z + dz),
                            (3, 2, 3), p['butter'], root)
                toy.box('container latch', (x + 8, side * 14, z), (1, 1, 7), p['green'], root)
    toy.box('high bridge mast', (-48, 0, 25), (8, 10, 66), p['milk'], root)
    toy.box('high bridge', (-46, 0, 61), (16, 17, 10), p['milk'], root)
    for side in (-1, 1):
        traffic.window((-46, side * 9, 62), 3, p, root, side)
        detail.pipe('container keel pipe', [(-47, side * 14, -8),
            (-39, side * 15, -2), (49, side * 15, -2)], .7, p, root)
    for i, y in enumerate((-14, 14)):
        traffic.engine(root, p, (-58, y, -5), 8, 14, 'green', i)
    return ((-48, -7, 45), (-55, 0, -5), (42, 0, -13), (8, -14.8, -6), (-46, 0, 68))


def bowl(root, p, x):
    mesh = bmesh.new()
    rings = []
    for radius, z in ((9, -8), (17, 0), (22, 15), (20.4, 15), (15.5, 1), (8, -6.5)):
        rings.append([mesh.verts.new((x + radius * math.cos(i * math.tau / 24),
            radius * math.sin(i * math.tau / 24), z)) for i in range(24)])
    for a, b in zip(rings, rings[1:] + rings[:1]):
        for i in range(24):
            mesh.faces.new((a[i], a[(i + 1) % 24], b[(i + 1) % 24], b[i]))
    bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    kit.link('open ore hopper', mesh, p['green'], root, (.3, 2))
    for y in (-17, 17):
        toy.box('hopper support', (x, y, -4), (5, 5, 20), p['red'], root)
    for i, at in enumerate(((x - 7, -5, 3), (x + 7, -3, 4), (x, 8, 5))):
        toytowing.rock('ore chunk', at, (8, 7, 8), p['butter'], root, int(x + i + 200))
    kit.pipe('hopper retaining bar', [(x, -22, 16), (x, 22, 16)], 1, p['milk'], root, sides=12)


def oreCarrier(root, p):
    toy.box('ore keel', (0, 0, -13), (132, 17, 7), p['red'], root)
    for x in (-43, 0, 43):
        bowl(root, p, x)
    toy.box('ore bridge', (68, 0, 0), (19, 24, 19), p['milk'], root)
    for side in (-1, 1):
        traffic.window((68, side * 12.6, 4), 2.4, p, root, side)
        detail.pipe('ore service line', [(-56, side * 12, -9), (-45, side * 13, -6),
            (65, side * 13, -6)], .8, p, root)
    for i, y in enumerate((-13, 13)):
        traffic.engine(root, p, (-66, y, -4), 10, 15, 'milk', i)
    return ((-43, 0, -18), (-66, 0, -12), (44, 0, -18), (0, -19, -7), (68, 0, 11))


builders = {'liquid-tanker': liquidTanker, 'container-ship': containerShip, 'ore-carrier': oreCarrier}


def build(name):
    kit.reset()
    root, p = kit.empty('toy_ship_' + name), toy.palette()
    points = builders[name](root, p)
    for family, at in zip(('power', 'cruise', 'maneuver', 'cargo', 'utility'), points):
        traffic.port(root, p, family, at)
    detail.finish(root)
    root['detail_revision'] = 3
    root['concept'] = 'assets/concepts/toy/ships/ship-' + name + '-meadow.webp'
    toy.save(root, 'ship-' + name, 40000, 230)
