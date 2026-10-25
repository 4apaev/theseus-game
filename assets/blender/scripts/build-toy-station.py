"""build a station world with four ship berths."""

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy


def pad(root, p, name, at, size):
    x, y, z = at
    toy.drum(name + ' deck', at, size / 2, 5, p['milk'], root, 'Z')
    toy.drum(name + ' inset', (x, y, z + 3), size * .43, .5, p['green'], root, 'Z')
    toy.drum(name + ' underside', (x, y, z - 10), size * .28, 12, p['red'], root, 'Z')
    spot = kit.empty(name, root, (x, y, z + 25))
    spot['size'] = size
    for angle in (0, 120, 240):
        a = math.radians(angle)
        toy.drum(name + ' beacon', (x + math.cos(a) * size * .43,
            y + math.sin(a) * size * .43, z + 5), 1.4, 3, p['glow'], root, 'Z')


def halls(root, p):
    toy.box('market hall', (0, 10, 120), (72, 55, 45), p['butter'], root)
    for x in (-25, -12, 1, 14, 27):
        toy.drum('market roof rib', (x, 10, 140), 26, 5, p['red'], root)
    toy.box('market door', (0, -18, 119), (18, 2, 22), p['dark'], root)
    toy.box('market deck', (0, -38, 99), (76, 34, 5), p['milk'], root)
    toy.box('human door', (25, -18.4, 103.25), (3, 1, 3), p['dark'], root)
    for x in (-32, 32):
        toy.box('market rail', (x, -40, 102.3), (1, 24, 1.1), p['red'], root)
    toy.box('yard hall', (100, 0, 57), (65, 65, 58), p['red'], root)
    toy.box('yard opening', (100, -33.5, 58), (42, 2, 38), p['dark'], root)
    toy.box('yard floor', (100, -45, 35), (64, 30, 4), p['milk'], root)
    toy.drum('comms pedestal', (-110, 0, 67), 22, 34, p['red'], root, 'Z')
    toy.dish('comms dish', (-110, 0, 85), 44, p['green'], root)
    toy.drum('comms receiver', (-110, 0, 102), 4, 25, p['butter'], root, 'Z')
    toy.ball('chart dome', (18, 100, 78), (34, 31, 29), p['milk'], root)
    toy.drum('chart collar', (18, 100, 63), 32, 9, p['green'], root, 'Z')
    for name, at in (('exchange', (0, -20, 146)), ('rigging', (100, -35, 90)),
            ('comms', (-110, 0, 124)), ('chart', (18, 100, 110))):
        kit.empty('spot_' + name, root, at)


def build():
    kit.reset()
    p, root = toy.palette(), kit.empty('toy_station')
    toy.ball('world core', (0, 0, 0), (145, 118, 85), p['green'], root)
    toy.ball('world left lobe', (-75, 0, 25), (75, 95, 74), p['green'], root)
    toy.ball('world right lobe', (78, 0, -16), (80, 101, 70), p['green'], root)
    halls(root, p)
    for name, at in zip(('a', 'b', 'c', 'd'),
            ((-18, -38, 101.75), (18, -38, 101.75), (18, -48, 101.75), (-18, -48, 101.75))):
        kit.empty('walk_' + name, root, at)
    for name, at, size in (('berth', (10, -140, 120), 95), ('berth_b', (-160, -65, 32), 85),
            ('berth_c', (158, -83, 22), 100), ('berth_d', (30, 145, 110), 120)):
        pad(root, p, name, at, size)
    for index, points in enumerate(([(0, -20, 96), (-75, -45, 78), (-111, 0, 65)],
            [(20, -35, 91), (78, -75, 63), (100, -30, 39)],
            [(10, 30, 97), (30, 65, 74), (18, 100, 63)])):
        kit.pipe('fat pipe ' + str(index), points, 5, p['milk'], root, corner=12, sides=12)
    toy.save(root, 'station', 80000, 540)


if __name__ == '__main__':
    build()
