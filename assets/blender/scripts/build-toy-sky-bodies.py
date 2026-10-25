"""build six toy sky bodies and matching sprites."""

import math
import sys
from pathlib import Path

import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy
import toyorbit as orbit
import toytowing as towing


def band(root, p, latitude, width, role):
    mesh = bmesh.new()
    rings = []
    for row in range(7):
        lat = latitude - width / 2 + width * row / 6
        rings.append([mesh.verts.new((15.25 * math.cos(lat) * math.cos(n * math.tau / 48),
            15.25 * math.cos(lat) * math.sin(n * math.tau / 48), 15.25 * math.sin(lat))) for n in range(48)])
    for lower, upper in zip(rings, rings[1:]):
        for n in range(48):
            mesh.faces.new((lower[n], lower[(n + 1) % 48], upper[(n + 1) % 48], upper[n]))
    return kit.link('gas latitude band', mesh, p[role], root)


def craters(root, p, radius, count, role):
    for i in range(count):
        angle = i * 2.399963
        z = 1 - 2 * (i + .5) / count
        normal = Vector((math.sqrt(1 - z * z) * math.cos(angle), math.sqrt(1 - z * z) * math.sin(angle), z))
        mount = kit.empty('crater mount', root, normal * (radius - .1))
        mount.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
        size = radius * (.10 + .025 * (i % 3))
        kit.ring('rounded crater rim', (0, 0, 0), size, size * .18, p[role], mount, 'Z')
        toy.drum('crater floor', (0, 0, -.18), size * .75, .15, p[role], mount, 'Z')


def body(name):
    kit.reset()
    root, p = kit.empty('sky_' + name), toy.palette()
    size = 46
    if name == 'star':
        toy.ball('stellar core', (0, 0, 0), (13,) * 3, p['glow'], root)
        for i in range(14):
            a = i * math.tau / 14
            toy.ball('soft corona lobe', (12.7 * math.cos(a), 12.7 * math.sin(a), 0),
                (2.6, 2.6, 2.6), p['butter'], root)
        root['emitter'] = True
    elif name == 'gas-giant':
        toy.ball('gas giant', (0, 0, 0), (15,) * 3, p['butter'], root)
        for lat, width, role in ((-.65, .18, 'milk'), (-.24, .25, 'red'), (.19, .12, 'milk'), (.6, .22, 'red')):
            band(root, p, lat, width, role)
        for radius, thickness, role in ((21, 1.6, 'milk'), (24, 1.2, 'red'), (26.5, .6, 'butter')):
            ring = kit.ring('planet ring', (0, 0, 0), radius, thickness, p[role], root, 'Z')
            ring.rotation_euler.y = .22
        size = 76
    elif name == 'ice-world':
        toy.ball('ice world', (0, 0, 0), (13,) * 3, p['green'], root)
        for i, at in enumerate(((0, 0, 10), (0, 0, -10), (9, 1, 5), (-8, -6, 3), (3, 10, -4))):
            towing.rock('ice plate', at, (7, 7, 4), p['milk'], root, 31 + i)
    elif name == 'rocky-planet':
        toy.ball('rocky planet', (0, 0, 0), (13,) * 3, p['red'], root)
        craters(root, p, 13, 12, 'butter')
    else:
        radius = 9 if name == 'moon-pale' else 7
        toy.ball('moon body', (0, 0, 0), (radius,) * 3, p['milk'] if name == 'moon-pale' else p['dark'], root)
        craters(root, p, radius, 9, 'butter' if name == 'moon-pale' else 'green')
        size = 32
    root['detail_revision'] = 3
    root['display_asset'] = True
    root['radius_is_display_scale'] = True
    toy.save(root, name, 16000, size, 'sky')
    orbit.sprite(name, 'sky')


for name in ('star', 'rocky-planet', 'gas-giant', 'ice-world', 'moon-pale', 'moon-dark'):
    body(name)
