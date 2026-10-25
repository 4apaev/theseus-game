"""build the open dock and orbital fuel station."""

import math

import bpy

import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic
import toyutility


def beacon(root, p, at):
    x, y, z = at
    toy.drum('beacon base', at, 3, 3, p['milk'], root, 'Z')
    toy.ball('beacon lamp', (x, y, z + 3), (2, 2, 3), p['glow'], root)


def berth(root, at, name='berth', size=100):
    obj = kit.empty(name, root, at)
    obj['size'] = size
    return obj


def dryDock(root, p):
    for x in (-145, 0, 145):
        kit.pipe('dock structural hoop', [(x, -60, -60), (x, -60, 60),
            (x, 60, 60), (x, 60, -60), (x, -60, -60)],
            10, p['red'], root, corner=16, sides=12)
        for side in (-1, 1):
            for z in (-40, 0, 40):
                toy.box('scaffold ledge', (x, side * 46, z), (14, 13, 2), p['green'], root)
                for dx in (-6, 6):
                    kit.pipe('scaffold rail', [(x + dx, side * 40, z + 1.3),
                        (x + dx, side * 40, z + 2.4), (x + dx, side * 52, z + 2.4)],
                        .15, p['butter'], root, sides=6)
            beacon(root, p, (x, side * 58, 72))
    for y in (-55, 55):
        for z in (-55, 55):
            toy.box('longitudinal beam', (0, y, z), (312, 11, 11), p['green'], root)
    hall = toy.box('dock workshop hall', (0, -78, -38), (320, 25, 25), p['milk'], root)
    detail.seam('workshop segments', hall, [(0, (-110, -60, -10, 40, 90, 140))], .4)
    for x in range(-140, 141, 20):
        traffic.window((x, -91, -35), 2, p, root)
    for x in (-90, 70):
        toy.box('internal crane rail', (x, 0, 44), (6, 98, 6), p['butter'], root)
        toy.box('internal crane carriage', (x, -10, 38), (12, 13, 9), p['milk'], root)
        toyutility.arm(root, p, 'internal tool arm', [(x, -10, 32),
            (x + 12, -10, 24), (x + 15, -5, 10)], 1.5)
        toy.drum('internal tool magnet', (x + 15, -5, 8), 4, 3, p['green'], root, 'Z')
    for x in (-145, 0, 145):
        for side in (-1, 1):
            for z in (-39, 0, 39):
                toy.box('hoop service clamp', (x, side * 60, z), (23, 24, 8), p['butter'], root)
                toy.ball('hoop nav lamp', (x + 12.2, side * 60, z), (1, 3, 2), p['glow'], root)
    for side in (-1, 1):
        for z in (-55, 55):
            kit.pipe('dock service main', [(-149, side * 68, z), (149, side * 68, z)],
                2.5, p['butter'], root, sides=8)
        for x in (-105, -35, 35, 105):
            kit.pipe('dock diagonal brace', [(x - 30, side * 55, -50), (x + 30, side * 55, 50)],
                2, p['green'], root, sides=8)
    berth(root, (0, 0, 0), size=220)
    return {'rigging': (0, -78, -20), 'exchange': (90, -78, -20),
        'comms': (-90, -78, -20), 'chart': (0, -78, -20)}


def gasStation(root, p):
    toy.ball('fuel central hub', (0, 0, 0), (42, 42, 42), p['green'], root)
    for x, y in ((-90, 0), (90, 0), (0, -90), (0, 90)):
        axis = 'X' if x else 'Y'
        toy.drum('fuel tank arm', (x * .5, y * .5, 0), 12, 50, p['red'], root, axis)
        toy.ball('station pressure sphere', (x, y, 0), (40,) * 3, p['milk'], root)
        kit.ring('tank hoop', (x, y, 0), 40.4, 2, p['green'], root, axis)
        toy.drum('tank valve', (x, y, 43), 6, 6, p['green'], root, 'Z')
        for a in (0, 60, 120, 180, 240, 300):
            angle = math.radians(a)
            mount = kit.empty('tank lamp mount', root,
                (x + 40 * math.cos(angle), y + 40 * math.sin(angle), 0))
            mount.rotation_euler.z = angle + math.pi / 2
            traffic.window((0, 0, 0), 2.5, p, mount)
    for y in (-28, 28):
        toyutility.arm(root, p, 'fuel pump arm', [(24, y, 25), (63, y, 44),
            (115, y, 40), (153, y, 23)], 3)
        kit.pipe('fuel hose', [(29, y, 22), (65, y, 23), (87, y, 6),
            (119, y, 35), (153, y, 20)], 1.7, p['red'], root, corner=10, sides=12)
    toy.drum('lower service mast', (0, 0, -55), 7, 35, p['butter'], root, 'Z')
    toy.ball('lower service cabin', (0, 0, -78), (22, 22, 15), p['red'], root)
    toy.dish('fuel comms dish', (0, -27, -68), 12, p['green'], root)
    for z, radius in ((-24, 35), (0, 43), (24, 35)):
        kit.ring('hub service hoop', (0, 0, z), radius, 2, p['butter'], root, 'Z')
    for x in (-90, 90):
        for z in (-7, 7):
            kit.ring('tank valve collar', (x * .5, 0, 0), 13.5, 1.5, p['butter'], root, 'X').location.x += z
    traffic.bridge(root, p, (0, 0, 43), 16)
    toy.box('fuel sign post', (0, 0, 71), (6, 6, 40), p['red'], root)
    toy.box('fuel sign frame', (0, 0, 94), (65, 7, 28), p['butter'], root)
    toy.box('fuel sign face', (0, -4.1, 94), (60, 1, 23), p['milk'], root)
    curve = bpy.data.curves.new('fuel sign type', 'FONT')
    curve.body, curve.align_x, curve.size, curve.extrude = 'fuel', 'CENTER', 20, .2
    label = bpy.data.objects.new('fuel sign letters', curve)
    bpy.context.collection.objects.link(label)
    label.parent, label.location = root, (0, -5, 87)
    label.rotation_euler.x = math.pi / 2
    label.data.materials.append(p['dark'])
    bpy.context.view_layer.objects.active = label
    label.select_set(True)
    bpy.ops.object.convert(target='MESH')
    label.select_set(False)
    back = label.copy()
    back.data = label.data.copy()
    bpy.context.collection.objects.link(back)
    back.name = 'fuel sign back letters'
    back.location = (0, 5, 87)
    back.rotation_euler.z = math.pi
    toy.box('fuel sign back face', (0, 4.1, 94), (60, 1, 23), p['milk'], root)
    for x in (-25, 0, 25):
        beacon(root, p, (x, 0, 111))
    berth(root, (153, 0, 38), size=110)
    return {'exchange': (0, 0, 60), 'rigging': (25, 0, 32),
        'comms': (0, -27, -53), 'chart': (0, 0, 60)}


def build(name):
    kit.reset()
    root, p = kit.empty('toy_station_' + name), toy.palette()
    spots = {'dry-dock': dryDock, 'gas-station': gasStation}[name](root, p)
    for key, at in spots.items():
        kit.empty('spot_' + key, root, at)
    detail.finish(root)
    root['detail_revision'] = 3
    root['surface_clearance'] = .25
    root['concept'] = 'assets/concepts/toy/station/station-' + name + '-meadow.webp'
    toy.save(root, 'station-' + name, 60000, 460)
