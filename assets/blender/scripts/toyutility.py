"""build the fuel and repair utility ships."""

import math

import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic


def arm(root, p, name, points, radius=2):
    kit.pipe(name, points, radius, p['butter'], root, corner=2, sides=12)
    for at in points[1:-1]:
        toy.drum(name + ' hinge', at, radius * 1.6, radius * 2.4, p['green'], root, 'Y')


def refueller(root, p):
    toy.drum('fuel drum', (0, 0, 0), 20, 34, p['green'], root, 'Y')
    for side in (-1, 1):
        y = side * 19
        toy.drum('hose reel flange', (0, y, 0), 16, 2, p['red'], root, 'Y')
        toy.drum('hose reel spool', (0, y + side * 3, 0), 12, 4, p['dark'], root, 'Y')
        toy.drum('hose outer flange', (0, y + side * 6, 0), 16, 2, p['red'], root, 'Y')
        for a in range(0, 360, 90):
            angle = math.radians(a)
            detail.bolt('reel latch', (math.cos(angle) * 14, y + side * 7.4,
                math.sin(angle) * 14), .8, p['butter'], root, 'Y')
    toy.box('fuel cab tongue', (28, 0, -4), (30, 13, 9), p['milk'], root)
    traffic.bridge(root, p, (29, 0, 2), 6)
    arm(root, p, 'fuel boom', [(-3, 0, 19), (-3, 0, 29), (29, 0, 45), (43, 0, 38)], 2)
    kit.pipe('fuel boom hose', [(0, -24, 0), (12, -24, -3), (20, -10, 18),
        (2, -3, 30), (30, -3, 43), (37, -3, 29), (44, 0, 36)], 1, p['red'], root, corner=4, sides=12)
    detail.tube('fuel nozzle', (46, 0, 37), 2.8, 1.5, 7, p['milk'], root)
    for i, y in enumerate((-15, 15)):
        traffic.engine(root, p, (-29, y, 0), 7, 14, 'milk', i)
    return ((-9, -9, 18), (-22, 0, -3), (12, 0, -20), (0, -28, 0), (38, 0, 2))


def spanner(root, p, at, material):
    x, y, z = at
    toy.box('spanner stem', (x, y, z), (2, 2, 12), material, root)
    kit.pipe('spanner jaw', [(x - 3, y, z + 10), (x - 4, y, z + 6),
        (x, y, z + 4), (x + 4, y, z + 6), (x + 3, y, z + 10)],
        1.3, material, root, corner=1, sides=10)


def repairTender(root, p):
    deck = toy.box('work tray', (0, 0, -4), (68, 55, 7), p['milk'], root)
    detail.seam('deck seams', deck, [(0, (-20, -5, 10, 25)), (1, (-16, 0, 16))], .3)
    for side in (-1, 1):
        toy.box('tray side', (3, side * 28, 0), (66, 4, 12), p['red'], root)
        mount = kit.empty('service arm mount', root, (0, side * 28, 3))
        arm(mount, p, 'service arm', [(0, 0, 0), (9, side * 10, 0), (20, side * 20, 2)], 2)
        for dx in (-3, 3):
            toy.box('service clamp jaw', (20 + dx, side * 50, 5), (2, 7, 8), p['milk'], root)
        traffic.window((21, side * 30.6, 1), 2.4, p, root, side)
    toy.box('tray front', (35, 0, 0), (4, 58, 12), p['red'], root)
    toy.box('workshop rear', (-26, 0, 10), (18, 42, 26), p['milk'], root)
    toy.box('workshop roof', (-25, 0, 25), (21, 45, 4), p['green'], root)
    toy.box('tool rack recess', (-15.8, 0, 12), (.6, 31, 18), p['dark'], root)
    for y, role in ((-10, 'butter'), (0, 'green'), (10, 'red')):
        mount = kit.empty('rack tool mount', root, (-14.8, y, 10))
        mount.rotation_euler.z = math.pi / 2
        spanner(mount, p, (0, 0, 0), p[role])
    traffic.bridge(root, p, (-25, 0, 29), 6)
    toy.drum('magnet arm base', (9, 0, 1), 5, 3, p['green'], root, 'Z')
    arm(root, p, 'magnet arm', [(9, 0, 3), (9, 0, 13), (22, 0, 20), (29, 0, 10)], 2)
    toy.drum('service magnet', (29, 0, 8), 4, 2, p['red'], root, 'Z')
    for i, y in enumerate((-20, 20)):
        traffic.engine(root, p, (-40, y, 5), 8, 14, 'red', i)
    return ((-23, -16, 28), (-37, 0, 0), (3, 0, -9), (14, -31, 0), (-23, 16, 28))


def build(name):
    kit.reset()
    root, p = kit.empty('toy_ship_' + name), toy.palette()
    points = {'refueller': refueller, 'repair-tender': repairTender}[name](root, p)
    for family, at in zip(('power', 'cruise', 'maneuver', 'cargo', 'utility'), points):
        traffic.port(root, p, family, at)
    detail.finish(root)
    root['detail_revision'] = 3
    root['concept'] = 'assets/concepts/toy/ships/ship-' + name + '-meadow.webp'
    toy.save(root, 'ship-' + name, 40000, 155)
