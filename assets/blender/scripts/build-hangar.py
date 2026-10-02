"""Build the hangar fleet: the ships and robots after the hangar art.

blender --background --python scripts/build-hangar.py -- --output /tmp/hangar [--only police-light] [--no-render]

each model follows one painting in ~/Work/theseus/assets/hangar. the shared
parts are in paintkit.py. this file adds the hangar forms: a faceted cab, hull
segments with plates, engine pods, tanks, rings, dishes and arms.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paintkit import *  # noqa: E402,F403


parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
parser.add_argument('--only', default='')
parser.add_argument('--no-render', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)


# ── paint: the kit palette and the hangar colours ─────────────────

def colors(p):
    return {**p,
        'blue': mat('police blue', '#2D5296'), 'blueD': mat('police blue dark', '#213B6B'),
        'stripe': mat('signal red', '#B0473A'), 'maroon': mat('maroon', '#7A2F35'),
        'sky': mat('blue lamp', '#4F8BFF', emission=6), 'amber': mat('amber lamp', '#FFB020', emission=6),
        'spot': mat('spot white', '#F4F4F0', emission=6), 'sage': mat('sage', '#66744E')}


# ── the faceted hull: octagon sections along x ────────────────────

def octagon(w, zb, zt, cb, ct):
    """the 8 corners of a section. the facets: 0 low starboard cut, 1 keel, 2 low port cut,
    3 port side, 4 high port cut, 5 roof, 6 high starboard cut, 7 starboard side"""
    return [(-w, zb + cb), (-w + cb, zb), (w - cb, zb), (w, zb + cb), (w, zt - ct), (w - ct, zt), (-w + ct, zt), (-w, zt - ct)]


def loft(name, sections, material, parent, round_=.04):
    """a hull through sections (x, half width, bottom, top, low cut, high cut). returns the rings"""
    bm = bmesh.new()
    rings = [[bm.verts.new((x, y, z)) for y, z in octagon(*s)] for x, *s in sections]
    for a, b in zip(rings, rings[1:]):
        for k in range(8): bm.faces.new([a[k], a[(k + 1) % 8], b[(k + 1) % 8], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    coords = [[Vector(v.co) for v in r] for r in rings]
    link(name, bm, material, parent, (round_, 2) if round_ else None)
    return coords


def facet(rings, i, k, box):
    """the corners of a window on facet k between ring i and i+1, and its outward normal.
    box (u0, u1, v0, v1): u runs along the facet edge, v from ring i to ring i+1"""
    a0, a1, b0, b1 = rings[i][k], rings[i][(k + 1) % 8], rings[i + 1][k], rings[i + 1][(k + 1) % 8]
    at = lambda u, v: a0.lerp(a1, u).lerp(b0.lerp(b1, u), v)
    u0, u1, v0, v1 = box
    quad = [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)]
    n = (quad[1] - quad[0]).cross(quad[3] - quad[0]).normalized()
    middle = sum(quad, Vector()) / 4
    axis = sum(rings[i] + rings[i + 1], Vector()) / 16
    if n.dot(middle - axis) < 0: n = -n
    return quad, n


def panel(name, rings, i, k, box, material, parent, depth=.04, rise=0):
    """a plate on a facet, `depth` thick, `rise` off the surface"""
    quad, n = facet(rings, i, k, box)
    bm = bmesh.new()
    lo = [bm.verts.new(q + n * (rise - .01)) for q in quad]
    hi = [bm.verts.new(q + n * (rise + depth)) for q in quad]
    bm.faces.new(lo); bm.faces.new(hi)
    for j in range(4): bm.faces.new([lo[j], lo[(j + 1) % 4], hi[(j + 1) % 4], hi[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link(name, bm, material, parent, (.012, 1))


def window(name, rings, i, k, box, p, parent, frame='cream', rim=.05):
    """a pane of smoked glass in a frame"""
    u0, u1, v0, v1 = box
    quad, _ = facet(rings, i, k, box)
    du, dv = rim / max((quad[1] - quad[0]).length, .01), rim / max((quad[3] - quad[0]).length, .01)
    panel(name + ' frame', rings, i, k, box, p[frame], parent, .03)
    panel(name, rings, i, k, (u0 + du, u1 - du, v0 + dv, v1 - dv), p['glass'], parent, .04)


# ── hull parts, as the hangar paintings repeat them ───────────────

def segment(name, x0, x1, w, h, body, p, parent, z=0, cut=.35, n=1, bands=None, roof=None):
    """a hull block with 45° corners, tiled: plates on the roof and the high cuts,
    rows of plates on the flanks. bands: (colour, low, high) rows, from the block centre"""
    length, flat = x1 - x0, h / 2 - cut
    chamfered(name, ((x0 + x1) / 2, 0, z), (length, w, h), p[body], parent, cut)
    step = length / n
    for k in range(n):
        x = x0 + step * (k + .5)
        cols = 2 if w - 2 * cut > 1.3 else 1
        for c in range(cols):
            span = (w - 2 * cut - .16) / cols
            y = (c - (cols - 1) / 2) * span
            block(name + ' roof plate', (x, y, z + h / 2 + .02), (step - .14, span - .08, .06), p[roof or body], parent, .03)
        for s in (-1, 1):
            plate = block(name + ' cut plate', (x, s * (w / 2 - cut / 2 + .014), z + flat + cut / 2 + .014), (step - .14, .06, cut * 1.414 - .12), p[roof or body], parent, .03)
            plate.rotation_euler.x = s * math.pi / 4
            for color, lo, hi in bands or [(body, -flat + .06, flat - .06)]:
                block(name + ' flank plate', (x, s * (w / 2 + .02), z + (lo + hi) / 2), (step - .14, .06, hi - lo), p[color], parent, .03)


def run(name, segs, w, h, body, p, parent, z=0, cut=.35, bands=None, roof=None):
    """hull blocks in a row over a dark core, a dark joint in each gap"""
    x0, x1 = segs[0][0], segs[-1][1]
    chamfered(name + ' core', ((x0 + x1) / 2, 0, z), (x1 - x0, w - .3, h - .3), p['dark'], parent, cut - .05)
    for a, b in segs: segment(name, a, b, w, h, body, p, parent, z, cut, bands=bands, roof=roof)
    for (_, a), (b, _) in zip(segs, segs[1:]):
        chamfered(name + ' joint', ((a + b) / 2, 0, z), (b - a + .02, w - .08, h - .08), p['dark'], parent, cut)


def strap(name, x, w, h, p, parent, z=0, cut=.35, width=.22, color='mustard'):
    """a band round a hull block"""
    chamfered(name, (x, 0, z), (width, w + .16, h + .16), p[color], parent, cut + .04)


def pod(name, x0, x1, y, z, r, p, parent, body='teal', bands=(('cream', .55),), front='grille'):
    """an engine pod: an octagon prism with bands, dark caps, a lamp, a drive exit aft"""
    length, cut = x1 - x0, r * .58
    chamfered(name, ((x0 + x1) / 2, y, z), (length, 2 * r, 2 * r), p[body], parent, cut)
    for c, at in bands:
        chamfered(name + ' band', (x0 + length * at, y, z), (length * .2, 2 * r + .06, 2 * r + .06), p[c], parent, cut + .02)
    chamfered(name + ' aft cap', (x0 - .12, y, z), (.26, 2 * r - .1, 2 * r - .1), p['dark'], parent, cut * .9)
    lamp(name + ' aft lamp', (x0 - .26, y, z + r * .35), (.04, r * .95, r * .3), '-x', p, parent)
    vent(name + ' aft grille', (x0 - .25, y, z - r * .25), (.03, r * 1.0, r * .55), '-x', p, parent, 3)
    s = empty(name + ' plume', parent, (x0 - .3, y, z)); s['plume'], s['radius'] = True, r * .6
    chamfered(name + ' front cap', (x1 + .1, y, z), (.22, 2 * r - .12, 2 * r - .12), p['dark'], parent, cut * .9)
    if front == 'grille': vent(name + ' intake', (x1 + .22, y, z), (.03, r * 1.15, r * 1.05), '+x', p, parent, 5)
    else: lamp(name + ' front lamp', (x1 + .22, y, z), (.04, r * .9, r * .4), '+x', p, parent)


def lightbar(name, at, colors_, p, parent, size=.2):
    """a police bar: a dark base, glowing blocks in a row across the ship"""
    x, y, z = at
    block(name + ' base', (x, y, z), (size * 1.2, size * (len(colors_) + .6), size * .5), p['dark'], parent, .03)
    for k, c in enumerate(colors_):
        yy = y + (k - (len(colors_) - 1) / 2) * size * 1.05
        block(f'lightbar {c} {k}', (x, yy, z + size * .55), (size * .9, size * .9, size * .6), p[c], parent, .02, 1)


def shield(name, at, size, p, parent, side=1):
    """the authority shield on a flank: a cream outline on blue"""
    x, y, z = at
    s = size
    outline = [(-.5, .6), (.5, .6), (.5, 0), (0, -.62), (-.5, 0)]
    inner = [(-.32, .44), (.32, .44), (.32, -.02), (0, -.4), (-.32, -.02)]
    y0 = y + side * .005
    prism(name, [(x + a * s, z + b * s) for a, b in outline], min(y0, y0 + side * .03), max(y0, y0 + side * .03), p['cream'], parent, 0)
    y1 = y + side * .03
    prism(name + ' field', [(x + a * s, z + b * s) for a, b in inner], min(y1, y1 + side * .02), max(y1, y1 + side * .02), p['blue'], parent, 0)


# ── the cab: every hangar ship starts with one ────────────────────

def cab(p, hull, x0, w, h, body, frame='cream', panes=2, length=1.8, stripe=None):
    """a faceted cab: a straight part, a steep windscreen, a short nose face.
    glass wraps the brow: the windscreen, corner and quarter panes, a side pane.
    stripe (u0, u1) paints a band on the cab flanks. returns the rings and the nose x"""
    hw, H, k = w / 2, h / 2, length / 1.8
    rings = loft('cab', [(x0, hw, -H, H, .35, .35), (x0 + .75 * k, hw, -H, H, .35, .35), (x0 + 1.3 * k, hw - .08, -H + .04, .22 * H, .35, .3),
        (x0 + 1.62 * k, hw - .16, -H + .1, .1 * H, .32, .22), (x0 + 1.8 * k, hw - .24, -H + .2, -.02, .28, .16)], p[body], hull)
    for f_ in (4, 5, 6): panel('visor', rings, 1, f_, (0, 1, 0, 1), p[frame], hull, .03)
    for i in range(panes): window('windscreen', rings, 1, 5, (.03 + .94 * i / panes, .03 + .94 * (i + 1) / panes, .1, .92), p, hull, frame)
    for f_ in (4, 6):
        window('corner window', rings, 1, f_, (.1, .9, .1, .92), p, hull, frame)
        window('quarter window', rings, 0, f_, (.1, .9, .2, .96), p, hull, frame)
    for f_, u in ((3, (.72, .98)), (7, (.02, .28))): window('side window', rings, 0, f_, (*u, .2, .96), p, hull, frame)
    if stripe:
        for f_, u in ((3, stripe), (7, (1 - stripe[1], 1 - stripe[0]))): panel('cab stripe', rings, 0, f_, (*u, 0, 1), p[frame], hull, .03)
    for y in (-.42, .42): lamp('brow lamp', (x0 + .72 * k, y, H + .03), (.22, .1, .04), '+z', p, hull)
    return rings, x0 + length


def civil_cab(p, hull, x0, w, h, body='cream', trim='teal', panes=2, length=2.0):
    """the cab of the trade ships: cream, teal cheeks and chin, a dark grille in the nose"""
    H = h / 2
    rings, nose = cab(p, hull, x0, w, h, body, body, panes, length)
    for i in (1, 2, 3):
        for f_, u in ((3, (0, .42)), (7, (.58, 1))): panel('cheek', rings, i, f_, (*u, 0, 1), p[trim], hull, .03)
        for f_ in (0, 2): panel('chin', rings, i, f_, (0, 1, 0, 1), p[trim], hull, .03)
    for f_, u in ((3, (0, .3)), (7, (.7, 1))): panel('cab skirt', rings, 0, f_, (*u, 0, 1), p[trim], hull, .03)
    block('grille frame', (nose + .01, 0, -H + .62), (.08, .9, .5), p['dark'], hull, .04)
    vent('grille', (nose + .04, 0, -H + .62), (.04, .74, .36), '+x', p, hull, 4)
    for s in (-1, 1):
        lamp('nose lamp', (nose + .02, s * (w / 2 - .5), -H + .62), (.04, .14, .3), '+x', p, hull)
        lamp('chin lamp', (nose - .3, s * (w / 2 - .3), -H + .22), (.3, .04, .1), '+y' if s > 0 else '-y', p, hull)
    lamp('brow strip', (nose - .55, 0, .3 * H + .03), (.04, .9, .08), '+x', p, hull)
    antenna('cab mast', (x0 + .3, .5, H + .05), .55, p, hull)
    return rings, nose


def beam(name, a, b, size, material, parent, round_=.04):
    """a square bar from point a to point b"""
    a, b = Vector(a), Vector(b)
    obj = block(name, (a + b) / 2, ((b - a).length, size, size), material, parent, round_)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((1, 0, 0)).rotation_difference((b - a).normalized())
    return obj


def crane(name, pts, p, parent, side=(0, 1, 0), color='mustard'):
    """a robot arm: a turret, a boom and a stick, dark joints, a claw that hangs"""
    base, elbow, wrist = (Vector(q) for q in pts)
    g = empty(name, parent)
    barrel(name + ' turret', base + Vector((0, 0, .1)), .34, .2, p['dark'], g, 'Z', sides=12)
    ring(name + ' collar', base + Vector((0, 0, .22)), .3, .05, p['mustard'], g, 'Z')
    beam(name + ' boom', base + Vector((0, 0, .25)), elbow, .3, p[color], g)
    beam(name + ' stick', elbow, wrist, .24, p[color], g)
    for q, r in ((base + Vector((0, 0, .3)), .22), (elbow, .2), (wrist, .16)):
        barrel(name + ' joint', q, r, .42, p['dark'], g, 'Y', sides=12).rotation_euler.z = math.atan2(side[0], side[1])
        barrel(name + ' pin', q, r * .45, .48, p['mustard'], g, 'Y', sides=8).rotation_euler.z = math.atan2(side[0], side[1])
    claw = wrist + Vector((0, 0, -.5))
    beam(name + ' drop', wrist, claw, .1, p['dark'], g)
    block(name + ' claw head', claw, (.3, .3, .24), p['dark'], g, .05)
    lamp(name + ' claw lamp', claw + Vector((.15, 0, 0)), (.04, .16, .1), '+x', p, g)
    for s in (-1, 1): pipe(name + ' claw', [claw + Vector((s * .1, 0, -.1)), claw + Vector((s * .16, 0, -.42)), claw + Vector((s * .02, 0, -.5))], .045, p['dark'], g, .08)
    return g


def dome(name, at, r, depth, axis, material, parent, sides=20):
    """a domed end cap: half a sphere, flattened to `depth`, facing `axis` (+x, -x, +z)"""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=sides, v_segments=10, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.001], context='VERTS')
    bmesh.ops.scale(bm, vec=(1, 1, depth / r), verts=bm.verts)
    turn = {'+x': Matrix.Rotation(math.pi / 2, 3, 'Y'), '-x': Matrix.Rotation(-math.pi / 2, 3, 'Y'), '+z': Matrix.Identity(3)}[axis]
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=turn)
    return link(name, bm, material, parent, None, at)


def tank(name, at, r, length, p, parent, body='cream', band='stripe'):
    """a pressure tank: a drum with domed ends, two bands, a hatch with a lamp on top"""
    x, y, z = at
    barrel(name, at, r, length, p[body], parent, 'X', sides=20)
    for s in (-1, 1):
        dome(name + ' dome', (x + s * length / 2, y, z), r, r * .55, '+x' if s > 0 else '-x', p[body], parent)
        barrel(name + ' band', (x + s * length * .2, y, z), r + .025, length * .13, p[band], parent, 'X', sides=20, round_=.01)
    barrel(name + ' hatch', (x - length * .05, y, z + r + .04), .2, .16, p['dark'], parent, 'Z', sides=12)
    ring(name + ' hatch rim', (x - length * .05, y, z + r + .1), .2, .035, p['mustard'], parent, 'Z')
    barrel(name + ' hatch lamp', (x - length * .05, y, z + r + .14), .09, .05, p['lamp'], parent, 'Z', sides=10, round_=0)


def plating(name, rings, facets, color, parent, spans=None, gap=.05, depth=.04):
    """plates over facets of a loft, one per facet and span, a dark seam round each"""
    for i in spans or range(len(rings) - 1):
        for f_ in facets:
            quad, _ = facet(rings, i, f_, (0, 1, 0, 1))
            du, dv = gap / max((quad[1] - quad[0]).length, .01), gap / max((quad[3] - quad[0]).length, .01)
            if du < .45 and dv < .45: panel(name, rings, i, f_, (du, 1 - du, dv, 1 - dv), color, parent, depth)


def truss(name, x0, x1, half, p, parent, z=0, bay=1.0):
    """a lattice beam along x: four dark rails, cross braces and diagonals on the flanks"""
    for y in (-half, half):
        for zz in (z - half, z + half): block(name + ' rail', ((x0 + x1) / 2, y, zz), (x1 - x0, .1, .1), p['dark'], parent, 0)
    n = max(1, round((x1 - x0) / bay))
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        for y in (-half, half): block(name + ' post', (x, y, z), (.08, .08, 2 * half), p['dark'], parent, 0)
        for zz in (z - half, z + half): block(name + ' tie', (x, 0, zz), (.08, 2 * half, .08), p['dark'], parent, 0)
        if k < n:
            xa, xb = x, x0 + (x1 - x0) * (k + 1) / n
            for y in (-half, half): beam(name + ' brace', (xa, y, z - half), (xb, y, z + half) if k % 2 else (xb, y, z - half + 2 * half), .06, p['dark'], parent, 0)


def dish(name, at, r, depth, p, parent, axis='+x', color='cream'):
    """a parabolic dish facing `axis`: a shallow shell, a rim, a feed on spokes"""
    R = (r * r + depth * depth) / (2 * depth)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=R)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > -R + depth + .001], context='VERTS')
    bmesh.ops.translate(bm, vec=Vector((0, 0, R - depth)), verts=bm.verts)
    turn = {'+x': Matrix.Rotation(math.pi / 2, 3, 'Y'), '+z': Matrix.Identity(3), '-z': Matrix.Rotation(math.pi, 3, 'X')}[axis]
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=turn)
    shell = link(name, bm, p[color], parent, None, at)
    shell.modifiers.new('shell', 'SOLIDIFY').thickness = max(.04, r * .04)
    return shell


# ── the light police ship: a patrol van ────────────────────────────

PL_W, PL_H = 2.3, 2.0
PL_BANDS = [('blue', .36, .58), ('cream', -.1, .32), ('blue', -.58, -.14)]


def police_cab(p, hull, x0, w, h, panes=2, length=1.8, bars=('sky', 'sky', 'amber')):
    """the police cab: glass in a cream frame, a bar on the roof, a bumper of dark blocks"""
    H = h / 2
    rings, nose = cab(p, hull, x0, w, h, 'blue', 'cream', panes, length, (.34, .66))
    lightbar('cab', (x0 + .35, 0, H + .12), bars, p, hull, .26)
    antenna('cab mast', (x0 + .2, -.68, H + .05), .55, p, hull)
    for s in (-1, 1): lamp('nose lamp', (nose + .01, s * (w / 2 - .55), -.2), (.04, .26, .12), '+x', p, hull)
    block('bumper plate', (nose + .02, 0, -H + .48), (.08, w - 1.1, .3), p['cream'], hull, .03)
    n = 4 if w < 2.5 else 5
    for k in range(n): block('bumper', (nose + .02, (k - (n - 1) / 2) * .44, -H + .14), (.36, .4, .34), p['dark'], hull, .08)
    lamp('bumper lamp', (nose + .21, 0, -H + .14), (.04, .28, .12), '+x', p, hull)
    return rings, nose


def police_light(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    w, h, H = PL_W, PL_H, PL_H / 2
    run('hull', [(-3.9, -2.3), (-2.12, -.52), (-.34, 1.24), (1.42, 3.0)], w, h, 'blue', p, hull, bands=PL_BANDS)
    police_cab(p, hull, 3.0, w, h)
    for s in (-1, 1):
        side = '+y' if s > 0 else '-y'
        y = s * (w / 2 + .06)
        block('shield patch', (.45, y, .1), (1.1, .05, 1.0), p['blue'], hull, .03)
        shield('shield', (.45, y + s * .02, .12), .8, p, hull, s)
        lamp('flank lamp', (2.1, y, .42), (.32, .04, .12), side, p, hull)
        lamp('flank lamp', (-1.0, y, .42), (.32, .04, .12), side, p, hull)
        lamp('flank lamp low', (-3.0, y, -.42), (.32, .04, .12), side, p, hull)
        vent('flank vent', (1.0, y, -.42), (.46, .04, .26), side, p, hull)
        block('door', (2.4, y, -.38), (.5, .05, .56), p['dark'], hull, .03)
        handle('door rail', (2.72, y + s * .03, -.15), (2.72, y + s * .03, -.6), (0, s, 0), p, hull, .08)
    # the deckhouse on the aft roof: a hatch, a second bar, a mast
    segment('deckhouse', -3.7, -.9, 1.5, .5, 'blue', p, hull, H + .25, .14)
    block('hatch', (-1.6, 0, H + .53), (.66, .66, .06), p['dark'], hull, .03)
    block('hatch lid', (-1.6, 0, H + .57), (.52, .52, .06), p['blueD'], hull, .03)
    lightbar('deck', (-1.0, 0, H + .56), ('amber', 'sky', 'sky'), p, hull, .22)
    antenna('deck mast', (-2.5, .36, H + .5), .75, p, hull)
    for s in (-1, 1): lamp('deck lamp', (-3.2, s * .76, H + .3), (.3, .04, .1), '+y' if s > 0 else '-y', p, hull)
    # the pods: two high aft, two low under the waist
    for s in (-1, 1):
        pod('upper pod', -4.6, -1.7, s * (w / 2 + .5), .55, .62, p, drive, 'blue', (('cream', .62), ('blue', .2)), 'lamp')
        block('pod pylon', (-3.2, s * (w / 2 + .1), .55), (1.6, .3, .5), p['dark'], drive, .04)
        pod('lower pod', -1.9, .6, s * (w / 2 + .38), -.8, .46, p, drive, 'blue', (('cream', .3),), 'grille')
        barrel('piston', (-.65, s * (w / 2 - .1), -.98), .12, 1.6, p['shade'], drive, 'X', sides=10)
    return hull


# ── the heavy police ship: a long armoured carrier ─────────────────

PH_W, PH_H = 2.6, 2.3
PH_BANDS = [('blue', .46, .73), ('cream', -.08, .38), ('blue', -.73, -.16)]


def radar(name, at, p, parent, r=.5):
    """a radar tower: a dark block, a mast, a dish that turns"""
    x, y, z = at
    chamfered(name + ' tower', (x, y, z + .3), (.9, .8, .6), p['blue'], parent, .18)
    lamp(name + ' lamp', (x + .46, y, z + .38), (.04, .4, .1), '+x', p, parent)
    barrel(name + ' mast', (x, y, z + .8), .09, .5, p['dark'], parent, 'Z', sides=10)
    arm = empty(name + ' arm', parent, (x, y, z + 1.1)); arm['spin'] = .8
    barrel(name + ' dish', (0, 0, .05), r, .14, p['cream'], arm, 'Z', top=r * .9, sides=20)
    barrel(name + ' rim', (0, 0, -.04), r * 1.02, .06, p['blueD'], arm, 'Z', sides=20, round_=0)
    barrel(name + ' feed', (0, 0, .18), .08, .12, p['dark'], arm, 'Z', sides=8)
    antenna(name + ' tip', (x + .28, y + .25, z + .6), .5, p, parent)


def police_heavy(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    w, h, H = PH_W, PH_H, PH_H / 2
    segs = [(-5.7, -4.25), (-4.07, -2.62), (-2.44, -.99), (-.81, .64), (.82, 2.27), (2.45, 3.9)]
    run('hull', segs, w, h, 'blue', p, hull, bands=PH_BANDS)
    police_cab(p, hull, 3.9, w, h, 3, 2.0, ('sky', 'amber', 'sky'))
    antenna('cab mast 2', (4.1, .62, H + .05), .45, p, hull)
    for s in (-1, 1):
        side, y = ('+y' if s > 0 else '-y'), s * (w / 2 + .06)
        block('shield patch', (-.08, y, .15), (1.2, .05, 1.12), p['blue'], hull, .03)
        shield('shield', (-.08, y + s * .02, .18), .92, p, hull, s)
        for x in (3.1, 1.55, -1.7, -3.35): lamp('flank lamp', (x, y, .58), (.32, .04, .12), side, p, hull)
        for x in (2.0, -2.2): vent('flank vent', (x, y, -.45), (.5, .04, .3), side, p, hull)
        for x in (.9, -4.9): block('door', (x, y, -.4), (.46, .05, .6), p['dark'], hull, .03)
        # mustard pipes along the low flank, clamped at each joint
        pipe('low pipe', [(3.6, s * (w / 2 + .12), -.85), (-5.3, s * (w / 2 + .12), -.85)], .07, p['mustard'], hull)
        pipe('low pipe 2', [(2.4, s * (w / 2 + .1), -.68), (-3.9, s * (w / 2 + .1), -.68)], .045, p['dark'], hull)
        for x0, x1 in segs[1:]: block('clamp', (x0 - .09, s * (w / 2 + .12), -.78), (.16, .14, .28), p['mustard'], hull, .03)
    # the deck on the roof: a hatch, a bar, masts, the radar
    segment('deck', -4.6, .6, 1.7, .5, 'blue', p, hull, H + .25, .14)
    for x in (-1.0, -2.6): vent('deck vent', (x, 0, H + .52), (.6, .5, .04), '+z', p, hull)
    lightbar('deck', (.1, 0, H + .56), ('sky', 'amber', 'sky'), p, hull, .22)
    antenna('deck mast', (-.4, .45, H + .5), .7, p, hull)
    radar('radar', (-3.8, 0, H + .5), p, hull)
    # four pods aft, two high and two low a side
    for s in (-1, 1):
        for z in (.62, -.62):
            pod('pod', -6.6, -3.4, s * (w / 2 + .5), z, .6, p, drive, 'blue', (('cream', .6),), 'grille' if z > 0 else 'lamp')
        block('pod pylon', (-5.0, s * (w / 2 + .1), 0), (2.0, .3, 1.5), p['dark'], drive, .05)
    return hull


# ── the freighter: cargo blocks, cranes, a stacked drive ─────────

FR_W, FR_H = 2.6, 2.4
FR_BANDS = [('cream', .38, .84), ('olive', -.84, .3)]


def freighter(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    w, h, H = FR_W, FR_H, FR_H / 2
    holds = [(-6.4, -3.3), (-3.06, .04), (.28, 3.38)]
    run('hold', holds, w, h, 'cream', p, hull, bands=FR_BANDS)
    for (a, b), x in zip(holds, (-4.85, -1.51, 1.83)):
        for s in (-1, 1):
            vent('hold vent', (x + .9, s * (w / 2 + .06), -.25), (.04 * 0 + .5, .04, .34), '+y' if s > 0 else '-y', p, hull)
            lamp('hold lamp', (x - 1.0, s * (w / 2 + .06), .64), (.3, .04, .1), '+y' if s > 0 else '-y', p, hull)
        vent('roof grille', (x, .3, H + .07), (.9, .4, .04), '+z', p, hull)
        chamfered('skirt', (x, 0, -H - .28), (b - a - .5, w - .5, .56), p['teal' if x < 0 else 'olive'], hull, .14)
    for x in (-3.18, .16, 3.5):
        for d in (-.13, .13): strap('strap', x + d, w, h, p, hull, width=.12)
    # the fore block and the cab
    segment('fore', 3.62, 5.0, w, h, 'cream', p, hull, bands=[('cream', .1, .84), ('teal', -.84, .02)])
    civil_cab(p, hull, 5.0, w, h)
    # pipes along the low flank, a feed between the blocks
    for s in (-1, 1):
        y = s * (w / 2 + .12)
        pipe('low pipe', [(4.8, y, -.95), (-7.0, y, -.95)], .07, p['mustard'], hull)
        pipe('mid pipe', [(3.4, y, -.02), (-6.3, y, -.02)], .05, p['mustard'], hull)
        for x in (-3.18, .16, 3.5): block('clamp', (x, y, -.5), (.16, .14, 1.0), p['mustard'], hull, .03)
    # the aft block: a band, a grille, two pods a side, stacked
    segment('aft', -9.0, -6.64, w, h, 'cream', p, hull, bands=[('cream', .1, .84), ('teal', -.84, .02)])
    strap('aft band', -7.6, w, h, p, hull, width=.36)
    for s in (-1, 1): vent('aft grille', (-8.4, s * (w / 2 + .06), .45), (.7, .04, .5), '+y' if s > 0 else '-y', p, hull, 4)
    antenna('aft mast', (-8.3, -.4, H + .05), .8, p, hull)
    for s in (-1, 1):
        for z in (.62, -.62): pod('pod', -10.6, -8.6, s * (w / 2 - .2), z, .6, p, drive, 'teal', (('cream', .55),), 'lamp')
    crane('crane fore', [(2.6, -.75, H + .08), (3.5, -.9, H + 2.0), (4.7, -1.4, H + 1.6)], p, root)
    crane('crane aft', [(-2.0, w / 2 + .1, -.25), (-2.6, w / 2 + 1.6, .9), (-1.4, w / 2 + 2.6, .4)], p, root, (1, 0, 0))
    return hull


# ── the tanker: six pressure tanks on a frame ─────────────────────

TK_W, TK_H = 2.6, 2.4


def tanker(p, root):
    p = colors(p)
    hull, cargo, drive = empty('hull', root), empty('cargo', root), empty('drive', root)
    w, h, H = TK_W, TK_H, TK_H / 2
    # the frame: a dark keel, cradles between the tanks, red posts, mustard straps over each tank
    chamfered('keel', (-2.0, 0, -H + .25), (11.8, 1.8, .5), p['dark'], hull, .15)
    for x in (-7.6, -4.0, -.4, 3.2):
        chamfered('cradle', (x, 0, -.72), (.4, w + .7, .6), p['dark'], hull, .12)
        for s in (-1, 1): block('frame post', (x, s * (w / 2 + .42), -.2), (.36, .16, 1.5), p['stripe'], hull, .04)
    for y in (-.84, .84):
        for x in (-5.8, -2.2, 1.4):
            tank('tank', (x, y, .2), .8, 2.5, p, cargo)
            for d in (-1.1, 1.1): ring('tank strap', (x + d, y, .2), .83, .05, p['mustard'], cargo, 'X')
    # pipes: a manifold along the top, feeds to the hatches, rails low on the flanks
    pipe('manifold', [(3.4, 0, H - .05), (-7.8, 0, H - .05)], .09, p['mustard'], cargo)
    for x in (-5.8, -2.2, 1.4):
        for y in (-.84, .84): pipe('feed', [(x - .13, 0, H - .05), (x - .13, y * .5, H + .1), (x - .13, y, H - .05 + .1)], .045, p['mustard'], cargo, .06)
    for s in (-1, 1):
        y = s * (w / 2 + .42)
        pipe('low rail', [(3.4, y, -.95), (-7.8, y, -.95)], .08, p['mustard'], hull)
        pipe('low rail 2', [(3.3, s * (w / 2 + .3), -.62), (-7.7, s * (w / 2 + .3), -.62)], .05, p['dark'], hull)
    # the fore block and the cab
    segment('fore', 3.4, 4.9, w, h, 'cream', p, hull, bands=[('cream', .1, .84), ('teal', -.84, .02)])
    for s in (-1, 1): block('fore post', (3.62, s * (w / 2 + .1), 0), (.2, .14, h - .3), p['mustard'], hull, .03)
    civil_cab(p, hull, 4.9, w, h)
    # the aft block and two big pods
    segment('aft', -9.6, -7.8, w, h, 'cream', p, hull, bands=[('teal', .1, .84), ('cream', -.84, .02)])
    strap('aft band', -8.4, w, h, p, hull, width=.34)
    antenna('aft mast', (-9.0, .3, H + .05), .7, p, hull)
    for s in (-1, 1):
        pod('pod', -11.2, -8.6, s * (w / 2 + .1), .2, .78, p, drive, 'teal', (('cream', .62), ('mustard', .25)), 'grille')
    return hull


# ── the transport: a bus between the stations ─────────────────────

TR_W, TR_H = 2.5, 2.6
TR_BANDS = [('cream', .02, .92), ('teal', -.92, -.06)]


def flank_window(name, x, y, z, s, p, parent, size=(.62, .52)):
    """a passenger window on a flank: a cream frame, smoked glass, a lamp over it"""
    side = '+y' if s > 0 else '-y'
    block(name + ' frame', (x, y, z), (size[0] + .12, .05, size[1] + .12), p['cream'], parent, .03)
    block(name, (x, y + s * .02, z), (size[0], .04, size[1]), p['glass'], parent, .03, 1)
    lamp(name + ' lamp', (x, y + s * .01, z + size[1] / 2 + .14), (.16, .04, .06), side, p, parent)


def transport(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    w, h, H = TR_W, TR_H, TR_H / 2
    run('body', [(-5.0, -.7), (-.52, 3.6)], w, h, 'cream', p, hull, bands=TR_BANDS)
    civil_cab(p, hull, 3.6, w, h, panes=2, length=2.1)
    for s in (-1, 1):
        side, y = ('+y' if s > 0 else '-y'), s * (w / 2 + .07)
        for k in range(7): flank_window('window', 3.0 - k * .9 - (.18 if k > 3 else 0), y, .5, s, p, hull)
        # the door: olive, a pane, rails and a step
        block('door', (-.61, y, -.42), (.8, .06, 1.2), p['olive'], hull, .04)
        block('door pane', (-.61, y + s * .03, -.05), (.16, .03, .34), p['glass'], hull, .02, 1)
        for x in (-1.08, -.14): handle('door rail', (x, y + s * .03, -.05), (x, y + s * .03, -.85), (0, s, 0), p, hull, .1)
        block('step', (-.61, y + s * .1, -1.06), (.9, .2, .08), p['mustard'], hull, .02)
        for x in (2.2, 1.0, -2.0, -3.3): block('locker', (x, y, -.5), (.95, .05, .62), p['olive'], hull, .03)
        for x in (2.2, -3.3): vent('locker vent', (x - .25, y + s * .02, -.5), (.24, .03, .3), side, p, hull, 3)
        lamp('flank lamp', (-1.55, y, -.18), (.04 * 0 + .26, .04, .1), side, p, hull)
        pipe('sill', [(3.5, s * (w / 2 + .1), -.08), (-4.9, s * (w / 2 + .1), -.08)], .04, p['mustard'], hull)
    for x in (2.5, -1.7): vent('roof grille', (x, 0, H + .07), (1.1, .5, .04), '+z', p, hull)
    for x in (1.0, -.62, -3.4): strap('roof strap', x, w, h, p, hull, width=.14)
    block('roof hatch', (-2.6, .3, H + .1), (.5, .5, .1), p['dark'], hull, .03)
    # the aft: two pods high at the corners, a teal block between them
    segment('aft', -6.0, -5.1, w - .3, h - .4, 'teal', p, hull, -.1)
    for s in (-1, 1):
        pod('pod', -7.0, -4.6, s * (w / 2 - .05), H - .3, .62, p, drive, 'cream', (('mustard', .25), ('teal', .75)), 'grille')
    return hull


# ── the prison barge: cell blocks on both flanks ──────────────────

PR_W, PR_H = 2.4, 2.3


def cell_block(name, x, s, p, parent, w, length=2.5):
    """a cell block on a flank: a cream box, a maroon door, a dark slot, a lamp"""
    y, side = s * (w / 2 + .32), '+y' if s > 0 else '-y'
    chamfered(name, (x, y, .05), (length, .7, 1.9), p['cream'], parent, .16)
    block(name + ' door', (x + .2, y + s * .36, -.3), (.5, .05, 1.0), p['maroon'], parent, .03)
    for k in (-1, 0, 1): block(name + ' hinge', (x + .2 + k * .14, y + s * .39, .26), (.08, .04, .14), p['dark'], parent, .02, 1)
    block(name + ' slot', (x + .2, y + s * .36, .62), (1.5, .05, .12), p['black'], parent, .02, 1)
    lamp(name + ' lamp', (x - .8, y + s * .36, .62), (.22, .04, .1), side, p, parent)
    block(name + ' roof', (x, y - s * .05, 1.02), (length - .3, .5, .1), p['shade'], parent, .03)


def prison(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    w, h, H = PR_W, PR_H, PR_H / 2
    run('hull', [(-6.6, -3.75), (-3.55, -.7), (-.5, 2.35), (2.55, 4.0)], w, h, 'olive', p, hull,
        bands=[('olive', .3, .78), ('cream', -.78, .22)], roof='cream')
    for x in (-5.2, -2.15, .9):
        for s in (-1, 1): cell_block('cell', x, s, p, hull, w)
        vent('roof vent', (x - .2, 0, H + .08), (1.0, .5, .04), '+z', p, hull)
    block('spine stripe', (-1.3, 0, H + .07), (10.4, .34, .04), p['maroon'], hull, .015, 1)
    for x in (-3.65, -.6, 2.45): block('roof block', (x, 0, H + .24), (.7, .9, .4), p['olive'], hull, .05)
    antenna('roof mast', (-.6, 0, H + .44), .5, p, hull)
    # the cab: cream with olive cheeks, a maroon stripe
    segment('fore', 4.12, 5.2, w, h, 'cream', p, hull, bands=[('cream', .1, .78), ('maroon', -.3, .06), ('olive', -.78, -.36)])
    rings, nose = civil_cab(p, hull, 5.2, w, h, 'cream', 'olive')
    for f_, u in ((3, (.36, .5)), (7, (.5, .64))): panel('cab stripe', rings, 0, f_, (*u, 0, 1), p['maroon'], hull, .03)
    # skirt boxes and a pipe under the cells
    for x in (-5.2, -2.15, .9, 3.3):
        chamfered('skirt', (x, 0, -H - .25), (2.2, w - .3, .5), p['olive'], hull, .14)
        for s in (-1, 1): lamp('skirt lamp', (x + .6, s * (w / 2 - .14), -H - .25), (.3, .04, .1), '+y' if s > 0 else '-y', p, hull)
    for s in (-1, 1): pipe('low pipe', [(4.1, s * (w / 2 + .1), -.95), (-6.7, s * (w / 2 + .1), -.95)], .07, p['mustard'], hull)
    # the aft: a tower with a mast, two pods banded olive and maroon
    segment('aft', -8.2, -6.78, w - .2, h - .2, 'cream', p, hull, bands=[('maroon', .2, .7), ('cream', -.7, .14)])
    chamfered('aft tower', (-7.5, 0, H + .35), (.9, 1.0, .7), p['cream'], hull, .2)
    block('aft tower band', (-7.5, 0, H + .35), (.3, 1.06, .74), p['maroon'], hull, .04)
    antenna('aft mast', (-7.5, 0, H + .7), .55, p, hull)
    for s in (-1, 1):
        for z in (.55, -.6): pod('pod', -9.8, -7.4, s * (w / 2 + .15), z, .56, p, drive, 'dark', (('olive', .3), ('maroon', .7)), 'lamp')
    return hull


# ── the frigate: a long hull, gun pods on outriggers ──────────────

FG_W, FG_H = 2.5, 2.3
FG_BANDS = [('cream', .3, .78), ('olive', -.78, .22)]


def gun_pod(name, x0, x1, y, z, r, s, p, parent):
    """a weapon pod: cream and teal, a dark flank grille with a lamp strip, a gun forward"""
    length, cut, side = x1 - x0, r * .58, '+y' if s > 0 else '-y'
    chamfered(name, ((x0 + x1) / 2, y, z), (length, 2 * r, 2 * r), p['cream'], parent, cut)
    chamfered(name + ' aft', (x0 + length * .14, y, z), (length * .28, 2 * r + .03, 2 * r + .03), p['teal'], parent, cut)
    chamfered(name + ' band', (x0 + length * .64, y, z), (length * .12, 2 * r + .07, 2 * r + .07), p['mustard'], parent, cut + .02)
    block(name + ' grille', (x0 + length * .4, y + s * (r + .02), z - r * .1), (length * .34, .05, r * 1.1), p['dark'], parent, .03)
    lamp(name + ' strip', (x0 + length * .4, y + s * (r + .05), z + r * .05), (length * .26, .04, .1), side, p, parent)
    vent(name + ' vent', (x0 + length * .4, y + s * (r + .05), z - r * .45), (length * .26, .03, .18), side, p, parent, 2)
    chamfered(name + ' nose', (x1 + .1, y, z), (.2, 2 * r - .14, 2 * r - .14), p['dark'], parent, cut * .9)
    lamp(name + ' nose lamp', (x1 + .21, y, z + r * .45), (.04, r * .9, .1), '+x', p, parent)
    barrel(name + ' gun', (x1 + .62, y, z - .05), .12, .9, p['dark'], parent, 'X', sides=10)
    barrel(name + ' muzzle', (x1 + 1.08, y, z - .05), .17, .14, p['black'], parent, 'X', sides=10)
    chamfered(name + ' cap', (x0 - .1, y, z), (.2, 2 * r - .14, 2 * r - .14), p['dark'], parent, cut * .9)
    antenna(name + ' mast', (x0 + length * .78, y, z + r), .4, p, parent)


def frigate(p, root):
    p = colors(p)
    hull, drive, arms = empty('hull', root), empty('drive', root), empty('armament', root)
    w, h, H = FG_W, FG_H, FG_H / 2
    segs = [(-6.9, -4.6), (-4.4, -2.1), (-1.9, .6), (.8, 3.2)]
    run('hull', segs, w, h, 'cream', p, hull, bands=FG_BANDS)
    for (a, b), c in zip(segs, ('teal', 'cream', 'teal', 'cream')):
        if c == 'teal':
            for s in (-1, 1): block('teal plate', ((a + b) / 2 + .5, s * (w / 2 + .06), .55), (1.0, .05, .4), p['teal'], hull, .03)
    for x in (-4.5, -2.0, .7):
        for d in (-.1, .1): strap('strap', x + d, w, h, p, hull, width=.1)
    for s in (-1, 1):
        side, y = ('+y' if s > 0 else '-y'), s * (w / 2 + .07)
        for x in (2.3, -.6, -3.2, -5.6): lamp('flank lamp', (x, y, .58), (.3, .04, .1), side, p, hull)
        pipe('low pipe', [(3.4, s * (w / 2 + .12), -.92), (-7.0, s * (w / 2 + .12), -.92)], .07, p['mustard'], hull)
        pipe('mid pipe', [(3.0, s * (w / 2 + .12), .26), (-6.7, s * (w / 2 + .12), .26)], .045, p['mustard'], hull)
    # the gun rail on the fore roof
    block('rail bed', (1.3, 0, H + .08), (3.4, .62, .16), p['dark'], hull, .04)
    for y in (-.16, .16): block('rail', (1.4, y, H + .2), (3.2, .08, .08), p['black'], hull, .02)
    lamp('rail lamp', (3.0, 0, H + .2), (.04, .3, .08), '+x', p, hull)
    # the fore block and the cab, two masts on the cab roof
    segment('fore', 3.4, 4.6, w, h, 'cream', p, hull, bands=[('cream', .1, .78), ('teal', -.78, .02)])
    civil_cab(p, hull, 4.6, w, h)
    antenna('cab mast 2', (4.7, -.5, H + .05), .7, p, hull)
    # two gun pods on dark pylons
    for s in (-1, 1):
        gun_pod('gun pod', -2.7, 1.0, s * (w / 2 + 1.3), -.05, .58, s, p, arms)
        chamfered('pylon', (-.8, s * (w / 2 + .45), -.05), (1.6, 1.0, .36), p['dark'], arms, .1)
    # the aft block and four pods
    segment('aft', -8.7, -7.1, w, h, 'cream', p, hull, bands=[('teal', .1, .78), ('cream', -.78, .02)])
    strap('aft band', -7.9, w, h, p, hull, width=.34)
    for x in (-8.1, -7.4): antenna('aft mast', (x, -.4 + (x + 8.1), H + .05), .7 + (x + 8.1), p, hull)
    for s in (-1, 1):
        for z in (.6, -.6): pod('pod', -10.4, -8.4, s * (w / 2 - .15), z, .6, p, drive, 'teal', (('cream', .3), ('mustard', .7)), 'lamp')
    return hull


# ── the corvette: a sleek wedge, dark below, a heavy drive ────────

def corvette(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    plate = mat('armour orange', '#C2512F')
    rings = loft('hull', [(-5.4, 1.05, -.8, .72, .3, .3), (-4.4, 1.2, -.95, .85, .34, .34), (-1.6, 1.2, -.95, .85, .34, .34), (1.2, 1.18, -.92, .82, .34, .34),
        (3.6, 1.0, -.78, .66, .3, .3), (5.4, .62, -.52, .38, .22, .2), (6.5, .24, -.26, .08, .1, .08)], p['dark'], hull)
    plating('cream plate', rings, (3, 4, 5, 6, 7), p['cream'], hull)
    for i in range(len(rings) - 1):
        for f_, u in ((3, (.04, .45)), (7, (.55, .96))): panel('dark plate', rings, i, f_, (*u, .03, .97), p['dark'], hull, .05)
    # the spine: a dark channel, a block on it, the cockpit bump, the sensor mast
    block('spine', (-.6, 0, .92), (6.4, .7, .14), p['dark'], hull, .04)
    chamfered('spine block', (.9, 0, 1.12), (1.3, .62, .34), p['dark'], hull, .12)
    chamfered('cockpit', (3.4, 0, .86), (1.4, .9, .5), p['cream'], hull, .16)
    block('cockpit glass', (4.1, 0, .9), (.06, .66, .16), p['glass'], hull, .02, 1)
    for y in (-.24, .24): lamp('cockpit lamp', (4.11, y, .9), (.04, .14, .06), '+x', p, hull)
    barrel('sensor pole', (2.2, -.5, 1.25), .06, .7, p['dark'], hull, 'Z', sides=8)
    block('sensor head', (2.25, -.5, 1.66), (.4, .3, .22), p['shade'], hull, .04)
    lamp('sensor lamp', (2.46, -.5, 1.66), (.04, .2, .08), '+x', p, hull)
    # flanks: grille skirts, orange armour, lamps
    for s in (-1, 1):
        side, y = ('+y' if s > 0 else '-y'), s * 1.24
        for x0, x1 in ((-3.2, -.2), (.4, 2.6)):
            block('skirt', ((x0 + x1) / 2, s * 1.3, -.5), (x1 - x0, .14, .62), p['dark'], hull, .04)
            for k in range(int((x1 - x0) / .32)): block('skirt slat', (x0 + .2 + k * .32, s * 1.38, -.5), (.08, .04, .46), p['black'], hull, 0)
        for x in (-1.3, 1.6): block('armour', (x, y + s * .04, .3), (1.0, .06, .5), plate, hull, .03)
        for x in (4.6, 3.0, -2.6): lamp('flank lamp', (x, s * (1.12 if x > 4 else 1.25), .1), (.3, .04, .1), side, p, hull)
    lamp('tip lamp', (6.51, 0, -.06), (.04, .3, .1), '+x', p, hull)
    for s in (-1, 1): lamp('bow lamp', (5.9, s * .4, -.2), (.3, .04, .08), '+y' if s > 0 else '-y', p, hull)
    # the drive: a dark slab over the stern, a heavy nozzle with a glowing ring
    chamfered('stern slab', (-4.3, 0, 1.25), (1.0, 2.2, .8), p['dark'], hull, .2)
    lamp('slab lamp', (-3.79, .7, 1.25), (.04, .3, .1), '+x', p, hull)
    chamfered('drive housing', (-5.9, 0, 0), (1.2, 1.9, 1.7), p['dark'], drive, .5)
    ring('drive glow', (-6.5, 0, 0), .78, .07, p['lamp'], drive, 'X')
    nozzle('drive', (-6.85, 0, 0), .85, .7, p, drive)
    for s in (-1, 1): nozzle('trim drive', (-6.2, s * .9, -.6), .28, .4, p, drive)
    return hull


# ── the battleship: an armoured wedge, towers of masts ────────────

BS_W, BS_H = 3.2, 2.8
BS_BANDS = [('cream', .52, 1.0), ('olive', -.62, .44), ('cream', -1.0, -.7)]


def masts(name, at, heights, p, parent, base=(.7, .6, .36)):
    """a tower of antennas on a dark block"""
    x, y, z = at
    chamfered(name, (x, y, z + base[2] / 2), base, p['dark'], parent, .1)
    lamp(name + ' lamp', (x + base[0] / 2 + .01, y, z + base[2] / 2), (.04, base[1] * .6, .08), '+x', p, parent)
    for k, hh in enumerate(heights):
        antenna(name + ' mast', (x + (k - (len(heights) - 1) / 2) * .22, y + (.12 if k % 2 else -.12), z + base[2]), hh, p, parent)


def battleship(p, root):
    p = colors(p)
    hull, drive, deck = empty('hull', root), empty('drive', root), empty('deck', root)
    w, h, H = BS_W, BS_H, BS_H / 2
    segs = [(-10.0, -7.3), (-7.1, -4.4), (-4.2, -1.5), (-1.3, 1.4), (1.6, 4.3)]
    run('hull', segs, w, h, 'cream', p, hull, cut=.5, bands=BS_BANDS)
    for (a, b) in segs:
        for s in (-1, 1):
            side, y = ('+y' if s > 0 else '-y'), s * (w / 2 + .07)
            block('armour grille frame', ((a + b) / 2 + .55, y, -.05), (.74, .05, .9), p['dark'], hull, .03)
            vent('armour grille', ((a + b) / 2 + .55, y + s * .02, -.05), (.6, .04, .76), side, p, hull, 5)
            lamp('flank lamp', ((a + b) / 2 - .6, y, .76), (.3, .04, .1), side, p, hull)
        for s in (-1, 1):
            chamfered('roof box', ((a + b) / 2, s * 1.18, H + .2), (b - a - .7, .62, .4), p['cream'], hull, .12)
            vent('roof box vent', ((a + b) / 2 + .2, s * 1.18, H + .41), (.8, .34, .04), '+z', p, hull, 3)
        chamfered('skirt', ((a + b) / 2, 0, -H - .28), (b - a - .6, w - .6, .56), p['olive'], hull, .16)
    for _, x in segs[:-1]:
        for d in (-.12, .12): strap('strap', x + .1 + d, w, h, p, hull, cut=.5, width=.12)
    for s in (-1, 1):
        pipe('low pipe', [(4.4, s * (w / 2 + .14), -1.05), (-10.1, s * (w / 2 + .14), -1.05)], .08, p['mustard'], hull)
        pipe('mid pipe', [(4.0, s * (w / 2 + .14), -.72), (-9.8, s * (w / 2 + .14), -.72)], .05, p['mustard'], hull)
    # the bow: armour plates over a faceted wedge, a grille with lamp bars
    rings = loft('bow', [(4.3, w / 2, -H, H, .5, .5), (5.9, w / 2 - .12, -H + .1, H - .2, .55, .55), (7.2, w / 2 - .45, -H + .3, .55, .5, .45),
        (8.0, w / 2 - .8, -H + .55, .05, .38, .3)], p['dark'], hull)
    plating('bow plate', rings, (2, 3, 4, 5, 6, 7, 0), p['cream'], hull, gap=.1, depth=.14)
    for s in (-1, 1):
        vent('bow grille', (5.2, s * (w / 2 + .05), -.35), (.8, .04, .6), '+y' if s > 0 else '-y', p, hull, 4)
        vent('bow grille high', (6.3, s * (w / 2 - .02), .55), (.5, .04, .3), '+y' if s > 0 else '-y', p, hull, 3)
    block('nose grille frame', (8.02, 0, -.45), (.08, 1.0, .7), p['dark'], hull, .04)
    vent('nose grille', (8.05, 0, -.45), (.04, .84, .56), '+x', p, hull, 5)
    for s in (-1, 1):
        lamp('nose bar', (8.03, s * .62, -.45), (.04, .12, .5), '+x', p, hull)
        lamp('cheek lamp', (6.6, s * (w / 2 - .2), -.2), (.3, .04, .1), '+y' if s > 0 else '-y', p, hull)
        lamp('brow lamp', (6.8, s * .55, .82), (.24, .1, .04), '+z', p, hull)
    # the deck: a raised spine, three towers of masts
    segment('deck', -8.6, 2.4, 1.9, .6, 'cream', p, deck, H + .3, .18)
    for x in (-6.4, -2.0, 1.4): strap('deck strap', x, 1.9, .6, p, deck, H + .3, .18, .14)
    masts('tower fore', (2.2, 0, H + .6), (.5, .7), p, deck)
    masts('tower mid', (-1.2, 0, H + .6), (.9, 1.2, .7), p, deck)
    masts('tower aft', (-6.0, 0, H + .6), (1.0, 1.6, 1.3, .8), p, deck, (1.1, .8, .5))
    # the aft: a teal block, four pods
    segment('aft', -11.4, -10.2, w - .2, h - .2, 'teal', p, hull, cut=.45, bands=[('teal', .1, .9), ('cream', -.9, .04)])
    for s in (-1, 1):
        for z in (.7, -.7): pod('pod', -13.0, -10.4, s * (w / 2 - .2), z, .7, p, drive, 'cream', (('mustard', .3), ('teal', .72)), 'lamp')
    return hull


# ── the yacht: a boat hull, a glazed cabin, a winch and a crane ───

def yacht(p, root):
    p = colors(p)
    hull, drive = empty('hull', root), empty('drive', root)
    rings = loft('hull', [(-4.0, 1.25, -.9, .42, .45, .1), (1.0, 1.32, -.95, .45, .5, .1), (3.0, 1.18, -.85, .45, .5, .1),
        (4.3, .78, -.58, .43, .36, .1), (5.1, .3, -.24, .4, .14, .08)], p['teal'], hull)
    for i in range(4):
        for f_ in (4, 5, 6): panel('deck', rings, i, f_, (0, 1, 0, 1), p['cream'], hull, .03)
        for f_, u in ((3, (.5, 1)), (7, (0, .5))): panel('topside', rings, i, f_, (*u, 0, 1), p['cream'], hull, .03)
    for f_, u in ((3, (.05, .45)), (7, (.55, .95))): panel('bow stripe', rings, 3, f_, (*u, .2, 1), p['cream'], hull, .035)
    # the cabin: a cream house, glass on all sides, a mast with a dome
    cabin = loft('cabin', [(-1.4, .95, .42, 1.3, .05, .28), (1.9, .95, .42, 1.3, .05, .28), (2.9, .86, .42, .78, .05, .16)], p['cream'], hull)
    for k in range(4): window('cabin window', cabin, 0, 3, (.18, .86, .06 + k * .235, .25 + k * .235), p, hull, 'dark', .03)
    for k in range(4): window('cabin window', cabin, 0, 7, (.14, .82, .06 + k * .235, .25 + k * .235), p, hull, 'dark', .03)
    for u in ((.04, .5), (.5, .96)): window('windscreen', cabin, 1, 5, (*u, .14, .9), p, hull, 'dark', .03)
    for f_ in (4, 6): window('corner window', cabin, 1, f_, (.1, .9, .14, .9), p, hull, 'dark', .03)
    block('cabin roof', (.0, 0, 1.36), (2.6, 1.3, .1), p['shade'], hull, .03)
    block('roof hatch', (.6, 0, 1.43), (.5, .5, .06), p['dark'], hull, .02)
    barrel('mast', (-.6, 0, 1.75), .08, .8, p['dark'], hull, 'Z', sides=8)
    dome('radar dome', (-.6, 0, 2.15), .2, .2, '+z', p['white'], hull)
    lamp('mast lamp', (-.5, .09, 1.8), (.1, .04, .08), '+y', p, hull)
    antenna('whip', (.0, -.4, 1.4), 1.0, p, hull)
    # rails along the deck edges
    for s in (-1, 1):
        pipe('bow rail', [(2.9, s * 1.0, .45), (2.9, s * 1.0, .66), (4.4, s * .5, .66), (4.4, s * .5, .45)], .035, p['mustard'], hull, .08)
        pipe('aft rail', [(-1.6, s * 1.1, .45), (-1.6, s * 1.1, .7), (-3.7, s * 1.1, .7), (-3.7, s * 1.1, .45)], .035, p['mustard'], hull, .08)
        pipe('rub rail', [(4.0, s * .95, -.1), (-3.9, s * 1.33, -.1)], .05, p['mustard'], hull)
        block('side door', (.6, s * 1.31, -.38), (1.1, .05, .62), p['tealD'], hull, .03)
        handle('door rail', (1.3, s * 1.34, -.12), (1.3, s * 1.34, -.6), (0, s, 0), p, hull, .08)
        block('rub strake', (-.6, s * 1.3, -.44), (6.0, .1, .14), p['dark'], hull, .03)
        for x in (3.6, 1.8, -2.4): lamp('flank lamp', (x, s * (1.34 if x < 3 else 1.2), .2), (.26, .04, .1), '+y' if s > 0 else '-y', p, hull)
    block('cleat', (3.9, 0, .5), (.26, .2, .1), p['mustard'], hull, .03)
    block('bow hatch', (3.2, 0, .47), (.5, .44, .06), p['dark'], hull, .02)
    # the aft deck: a winch, a crane
    barrel('winch drum', (-2.3, 0, .8), .34, 1.0, p['dark'], hull, 'Y', sides=14)
    for y in (-.56, .56): barrel('winch cheek', (-2.3, y, .8), .44, .14, p['mustard'], hull, 'Y', sides=12)
    for k in range(6): ring('winch cable', (-2.3, -.4 + k * .16, .8), .35, .03, p['black'], hull, 'Y')
    crane('crane', [(-3.3, .5, .45), (-3.3, .3, 1.9), (-2.4, .3, 2.0)], p, root, color='cream')
    # the stern: stacked dark rings round a drive
    for k, (x, r) in enumerate(((-4.2, .95), (-4.55, .82), (-4.9, .7))): chamfered('stern ring', (x, 0, -.25), (.3, 2 * r, 2 * r), p['dark'], drive, r * .45)
    nozzle('drive', (-5.2, 0, -.25), .55, .4, p, drive)
    return hull


# ── the research ship: a dish, telescopes, booms, a truss spine ───

def sensor(name, at, p, parent, r=.22, length=.6, axis='X'):
    """a sensor pod: a cream drum, a dark ring, a glowing lens"""
    x, y, z = at
    barrel(name, at, r, length, p['cream'], parent, axis, sides=12)
    off = {'X': Vector((length / 2, 0, 0)), 'Y': Vector((0, length / 2, 0)), 'Z': Vector((0, 0, -length / 2))}[axis]
    barrel(name + ' ring', Vector(at) + off * .9, r + .03, .1, p['dark'], parent, axis, sides=12)
    barrel(name + ' lens', Vector(at) + off * 1.08, r * .6, .04, p['lamp'], parent, axis, sides=12, round_=0)


def research(p, root):
    p = colors(p)
    hull, drive, rig = empty('hull', root), empty('drive', root), empty('instruments', root)
    truss('spine', -5.6, 3.6, .55, p, hull, 0, 1.15)
    for (x0, x1), c in (((1.2, 3.0), 'teal'), ((-1.4, .6), 'cream'), ((-4.4, -2.4), 'teal')):
        segment('module', x0, x1, 1.7, 1.6, c, p, hull, cut=.3)
        for x in (x0 - .05, x1 + .05): strap('module frame', x, 1.7, 1.6, p, hull, cut=.3, width=.1)
        for s in (-1, 1): lamp('module lamp', (x1 - .3, s * .92, .25), (.04 * 0 + .26, .04, .1), '+y' if s > 0 else '-y', p, hull)
        vent('module vent', ((x0 + x1) / 2, 0, .86), (.7, .3, .04), '+z', p, hull)
    for x in (-3.0, .2): barrel('canister', (x, .45, -.95), .28, 1.4, p['olive'], hull, 'X', sides=12)
    # the dish at the bow, a collar to the spine
    for k, (x, r) in enumerate(((3.8, .7), (4.15, .82), (4.5, .7))): barrel('collar', (x, 0, 0), r, .3, p['dark'], hull, 'X', sides=16)
    dish('dish', (4.75, 0, 0), 2.1, .55, p, rig)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        rim = Vector((4.78, 2.05 * math.cos(a), 2.05 * math.sin(a)))
        beam('spoke', (5.3, .0, .0), rim, .08, p['dark'], rig, .01)
        block('rim clamp', rim, (.2, .26, .26), p['mustard'], rig, .04)
        lamp('rim lamp', rim + Vector((.11, 0, 0)), (.04, .14, .14), '+x', p, rig)
    barrel('feed hub', (4.35, 0, 0), .32, .3, p['dark'], rig, 'X', sides=12)
    barrel('feed mount', (5.3, 0, 0), .3, .3, p['mustard'], rig, 'X', sides=12)
    barrel('feed rod', (5.9, 0, 0), .08, 1.0, p['white'], rig, 'X', sides=8)
    barrel('feed cap', (6.45, 0, 0), .16, .18, p['dark'], rig, 'X', sides=10)
    # telescopes on a mount over the fore module
    block('scope mount', (2.4, 0, 1.0), (.5, .5, .4), p['dark'], rig, .05)
    sensor('telescope', (2.7, -.2, 1.45), p, rig, .32, 1.6)
    sensor('finder', (2.5, .45, 1.2), p, rig, .18, .7)
    antenna('scope mast', (1.6, .3, .82), .9, p, rig)
    # booms with sensors, a small dish below
    for a, b in (((2.2, -.6, -.55), (3.4, -2.6, -2.2)), ((-.6, .9, 0), (-1.4, 3.6, -.9)), ((-.4, -.3, -.6), (-.4, -.3, -2.0))):
        beam('boom', a, b, .08, p['dark'], rig, .01)
        block('boom joint', a, (.22, .22, .22), p['mustard'], rig, .04)
    sensor('boom sensor', (3.55, -2.7, -2.3), p, rig, .24, .7)
    sensor('boom sensor', (-1.5, 3.75, -.95), p, rig, .24, .7)
    dish('small dish', (-.4, -.3, -2.1), .55, .14, p, rig, '-z')
    antenna('spine mast', (-.4, -.4, .85), .7, p, rig)
    # the drive: two black bells in cream housings
    for y in (-.62, .62):
        chamfered('housing', (-6.1, y, .2), (1.0, 1.1, 1.1), p['cream'], drive, .26)
        barrel('bell', (-7.0, y, .2), .5, .9, p['black'], drive, 'X', top=.72, sides=16)
        s = empty('drive plume', drive, (-7.5, y, .2)); s['plume'], s['radius'] = True, .55
    strap('aft frame', -5.55, 1.7, 1.6, p, hull, cut=.3, width=.14)
    return hull


# ── the colony ship: rings round a spine, gardens under glass ──────

def hoop(name, x, R, p, parent, n=24, axial=.7, radial=.5):
    """a habitat ring round the x axis: cream blocks, an olive rim, lamps on the bow face"""
    for k in range(n):
        a = (k + .5) / n * math.tau
        arc = math.tau * R / n
        c, o = Vector((x, R * math.cos(a), R * math.sin(a))), Vector((0, math.cos(a), math.sin(a)))
        block(name, c, (axial, arc - .04, radial), p['cream'], parent, .05, 1).rotation_euler.x = a - math.pi / 2
        block(name + ' rim', c + o * (radial / 2 + .05), (axial + .06, arc - .02, .12), p['sage'], parent, .03, 1).rotation_euler.x = a - math.pi / 2
        if k % 2: block(name + ' window', c + Vector((axial / 2 + .01, 0, 0)), (.04, arc * .45, radial * .3), p['lamp'], parent, .01, 1).rotation_euler.x = a - math.pi / 2
        if k % 6 == 0: block(name + ' clamp', c + o * (radial / 2 + .12), (axial * .5, arc * .3, .12), p['mustard'], parent, .03, 1).rotation_euler.x = a - math.pi / 2


def garden(name, x0, x1, r, p, parent, seed=3):
    """a greenhouse drum: green inside, trees on top, cream ribs round it"""
    leaf, leaf2 = mat('leaf', '#4F7D3B'), mat('leaf light', '#6E9A45')
    cx, length = (x0 + x1) / 2, x1 - x0
    barrel(name, (cx, 0, 0), r, length, leaf, parent, 'X', sides=16)
    rnd = __import__('random').Random(seed)
    for k in range(14):
        a = rnd.uniform(-1.3, 1.3)
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(.22, .34))
        link(name + ' tree', bm, leaf2 if k % 2 else leaf, parent, None, (rnd.uniform(x0 + .3, x1 - .3), r * .8 * math.sin(a), r * .8 * math.cos(a)))
    for k in range(int(length / .5) + 1): ring(name + ' rib', (x0 + k * length / int(length / .5), 0, 0), r + .04, .04, p['cream'], parent, 'X')
    for x in (x0, x1): barrel(name + ' cap', (x, 0, 0), r + .08, .16, p['cream'], parent, 'X', sides=16)


def colony(p, root):
    p = colors(p)
    hull, drive, habitat = empty('hull', root), empty('drive', root), empty('habitat', root)
    w, h, H = 2.2, 2.0, 1.0
    truss('spine', -6.4, 4.6, .5, p, hull, 0, 1.0)
    for x in (3.4, -.6, -4.6):
        hoop('ring', x, 2.3, p, habitat)
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            beam('ring spoke', (x, .5 * math.cos(a), .5 * math.sin(a)), (x, 2.05 * math.cos(a), 2.05 * math.sin(a)), .14, p['dark'], habitat, .02)
    garden('garden', -.05, 2.95, .85, p, habitat, 3)
    garden('garden', -4.05, -1.15, .85, p, habitat, 5)
    olive = mat('sphere olive', '#5F7046')
    for x, y, z in ((1.0, 1.35, -.7), (-3.4, -1.35, -.6), (-2.2, 1.35, .7)):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=9, radius=.5)
        link('fuel sphere', bm, olive, habitat, (.04, 1), (x, y, z))
        ring('sphere band', (x, y, z), .51, .04, p['mustard'], habitat, 'Z')
    for x, y, z in ((2.0, -1.3, -.6), (-1.9, -1.3, .65)):
        barrel('drum', (x, y, z), .36, 1.1, p['cream'], habitat, 'X', sides=12)
        barrel('drum band', (x, y, z), .38, .3, p['teal'], habitat, 'X', sides=12)
    # the fore block with side drums, the cab
    segment('fore', 4.7, 6.4, w, h, 'cream', p, hull, bands=[('cream', .1, .64), ('teal', -.64, .02)])
    for s in (-1, 1):
        barrel('fore drum', (5.4, s * (w / 2 + .3), -.2), .4, 1.2, p['cream'], hull, 'X', sides=12)
        barrel('fore drum band', (5.4, s * (w / 2 + .3), -.2), .42, .3, p['teal'], hull, 'X', sides=12)
        lamp('fore lamp', (6.0, s * (w / 2 + .3), .22), (.2, .04, .08), '+y' if s > 0 else '-y', p, hull)
    civil_cab(p, hull, 6.4, w, h, panes=2, length=1.9)
    antenna('cab mast 2', (6.5, -.45, H + .05), .65, p, hull)
    # the aft: an engine block, four pods
    segment('aft', -8.0, -6.5, w + .2, h + .2, 'cream', p, hull, bands=[('teal', .1, .74), ('cream', -.74, .04)])
    strap('aft band', -7.2, w + .2, h + .2, p, hull, width=.3)
    for x in (-7.6, -7.0): antenna('aft mast', (x, .5, H + .15), .6, p, hull)
    for s in (-1, 1):
        for z in (.55, -.55): pod('pod', -9.6, -7.8, s * (w / 2 + .1), z, .5, p, drive, 'cream', (('teal', .3), ('mustard', .72)), 'lamp')
    return hull


# ── the tug: two jaws, a winch, a high cab, pods on outriggers ─────

def jaw(name, s, p, parent):
    """one jaw of the claw: an arm forward, a hook turned in, armour in three colours"""
    pts = [Vector((1.4, s * 1.35, -.4)), Vector((3.5, s * 1.35, -.4)), Vector((4.25, s * .95, -.4)), Vector((4.0, s * .5, -.4))]
    for (a, b), c, size in zip(zip(pts, pts[1:]), ('cream', 'teal', 'dark'), (.62, .56, .46)):
        beam(name, a, b, size, p[c], parent, .08).scale.z = 1.7
    for a, b in zip(pts, pts[1:3]):
        beam(name + ' rail', a + Vector((0, 0, .56)), b + Vector((0, 0, .56)), .16, p['mustard'], parent, .04)
    block(name + ' plate', (2.4, s * 1.68, -.4), (1.4, .06, .62), p['teal'], parent, .03)
    block(name + ' band', (3.3, s * 1.68, -.4), (.24, .07, 1.0), p['mustard'], parent, .03)
    for z in (-.05, -.75): lamp(name + ' lamp', (4.4, s * .98, z), (.04, .2, .16), '+x', p, parent)
    barrel(name + ' hinge', (1.5, s * 1.35, -.4), .32, .5, p['dark'], parent, 'Z', sides=12)
    barrel(name + ' hinge cap', (1.5, s * 1.35, -.1), .2, .12, p['mustard'], parent, 'Z', sides=10)


def tug(p, root):
    p = colors(p)
    hull, drive, claw = empty('hull', root), empty('drive', root), empty('claw', root)
    w, h, H = 2.4, 2.0, 1.0
    run('body', [(-3.0, -.9), (-.72, 1.4)], w, h, 'cream', p, hull, bands=[('cream', .05, .64), ('teal', -.64, -.02)])
    rings, nose = cab(p, hull, 1.4, w - .2, h + .2, 'cream', 'cream', 2, 1.3)
    for f_, u in ((3, (0, .3)), (7, (.7, 1))): panel('cab skirt', rings, 0, f_, (*u, 0, 1), p['teal'], hull, .03)
    block('cab face', (nose - .05, 0, -.55), (.2, 1.3, .5), p['teal'], hull, .05)
    for s in (-1, 1): lamp('face lamp', (nose + .06, s * .45, -.55), (.04, .2, .12), '+x', p, hull)
    pipe('roof rail', [(.2, -.3, H + .1), (.2, -.3, H + .3), (1.0, -.3, H + .3), (1.0, -.3, H + .1)], .045, p['mustard'], hull, .08)
    antenna('cab mast', (.4, .45, H + .05), .7, p, hull)
    vent('roof vent', (-1.8, 0, H + .07), (.8, .5, .04), '+z', p, hull)
    # the claw: a base, a winch between the jaws, two jaws
    block('jaw base', (2.3, 0, -.45), (1.4, 2.0, .9), p['dark'], claw, .08)
    barrel('winch drum', (3.0, 0, -.35), .42, 1.3, p['dark'], claw, 'Y', sides=14)
    for k in range(8): ring('winch cable', (3.0, -.52 + k * .15, -.35), .43, .035, p['black'], claw, 'Y')
    for y in (-.75, .75): barrel('winch cheek', (3.0, y, -.35), .52, .14, p['mustard'], claw, 'Y', sides=12)
    for s in (-1, 1): jaw('jaw', s, p, claw)
    # flanks: a ladder, a teal hatch, rails, pipes
    for s in (-1, 1):
        side, y = ('+y' if s > 0 else '-y'), s * (w / 2 + .08)
        for x in (-.15, .25): block('ladder rail', (x, y + s * .04, .05), (.06, .06, 1.2), p['mustard'], hull, .02)
        for k in range(5): block('ladder rung', (.05, y + s * .04, -.45 + k * .24), (.46, .05, .05), p['mustard'], hull, .01, 1)
        block('hatch', (-1.4, y, -.05), (.7, .05, .7), p['teal'], hull, .04)
        vent('hatch vent', (-1.4, y + s * .03, -.05), (.4, .03, .3), side, p, hull, 3)
        handle('rail', (-2.5, y + s * .02, .4), (-2.5, y + s * .02, -.4), (0, s, 0), p, hull, .12)
        pipe('flank pipe', [(1.3, y + s * .06, -.75), (-2.9, y + s * .06, -.75)], .06, p['mustard'], hull)
        pipe('arc pipe', [(.9, s * (w / 2 + .05), .55), (.9, s * (w / 2 + .3), .55), (-.4, s * (w / 2 + .3), .55), (-.4, s * (w / 2 + .05), .55)], .06, p['mustard'], hull, .12)
        lamp('flank lamp', (.9, y, -.3), (.04 * 0 + .26, .04, .1), side, p, hull)
    # pods on outriggers, high and aft
    for s in (-1, 1):
        beam('outrigger', (-1.6, s * (w / 2 - .1), .4), (-2.4, s * (w / 2 + .8), .45), .3, p['dark'], drive)
        pipe('outrigger pipe', [(-1.0, s * (w / 2), .7), (-1.6, s * (w / 2 + .9), 1.0), (-2.2, s * (w / 2 + 1.1), 1.0)], .06, p['mustard'], drive, .12)
        pod('pod', -3.9, -1.3, s * (w / 2 + 1.0), .45, .6, p, drive, 'teal', (('cream', .7),), 'grille')
    return hull


# ── the liner: a sea hull, a market deck, houses in tiers ──────────

AWNINGS = ['#B0473A', '#D9A93A', '#46757A', '#E4D5B0', '#2F5D8C']


def stall(name, x, y, s, color, p, parent, z=0):
    """a market stall: four posts, a sloped awning, crates on a counter, a lamp"""
    for dx in (-.45, .45):
        for dy in (-.3, .3): block(name + ' post', (x + dx, y + dy, z + .4), (.05, .05, .8), p['dark'], parent, 0)
    block(name + ' awning', (x, y, z + .86), (1.06, .78, .07), mat('awning ' + color, color), parent, .02, 1).rotation_euler.x = s * .22
    block(name + ' counter', (x, y + s * .22, z + .22), (.9, .24, .44), p['shade'], parent, .02)
    for k, dx in enumerate((-.25, .1, .3)): block(name + ' crate', (x + dx, y - s * .05, z + .14 + (k % 2) * .1), (.2, .2, .2 + (k % 2) * .08), p['mustard'] if k % 2 else p['olive'], parent, .02)
    lamp(name + ' lamp', (x, y, z + .78), (.1, .1, .04), '-z', p, parent)


def house(name, x0, x1, y, depth, height, color, p, parent, z=0, windows=3):
    """a deck house: a coloured box, a flat roof, lit windows, a door"""
    cx = (x0 + x1) / 2
    block(name, (cx, y, z + height / 2), (x1 - x0, depth, height), mat('house ' + color, color), parent, .04)
    block(name + ' roof', (cx, y, z + height + .04), (x1 - x0 + .1, depth + .1, .08), p['shade'], parent, .02)
    for s in (-1, 1):
        for k in range(windows):
            block(name + ' window', (x0 + (k + .5) * (x1 - x0) / windows, y + s * (depth / 2 + .01), z + height * .62), (.22, .03, .18), p['lamp'], parent, .01, 1)
    block(name + ' door', (x1 - .3, y + depth / 2 + .01, z + .3), (.26, .03, .5), p['dark'], parent, .01, 1)


def railing(name, x0, x1, y, z, p, parent, step=.5):
    """a deck rail: dark posts, a top bar"""
    for k in range(int((x1 - x0) / step) + 1): block(name + ' post', (x0 + k * step, y, z + .2), (.04, .04, .4), p['dark'], parent, 0)
    block(name, ((x0 + x1) / 2, y, z + .4), (x1 - x0, .05, .05), p['dark'], parent, 0)


def liner(p, root):
    p = colors(p)
    hull, decks, drive = empty('hull', root), empty('decks', root), empty('drive', root)
    D = .8
    rings = loft('hull', [(-7.6, 2.1, -1.4, D, .9, .08), (-5.0, 2.3, -1.6, D, 1.0, .08), (4.0, 2.3, -1.6, D, 1.0, .08),
        (6.6, 1.6, -1.15, D, .75, .08), (8.2, .5, -.45, D, .3, .08)], p['dark'], hull)
    plating('hull plate', rings, (0, 2, 3, 7), p['teal'], hull, gap=.04)
    for s in (-1, 1):
        side = '+y' if s > 0 else '-y'
        for k in range(18): lamp('porthole', (-6.6 + k * .7, s * 2.37, .32), (.18, .04, .14), side, p, hull)
        for k in range(14): lamp('porthole low', (-5.4 + k * .7, s * 2.37, -.18), (.18, .04, .14), side, p, hull)
        for x in (-3.0, 2.2): block('fender', (x, s * 2.4, -.45), (1.3, .12, .3), p['cream'], hull, .05)
        block('boot stripe', (-.6, s * 2.36, -.56), (9.0, .05, .08), p['mustard'], hull, .02)
    for i in range(len(rings) - 1): panel('bulwark', rings, i, 5, (0, 1, 0, 1), p['cream'], hull, .1)
    # the fore deck: a bridge under a red roof, a crane with a crate
    bridge = empty('bridge', decks, (0, 0, D + .72))
    cab(p, bridge, 4.0, 3.0, 1.4, 'cream', 'cream', 3, 1.9)
    block('bridge roof', (5.0, 0, .78), (1.7, 2.8, .1), mat('awning #B0473A', '#B0473A'), bridge, .03).rotation_euler.y = .12
    crane('crane', [(2.9, -1.3, D), (3.1, -1.4, D + 2.4), (4.3, -1.6, D + 2.3)], p, root, color='dark')
    block('crane crate', (4.3, -1.6, D + 1.1), (.5, .5, .5), p['mustard'], root, .06)
    # the market deck: stalls along both rails, a house between
    z1 = D + .05
    block('market floor', (-.4, 0, z1), (8.2, 4.2, .1), p['shade'], decks, .02)
    for k, x in enumerate((2.8, 1.6, .4, -.8, -2.0, -3.2)):
        for s in (-1, 1): stall('stall', x, s * 1.6, s, AWNINGS[(k + (s > 0) * 2) % 5], p, decks, z1)
    house('hall', -3.8, 3.4, 0, 1.6, 1.0, '#E4D5B0', p, decks, z1, 6)
    for s in (-1, 1): railing('rail', -4.4, 3.6, s * 2.05, z1, p, decks)
    # the upper decks: two houses, plants, rails, then the top with a mast and a dish
    z2 = z1 + 1.1
    block('upper deck', (-1.2, 0, z2), (6.2, 3.2, .14), p['cream'], decks, .03)
    house('red house', -.6, 1.6, .2, 2.0, .9, '#9A3B2C', p, decks, z2 + .07, 3)
    house('green house', -3.8, -.8, -.1, 2.2, .8, '#4E7C6A', p, decks, z2 + .07, 3)
    for x, y in ((1.8, 1.3), (-1.0, 1.35), (-3.9, -1.3), (.2, -1.35)):
        block('planter', (x, y, z2 + .17), (.36, .36, .2), p['dark'], decks, .03)
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.24)
        link('bush', bm, mat('leaf', '#4F7D3B'), decks, None, (x, y, z2 + .45))
    for s in (-1, 1): railing('upper rail', -4.2, 1.8, s * 1.55, z2 + .07, p, decks)
    z3 = z2 + 1.0
    block('top deck', (-2.0, 0, z3), (3.4, 2.4, .14), p['cream'], decks, .03)
    chamfered('top block', (-1.2, -.4, z3 + .45), (1.3, 1.0, .8), p['mustard'], decks, .12)
    house('top house', -3.4, -2.0, .3, 1.2, .7, '#E4D5B0', p, decks, z3 + .07, 2)
    barrel('mast', (-2.6, -.5, z3 + 1.1), .08, 2.0, p['dark'], decks, 'Z', sides=8)
    block('mast yard', (-2.6, -.5, z3 + 1.7), (.1, 1.2, .08), p['dark'], decks, 0)
    for y in (-1.0, -.5, 0): antenna('mast whip', (-2.6, y, z3 + 1.7), .45 + abs(y) * .2, p, decks)
    dish('dish', (-.4, .6, z3 + .9), .5, .14, p, decks, '+z')
    barrel('dish post', (-.4, .6, z3 + .45), .06, .7, p['dark'], decks, 'Z', sides=8)
    # the stern: dark drive blocks
    for y in (-1.1, 1.1):
        chamfered('drive block', (-8.0, y, -.2), (1.4, 1.5, 1.5), p['dark'], drive, .4)
        nozzle('drive', (-8.85, y, -.2), .5, .4, p, drive)
    chamfered('stern block', (-7.6, 0, D + .4), (1.2, 3.4, .8), p['cream'], decks, .2)
    return hull


# ── the police robots: a patrol unit, an inspection unit ──────────
# a robot faces +x. joints: head, arm_l, arm_r, leg_l, leg_r.

def badge(name, at, size, p, parent):
    """the shield on a chest, facing +x: a cream shield, a blue field, a cream heart"""
    x, y, z = at
    for k, (pts, c, dx) in enumerate((([(-.5, .6), (.5, .6), (.5, 0), (0, -.62), (-.5, 0)], 'cream', 0),
            ([(-.36, .46), (.36, .46), (.36, -.02), (0, -.42), (-.36, -.02)], 'blue', .01))):
        bm = bmesh.new()
        lo = [bm.verts.new((x + dx, y + a_ * size, z + b * size)) for a_, b in pts]
        hi = [bm.verts.new((x + dx + .015, y + a_ * size, z + b * size)) for a_, b in pts]
        bm.faces.new(lo); bm.faces.new(list(reversed(hi)))
        for i in range(len(pts)): bm.faces.new([lo[i], lo[(i + 1) % len(pts)], hi[(i + 1) % len(pts)], hi[i]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        link(name + (' field' if k else ''), bm, p[c], parent)


def robot_head(p, root, at, s=1.0):
    """a police head: a blue box, a cream stripe, a dark visor, two eyes, ears, a bar on top"""
    head = empty('head', root, at); head['joint'] = True
    eye = mat('robot eye', '#9FF2FF', emission=6)
    block('skull', (0, 0, .2 * s), (.5 * s, .56 * s, .42 * s), p['blue'], head, .1 * s)
    block('skull stripe', (-.02 * s, 0, .2 * s), (.48 * s, .14 * s, .44 * s), p['cream'], head, .04 * s)
    block('visor', (.235 * s, 0, .17 * s), (.05, .42 * s, .26 * s), p['black'], head, .05 * s)
    for y in (-.09, .09): block('eye', (.262 * s, y * s, .17 * s), (.02, .06 * s, .1 * s), eye, head, .015, 1)
    for y in (-.13, .13): lamp('brow lamp', (.24 * s, y * s, .36 * s), (.03, .08 * s, .035 * s), '+x', p, head)
    for sy in (-1, 1):
        barrel('ear', (0, sy * .3 * s, .2 * s), .12 * s, .06, p['cream'], head, 'Y', sides=14)
        ring('ear rim', (0, sy * .32 * s, .2 * s), .11 * s, .022, p['mustard'], head, 'Y')
        block('ear slot', (0, sy * .335 * s, .2 * s), (.03 * s, .01, .1 * s), p['dark'], head, 0)
    block('bar base', (0, 0, .43 * s), (.16 * s, .34 * s, .05 * s), p['dark'], head, .02)
    for k, c in enumerate(('amber', 'dark', 'sky')):
        block(f'lightbar {c}' if c != 'dark' else 'bar middle', (0, (k - 1) * .11 * s, .48 * s), (.12 * s, .1 * s, .07 * s), p[c], head, .015, 1)
    return head


def police_patrol(p, root):
    p = colors(p)
    torso = empty('torso', root, (0, 0, .5))
    block('chest', (0, 0, .12), (.34, .42, .36), p['blue'], torso, .07)
    block('chest band', (0, 0, .06), (.36, .44, .14), p['cream'], torso, .03)
    badge('badge', (.18, 0, .06), .11, p, torso)
    lamp('chest lamp', (.18, 0, .23), (.03, .12, .04), '+x', p, torso)
    for sy in (-1, 1): block('chest side', (-.02, sy * .21, .1), (.2, .04, .2), p['dark'], torso, .02)
    block('hip', (0, 0, -.1), (.22, .32, .1), p['dark'], torso, .03)
    barrel('neck', (0, 0, .33), .06, .08, p['dark'], torso, 'Z', sides=8)
    robot_head(p, root, (0, 0, .86))
    for sy, n in ((1, 'arm_l'), (-1, 'arm_r')):
        arm = empty(n, root, (0, sy * .25, .72)); arm['joint'] = True
        block('shoulder', (0, sy * .04, 0), (.16, .12, .14), p['blue'], arm, .05)
        block('shoulder stripe', (0, sy * .1, 0), (.06, .02, .14), p['cream'], arm, .01, 1)
        barrel('elbow', (0, sy * .04, -.13), .045, .1, p['dark'], arm, 'Y', sides=10)
        ring('elbow ring', (0, sy * .06, -.13), .045, .012, p['mustard'], arm, 'Y')
        block('forearm', (.02, sy * .04, -.24), (.14, .12, .14), p['blue'], arm, .04)
        block('fist', (.03, sy * .04, -.35), (.1, .09, .08), p['cream'], arm, .03)
        if sy > 0: lamp('wrist lamp', (.1, sy * .04, -.24), (.02, .06, .06), '+x', p, arm)
    for sy, n in ((1, 'leg_l'), (-1, 'leg_r')):
        leg = empty(n, root, (0, sy * .1, .38)); leg['joint'] = True
        barrel('knee', (0, 0, -.09), .05, .12, p['dark'], leg, 'Y', sides=10)
        ring('knee ring', (0, sy * .06, -.09), .05, .012, p['mustard'], leg, 'Y')
        block('boot', (.03, 0, -.26), (.22, .14, .14), p['blue'], leg, .04)
        block('toe cap', (.11, 0, -.27), (.07, .15, .1), p['cream'], leg, .03)
        block('sole', (.03, 0, -.345), (.24, .15, .03), p['black'], leg, .01, 1)
        lamp('boot lamp', (.0, sy * .072, -.24), (.06, .02, .04), '+y' if sy > 0 else '-y', p, leg)
    return torso


def police_inspector(p, root):
    p = colors(p)
    torso = empty('torso', root, (0, 0, .78))
    block('chest', (0, 0, .1), (.5, .74, .56), p['blue'], torso, .1)
    block('chest band', (.01, 0, .1), (.5, .2, .58), p['cream'], torso, .04)
    badge('badge', (.26, 0, .06), .13, p, torso)
    for sy in (-1, 1): lamp('chest lamp', (.26, sy * .26, .26), (.03, .1, .05), '+x', p, torso)
    block('belly', (0, 0, -.25), (.4, .6, .2), p['blue'], torso, .06)
    block('hip', (0, 0, -.38), (.3, .5, .12), p['dark'], torso, .03)
    robot_head(p, root, (.04, 0, 1.12), .72)
    for sy, n in ((1, 'arm_l'), (-1, 'arm_r')):
        arm = empty(n, root, (0, sy * .48, .98)); arm['joint'] = True
        block('shoulder', (0, sy * .06, 0), (.36, .3, .3), p['blue'], arm, .08)
        block('shoulder stripe', (0, sy * .06, .155), (.37, .08, .02), p['cream'], arm, .01, 1)
        lamp('shoulder lamp', (.185, sy * .1, -.05), (.02, .1, .05), '+x', p, arm)
        barrel('elbow', (0, sy * .06, -.25), .08, .2, p['dark'], arm, 'Y', sides=12)
        ring('elbow ring', (0, sy * .12, -.25), .08, .018, p['mustard'], arm, 'Y')
        if sy < 0:
            # the scanner arm: a block with a glowing screen
            block('scanner', (.14, sy * .06, -.42), (.42, .24, .24), p['blue'], arm, .05)
            block('scanner stripe', (.1, sy * .06, -.42), (.06, .25, .25), p['cream'], arm, .01, 1)
            block('scanner screen', (.36, sy * .06, -.42), (.04, .2, .18), p['lamp'], arm, .02, 1)
        else:
            # the riot shield
            block('forearm', (.02, sy * .06, -.4), (.2, .2, .22), p['blue'], arm, .05)
            block('shield', (.08, sy * .24, -.5), (.06, .44, .8), p['blue'], arm, .04)
            block('shield stripe', (.08, sy * .27, -.5), (.065, .02, .8), p['cream'], arm, .01, 1)
            block('shield band', (.08, sy * .24, -.42), (.066, .44, .1), p['cream'], arm, .01, 1)
            lamp('shield lamp', (.115, sy * .24, -.18), (.02, .2, .04), '+x', p, arm)
    for sy, n in ((1, 'leg_l'), (-1, 'leg_r')):
        leg = empty(n, root, (0, sy * .2, .4)); leg['joint'] = True
        barrel('hip joint', (0, 0, 0), .08, .16, p['dark'], leg, 'Y', sides=12)
        block('thigh', (0, 0, -.1), (.2, .18, .16), p['dark'], leg, .04)
        block('shin', (.02, 0, -.22), (.26, .22, .16), p['blue'], leg, .06)
        lamp('shin lamp', (.155, 0, -.2), (.02, .1, .04), '+x', p, leg)
        block('boot', (.05, 0, -.33), (.36, .24, .12), p['blue'], leg, .05)
        block('toe cap', (.18, 0, -.33), (.1, .25, .1), p['cream'], leg, .03)
        block('sole', (.05, 0, -.39), (.38, .25, .03), p['black'], leg, .01, 1)
    return torso


# ── build ──────────────────────────────────────────────────────────

ROBOTS = [('police-patrol', police_patrol, 2.3), ('police-inspector', police_inspector, 3.0)]
SHIPS = [('police-light', police_light, 12), ('police-heavy', police_heavy, 15), ('freighter', freighter, 21), ('tanker', tanker, 20), ('transport', transport, 14), ('prison', prison, 18), ('frigate', frigate, 19), ('corvette', corvette, 15), ('battleship', battleship, 27), ('yacht', yacht, 11), ('research', research, 17), ('colony', colony, 19), ('tug', tug, 13), ('liner', liner, 21)]
manifest = []
for kind, models in (('hangar', SHIPS), ('robots', ROBOTS)):
    for name, fn, size in models:
        if args.only and args.only != name: continue
        manifest.append(build(name, fn, kind, size, out, not args.no_render))
(out / 'hangar.json').write_text(json.dumps(manifest, indent=4) + '\n')
print(json.dumps(manifest))
