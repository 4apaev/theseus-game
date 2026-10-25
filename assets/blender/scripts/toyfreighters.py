"""build specialised freighters from the new meadow frames."""

import math

import bmesh
from mathutils import Vector

import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic


def smallBall(name, at, size, material, root):
    mesh = bmesh.new()
    bmesh.ops.create_uvsphere(mesh, u_segments=12, v_segments=6, radius=1)
    bmesh.ops.scale(mesh, vec=Vector(size), verts=mesh.verts)
    return kit.link(name, mesh, material, root, at=at)


def coldStorage(root, p):
    toy.box('cold keel', (0, 0, -7), (88, 22, 10), p['red'], root)
    toy.ball('cold bow', (40, 0, -3), (15, 14, 10), p['red'], root)
    traffic.bridge(root, p, (43, 0, 6), 8)
    for x, height in ((-28, 55), (-2, 43), (24, 31)):
        toy.box('insulated seal', (x, 0, height / 2), (23, 24, height), p['green'], root)
        chest = toy.box('insulated chest', (x, 0, height / 2), (20, 25.2, height - 2), p['milk'], root)
        detail.seam('chest seam', chest, [(0, (x,))], .3)
        for side in (-1, 1):
            for z in (height * .25, height * .7):
                toy.box('cold latch', (x + 7, side * 13.4, z), (5, 1.2, 2), p['butter'], root)
                detail.bolt('cold hinge', (x - 7, side * 13.4, z), .55, p['butter'], root, 'Y')
            traffic.window((x - 3, side * 13.3, height * .7), 1.5, p, root, side)
            detail.pipe('cold feed', [(x, side * 16, -1), (x, side * 16, height - 8),
                (x, side * 11, height - 3)], .8, p, root)
        traffic.drum('cold vent', (x, 0, height + 1), 3, 2, p['butter'], root, 'Z')
        for n in (-1, 0, 1):
            crystal = kit.prism('vent frost', [(-1, 0), (0, 4), (1.5, 1)], -.5, .5, p['milk'], root, .1)
            crystal.location = (x + n * 2, 0, height + 3 + abs(n))
    for i, y in enumerate((-15, 15)):
        traffic.engine(root, p, (-42, y, 0), 8, 14, 'green', i)
    return ((-28, 0, 58), (-44, 0, -4), (39, 0, -13), (6, -13, -5), (25, 0, 34))


def animal(root, p, at, side, cow):
    x, y, z = at
    smallBall('pen animal body', (x, y, z), (2.4, .35, 1.5), p['milk'], root)
    smallBall('pen animal head', (x + 2.3, y, z + .7), (.9, .4, .9), p['milk'], root)
    for dx in (-1.5, 1.5):
        toy.box('pen animal leg', (x + dx, y, z - 1.5), (.5, .4, 1.5), p['milk'], root)
    if cow:
        smallBall('cow patch', (x - .6, y + side * .34, z + .2), (.8, .12, .6), p['dark'], root)
    else:
        for dx in (-1.5, 0, 1.5):
            smallBall('sheep wool', (x + dx, y, z + .9), (1, .4, .8), p['milk'], root)


def livestock(root, p):
    toy.box('pen front bridge', (36, 0, 0), (26, 67, 14), p['red'], root)
    traffic.bridge(root, p, (38, 0, 9), 8)
    for i, side in enumerate((-1, 1)):
        y = side * 24
        toy.box('sealed pen gallery', (-5, y, 0), (77, 17, 17), p['milk'], root)
        for x in (-33, -14, 5, 24):
            toy.box('pen rib', (x, y, 0), (2.3, 18.8, 18.8), p['red'], root)
            traffic.drum('pen vent', (x, y, 12), 2.4, 6, p['butter'], root, 'Z')
        for j, x in enumerate((-24, -5, 14)):
            for face in (-1, 1):
                py = y + face * 8.9
                toy.box('pen window frame', (x, py, 0), (13.5, 1, 10), p['green'], root)
                toy.box('pen window glass', (x, py + face * .7, 0), (11.5, .3, 8), p['dark'], root)
                animal(root, p, (x, py + face * 1.1, -.1), face, j == 1)
        detail.pipe('pen air line', [(-39, y, 10), (-35, y, 13), (27, y, 13)], .8, p, root)
        traffic.engine(root, p, (-48, y, 0), 10, 16, 'green', i)
    return ((34, -20, 9), (22, 0, 0), (40, 0, -9), (36, -33.4, 0), (34, 20, 9))


def gasCarrier(root, p):
    toy.box('pressure spine', (-3, 0, 5), (104, 10, 8), p['butter'], root)
    spheres = [(-33, -18, 2, 16), (-33, 18, 2, 16), (1, -20, 2, 20),
        (1, 20, 2, 20), (38, 0, 2, 23), (13, 0, -23, 14)]
    for x, y, z, radius in spheres:
        toy.ball('pressure sphere', (x, y, z), (radius,) * 3, p['green'], root)
        kit.ring('pressure hoop', (x, y, z), radius + .2, 1.2, p['red'], root)
        for side in (-1, 1):
            toy.box('pressure buckle', (x, y + side * (radius + .8), z), (4, 2, 6), p['red'], root)
            detail.bolt('pressure buckle bolt', (x, y + side * (radius + 2.1), z), .7, p['butter'], root, 'Y')
        traffic.drum('pressure valve', (x, y, z + radius + 1), 3, 2, p['butter'], root, 'Z')
    for side in (-1, 1):
        kit.pipe('pressure main', [(-37, side * 13, 18), (0, side * 13, 27),
            (35, side * 10, 20)], 1.5, p['milk'], root, corner=3, sides=12)
    toy.box('bridge hanger', (48, 0, -20), (6, 7, 22), p['red'], root)
    traffic.bridge(root, p, (50, 0, -34), 7)
    for i, y in enumerate((-15, 15)):
        traffic.engine(root, p, (-57, y, 4), 9, 16, 'butter', i)
    return ((1, 0, 27), (-55, 0, 5), (31, 0, -30), (2, -41.7, 2), (39, 0, 27))


builders = {'cold-storage': coldStorage, 'livestock': livestock, 'gas-carrier': gasCarrier}
lengths = {'cold-storage': 110, 'livestock': 120, 'gas-carrier': 145}


def build(name):
    kit.reset()
    root, p = kit.empty('toy_ship_' + name), toy.palette()
    points = builders[name](root, p)
    for family, at in zip(('power', 'cruise', 'maneuver', 'cargo', 'utility'), points):
        traffic.port(root, p, family, at)
    detail.finish(root)
    extent = toy.bounds(root)
    scale = lengths[name] / (extent[0][1] - extent[0][0])
    for obj in root.children:
        obj.location *= scale
        obj.scale *= scale
    root['detail_revision'] = 3
    root['concept'] = 'assets/concepts/toy/ships/ship-' + name + '-meadow.webp'
    toy.save(root, 'ship-' + name, 40000, lengths[name] * 1.4)
