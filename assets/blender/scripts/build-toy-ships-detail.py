"""build four toy ships with separate panels and deep engine nozzles."""

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import toykit as toy
import toyships
import toydetail as detail


def engines(root, p):
    for obj in list(root.children_recursive):
        if obj.type == 'MESH' and obj.name.startswith(('engine housing', 'engine nozzle', 'engine glow')):
            bpy.data.objects.remove(obj, do_unlink=True)
    for y in (-15, 15):
        toy.drum('engine housing', (-23.5, y, 0), 8, 12, p['green'], root)
        detail.tube('deep nozzle', (-32.5, y, 0), 7.8, 5.8, 7, p['milk'], root)
        kit.ring('nozzle rim', (-36.7, y, 0), 6.85, .55, p['red'], root)
        toy.drum('recessed engine light', (-29.8, y, 0), 5.4, .3, p['glow'], root)
        for angle in range(0, 360, 90):
            a = math.radians(angle)
            detail.bolt('engine rim bolt', (-37.7, y + math.cos(a) * 6.9,
                math.sin(a) * 6.9), .45, p['butter'], root, 'X')
        for x in (-23, -19):
            kit.ring('engine band', (x, y, 0), 8, .65, p['red'], root)
        toy.box('engine fin', (-22, y, 9), (10, 1.2, 6), p['butter'], root)


def hullPanels(root, p, kind):
    material = p['butter'] if kind == 'industrial' else p['green'] if kind == 'military' else p['red']
    for obj in root.children_recursive:
        if obj.type == 'MESH' and obj.name == 'hull':
            obj.data.materials[0] = material
    for side in (-1, 1):
        y = side * (8.5 if kind == 'research' else 12.7)
        for x in (-14, -5, 4):
            panel = toy.box('hull panel', (x, y, 0), (7.8, 1.8, 10), material, root)
            detail.bolt('panel bolt', (x - 2, y + side * 1.25, -2), .45, p['butter'], root, 'Y')
        for x in (-12, -3, 6):
            detail.window('port window', (x, y + side * 1.4, 4), 1.6, p, root, 'Y') if side < 0 else backWindow(root, p, x, y)
        detail.pipe('service pipe', [(-18, y + side * 2, -5), (4, y + side * 2, -5),
            (12, y + side * 2, -1)], .7, p, root)
        detail.clamps('service pipe', [((-10, y + side * 2, -5), 'X'),
            ((1, y + side * 2, -5), 'X')], .7, p, root)
    cockpit = next(obj for obj in root.children_recursive if obj.name == 'cockpit window')
    cockpit.data.materials[0] = p['green']
    bpy.data.objects.remove(cockpit, do_unlink=True)
    toy.ball('cockpit seal', (29.8, 0, 5.5), (3.4, 9.4, 6.5), p['milk'], root)
    toy.ball('cockpit glass', (31, 0, 5.8), (3.3, 8.5, 5.6), p['green'], root)
    for y in (-7, 7):
        mount = kit.empty('nose lamp mount', root, (31.8, y, -2))
        mount.rotation_euler.z = math.pi
        detail.window('nose lamp', (0, 0, 0), 1.6, p, mount, 'X')
    toy.box('top equipment case', (-15, 0, 12.5), (10, 9, 4), p['milk'], root)
    kit.pipe('case handle', [(-18, 0, 14.8), (-18, 0, 17), (-12, 0, 17),
        (-12, 0, 14.8)], .55, p['butter'], root, corner=.8, sides=8)


def hullFittings(root, p, kind):
    for side in (-1, 1):
        for x in (16, 23):
            mount = kit.empty('cockpit side port', root, (x, side * 11.8, 3))
            mount.rotation_euler.z = math.pi if side > 0 else 0
            detail.window('cockpit round window', (0, 0, 0), 2, p, mount)
        for x in (-24, -19):
            toy.box('engine access cover', (x, side * 15, 8.3),
                (3.7, 8, 1.1), p['green'], root)
            for y in (-2.2, 2.2):
                detail.bolt('engine cover bolt', (x, side * 15 + y, 9.1), .45, p['butter'], root)
        detail.pipe('engine feed', [(-26, side * 9, 5), (-21, side * 7, 10),
            (-7, side * 7, 10)], .65, p, root)
    height = 8.2 if kind == 'research' else 11.9
    for x in (-3, 5):
        toy.box('dorsal panel', (x, 0, height), (6.8, 8, 1), p['milk'], root)
        for y in (-2.8, 2.8):
            detail.bolt('dorsal panel bolt', (x, y, height + .8), .45, p['butter'], root)


def backWindow(root, p, x, y):
    mount = kit.empty('back window mount', root, (x, y + 1.4, 4))
    mount.rotation_euler.z = math.pi
    detail.window('port window', (0, 0, 0), 1.6, p, mount, 'Y')


def cargo(root, p):
    for obj in root.children:
        if obj.name in ('socket_cargo1', 'clip cargo1'):
            obj.location.y -= 10
        elif obj.name == 'port stem cargo1':
            obj.location.y -= 5
            obj.scale.y = 3.5
    for side in (-1, 1):
        for x in (-10, 9):
            pod = toy.box('side cargo case', (x, side * 17, -10), (15, 9, 17), p['milk'], root)
            detail.seam('cargo case seam', pod, [(2, (-10,))], .35)
            toy.box('cargo strap', (x, side * 22, -10), (2, 1.1, 16), p['green'], root)
            toy.box('cargo latch', (x, side * 22.8, -9), (4, .7, 4), p['red'], root)
            detail.bolt('cargo latch pin', (x, side * 23.4, -9), .65, p['butter'], root, 'Y')
    for obj in list(root.children_recursive):
        if obj.name.startswith('belly pod'):
            detail.seam('belly case seam', obj, [(0, (obj.location.x,))], .35)


def military(root, p):
    for side in (-1, 1):
        for x in (0, 12):
            toy.box('armour plate', (x, side * 18, 4), (10, 1.5, 8), p['milk'], root)
            detail.bolt('armour bolt', (x, side * 19.1, 5), .65, p['butter'], root, 'Y')
        toy.box('wedge skid', (23, side * 13, -7), (13, 7, 6), p['milk'], root)
    turret = next(obj for obj in root.children_recursive if obj.name == 'turret_spin')
    detail.tube('gun muzzle', (14, 0, 5), 3.6, 2.1, 3, p['milk'], turret)
    toy.drum('gun bore', (12.2, 0, 5), 1.9, .3, p['dark'], turret)
    for side in (-1, 1):
        toy.box('turret cheek', (0, side * 6, 2), (8, 2, 6), p['green'], turret)
    for x in (10, 20):
        toy.box('wedge split plate', (x, 0, 10), (8, 14, 1.7), p['green'], root)


def industrial(root, p):
    for side in (-1, 1):
        for x, y, z in ((13, side * 14, -3), (27, side * 18, -5)):
            toy.drum('claw joint', (x, y, z), 3.2, 4, p['green'], root, 'Z')
            detail.bolt('claw joint pin', (x, y, z + 2.5), 1.2, p['red'], root)
        kit.pipe('claw hydraulic', [(9, side * 16, 0), (21, side * 22, -1),
            (29, side * 20, -3)], .7, p['green'], root, corner=2, sides=8)
    for x in (-8, -5, -2):
        kit.ring('winch cable', (x, 18, 6), 4.2, .45, p['green'], root)
    head = next(obj for obj in root.children_recursive if obj.name == 'drill head')
    bpy.data.objects.remove(head, do_unlink=True)
    kit.barrel('drill head', (42, 0, 2), 7.5, 12, p['green'], root,
        top=.9, sides=24, round_=.5)
    for x, radius in ((37.5, 6.8), (40.5, 5.2), (43.5, 3.5), (46.5, 1.8)):
        kit.ring('drill cutting ridge', (x, 0, 2), radius, .5, p['milk'], root)


def research(root, p):
    for side in (-1, 1):
        for x in (-9, 2, 12):
            kit.barrel('sample tank', (x, side * 14, -5), 3, 8, p['milk'], root,
                sides=16, round_=.6)
            kit.ring('sample tank belt', (x, side * 14, -5), 3, .6, p['butter'], root)
    kit.ring('lab dome collar', (3, 16, 12), 9.5, .8, p['butter'], root, 'Z')
    for x in (-2, 4, 9):
        toy.drum('lab specimen', (x, 17, 13), 1.2, 4, p['milk'], root, 'Z')
    detail.pipe('lab feed', [(3, 8, 5), (3, 11, 8), (3, 15, 8)], .7, p, root)
    for obj in list(root.children_recursive):
        if obj.name.startswith(('dish bracket', 'dish stem', 'research dish')):
            bpy.data.objects.remove(obj, do_unlink=True)
    toy.box('dish bracket', (-15, -11, 10), (6, 9, 7), p['milk'], root)
    toy.drum('dish mast', (-15, -12, 18), 2, 12, p['butter'], root, 'Z')
    mount = kit.empty('dish tilt mount', root, (-15, -12, 24))
    mount.rotation_euler.y = math.radians(30)
    toy.dish('research dish', (0, 0, 0), 13, p['red'], mount)
    kit.ring('dish lip', (0, 0, 5.6), 13, .6, p['milk'], mount, 'Z')
    toy.drum('dish receiver', (0, 0, 6), 1.2, 12, p['butter'], mount, 'Z')
    toy.ball('dish tip', (0, 0, 13), (1.7, 1.7, 1.7), p['glow'], mount)
    for x in (-4, 3, 10):
        mount = kit.empty('lab window mount', root, (x, 24.7, 16))
        mount.rotation_euler.z = math.pi
        detail.window('lab round window', (0, 0, 0), 1.6, p, mount)
    for x in (8, 18):
        toy.drum('antenna', (x, 8, 18), .45, 10, p['butter'], root, 'Z')
        toy.ball('antenna tip', (x, 8, 23.7), (.9, .9, .9), p['glow'], root)


def build(kind):
    kit.reset()
    p, root = toy.palette(), kit.empty('toy_ship_' + kind)
    toyships.hull(root, p, kind)
    engines(root, p)
    hullPanels(root, p, kind)
    hullFittings(root, p, kind)
    {'cargo': cargo, 'military': military, 'industrial': industrial, 'research': research}[kind](root, p)
    detail.clips(root, p)
    detail.finish(root)
    root['detail_revision'] = 2
    for obj in root.children:
        if obj.name.startswith('exhaust'):
            obj.location.x = -37.4
    extent = toy.bounds(root)
    if kind == 'cargo':
        scale = 70 / (extent[0][1] - extent[0][0])
        for obj in root.children:
            obj.location *= scale
            obj.scale *= scale
        extent = toy.bounds(root)
    if not 60 <= extent[0][1] - extent[0][0] <= 150:
        raise ValueError('ship length is outside 60 to 150 metres')
    toy.save(root, 'ship-' + kind, 40000, 110)


for kind in ('cargo', 'military', 'industrial', 'research'):
    build(kind)
