"""build six traffic hulls from their meadow concept frames."""

import math

import paintkit as kit
import toykit as toy
import toydetail as detail


def drum(name, at, radius, length, material, root, axis='X'):
    return kit.barrel(name, at, radius, length, material, root, axis,
        sides=16, round_=min(.5, length * .15))


def window(at, radius, p, root, side=-1):
    x, y, z = at
    drum('window frame', at, radius, .5, p['butter'], root, 'Y')
    kit.barrel('round lit window', (x, y + side * .4, z), radius * .72,
        .2, p['glow'], root, 'Y', sides=16, round_=0)


def engine(root, p, at, radius, length, role='red', index=0):
    x, y, z = at
    drum('engine barrel', at, radius, length, p[role], root)
    lip = x - length / 2 - 3
    detail.tube('deep engine nozzle', (lip, y, z), radius * .93,
        radius * .69, 6, p['dark'], root)
    kit.ring('engine nozzle lip', (lip - 3.3, y, z), radius * .81, .6, p['milk'], root)
    drum('engine recessed glow', (lip + 2.5, y, z), radius * .65, .2, p['glow'], root)
    kit.ring('engine strap', (x + length * .27, y, z), radius + .15, .6, p['milk'], root)
    kit.ring('engine rear strap', (x - length * .3, y, z), radius + .15, .6, p['milk'], root)
    for side in (-1, 1):
        at = (x, y + side * (radius + .2), z)
        toy.box('engine service panel', at, (length * .4, 1.3, radius * .9), p[role], root)
        for dx in (-length * .12, length * .12):
            detail.bolt('engine panel bolt', (x + dx, at[1] + side * .95, z),
                .55, p['butter'], root, 'Y')
    detail.pipe('engine top feed', [(x - length * .3, y, z + radius + .1),
        (x - length * .15, y, z + radius + 1.8),
        (x + length * .3, y, z + radius + 1.8)], .65, p, root)
    for angle in (45, 135, 225, 315):
        a = math.radians(angle)
        detail.bolt('nozzle bolt', (lip - 4, y + radius * .81 * math.cos(a),
            z + radius * .81 * math.sin(a)), .55, p['butter'], root, 'X')
    obj = kit.empty('exhaust' if index == 0 else 'exhaust_b', root, (lip - 3.5, y, z))
    obj['plume'], obj['radius'] = True, radius * .65


def port(root, p, family, at):
    mount = kit.empty('port mount ' + family, root, at)
    if family == 'cruise':
        mount.rotation_euler.y = -math.pi / 2
    elif family == 'cargo':
        mount.rotation_euler.x = math.pi / 2
    elif family == 'maneuver':
        mount.rotation_euler.x = math.pi
    drum('port base ' + family, (0, 0, 0), 3.6, 1.5, p['red'], mount, 'Z')
    drum('port clip ' + family, (0, 0, 1.1), 2.8, .6, p['dark'], mount, 'Z')
    kit.ring('port rim ' + family, (0, 0, 1.6), 2.9, .4, p['milk'], mount, 'Z')
    for x, y in ((-3, 0), (3, 0), (0, -3), (0, 3)):
        toy.box('port latch ' + family, (x, y, 1.5), (1.4, 1.4, 1.3), p['butter'], mount)
    socket = kit.socket(mount, family + '1', family, (0, 0, 1.8))
    socket['size'] = 6


def bridge(root, p, at, radius):
    x, y, z = at
    drum('bridge lower ring', at, radius, 3, p['milk'], root, 'Z')
    drum('bridge cabin', (x, y, z + 3), radius * .91, 4, p['green'], root, 'Z')
    drum('bridge roof', (x, y, z + 5.5), radius, 1.2, p['milk'], root, 'Z')
    for angle in range(0, 360, 45):
        a = math.radians(angle)
        mount = kit.empty('bridge window mount', root,
            (x + math.cos(a) * radius * .94, y + math.sin(a) * radius * .94, z + 3))
        mount.rotation_euler.z = a + math.pi / 2
        window((0, 0, 0), 1.1, p, mount)


def tanker(root, p):
    toy.box('tanker keel', (0, 0, -9), (78, 14, 5), p['red'], root)
    for x in (-24, 0, 24):
        toy.ball('capsule tank', (x, 0, 1), (15, 13, 13), p['milk'], root)
        kit.ring('tank red hoop', (x, 0, 1), 13.25, 1.3, p['red'], root)
        for y in (-13.7, 13.7):
            toy.box('tank buckle', (x, y, 1), (3, 2, 4), p['butter'], root)
            window((x + 4, y * .94, 4), 1.2, p, root, -1 if y < 0 else 1)
    for side in (-1, 1):
        points = [(-32, side * 10, 12), (-25, side * 10, 16),
            (26, side * 10, 16), (32, side * 10, 10)]
        detail.pipe('tank feed', points, 1, p, root)
        detail.clamps('tank feed', [((x, side * 10, 16), 'X') for x in (-18, 10)], 1, p, root)
        engine(root, p, (-37, side * 11, 0), 7, 14, index=0 if side < 0 else 1)
    bridge(root, p, (29, 0, 13), 6)
    return ((-24, 0, 15), (-36, 0, 0), (32, 0, -12), (0, -14, 0), (17, 0, 15))


def liner(root, p):
    hull = toy.box('liner hull', (0, 0, 0), (90, 25, 18), p['milk'], root)
    detail.seam('liner hull seam', hull, [(0, (-28, -8, 12, 32))], .35)
    toy.ball('liner rounded bow', (37, 0, -1), (16, 12, 10), p['red'], root)
    toy.box('lower passenger deck', (0, 0, 11), (80, 23, 5), p['green'], root)
    toy.box('upper passenger deck', (2, 0, 17), (61, 18, 7), p['milk'], root)
    toy.box('lounge roof', (2, 0, 21), (60, 19, 2), p['green'], root)
    for side in (-1, 1):
        for x in range(-36, 37, 8):
            window((x, side * 12.8, 4), 1.25, p, root, side)
        for x in range(-22, 27, 8):
            window((x, side * 9.3, 17), 1.1, p, root, side)
        detail.pipe('liner service', [(-35, side * 13.4, -5), (28, side * 13.4, -5)], .7, p, root)
        engine(root, p, (-44, side * 16, 3), 8, 17, index=0 if side < 0 else 1)
    bridge(root, p, (19, 0, 22), 7)
    for x in (-17, -5):
        toy.box('liner roof vent', (x, 0, 23), (7, 8, 2), p['red'], root)
        for y in (-2.5, 0, 2.5):
            toy.box('liner vent rib', (x, y, 24.4), (5, 1, .7), p['butter'], root)
    detail.pipe('lounge roof conduit', [(-24, 6, 22.5), (-15, 6, 25),
        (7, 6, 25), (12, 6, 22.5)], .7, p, root)
    return ((-23, 0, 23), (-46, 0, 0), (37, 0, -11), (0, -14, -2), (4, 0, 23))


def tug(root, p):
    cab = toy.box('tug central cab', (-5, 0, 0), (24, 23, 20), p['green'], root)
    detail.seam('cab seam', cab, [(0, (-10,))], .4)
    bridge(root, p, (-3, 0, 11), 6)
    for side in (-1, 1):
        for x in (-10, -3, 4):
            window((x, side * 11.9, 4), 1.5, p, root, side)
    for side in (-1, 1):
        engine(root, p, (-22, side * 17, 0), 11, 24, index=0 if side < 0 else 1)
        points = [(2, side * 10, -3), (17, side * 20, -3), (34, side * 20, -3)]
        kit.pipe('tug claw arm', points, 2.8, p['butter'], root, corner=3, sides=12)
        for x, y, z in points[1:]:
            drum('claw hinge', (x, y, z), 3.8, 7, p['butter'], root, 'Z')
            detail.bolt('claw hinge pin', (x, y, z + 4), 1.6, p['green'], root)
        for dz in (-1, 1):
            kit.pipe('claw jaw', [(34, side * 20, -3), (37, side * 20, -3 + dz * 7),
                (43, side * 20, -3 + dz * 7)], 2, p['milk'], root, corner=2, sides=12)
        detail.pipe('claw hydraulic', [(3, side * 12, 1), (18, side * 20, 1),
            (31, side * 20, 1)], .7, p, root)
    drum('tug winch', (9, 0, -1), 4, 10, p['dark'], root, 'Y')
    for y in (-5, 5):
        kit.ring('winch flange', (9, y, -1), 4, .7, p['butter'], root, 'Y')
    return ((-13, 0, 12), (-22, 0, 0), (5, 0, -12), (-5, -13, 0), (6, 0, 12))


def police(root, p):
    hull = kit.prism('patrol wedge', [(-25, -8), (32, -6), (36, 1),
        (20, 9), (-25, 12)], -13, 13, p['green'], root, 2)
    detail.seam('patrol panel seam', hull, [(0, (-12, 5, 22))], .4)
    for side in (-1, 1):
        panel = toy.box('patrol armour', (-3, side * 13.8, 0), (36, 2, 12), p['milk'], root)
        detail.seam('armour seam', panel, [(0, (-9, 6))], .3)
        for x in (-15, -4, 7):
            window((x, side * 15.2, 3), 1.4, p, root, side)
        engine(root, p, (-29, side * 14, 0), 8, 18, 'green', 0 if side < 0 else 1)
        detail.pipe('patrol conduit', [(-18, side * 15.3, -5), (20, side * 15.3, -5)], .8, p, root)
    bridge(root, p, (19, 0, 9), 7)
    drum('siren mast', (-2, 0, 16), 2.4, 7, p['milk'], root, 'Z')
    drum('siren crossbar', (-2, 0, 20.5), 5, 2, p['butter'], root, 'Z')
    for y, role in ((-3, 'red'), (3, 'glow')):
        drum('police beacon ' + role, (-2, y, 23.5), 1.8, 4, p[role], root, 'Z')
    for x in (-14, 1, 14):
        for side in (-1, 1):
            toy.box('patrol top panel', (x, side * 8, 11.3 - (x + 14) * .065),
                (11, 6, 1.2), p['green'], root)
    toy.box('patrol bow bumper', (34, 0, -2), (5, 19, 5), p['butter'], root)
    return ((-17, 0, 13), (-27, 0, 0), (27, 0, -9), (-5, -17, -2), (10, 0, 12))


def raider(root, p):
    hull = toy.box('raider hull', (0, 0, 0), (57, 23, 20), p['red'], root)
    detail.seam('raider hull seam', hull, [(0, (-17, 0, 17))], .5)
    toy.ball('angry cockpit', (24, 0, 4), (10, 10, 7), p['green'], root)
    toy.box('angry window', (29, -7, 5), (10, 2.2, 2), p['dark'], root)
    for index, (x, y, z, size) in enumerate(((-18, -12.4, 1, (13, 2, 13)),
            (4, -12.4, -3, (15, 2, 9)), (-6, 0, 11.2, (17, 15, 2)),
            (18, 0, 11.2, (12, 17, 2)), (8, 12.4, 2, (17, 2, 13)))):
        toy.box('patch plate', (x, y, z), size, p['green'] if index % 2 == 0 else p['milk'], root)
        axis = 'Y' if y else 'Z'
        for dx in (-size[0] * .35, size[0] * .35):
            at = (x + dx, y + (-1.6 if y < 0 else 1.6 if y > 0 else 0), z + (1.6 if not y else 0))
            detail.bolt('patch bolt', at, .7, p['butter'], root, axis)
    engine(root, p, (-33, 4, 1), 12, 21, 'milk')
    engine(root, p, (-22, -17, -7), 4, 12, 'green', 1)
    for y, z in ((-7, -2), (7, -2), (0, 10)):
        kit.barrel('blunt ram spike', (36, y, z), 3, 9, p['butter'], root,
            top=.8, sides=8, round_=.6)
    detail.pipe('patch conduit', [(-22, -15, -7), (8, -15, -7), (24, -11, -3)], 1, p, root)
    for x in (-9, -3, 3):
        window((x, -11.8, 6), 1.3, p, root)
    toy.box('cockpit angry brow', (29, -7.5, 7.5), (10, 3, 1.5), p['butter'], root)
    bridge(root, p, (-8, 0, 13), 5)
    return ((-18, 0, 13), (-29, -5, 1), (25, 0, -12), (0, -16, -2), (15, 0, 14))


def courier(root, p):
    kit.prism('courier dart', [(-26, -5), (39, -2), (28, 3),
        (-12, 7), (-26, 5)], -6, 6, p['red'], root, 1.7)
    toy.ball('courier canopy rim', (19, 0, 6), (9, 6, 2), p['milk'], root)
    toy.ball('courier canopy', (18, 0, 8), (8, 5.5, 5), p['green'], root)
    for side in (-1, 1):
        engine(root, p, (-25, side * 12, 0), 6, 17, 'milk', 0 if side < 0 else 1)
        kit.pipe('courier engine strut', [(-19, side * 5, 1), (-21, side * 12, 1)],
            2, p['green'], root, sides=12)
        fin = kit.prism('courier fin', [(-34, 1), (-21, 1), (-27, 12),
            (-34, 14)], -1, 1, p['butter'], root, .7)
        fin.location.y = side * 13
        fin.rotation_euler.x = side * math.radians(-35)
        for x in (9, 17, 25):
            window((x, side * 6.5, 0), 1, p, root, side)
    detail.pipe('courier top feed', [(-17, 0, 8), (-6, 0, 9), (8, 0, 8)], .7, p, root)
    for x in (-13, -2, 9):
        toy.box('courier top panel', (x, 0, 7.2 - (x + 13) * .07),
            (9.5, 9, .8), p['red'], root)
    toy.ball('courier nose cap', (36, 0, 0), (4, 4, 2.4), p['milk'], root)
    for side in (-1, 1):
        toy.drum('courier sensor', (28, side * 6, -3), 2, 5, p['butter'], root)
        detail.bolt('sensor light', (31, side * 6, -3), 1.3, p['glow'], root, 'X')
    return ((-17, 0, 9), (-28, 0, 0), (27, 0, -5), (-5, -8, 0), (6, 0, 8))


def build(kind):
    kit.reset()
    p, root = toy.palette(), kit.empty('toy_ship_' + kind.replace('-', '_'))
    builders = {'tanker': tanker, 'liner': liner, 'tug': tug,
        'police-cutter': police, 'raider': raider, 'courier': courier}
    positions = builders[kind](root, p)
    for family, at in zip(('power', 'cruise', 'maneuver', 'cargo', 'utility'), positions):
        port(root, p, family, at)
    length = {'tanker': 120, 'liner': 160, 'tug': 80,
        'police-cutter': 90, 'raider': 100, 'courier': 65}[kind]
    extent = toy.bounds(root)
    scale = length / (extent[0][1] - extent[0][0])
    for obj in root.children:
        obj.location *= scale
        obj.scale *= scale
    detail.finish(root)
    root['detail_revision'] = 2
    root['concept'] = 'assets/concepts/toy/ships/' + kind + '-flight.webp'
    toy.save(root, 'ship-' + kind, 40000, length * 1.35)
