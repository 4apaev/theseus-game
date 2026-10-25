"""build three weapon toys on the standard module mount."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy
import toyorbit as orbit
import toydetail as detail


def build(name):
    kit.reset()
    root, p = kit.empty('toy_module_' + name), toy.palette()
    toy.drum('weapon mount', (0, 0, .65), 2.8, 1, p['dark'], root, 'Z')
    toy.drum('turret base', (0, 0, 2), 3.8, 1.5, p['red'], root, 'Z')
    if name == 'cannon':
        toy.box('cannon breech', (-1, 0, 4), (6, 5, 4), p['green'], root)
        detail.tube('cannon hollow barrel', (5, 0, 4), 1.7, 1.05, 8, p['milk'], root)
        toy.drum('cannon dark bore', (1.4, 0, 4), 1.03, .15, p['dark'], root)
        kit.empty('muzzle', root, (9.1, 0, 4))
    elif name == 'missile-pod':
        toy.box('missile pod case', (0, 0, 4.5), (7, 6.5, 5), p['green'], root)
        toy.box('missile pod face', (3.8, 0, 4.5), (.5, 6, 4.5), p['dark'], root)
        for y in (-1.7, 1.7):
            for z in (3.3, 5.7):
                kit.barrel('missile nose', (4.5, y, z), .85, 1.6, p['red'], root,
                    'X', top=.1, sides=12, round_=.1)
                kit.empty('muzzle', root, (5.4, y, z))
    else:
        toy.drum('beam generator', (0, 0, 4), 2.6, 3, p['green'], root, 'Z')
        mount = kit.empty('emitter tilt', root, (0, 0, 6))
        mount.rotation_euler.y = math.pi / 2
        toy.dish('beam dish', (0, 0, 0), 4.4, p['milk'], mount)
        toy.drum('beam feed', (0, 0, 1.8), .8, 3.6, p['red'], mount, 'Z')
        toy.ball('beam lens', (0, 0, 3.7), (1,) * 3, p['glow'], mount)
        kit.empty('muzzle', mount, (0, 0, 4.8))
    root['family'], root['mount_radius'], root['mount_axis'] = 'utility', 2.8, '+y'
    root['source_mount_axis'] = '+z'
    root['detail_revision'] = 3
    toy.save(root, name, 3000, 25, 'modules')
    orbit.sprite(name, 'modules')


for name in ('cannon', 'missile-pod', 'beam-emitter'):
    build(name)
