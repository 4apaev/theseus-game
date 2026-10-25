"""build toy hulls with five shared module ports."""

import math

import paintkit as kit
import toykit as toy

sockets = {
    'power1': ('power', (-8, 0, 14)),
    'cruise1': ('cruise', (-27, 0, 0)),
    'maneuver1': ('maneuver', (25, 0, -9)),
    'cargo1': ('cargo', (0, -15, -6)),
    'utility1': ('utility', (13, 0, 16))
}


def ports(root, p):
    stems = {
        'power': ((-8, 0, 12), 4, 'Z'),
        'cruise': ((-26, 0, 0), 2, 'X'),
        'maneuver': ((25, 0, -7), 4, 'Z'),
        'cargo': ((0, -13, -6), 4, 'Y'),
        'utility': ((13, 0, 13.5), 5, 'Z')
    }
    for slot, (family, at) in sockets.items():
        center, length, axis = stems[family]
        toy.drum('port stem ' + slot, center, 3, length, p['milk'], root, axis)
        spot = kit.socket(root, slot, family, at)
        spot['size'] = 6
        if family == 'cruise':
            spot.rotation_euler.y = -math.pi / 2
        elif family == 'cargo':
            spot.rotation_euler.x = math.pi / 2
        elif family == 'maneuver':
            spot.rotation_euler.x = math.pi
        toy.drum('clip ' + slot, at, 3, 1, p['dark'], root,
            'X' if family == 'cruise' else 'Y' if family == 'cargo' else 'Z')
    for y in (-15, 15):
        outlet = kit.empty('exhaust' if y < 0 else 'exhaust_b', root, (-36.1, y, 0))
        outlet['plume'], outlet['radius'] = True, 4.5


def hull(root, p, kind):
    toy.ball('hull', (0, 0, 0), (27, 9, 8) if kind == 'research' else (27, 13, 12), p['milk'], root)
    toy.ball('cockpit', (21.15, 0, 3), (13, 12, 11), p['red'], root)
    toy.ball('cockpit window', (29.15, 0, 5), (5, 8, 6), p['dark'], root)
    for y in (-15, 15):
        toy.drum('engine housing', (-26, y, 0), 8, 17, p['green'], root)
        toy.drum('engine nozzle', (-35.1, y, 0), 6.7, .8, p['dark'], root)
        toy.drum('engine glow', (-35.7, y, 0), 4.5, .3, p['glow'], root)
    {'cargo': cargo, 'military': military, 'industrial': industrial, 'research': research}[kind](root, p)
    ports(root, p)


def cargo(root, p):
    for x in (-10, 9):
        toy.box('belly pod', (x, 0, -16), (15, 22, 9), p['butter'], root)


def military(root, p):
    for y in (-1, 1):
        toy.box('armour shoulder', (4, y * 13, 0), (31, 9, 14), p['green'], root)
    kit.prism('wedge armour', [(8, -4), (34, -4), (30, 8), (8, 10)],
        -12, 12, p['red'], root, 2)
    toy.drum('turret pedestal', (0, 17, 9), 5, 7, p['milk'], root, 'Z')
    turret = kit.empty('turret_spin', root, (0, 17, 13))
    turret['spin'] = .12
    toy.drum('turret body', (0, 0, 0), 8, 6, p['red'], turret, 'Z')
    toy.drum('turret barrel', (7, 0, 5), 3, 12, p['dark'], turret)


def industrial(root, p):
    for y in (-1, 1):
        kit.pipe('claw arm', [(8, y * 12, -2), (23, y * 19, -5),
            (34, y * 16, -5)], 2, p['butter'], root, corner=5, sides=12)
        toy.box('claw jaw', (35, y * 14, -5), (8, 4, 8), p['red'], root)
    toy.drum('drill shaft', (34, 0, 2), 3, 12, p['green'], root)
    kit.barrel('drill head', (42, 0, 2), 5, 5, p['dark'], root,
        top=1, sides=16, round_=.7)
    toy.box('winch bracket', (-6, 14, 3), (10, 10, 5), p['milk'], root)
    toy.drum('winch spool', (-6, 18, 6), 4, 8, p['red'], root)
    for x in (-9, -3):
        kit.ring('winch flange', (x, 18, 6), 4, .6, p['butter'], root)


def research(root, p):
    toy.box('lab bracket', (3, 10, 6), (18, 16, 7), p['milk'], root)
    toy.ball('lab dome', (3, 16, 16), (13, 9, 8), p['green'], root)
    toy.drum('sensor mast', (-3, 20, 27), 1, 12, p['butter'], root, 'Z')
    toy.ball('sensor tip', (-3, 20, 34), (1.5, 1.5, 1.5), p['glow'], root)
    toy.box('dish bracket', (-15, -11, 10), (6, 9, 7), p['green'], root)
    toy.drum('dish stem', (-15, -15, 18), 2, 12, p['butter'], root, 'Z')
    toy.dish('research dish', (-15, -15, 24), 11, p['milk'], root)


def build(kind):
    kit.reset()
    p, root = toy.palette(), kit.empty('toy_ship_' + kind)
    hull(root, p, kind)
    extent = toy.bounds(root)
    length = extent[0][1] - extent[0][0]
    if kind == 'cargo' and not 69.9 <= length <= 70.1:
        raise ValueError('cargo hull length is outside 69.9 to 70.1 metres')
    if kind != 'cargo' and not 60 <= length <= 150:
        raise ValueError('ship length is outside 60 to 150 metres')
    toy.save(root, 'ship-' + kind, 30000, 105)
