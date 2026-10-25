"""build orbit controls and export matching transparent sprites."""

import math
from pathlib import Path

import bpy

import paintkit as kit
import toykit as toy
import toytraffic as traffic

assets = Path(__file__).resolve().parents[2]


def sprite(name, subfolder):
    view = 'reverse' if name in ('orbit-apoapsis', 'orbit-periapsis', 'orbit-dv-gauge', 'orbit-moon', 'orbit-planet') else 'preview'
    source = assets / 'blender/renders/toy' / subfolder / (name + '-' + view + '.png')
    image = bpy.data.images.load(str(source), check_existing=False)
    width, height = image.size
    side = 512
    scaledWidth, scaledHeight = side, round(height * side / width)
    image.scale(scaledWidth, scaledHeight)
    pixels = list(image.pixels[:])
    square = bpy.data.images.new(name + ' sprite', width=side, height=side, alpha=True)
    target = [0.0] * (side * side * 4)
    offset = (side - scaledHeight) // 2
    for row in range(scaledHeight):
        start = (row + offset) * side * 4
        target[start:start + side * 4] = pixels[row * side * 4:(row + 1) * side * 4]
    square.pixels = target
    folder = assets / 'concepts/toy/sprites'
    folder.mkdir(parents=True, exist_ok=True)
    square.filepath_raw, square.file_format = str(folder / (name + '.png')), 'PNG'
    square.save()
    bpy.data.images.remove(image)
    bpy.data.images.remove(square)


def arrow(root, p, role, ring=False):
    toy.drum('handle shaft', (3, 0, 0), .5, 6, p[role], root)
    if ring:
        kit.ring('normal ring head', (8, 0, 0), 2.2, .6, p[role], root)
    else:
        kit.barrel('handle arrowhead', (7.5, 0, 0), 2, 4, p[role], root,
            'X', top=.1, sides=16, round_=.2)


def pin(root, p, name):
    role = 'red' if name == 'apoapsis' else 'green'
    toy.drum('pin stem', (0, 0, 2), .45, 4, p[role], root, 'Z')
    toy.drum('pin disc', (0, 0, 6), 2.8, 1, p[role], root, 'Y')
    kit.ring('pin milk ring', (0, -.8, 6), 1.8, .35, p['milk'], root, 'Y')
    marks = 2 if name == 'apoapsis' else 1
    for i in range(marks):
        toy.box('apsis tactile mark', (i * 1.2 - (marks - 1) * .6, -1, 6),
            (.4, .2, 1.5), p['milk'], root)


def globe(root, p, moon=False):
    radius = 8 if moon else 13
    toy.ball('moon body' if moon else 'planet body', (0, 0, 0), (radius,) * 3,
        p['milk'] if moon else p['green'], root)
    if moon:
        for at, size in (((3, -5.4, 4), 1.5), ((-4, -5.5, 2), 2), ((1, -7, -2), 1)):
            toy.ball('moon crater', at, (size, .45, size), p['butter'], root)
    else:
        for at, size in (((-5, -9, 5), (5, 3, 5)), ((7, -6, -4), (4, 4, 5)),
                ((1, 7, 7), (6, 5, 3))):
            toy.ball('planet land patch', at, size, p['milk'], root)


def model(name):
    kit.reset()
    root, p = kit.empty('orbit_' + name), toy.palette()
    size = 22
    if name == 'node':
        toy.ball('maneuver centre', (0, 0, 0), (2.5,) * 3, p['butter'], root)
        for key, angle, axis, role in (('prograde', 0, 'z', 'green'),
                ('retrograde', math.pi, 'z', 'red'), ('radial', math.pi / 2, 'z', 'butter'),
                ('normal', -math.pi / 2, 'y', 'milk')):
            mount = kit.empty('handle_' + key, root)
            setattr(mount.rotation_euler, axis, angle)
            arrow(mount, p, role, key == 'normal')
            mount['control'] = key
            mount['joint'] = True
        size = 32
    elif name.startswith('handle-'):
        key = name.removeprefix('handle-')
        arrow(root, p, {'prograde': 'green', 'retrograde': 'red', 'radial': 'butter', 'normal': 'milk'}[key], key == 'normal')
        root['control'] = key
    elif name in ('apoapsis', 'periapsis'):
        pin(root, p, name)
        size = 17
    elif name == 'dv-gauge':
        toy.box('gauge shell', (0, 0, 0), (26, 3, 7), p['milk'], root)
        toy.box('gauge inset', (0, -1.8, 0), (24, .3, 5), p['dark'], root)
        for i in range(10):
            segment = kit.empty('segment_' + str(i), root, (-10.5 + i * 2.3, -2.2, 0))
            segment['index'], segment['joint'] = i, True
            toy.box('gauge fill', (0, 0, 0), (1.7, .4, 3.5), p['green'], segment)
        size = 36
    else:
        globe(root, p, name == 'moon')
        size = 42 if name == 'planet' else 27
    root['detail_revision'] = 3
    root['ui_asset'] = True
    toy.save(root, 'orbit-' + name, 12000, size, 'orbit')
    sprite('orbit-' + name, 'orbit')


def build():
    for name in ('node', 'handle-prograde', 'handle-retrograde', 'handle-radial',
            'handle-normal', 'apoapsis', 'periapsis', 'dv-gauge', 'planet', 'moon'):
        model(name)
