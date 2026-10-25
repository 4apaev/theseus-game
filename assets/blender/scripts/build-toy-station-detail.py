"""build the station with an awning, an open yard and pipe clamps."""

import importlib.util
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy
import toydetail as detail

source = Path(__file__).with_name('build-toy-station.py')
spec = importlib.util.spec_from_file_location('stationBase', source)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def market(root, p):
    for x in (-29, -17, -5, 7, 19, 31):
        toy.box('market awning stripe', (x, -31, 136), (11, 27, 5),
            p['butter'] if x in (-29, -5, 19) else p['milk'], root)
        toy.ball('awning scallop', (x, -44, 133), (5.4, 2.5, 4), p['butter'], root)
    for x in (-29, 29):
        toy.drum('awning post', (x, -41, 118), 1.5, 26, p['red'], root, 'Z')
    toy.box('market counter', (0, -28, 106), (40, 7, 9), p['green'], root)
    for index, x in enumerate((-23, -11, 1, 13, 25)):
        toy.box('market goods crate', (x, -42, 106), (7, 7, 7), p['red'] if index % 2 else p['butter'], root)
        toy.box('crate lid', (x, -42, 110), (7.8, 7.8, .8), p['milk'], root)
    for x in (-24, -8, 8, 24):
        detail.window('market upper window', (x, -18.9, 126), 3, p, root)
    for x in (-33, 33):
        toy.drum('market tank', (x, 8, 117), 8, 27, p['milk'], root, 'Z')
        kit.ring('market tank belt', (x, 8, 117), 8.4, 1, p['red'], root, 'Z')


def yard(root, p):
    for obj in list(root.children_recursive):
        if obj.name.startswith(('yard hall', 'yard opening')):
            bpy.data.objects.remove(obj, do_unlink=True)
    toy.box('yard rear wall', (100, 28, 60), (65, 5, 55), p['milk'], root)
    for x in (69, 131):
        toy.box('yard side wall', (x, -1.4, 60), (5, 53.2, 55), p['milk'], root)
    toy.box('yard roof', (100, 0, 89), (67, 65, 8), p['milk'], root)
    kit.pipe('yard red arch', [(70, -34, 36), (70, -34, 82), (79, -34, 92),
        (121, -34, 92), (130, -34, 82), (130, -34, 36)], 5, p['red'], root, corner=8, sides=12)
    for x in (78, 92, 108, 122):
        detail.window('yard arch light', (x, -39.8, 86), 2.3, p, root)
    toy.box('yard work bench', (120, 8, 40), (12, 22, 6), p['green'], root)
    toy.box('yard crane rail', (100, 2, 81), (48, 3, 3), p['green'], root)
    toy.box('yard crane trolley', (98, 2, 77), (8, 8, 4), p['butter'], root)
    toy.drum('yard crane cable', (98, 2, 63), .5, 24, p['dark'], root, 'Z')
    kit.ring('yard crane hook', (98, 2, 50), 2, .6, p['butter'], root, 'Y')
    for x in (82, 96, 115):
        toy.box('yard supply crate', (x, -22, 41), (8, 8, 8), p['butter'], root)
        toy.box('yard crate clasp', (x, -26.7, 41), (2, .8, 3), p['red'], root)


def pads(root, p):
    for name, (x, y, z), size in (('berth', (10, -140, 120), 95),
            ('berth_b', (-160, -65, 32), 85), ('berth_c', (158, -83, 22), 100),
            ('berth_d', (30, 145, 110), 120)):
        kit.ring(name + ' deck rim', (x, y, z + 3.8), size * .47, 1.3, p['butter'], root, 'Z')
        kit.ring(name + ' landing mark', (x, y, z + 3.7), size * .18, .6, p['butter'], root, 'Z')
        toy.box(name + ' landing bar', (x, y, z + 3.7), (size * .24, 1.3, .6), p['butter'], root)
        for angle in range(30, 360, 60):
            a = math.radians(angle)
            at = (x + math.cos(a) * size * .47, y + math.sin(a) * size * .47, z + 5)
            toy.box(name + ' rim bumper', at, (7, 4, 3), p['red'], root)
        toy.drum(name + ' support collar', (x, y, z - 14), size * .29, 3, p['butter'], root, 'Z')


def pipes(root, p):
    for name, points, radius, clamps in (
        ('market service', [(-31, -8, 107), (-63, -8, 93), (-95, -8, 75)], 4,
            [((-47, -8, 100), 'X')]),
        ('yard service', [(120, -29, 45), (144, -46, 34), (158, -65, 30)], 4,
            [((132, -37.5, 39.5), 'X')]),
        ('dome service', [(18, 87, 63), (18, 66, 70), (18, 37, 93)], 4,
            [((18, 75, 67), 'Y')])):
        detail.pipe(name, points, radius, p, root)
        detail.clamps(name, clamps, radius, p, root)
    routes = (
        [(0, -20, 96), (-45, -50, 105), (-95, -45, 95), (-110, -20, 84)],
        [(20, -35, 96), (65, -55, 99), (105, -50, 77), (120, -29, 45)],
        [(10, 30, 97), (30, 55, 104), (50, 80, 94), (18, 100, 80)])
    for index, points in enumerate(routes):
        kit.pipe('fat pipe ' + str(index), points, 5, p['green'], root, corner=10, sides=12)
        detail.clamps('main pipe ' + str(index), [(points[1], 'X')], 5, p, root)


def dome(root, p):
    obj = next(obj for obj in root.children_recursive if obj.name == 'chart dome')
    obj.data.materials[0] = p['green']
    kit.ring('chart dome rim', (18, 100, 79), 33.5, 1.2, p['butter'], root, 'Z')
    for angle in (0, 90):
        points = []
        for i in range(13):
            a = i * math.pi / 12
            span = 34 * math.cos(a)
            points.append((18 + span * math.cos(math.radians(angle)),
                100 + span * math.sin(math.radians(angle)), 78 + 29.8 * math.sin(a)))
        kit.pipe('dome frame', points, .8, p['milk'], root, corner=0, sides=8)
    for x in (8, 18, 28):
        toy.drum('dome lab tank', (x, 94, 82), 3, 14, p['milk'], root, 'Z')
    for x in (-120, -108, -96):
        detail.window('comms tower window', (x, -21, 69), 2.5, p, root)
    kit.ring('dish rim', (-110, 0, 104), 44, 1.5, p['milk'], root, 'Z')
    for x, y, z in ((-110, 0, 117), (0, 10, 154), (100, 0, 105)):
        toy.drum('facility beacon mast', (x, y, z), 1, 8, p['red'], root, 'Z')
        toy.ball('facility beacon tip', (x, y, z + 5), (2, 2, 2), p['glow'], root)


def wallDetails(root, p):
    for side in (-1, 1):
        for y in (-4, 12, 28):
            mount = kit.empty('market side window mount', root, (side * 37.2, y, 122))
            mount.rotation_euler.z = math.pi if side > 0 else 0
            detail.window('market side window', (0, 0, 0), 3.4, p, mount, 'X')
    for x in (-24, -8, 8, 24):
        mount = kit.empty('market rear window mount', root, (x, 38.8, 122))
        mount.rotation_euler.z = math.pi
        detail.window('market rear window', (0, 0, 0), 3.4, p, mount)
    rear = next(obj for obj in root.children_recursive if obj.name == 'yard rear wall')
    detail.seam('yard wall seam', rear, [(0, (84, 116))], .6, .7)
    for x in (80, 100, 120):
        mount = kit.empty('yard rear window mount', root, (x, 31.6, 65))
        mount.rotation_euler.z = math.pi
        detail.window('yard rear window', (0, 0, 0), 3.5, p, mount)
    for x in (80, 100, 120):
        toy.box('yard roof vent base', (x, 8, 94), (12, 16, 2), p['red'], root)
        for y in (3, 8, 13):
            toy.box('yard roof vent rib', (x, y, 95.8), (10, 2, 1), p['butter'], root)
    for x in (-24, 24):
        toy.drum('market roof tank', (x, 10, 164), 5, 12, p['milk'], root, 'Z')
        kit.ring('roof tank belt', (x, 10, 164), 5.3, .7, p['green'], root, 'Z')


def rockSurface(direction):
    lobes = (((0, 0, 0), (145, 118, 85)),
        ((-75, 0, 25), (75, 95, 74)), ((78, 0, -16), (80, 101, 70)))
    hits = []
    for centre, size in lobes:
        a = sum((direction[i] / size[i]) ** 2 for i in range(3))
        b = -2 * sum(direction[i] * centre[i] / size[i] ** 2 for i in range(3))
        c = sum((centre[i] / size[i]) ** 2 for i in range(3)) - 1
        disc = b * b - 4 * a * c
        if disc >= 0:
            t = (-b + math.sqrt(disc)) / (2 * a)
            hits.append((t, centre, size))
    t, centre, size = max(hits, key=lambda hit: hit[0])
    point = direction * t
    normal = Vector([(point[i] - centre[i]) / size[i] ** 2 for i in range(3)]).normalized()
    return point, normal


def rockDetails(root, p):
    for index, (azimuth, latitude) in enumerate(((20, 25), (65, -15), (115, 30),
            (160, 20), (205, 30), (250, -15), (290, 25), (335, 18))):
        a, b = math.radians(azimuth), math.radians(latitude)
        direction = Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b)))
        point, normal = rockSurface(direction)
        mount = kit.empty('rock service mount ' + str(index), root, point + normal * 1.5)
        mount.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
        toy.drum('rock service collar', (0, 0, 0), 11, 3, p['milk'], mount, 'Z')
        detail.window('rock service porthole', (0, 0, 2.2), 8, p, mount, 'Z')
        for x in (-5, 5):
            detail.bolt('rock collar bolt', (x, 4, 2.3), .7, p['butter'], mount)
        kit.pipe('rock surface conduit', [(-13, 0, 1), (-19, 0, 3),
            (-19, 18, 3), (-4, 25, 1)], 2.6, p['red'], mount, corner=3, sides=8)
    for index, (a, b) in enumerate(((45, 25), (135, 20), (225, 30), (315, 20))):
        azimuth, latitude = math.radians(a), math.radians(b)
        direction = Vector((math.cos(azimuth) * math.cos(latitude),
            math.sin(azimuth) * math.cos(latitude), math.sin(latitude)))
        point, normal = rockSurface(direction)
        mount = kit.empty('rock outcrop mount ' + str(index), root, point)
        mount.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
        toy.ball('rock outcrop', (0, 0, 0), (13, 10, 7), p['green'], mount)
        toy.ball('rock small outcrop', (12, 6, -1), (7, 6, 5), p['green'], mount)


def surfacePipes(root, p):
    for index, (start, end, latitude) in enumerate(((5, 55, 12),
            (100, 150, 12), (180, 230, 12), (270, 325, 8))):
        points = []
        for step in range(9):
            a = math.radians(start + (end - start) * step / 8)
            b = math.radians(latitude)
            direction = Vector((math.cos(a) * math.cos(b),
                math.sin(a) * math.cos(b), math.sin(b)))
            point, normal = rockSurface(direction)
            points.append(tuple(point + normal * 4.5))
        kit.pipe('surface trunk ' + str(index), points, 3.5,
            p['red'], root, corner=0, sides=8)


def serviceBuildings(root, p):
    for index, angle in enumerate((40, 140, 220, 320)):
        a, b = math.radians(angle), math.radians(38)
        direction = Vector((math.cos(a) * math.cos(b),
            math.sin(a) * math.cos(b), math.sin(b)))
        point, normal = rockSurface(direction)
        mount = kit.empty('service building mount ' + str(index), root, point)
        mount.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
        toy.box('service foundation', (0, 0, 1), (26, 22, 5), p['milk'], mount)
        toy.box('service cabin', (0, 0, 10), (20, 16, 16),
            p['butter'] if index % 2 else p['red'], mount)
        toy.box('service roof', (0, 0, 19), (23, 19, 3), p['milk'], mount)
        toy.box('service door', (0, -8.6, 6), (3, .7, 3), p['dark'], mount)
        detail.window('service window', (0, -8.8, 13), 3, p, mount)
        for x in (-5, 5):
            toy.box('service roof vent', (x, 0, 21.4), (4, 10, 1.2), p['green'], mount)
        kit.pipe('service supply pipe', [(10, 0, 10), (17, 0, 10),
            (17, 0, 0), (22, 0, -2)], 2, p['green'], mount, corner=3, sides=8)


def chartWindows(root, p):
    for index, angle in enumerate((30, 90, 150, 210, 270, 330)):
        a = math.radians(angle)
        local = Vector((29 * math.cos(a), 26.4 * math.sin(a), 15))
        normal = Vector((local.x / 34 ** 2, local.y / 31 ** 2, local.z / 29 ** 2)).normalized()
        mount = kit.empty('chart window mount ' + str(index), root,
            Vector((18, 100, 78)) + local + normal * 1.5)
        mount.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
        detail.window('chart round window', (0, 0, 0), 4.5, p, mount, 'Z')


def build():
    kit.reset()
    p, root = toy.palette(), kit.empty('toy_station')
    toy.ball('world core', (0, 0, 0), (145, 118, 85), p['green'], root)
    toy.ball('world left lobe', (-75, 0, 25), (75, 95, 74), p['green'], root)
    toy.ball('world right lobe', (78, 0, -16), (80, 101, 70), p['green'], root)
    base.halls(root, p)
    hall = next(obj for obj in root.children_recursive if obj.name == 'market hall')
    detail.seam('market panel seam', hall, [(0, (-22, 22))], .6, .7)
    for name, at in zip(('a', 'b', 'c', 'd'), ((-18, -38, 101.75),
            (18, -38, 101.75), (18, -48, 101.75), (-18, -48, 101.75))):
        kit.empty('walk_' + name, root, at)
    for name, at, size in (('berth', (10, -140, 120), 95), ('berth_b', (-160, -65, 32), 85),
            ('berth_c', (158, -83, 22), 100), ('berth_d', (30, 145, 110), 120)):
        base.pad(root, p, name, at, size)
    market(root, p)
    yard(root, p)
    pads(root, p)
    pipes(root, p)
    dome(root, p)
    wallDetails(root, p)
    rockDetails(root, p)
    chartWindows(root, p)
    surfacePipes(root, p)
    serviceBuildings(root, p)
    for obj in root.children_recursive:
        if obj.type != 'MESH':
            continue
        if obj.name.startswith(('rock outcrop', 'rock small outcrop')):
            modifier = obj.modifiers.new('outcrop facets', 'DECIMATE')
            modifier.ratio = .4
        if obj.name.startswith(('rock collar bolt', 'berth')):
            for modifier in obj.modifiers:
                if modifier.type == 'BEVEL':
                    modifier.segments = 1
    detail.finish(root)
    root['detail_revision'] = 5
    toy.save(root, 'station', 80000, 540)


build()
