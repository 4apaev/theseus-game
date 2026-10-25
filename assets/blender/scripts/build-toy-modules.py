"""build five modules for the toy hull ports."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy

families = {'reactor': 'power', 'cruise-drive': 'cruise',
    'maneuver': 'maneuver', 'cargo-pod': 'cargo', 'antenna': 'utility'}


def module(root, p, name):
    toy.drum('mount', (0, 0, .65), 2.8, 1, p['dark'], root, 'Z')
    if name == 'reactor':
        toy.drum('reactor shell', (0, 0, 5), 5, 7, p['red'], root, 'Z')
        toy.drum('reactor lid', (0, 0, 9.2), 4.4, 1, p['green'], root, 'Z')
        toy.ball('power glow', (0, 0, 10.2), (2.5, 2.5, .5), p['glow'], root)
    elif name == 'cruise-drive':
        toy.drum('drive shell', (0, 0, 6), 5.8, 9, p['green'], root, 'Z')
        toy.drum('drive throat', (0, 0, 11.2), 4.7, 1, p['dark'], root, 'Z')
        toy.drum('drive glow', (0, 0, 11.9), 3.6, .3, p['glow'], root, 'Z')
        kit.empty('exhaust', root, (0, 0, 12.2))
    elif name == 'maneuver':
        toy.box('manifold', (0, 0, 3), (7, 7, 3), p['milk'], root)
        for x, y in ((-4, 0), (4, 0), (0, 4)):
            toy.drum('thruster', (x, y, 6), 2.4, 4, p['red'], root, 'Z')
            toy.drum('thruster throat', (x, y, 8.8), 1.7, .5, p['dark'], root, 'Z')
            kit.empty('exhaust', root, (x, y, 9.2))
    elif name == 'cargo-pod':
        toy.box('cargo body', (0, 0, 5), (12, 10, 7), p['butter'], root)
        for x in (-4, 4):
            toy.box('cargo strap', (x, 0, 8.9), (1.5, 9, 1), p['red'], root)
    elif name == 'antenna':
        toy.drum('antenna stem', (0, 0, 4), 1, 5, p['red'], root, 'Z')
        toy.dish('antenna dish', (0, 0, 7), 5.8, p['milk'], root)
        toy.ball('receiver', (0, 0, 9), (1, 1, 1), p['butter'], root)


def build():
    for name, family in families.items():
        kit.reset()
        p, root = toy.palette(), kit.empty('toy_module_' + name)
        root['family'], root['mount_radius'], root['mount_axis'] = family, 2.8, '+y'
        root['source_mount_axis'] = '+z'
        module(root, p, name)
        toy.save(root, name, 3000, 24, 'modules')


if __name__ == '__main__':
    build()
