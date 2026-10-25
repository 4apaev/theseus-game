"""build towing hulls and separate loads."""

import math
import random

import bmesh
from mathutils import Vector

import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic


def rock(name, at, size, material, root, seed=7):
    rng = random.Random(seed)
    mesh = bmesh.new()
    bmesh.ops.create_icosphere(mesh, subdivisions=2, radius=1)
    for vertex in mesh.verts:
        vertex.co *= rng.uniform(.86, 1.12)
        vertex.co = Vector([vertex.co[i] * size[i] for i in range(3)])
    return kit.link(name, mesh, material, root, (.5, 2), at=at)


def asteroidBarge(root, p):
    raft = toy.box('barge drive raft', (-46, 0, 0), (24, 84, 15), p['red'], root)
    detail.seam('raft panel seam', raft, [(1, (-22, 0, 22))], .4)
    for i, y in enumerate((-33, -11, 11, 33)):
        mount = kit.empty('barge engine mount ' + str(i), root)
        traffic.engine(mount, p, (-61, y, 0), 8, 14, 'red', i)
        exhaust = next(obj for obj in mount.children if obj.name.startswith('exhaust'))
        exhaust.name = 'exhaust' if i == 0 else 'exhaust_' + str(i)
    for side in (-1, 1):
        y = side * 39
        rail = toy.box('barge long rail', (7, y, 0), (106, 7, 10), p['green'], root)
        detail.seam('rail section seam', rail, [(0, (-25, 0, 25))], .3)
        for x in (-12, 35):
            toy.box('clamp base', (x, y, 6), (8, 12, 5), p['butter'], root)
            kit.pipe('clamp arm', [(x, y, 8), (x, y - side * 4, 18),
                (x, side * 27, 22)], 2.4, p['red'], root, corner=3, sides=12)
            toy.drum('clamp grip', (x, side * 25, 22), 5, 4, p['milk'], root, 'Y')
            detail.bolt('clamp joint', (x, y + side * 4, 10), 2, p['green'], root, 'Y')
        detail.pipe('rail service line', [(-41, y, 7), (-30, y, 10),
            (48, y, 10)], .7, p, root)
    traffic.bridge(root, p, (-8, 39, 9), 6)
    load = kit.empty('tow_load', root, (9, 0, 9))
    load['asset'] = 'tow-asteroid.glb'
    load['attachment'] = 'clamp'
    return ((-45, -27, 9), (-60, 0, 0), (-44, 0, -9), (-45, -43, 0), (-45, 27, 9))


def icebergTug(root, p):
    beam = toy.box('ice tug drive beam', (0, 0, 0), (18, 86, 15), p['red'], root)
    detail.seam('beam section seam', beam, [(1, (-25, 0, 25))], .35)
    for i, y in enumerate((-36, 0, 36)):
        mount = kit.empty('ice tug engine mount ' + str(i), root)
        traffic.engine(mount, p, (-13, y, -1), 7, 13, 'green', i)
        exhaust = next(obj for obj in mount.children if obj.name.startswith('exhaust'))
        exhaust.name = 'exhaust' if i == 0 else 'exhaust_' + str(i)
    toy.box('bridge suspension', (8, 0, -11), (6, 10, 15), p['red'], root)
    traffic.bridge(root, p, (12, 0, -23), 7)
    for i, y in enumerate((-24, 0, 24)):
        tower = toy.box('tow tower', (-2, y, 18), (8, 5, 23), p['green'], root)
        traffic.drum('tow winch', (-4, y, 27), 4, 7, p['butter'], root, 'Y')
        kit.ring('winch flange', (-4, y - 4, 27), 4, .6, p['red'], root, 'Y')
        kit.ring('winch flange', (-4, y + 4, 27), 4, .6, p['red'], root, 'Y')
        spot = kit.empty('tow_' + chr(97 + i), root, (-9, y, 27))
        spot['cable_radius'] = .35
    load = kit.empty('tow_load', root, (-160, 0, 20))
    load['asset'], load['attachment'] = 'tow-iceberg.glb', 'cable'
    return ((0, -34, 9), (-10, 12, 0), (0, 25, -9), (0, -44, 0), (0, 34, 9))


def load(kind):
    kit.reset()
    root, p = kit.empty('tow_' + kind), toy.palette()
    if kind == 'asteroid':
        rock('asteroid load', (0, 0, 0), (43, 28, 30), p['butter'], root)
        for i, at in enumerate(((-20, -12, 16), (11, 17, 14), (22, -10, -13))):
            rock('asteroid lobe', at, (18, 16, 15), p['butter'], root, i + 20)
    else:
        rock('ice core', (0, 0, 0), (48, 49, 45), p['green'], root)
        for i, (x, y, z) in enumerate(((-15, -20, 15), (22, -14, 0), (-18, 22, -9),
                (15, 20, 21), (-17, -15, -24), (8, 4, 32))):
            rock('ice block', (x, y, z), (29, 30, 28), p['milk'], root, i + 50)
        for i, y in enumerate((-24, 0, 24)):
            kit.empty('tow_' + chr(97 + i), root, (48, y, 7))
    root['detail_revision'] = 3
    toy.save(root, 'tow-' + kind, 12000, 160)


def build(name):
    kit.reset()
    root, p = kit.empty('toy_ship_' + name), toy.palette()
    points = {'asteroid-barge': asteroidBarge, 'iceberg-tug': icebergTug}[name](root, p)
    for family, at in zip(('power', 'cruise', 'maneuver', 'cargo', 'utility'), points):
        traffic.port(root, p, family, at)
    detail.finish(root)
    root['detail_revision'] = 3
    root['concept'] = 'assets/concepts/toy/ships/ship-' + name + '-meadow.webp'
    toy.save(root, 'ship-' + name, 40000, 190 if name == 'asteroid-barge' else 130)
    load('asteroid' if name == 'asteroid-barge' else 'iceberg')
