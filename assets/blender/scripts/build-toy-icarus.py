"""build the sheltered antimatter plant and its emitter."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy
import toydetail as detail
import toytraffic as traffic
import toystationkits as stations
import toyorbit as orbit


def emitter(root, p):
    mount = kit.empty('beam emitter assembly', root, (134, 0, 0))
    mount.rotation_euler.y = math.pi / 2
    toy.dish('emitter dish', (0, 0, 0), 77, p['butter'], mount)
    kit.ring('emitter rim', (0, 0, 34), 77, 3, p['green'], mount, 'Z')
    for i in range(8):
        a = i * math.tau / 8
        toy.ball('emitter rim clamp', (77 * math.cos(a), 77 * math.sin(a), 34),
            (3, 3, 4), p['red'], mount)
        toy.ball('emitter nav lamp', (77 * math.cos(a), 77 * math.sin(a), 38),
            (1.5, 1.5, 1), p['glow'], mount)
    traffic.drum('beam feed housing' , (0, 0, 19), 15, 34, p['green'], mount, 'Z')
    traffic.drum('beam lens', (0, 0, 37), 11, 1, p['glow'], mount, 'Z')
    spot = kit.empty('beam_origin', mount, (0, 0, 39))
    spot['source_axis'] = '+z'
    spot['range_ly'] = 7
    return mount


def build():
    kit.reset()
    root, p = kit.empty('toy_station_icarus'), toy.palette()
    traffic.drum('plant spine', (0, 0, 0), 18, 269, p['red'], root)
    for y, z in ((-56, -25), (56, -25), (0, 68)):
        mount = kit.empty('star shield mount', root, (-112, y, z))
        mount.rotation_euler.y = -math.pi / 2
        toy.ball('star shield back', (0, 0, 0), (66, 66, 8), p['green'], mount)
        toy.ball('star shield face', (0, 0, 4), (64, 64, 9), p['butter'], mount)
        kit.ring('shield rim', (0, 0, 3), 65, 2, p['milk'], mount, 'Z')
        for i in range(8):
            a = i * math.tau / 8
            toy.ball('shield rim fastener', (65 * math.cos(a), 65 * math.sin(a), 5),
                (2.5, 2.5, 2.5), p['red'], mount)
        kit.pipe('shield strut' , [(-75, y * .8, z * .8), (-112, y, z)], 6, p['red'], root, sides=12)
    for x in (-35, 24):
        for y in (-28, 28):
            traffic.drum('antimatter vessel', (x, y, 0), 21, 91, p['milk'], root, 'Z')
            for z in (-29, 29):
                kit.ring('vessel collar', (x, y, z), 21.3, 2.1, p['red'], root, 'Z')
            traffic.window((x, y - 21.6, 0), 4, p, root)
            kit.pipe('plant feed', [(x, y, 48), (x, y, 57), (x + 21, y, 57), (x + 21, y, 8)],
                3.2, p['red'], root, corner=5, sides=12)
    for i in range(6):
        a = i * math.tau / 6
        mount = kit.empty('radiator mount', root, (70, 0, 0))
        mount.rotation_euler.x = a
        panel = toy.box('radiator fin', (0, 100, 0), (17, 155, 6), p['dark'], mount)
        detail.seam('radiator channels', panel, [(1, (40, 65, 90, 115, 140, 165))], .5)
        toy.box('radiator edge', (10, 100, 0), (2, 154, 7), p['green'], mount)
        toy.ball('radiator nav tip', (0, 176, 0), (2, 2, 2), p['glow'], mount)
    stations.hall(root, p, (-6, 0, 50), 24, 26)
    stations.aerial(root, p, (-6, 0, 83), 11)
    traffic.drum('sheltered pad', (0, -79, -28), 38, 8, p['milk'], root, 'Z')
    traffic.drum('sheltered deck', (0, -79, -23.5), 35, .5, p['green'], root, 'Z')
    kit.ring('sheltered pad target', (0, -79, -22.8), 23, 1, p['butter'], root, 'Z')
    kit.pipe('pad corridor', [(0, -29, -33), (0, -79, -33)], 7, p['red'], root, sides=12)
    berth = kit.empty('berth', root, (0, -79, -22))
    berth['size'] = 70
    emitter(root, p)
    for key, at in {'exchange': (-6, 0, 80), 'rigging': (0, -79, -18),
            'comms': (-6, 0, 105), 'chart': (134, 0, 65)}.items():
        kit.empty('spot_' + key, root, at)
    root['star_facing_axis'] = '-x'
    root['orbit_au'] = .05
    root['detail_revision'] = 3
    root['concept'] = 'assets/concepts/toy/station/station-icarus-meadow.webp'
    detail.finish(root)
    toy.save(root, 'station-icarus', 80000, 610)
    kit.reset()
    root, p = kit.empty('icarus_emitter'), toy.palette()
    emitter(root, p).location = (0, 0, 0)
    root['detail_revision'] = 3
    toy.save(root, 'icarus-emitter', 12000, 260, 'icarus')
    orbit.sprite('icarus-emitter', 'icarus')


build()
