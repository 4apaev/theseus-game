"""build six distinct station worlds from their concept frames."""

import json
import math
from pathlib import Path

import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic
import toytowing as towing
import toyutility

skins = {'market': 'sunny', 'mine': 'rust', 'lab': 'ice',
    'relay': 'grape', 'ship-yard': 'coral', 'gas-skimmer': 'mint'}


def palette(name):
    p = toy.palette()
    path = Path(__file__).resolve().parents[2] / 'concepts/toy/skins/skins.json'
    colours = json.loads(path.read_text())[skins[name]]
    for role, material in p.items():
        colour = (*kit.srgb(colours['toy-' + role]), 1)
        shader = material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = colour
        material.diffuse_color = colour
        if role == 'glow':
            shader.inputs['Emission Color'].default_value = colour
    return p


def windows(root, p, radius, z, count=10):
    for i in range(count):
        a = i * math.tau / count
        mount = kit.empty('window mount', root, (radius * math.cos(a), radius * math.sin(a), z))
        mount.rotation_euler.z = a + math.pi / 2
        traffic.window((0, 0, 0), 2.6, p, mount)


def hall(root, p, at, radius=25, height=30):
    mount = kit.empty('hall mount', root, at)
    traffic.drum('service hall', (0, 0, height / 2), radius, height, p['milk'], mount, 'Z')
    traffic.drum('hall roof', (0, 0, height + 1), radius + 2, 3, p['red'], mount, 'Z')
    windows(mount, p, radius + .45, height * .6, 8)
    toy.box('human door frame', (0, -radius - .8, 1.8), (2.4, 1, 3.6), p['red'], mount)
    toy.box('human door', (0, -radius - 1.45, 1.5), (1.6, .25, 3), p['dark'], mount)
    return mount


def pads(root, p, radius, z):
    for i, a in enumerate((0, math.pi / 2, math.pi, math.pi * 1.5)):
        x, y = radius * math.cos(a), radius * math.sin(a)
        kit.pipe('pad support', [(0, 0, z - 20), (x, y, z - 3)], 7, p['red'], root, sides=12)
        traffic.drum('landing pad base', (x, y, z), 38, 8, p['milk'], root, 'Z')
        traffic.drum('landing pad deck', (x, y, z + 4.5), 34, .5, p['dark'], root, 'Z')
        kit.ring('landing target', (x, y, z + 5.1), 21, .7, p['butter'], root, 'Z')
        for n in range(8):
            angle = n * math.tau / 8
            toy.ball('pad nav lamp', (x + 36 * math.cos(angle), y + 36 * math.sin(angle), z + 5),
                (1.5, 1.5, .8), p['glow'], root)
        obj = kit.empty('berth' if i == 0 else 'berth_' + chr(97 + i), root, (x, y, z + 6))
        obj['size'] = 70


def aerial(root, p, at, radius=18, tilt=0):
    mount = kit.empty('dish mast', root, at)
    mount.rotation_euler.y = tilt
    traffic.drum('dish neck', (0, 0, 0), 4, 15, p['red'], mount, 'Z')
    toy.dish('comms bowl', (0, 0, 8), radius, p['milk'], mount)
    traffic.drum('dish feed', (0, 0, 15), 1.8, 17, p['red'], mount, 'Z')
    toy.ball('dish tip', (0, 0, 24), (3,) * 3, p['butter'], mount)


def market(root, p):
    for radius, z, height in ((111, -30, 65), (99, 8, 22), (77, 24, 13)):
        towing.rock('terraced market rock', (0, 0, z), (radius, radius, height), p['red'], root)
        traffic.drum('market terrace', (0, 0, z + height * .7), radius, 5, p['green'], root, 'Z')
    hall(root, p, (0, 0, 35), 34, 55)
    hall(root, p, (0, 0, 94), 24, 24)
    for i in range(6):
        a = i * math.tau / 6
        mount = hall(root, p, (69 * math.cos(a), 69 * math.sin(a), 31), 15, 18)
        for n in range(12):
            angle = n * math.tau / 12
            petal = toy.box('striped stall awning', (20 * math.cos(angle), 20 * math.sin(angle), 22.5),
                (8, 7, 3), p['milk'] if n % 2 else p['butter'], mount)
            petal.rotation_euler.z = angle
        for n in (-1, 0, 1):
            toy.box('market crate', (n * 6, -20, 3), (5, 5, 5), p['butter'], mount)
    pads(root, p, 146, 26)
    aerial(root, p, (0, 0, -83), 20, math.pi)
    return {'exchange': (0, 0, 95), 'rigging': (69, 0, 54), 'comms': (0, 0, -90), 'chart': (0, 0, 121)}


def mine(root, p):
    toy.box('ore transfer crossbeam', (0, 0, -30), (154, 20, 20), p['milk'], root)
    for side in (-1, 1):
        towing.rock('split ore rock', (side * 67, 15, 0), (48, 60, 108), p['red'], root, 5 + side)
        mount = kit.empty('spin drill', root, (side * 38, -68, 8))
        mount.rotation_euler.y = -side * math.pi / 2
        traffic.drum('drill motor', (0, 0, -8), 25, 20, p['milk'], mount, 'Z')
        for n in range(5):
            kit.barrel('drill cone ridge', (0, 0, n * 6), 23 - n * 4, 8,
                p['green'], mount, 'Z', top=max(1, 19 - n * 4), sides=16, round_=.5)
    toy.box('extraction hall', (0, 0, 91), (112, 32, 27), p['milk'], root)
    for x in (-42, -21, 0, 21, 42):
        traffic.window((x, -16.5, 92), 3, p, root)
    for x in (-29, 0, 29):
        kit.pipe('ore chute', [(x, -15, 80), (x, -40, 32), (x, -55, -70)], 7, p['green'], root, sides=12)
        toy.dish('ore hopper', (x, -55, -91), 16, p['butter'], root)
        traffic.drum('ore outlet', (x, -55, -99), 6, 20, p['milk'], root, 'Z')
        for n in (-1, 1):
            towing.rock('ore chunk', (x + n * 5, -55, -82), (5, 5, 5), p['red'], root, 8 + n)
    pads(root, p, 150, -10)
    aerial(root, p, (64, 0, 119), 13)
    return {'exchange': (0, -20, 105), 'rigging': (67, 0, -10), 'comms': (64, 0, 137), 'chart': (0, 0, 107)}


def lab(root, p):
    hall(root, p, (0, 0, -32), 30, 96)
    traffic.drum('instrument tower', (0, 0, 92), 15, 45, p['red'], root, 'Z')
    windows(root, p, 15.5, 96, 6)
    traffic.drum('instrument mast', (0, 0, 133), 3, 35, p['green'], root, 'Z')
    for i in range(3):
        a = i * math.tau / 3
        x, y = 87 * math.cos(a), 87 * math.sin(a)
        kit.pipe('lab corridor', [(0, 0, 0), (x, y, 0)], 11, p['milk'], root, sides=12)
        mount = hall(root, p, (x, y, -25), 43, 25)
        toy.ball('opaque lab dome', (0, 0, 30), (42, 42, 34), p['butter'], mount)
        for turn in (0, math.pi / 2):
            points = [(42.4 * math.cos(t) * math.cos(turn), 42.4 * math.cos(t) * math.sin(turn),
                30 + 34.4 * math.sin(t)) for t in [n * math.pi / 12 for n in range(13)]]
            kit.pipe('dome rib', points, 2, p['milk'], mount, sides=8)
        aerial(mount, p, (0, 0, 68), 10)
    toy.ball('underslung reactor', (0, 0, -66), (26, 26, 22), p['red'], root)
    pads(root, p, 154, -23)
    return {'exchange': (87, 0, 45), 'rigging': (0, 0, -28), 'comms': (0, 0, 124), 'chart': (-43, 75, 45)}


def relay(root, p):
    towing.rock('relay asteroid', (0, 0, -62), (77, 74, 52), p['red'], root)
    hall(root, p, (0, 0, -18), 36, 32)
    for i in range(4):
        traffic.drum('relay stacked drum', (i * 3 - 4, 0, 37 + i * 36), 24 - i * 3, 33,
            p['red'] if i % 2 else p['milk'], root, 'Z')
    for i, (x, y, z, radius, tilt) in enumerate(((-66, 0, 78, 36, -.7), (64, 0, 48, 32, .7),
            (34, 35, 132, 28, .6), (-20, -42, 155, 28, -.4), (6, 0, 202, 48, .4))):
        kit.pipe('relay branch cable', [(0, 0, z - 20), (x, y, z - 10), (x, y, z)], 5, p['green'], root, sides=12)
        aerial(root, p, (x, y, z), radius, tilt)
    pads(root, p, 123, -24)
    return {'exchange': (0, -36, 2), 'rigging': (36, 0, 2), 'comms': (0, 0, 166), 'chart': (0, 0, 28)}


def shipYard(root, p):
    deck = toy.box('yard workshop floor', (0, 0, -23), (245, 113, 13), p['green'], root)
    detail.seam('floor joints', deck, [(0, (-75, -25, 25, 75))], .5)
    for x in (-95, 0, 95):
        points = [(x, 69 * math.cos(a), 4 + 92 * math.sin(a)) for a in [n * math.pi / 16 for n in range(17)]]
        kit.pipe('yard arch', points, 11, p['red'], root, sides=12)
        toy.box('inside gantry', (x, 0, 70), (7, 104, 7), p['butter'], root)
        toyutility.arm(root, p, 'workshop tool arm', [(x, 25, 67), (x + 12, 10, 40), (x + 8, 0, 12)], 2)
    for side in (-1, 1):
        wall = toy.box('workshop wall', (0, side * 63, 0), (246, 9, 45), p['milk'], root)
        for x in (-90, -60, -30, 0, 30, 60, 90):
            traffic.window((x, side * 68, 9), 3, p, root, side)
        for x in (-80, 0, 80):
            traffic.drum('yard belly tank', (x, side * 36, -45), 14, 40, p['milk'], root)
    for x in (-33, -11, 11, 33):
        toy.box('yard lower radiator', (x, 0, -57), (9, 50, 41), p['butter'], root)
    pads(root, p, 163, -14)
    hall(root, p, (94, 0, 83), 18, 20)
    aerial(root, p, (94, 0, 108), 13)
    return {'exchange': (94, 0, 107), 'rigging': (0, 0, 0), 'comms': (94, 0, 132), 'chart': (-95, 0, 91)}


def gasSkimmer(root, p):
    toy.ball('separator vessel', (0, 0, 0), (51, 51, 73), p['red'], root)
    for z, radius in ((-38, 48), (0, 55), (38, 48)):
        traffic.drum('separator collar', (0, 0, z), radius, 8, p['milk'], root, 'Z')
        windows(root, p, radius + .5, z, 8)
    for i in range(3):
        a = i * math.tau / 3
        mount = kit.empty('scoop mount', root)
        mount.rotation_euler.z = a
        kit.pipe('scoop transfer pipe', [(38, 0, 10), (87, 0, 10), (114, 0, 35)], 11, p['green'], mount, sides=12)
        bowl = kit.empty('scoop bowl mount', mount, (115, 0, 36))
        bowl.rotation_euler.y = math.pi / 2
        toy.dish('collector scoop', (0, 0, 0), 48, p['milk'], bowl)
        toy.dish('collector inner bowl', (0, 0, 5), 43, p['red'], bowl)
        kit.ring('collector lip', (0, 0, 21), 47, 2, p['green'], bowl, 'Z')
    traffic.drum('tether neck', (0, 0, -93), 7, 38, p['butter'], root, 'Z')
    traffic.drum('tether start', (0, 0, -139), 1.2, 55, p['green'], root, 'Z')
    anchor = kit.empty('tether', root, (0, 0, -167))
    anchor['toward'] = 'gas-giant'
    pads(root, p, 105, -27)
    hall(root, p, (0, 0, 64), 21, 19)
    aerial(root, p, (0, 0, 90), 16)
    return {'exchange': (0, 0, 86), 'rigging': (51, 0, 0), 'comms': (0, 0, 113), 'chart': (0, 0, 88)}



def fittings(root, p, name):
    if name == 'lab':
        for z in (-28, -3, 24, 52):
            kit.ring('tower service collar', (0, 0, z), 31, 2, p['green'], root, 'Z')
        for x in (-19, 19):
            kit.pipe('lab coolant riser', [(x, -28, -22), (x, -35, -16), (x, -35, 45), (x, -28, 51)],
                2, p['red'], root, sides=8)
    if name == 'relay':
        for i in range(4):
            mount = kit.empty('relay instrument band', root, (i * 3 - 4, 0, 37 + i * 36))
            radius = 24 - i * 3
            windows(mount, p, radius + .6, 0, 6)
            for z in (-14, 14):
                kit.ring('relay collar', (0, 0, z), radius + .7, 1.3, p['green'], mount, 'Z')
    if name == 'ship-yard':
        for x in (-95, 0, 95):
            for angle in (.3, .8, 1.3, 1.84, 2.34, 2.84):
                y, z = 69 * math.cos(angle), 4 + 92 * math.sin(angle)
                toy.ball('arch lamp bezel', (x + 10.5, y, z), (2, 4, 4), p['butter'], root)
                toy.ball('arch nav lamp', (x + 12.2, y, z), (.7, 2, 2), p['glow'], root)
        for x in (-80, 0, 80):
            for side in (-1, 1):
                kit.pipe('yard coolant pipe', [(x - 24, side * 69, -8), (x - 24, side * 74, -30),
                    (x + 24, side * 74, -30), (x + 24, side * 69, -8)], 3, p['red'], root, sides=8)
    if name == 'gas-skimmer':
        for i in range(6):
            a = i * math.tau / 6
            mount = kit.empty('separator valve mount', root, (57 * math.cos(a), 57 * math.sin(a), 0))
            mount.rotation_euler.z = a
            traffic.drum('separator valve', (0, 0, 0), 4, 7, p['butter'], mount)
            kit.ring('valve wheel', (4, 0, 0), 4, .7, p['red'], mount, 'X')


builders = {'market': market, 'mine': mine, 'lab': lab, 'relay': relay,
    'ship-yard': shipYard, 'gas-skimmer': gasSkimmer}


def build(name):
    kit.reset()
    root, p = kit.empty('toy_station_' + name), palette(name)
    for key, at in builders[name](root, p).items():
        kit.empty('spot_' + key, root, at)
    if name in ('market', 'ship-yard'):
        for i, at in enumerate(((-36, -36, 36), (36, -36, 36), (36, 36, 36), (-36, 36, 36))):
            point = (at[0], at[1], -15.9) if name == 'ship-yard' else at
            kit.empty('walk_' + chr(97 + i), root, point)
    fittings(root, p, name)
    root['skin'] = skins[name]
    root['concept'] = 'assets/concepts/toy/station/station-' + name + '-meadow.webp'
    root['detail_revision'] = 3
    detail.finish(root)
    toy.save(root, 'station-' + name, 80000, 550 if name == 'relay' else 490)
