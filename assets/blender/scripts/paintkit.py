"""The painted kit: flat paint, chunky parts, the merge, the export and the toon preview.

the build scripts import it: build-painted-fleet.py and build-hangar.py.
blender z up, bow +x, port +y. the glb export turns it to y up.
"""

import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector


# ── materials: flat paint, as the miniatures are painted ──────────

def srgb(value):
    rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]


MATS = {}


def mat(name, value, emission=0, rough=.72, metal=0):
    if name in MATS: return MATS[name]
    rgb = srgb(value)
    result = bpy.data.materials.new('painted / ' + name)
    result.diffuse_color = (*rgb, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Roughness'].default_value = rough
    shader.inputs['Metallic'].default_value = metal
    if emission:
        shader.inputs['Emission Color'].default_value = (*rgb, 1)
        shader.inputs['Emission Strength'].default_value = emission
    result['hex'], result['emissive'] = value, bool(emission)
    MATS[name] = result
    return result


def palette():
    return {
        'cream': mat('cream', '#E4D5B0'), 'shade': mat('cream shade', '#CDBB91'),
        'teal': mat('teal', '#46757A'), 'tealD': mat('teal dark', '#30555A'),
        'mustard': mat('mustard', '#E2A13B'), 'olive': mat('olive', '#6E7C49'),
        'rust': mat('rust', '#94402F'), 'dark': mat('gunmetal', '#3C3F44', rough=.55, metal=.3),
        'black': mat('engine throat', '#17191C', rough=.5), 'glass': mat('smoked glass', '#1F2B35', rough=.2),
        'lamp': mat('warm lamp', '#FFB347', emission=6), 'frost': mat('frost', '#BFE3F2'),
        'white': mat('reefer white', '#E6E4DC'), 'green': mat('green lamp', '#7CE08A', emission=5),
        'red': mat('red lamp', '#FF4A3A', emission=5),
    }


# ── geometry: chunky blocks with rounded edges, prisms, pipes ─────

def link(name, bm, material, parent, bevel=None, at=None):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(material)
    obj.parent = parent
    if at is not None: obj.location = at
    if bevel:
        modifier = obj.modifiers.new('rounded edge', 'BEVEL')
        modifier.width, modifier.segments = bevel
        modifier.limit_method = 'ANGLE'
        modifier.use_clamp_overlap = True
    return obj


def block(name, center, size, material, parent, round_=.06, seg=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return link(name, bm, material, parent, (min(round_, min(size) * .45), seg) if round_ else None, center)


def chamfered(name, center, size, material, parent, cut=.25, round_=.035):
    """a block with 45° corners along its length, the octagon section of the painted hulls"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    edges = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().x) > .9]
    bmesh.ops.bevel(bm, geom=edges, offset=min(cut, min(size[1], size[2]) * .45), segments=1, affect='EDGES', profile=.5)
    return link(name, bm, material, parent, (round_, 2), center)


def prism(name, points, y0, y1, material, parent, round_=.05):
    """an xz profile extruded along y"""
    bm = bmesh.new()
    a = [bm.verts.new((x, y1, z)) for x, z in points]
    b = [bm.verts.new((x, y0, z)) for x, z in points]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(len(points)):
        j = (i + 1) % len(points)
        bm.faces.new([b[i], b[j], a[j], a[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link(name, bm, material, parent, (round_, 2) if round_ else None)


def barrel(name, center, radius, length, material, parent, axis='X', top=None, sides=16, round_=.03, spin=0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=sides, radius1=radius,
        radius2=radius if top is None else top, depth=length)
    if spin: bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(spin, 3, 'Z'))
    turn = {'X': Matrix.Rotation(math.pi / 2, 3, 'Y'), 'Y': Matrix.Rotation(-math.pi / 2, 3, 'X'), 'Z': Matrix.Identity(3)}[axis]
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=turn)
    return link(name, bm, material, parent, (round_, 2) if round_ else None, center)


def ring(name, center, major, minor, material, parent, axis='X'):
    bm = bmesh.new()
    rings, sides = 24, 6
    grid = []
    for i in range(rings):
        a = i / rings * math.tau
        row = []
        for j in range(sides):
            b = j / sides * math.tau
            r = major + minor * math.cos(b)
            row.append(bm.verts.new((r * math.cos(a), r * math.sin(a), minor * math.sin(b))))
        grid.append(row)
    for i in range(rings):
        for j in range(sides):
            bm.faces.new([grid[i][j], grid[(i + 1) % rings][j], grid[(i + 1) % rings][(j + 1) % sides], grid[i][(j + 1) % sides]])
    turn = {'X': Matrix.Rotation(math.pi / 2, 3, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 3, 'X'), 'Z': Matrix.Identity(3)}[axis]
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=turn)
    return link(name, bm, material, parent, None, center)


def fillet(points, radius, steps=4):
    """round every inner corner of a polyline"""
    pts = [Vector(p) for p in points]
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u, w = (a - b).normalized(), (c - b).normalized()
        r = min(radius, (a - b).length * .45, (c - b).length * .45)
        p0, p1 = b + u * r, b + w * r
        for k in range(steps + 1):
            t = k / steps
            result.append(p0.lerp(b, t).lerp(b.lerp(p1, t), t))
    result.append(pts[-1])
    return result


def pipe(name, points, radius, material, parent, corner=.12, sides=8):
    path = fillet(points, corner)
    bm = bmesh.new()
    rings = []
    normal = None
    for i, p in enumerate(path):
        tangent = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        if normal is None:
            normal = tangent.cross(Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((1, 0, 0))).normalized()
        normal = (normal - tangent * normal.dot(tangent)).normalized()
        binormal = tangent.cross(normal)
        rings.append([bm.verts.new(p + (normal * math.cos(a) + binormal * math.sin(a)) * radius) for a in (k / sides * math.tau for k in range(sides))])
    for i in range(len(rings) - 1):
        for k in range(sides):
            bm.faces.new([rings[i][k], rings[i + 1][k], rings[i + 1][(k + 1) % sides], rings[i][(k + 1) % sides]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link(name, bm, material, parent)


def empty(name, parent=None, pos=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = pos
    return obj


# ── details, as the painter adds them ─────────────────────────────

AXES = {'+x': (0, 1), '-x': (0, -1), '+y': (1, 1), '-y': (1, -1), '+z': (2, 1), '-z': (2, -1)}


def lamp(name, center, size, facing, p, parent):
    """an orange strip in a dark frame, sunk into the paint"""
    axis, sign = AXES[facing]
    frame = list(size); frame[axis] = .06
    glow = [v * .72 for v in size]; glow[axis] = .07
    c = Vector(center)
    block(name + ' frame', c, frame, p['dark'], parent, .02, 1)
    lit = Vector(center); lit[axis] += sign * .02
    block(name, lit, glow, p['lamp'], parent, .015, 1)


def handle(name, a, b, out, p, parent, depth=.16):
    """a c-shaped grab rail from a to b, standing off the plate along `out`"""
    a, b, o = Vector(a), Vector(b), Vector(out) * depth
    pipe(name, [a, a + o, b + o, b], .035, p['mustard'], parent, .07)


def vent(name, center, size, facing, p, parent, slats=4):
    """a dark grille: louvers along its long side"""
    axis, sign = AXES[facing]
    block(name, center, size, p['dark'], parent, .02, 1)
    long, cross = sorted((i for i in range(3) if i != axis), key=lambda i: -size[i])
    for k in range(slats):
        c = Vector(center); c[axis] += sign * size[axis] * .5
        c[cross] += (k - (slats - 1) / 2) * size[cross] / slats
        span = [0, 0, 0]; span[axis], span[long], span[cross] = .02, size[long] * .85, size[cross] / (slats * 2.2)
        block(name + ' slat', c, span, p['black'], parent, 0)


def antenna(name, base, height, p, parent, tip='lamp'):
    barrel(name + ' foot', (base[0], base[1], base[2] + .06), .09, .12, p['dark'], parent, 'Z', sides=8)
    barrel(name, (base[0], base[1], base[2] + height / 2), .025, height, p['dark'], parent, 'Z', sides=6, round_=0)
    barrel(name + ' tip', (base[0], base[1], base[2] + height + .04), .045, .1, p[tip], parent, 'Z', sides=8, round_=0)


def nozzle(name, center, radius, length, p, parent, rim='dark'):
    """a drive bell opening aft, dark in the throat"""
    x, y, z = center
    barrel(name + ' bell', (x, y, z), radius, length, p[rim], parent, 'X', top=radius * .72)
    barrel(name + ' throat', (x - length / 2 - .005, y, z), radius * .78, .03, p['black'], parent, 'X', round_=0)
    s = empty(name + ' plume', parent, (x - length / 2 - .02, y, z))
    s['plume'], s['radius'] = True, radius * .7


def socket(root, name, family, pos, mount='light'):
    obj = empty('socket_' + name, root, pos)
    obj['family'], obj['mount'], obj['slot'] = family, mount, name
    return obj


# ── shipping containers: iso boxes in shipping colours ─────────────

BW, BH, BHC = .96, 1.0, 1.12          # width, height, high-cube height
BAY = 2.52                             # a 20 ft box and its gap
SHIPPING = ['#9A3B2C', '#2F5D8C', '#2E6F73', '#3E6B45', '#D2702E', '#D9A93A', '#8B8F93', '#E3E1DA', '#6E2B2B', '#24364F', '#B85C38', '#4E7C8A']


def darken(value, k):
    return '#' + ''.join(f'{max(0, min(255, round(int(value[i:i + 2], 16) * k))):02X}' for i in (1, 3, 5))


def wall(name, length, height, depth, pitch, material, parent, at, turn=0):
    """a corrugated wall: trapezoid ridges across its length, closed behind"""
    n = max(3, round(length / pitch))
    step = length / n
    ridge = []
    for k in range(n):
        x0 = -length / 2 + k * step
        ridge += [(x0, 0), (x0 + step * .18, depth), (x0 + step * .62, depth), (x0 + step * .8, 0)]
    poly = ridge + [(length / 2, 0), (length / 2, -.03), (-length / 2, -.03)]
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, -height / 2)) for x, y in poly]
    hi = [bm.verts.new((x, y, height / 2)) for x, y in poly]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if turn: bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(turn, 3, 'Z'))
    return link(name, bm, material, parent, None, at)


def container(name, kind, length, value, p, parent, at, high=False, logo=None):
    """an iso box: frame, corner castings, corrugated walls, doors with lock bars"""
    g = empty(name, parent, at)
    h, w = (BHC if high else BH), BW
    body, frame, steel = mat('box ' + value, value), mat('box frame ' + value, darken(value, .72)), p['dark']
    for sx in (-1, 1):
        for sy in (-1, 1):
            block('post', (sx * (length / 2 - .035), sy * (w / 2 - .035), 0), (.07, .07, h), frame, g, 0)
            for sz in (-1, 1): block('casting', (sx * (length / 2 - .04), sy * (w / 2 - .04), sz * (h / 2 - .04)), (.095, .095, .09), steel, g, 0)
        for sz in (-1, 1): block('end rail', (sx * (length / 2 - .035), 0, sz * (h / 2 - .045)), (.06, w - .16, .08), frame, g, 0)
    for sy in (-1, 1):
        for sz in (-1, 1): block('side rail', (0, sy * (w / 2 - .035), sz * (h / 2 - .045)), (length - .16, .06, .08), frame, g, 0)
    if kind == 'tank':
        barrel('tank', (0, 0, 0), h * .42, length - .3, body, g, 'X', sides=18)
        for x in (-length * .32, length * .32): ring('tank saddle', (x, 0, 0), h * .43, .03, frame, g, 'X')
        barrel('manhole', (0, 0, h * .42), .12, .08, steel, g, 'Z', sides=10)
        block('walkway', (0, 0, h / 2 - .02), (length * .6, .22, .03), steel, g, .01, 1)
        return g
    if kind == 'flat':
        block('floor', (0, 0, -h / 2 + .06), (length - .1, w - .1, .06), frame, g, .01, 1)
        for sx in (-1, 1): block('bulkhead', (sx * (length / 2 - .06), 0, 0), (.05, w - .14, h - .16), body, g, .01, 1)
        block('load', (0, 0, -.12), (length * .55, w * .7, h * .55), p['olive'], g, .04)
        for x in (-.25, .25): pipe('lashing', [(x * length, -w * .36, -h / 2 + .1), (x * length, -w * .36, .17), (x * length, w * .36, .17), (x * length, w * .36, -h / 2 + .1)], .015, p['mustard'], g, .04)
        return g
    for sy in (-1, 1): wall('side', length - .16, h - .17, .03, .25, body, g, (0, sy * (w / 2 - .05), 0), 0 if sy > 0 else math.pi)
    if kind == 'open': barrel('tarp', (0, 0, h / 2 - .04), w * .5, length - .18, mat('tarp ' + (logo or '#2F5D8C'), logo or '#2F5D8C'), g, 'X', sides=10).scale = (1, 1, .36)
    else: block('roof', (0, 0, h / 2 - .06), (length - .16, w - .1, .04), body, g, 0)
    if kind == 'reefer':
        block('machinery', (length / 2 - .05, 0, 0), (.05, w - .14, h - .17), p['white'], g, .01, 1)
        vent('reefer grille', (length / 2 - .02, -.15, -.1), (.03, .4, .5), '+x', p, g)
        barrel('reefer fan', (length / 2 - .02, .2, .15), .14, .03, steel, g, 'X', sides=14, round_=0)
        ring('reefer fan rim', (length / 2 - .01, .2, .15), .14, .02, frame, g, 'X')
        block('reefer box', (length / 2 - .02, .22, -.25), (.04, .18, .16), steel, g, .01, 1)
        lamp('reefer lamp', (length / 2 - .01, -.38, .38), (.03, .08, .04), '+x', {**p, 'lamp': p['green']}, g)
    else:
        block('doors', (length / 2 - .05, 0, 0), (.04, w - .14, h - .17), body, g, .008, 1)
        block('door seam', (length / 2 - .028, 0, 0), (.012, .016, h - .19), steel, g, 0)
        for y in (-.36, -.13, .13, .36):
            barrel('lock bar', (length / 2 - .022, y * w, 0), .012, h - .22, steel, g, 'Z', sides=6, round_=0)
            block('lock handle', (length / 2 - .014, y * w + .035, -.12), (.018, .07, .018), steel, g, 0)
    wall('end', w - .16, h - .17, .02, .15, body, g, (-length / 2 + .05, 0, 0), math.pi / 2)
    if logo and kind == 'dry':
        for sy in (-1, 1): block('logo', (0, sy * (w / 2 - .018), .08), (length * .48, .012, h * .3), mat('logo ' + logo, logo), g, 0)
    return g


# ── merge: one mesh per material per assembly, fewer draw calls ──

KEEP = ('tip', 'nav', 'lightbar', 'beacon', 'eye')


def consolidate(assembly, deep=True):
    """join the static meshes under an assembly. moving and blinking parts stay apart:
    each joint or spinning part is merged on its own"""
    meshes = []
    def walk(o):
        for c in o.children:
            if c.type == 'EMPTY':
                if c.get('spin') or c.get('joint'): consolidate(c)
                elif deep and not (c.get('sign') or c.name.startswith('socket_')): walk(c)
            elif c.type == 'MESH' and not any(k in c.name for k in KEEP):
                meshes.append(c)
    walk(assembly)
    if len(meshes) < 2: return
    for m in meshes:
        with bpy.context.temp_override(object=m, active_object=m, selected_objects=[m], selected_editable_objects=[m]):
            for mod in list(m.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes: m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    meshes[0].name = assembly.name + ' body'


def consolidate_all(root):
    for c in list(root.children):
        if c.type == 'EMPTY' and not c.name.startswith('socket_') and not c.get('sign'): consolidate(c)
    consolidate(root, deep=False)


# ── export: select an assembly, write it, count it ───────────────

def reset():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block_ in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block_):
            if item.users == 0: block_.remove(item)
    MATS.clear()


def export(root, path):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [root] + list(root.children_recursive): obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_apply=True,
        export_extras=True, export_animations=False, export_cameras=False, export_lights=False, export_yup=True)


def stats(root):
    deps = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for obj in root.children_recursive:
        if obj.type == 'MESH':
            mesh = obj.evaluated_get(deps).to_mesh()
            tris += sum(len(f.vertices) - 2 for f in mesh.polygons)
            obj.evaluated_get(deps).to_mesh_clear()
    return tris


# ── preview: toon light and an ink outline, at the painted angle ──

def toonify(size=14):
    outline = bpy.data.materials.new('preview / outline')
    outline.use_nodes = True
    nodes = outline.node_tree.nodes
    nodes.clear()
    em = nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (.012, .009, .007, 1)
    o = nodes.new('ShaderNodeOutputMaterial'); outline.node_tree.links.new(em.outputs[0], o.inputs[0])
    outline.use_backface_culling = True
    for m in list(MATS.values()):
        nt = m.node_tree
        base = nt.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:]
        nt.nodes.clear()
        out_ = nt.nodes.new('ShaderNodeOutputMaterial')
        if m.get('emissive'):
            em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = base; em.inputs['Strength'].default_value = 3
            nt.links.new(em.outputs[0], out_.inputs[0]); continue
        diff = nt.nodes.new('ShaderNodeBsdfDiffuse')
        rgb = nt.nodes.new('ShaderNodeShaderToRGB')
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        els = ramp.color_ramp.elements
        els[0].position, els[0].color = 0, (.46, .44, .5, 1)
        els[1].position, els[1].color = .12, (.74, .72, .74, 1)
        e3 = els.new(.36); e3.color = (1, 1, 1, 1)
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1
        a = next(i for i in mix.inputs if i.identifier == 'A_Color'); b = next(i for i in mix.inputs if i.identifier == 'B_Color')
        a.default_value = base
        em = nt.nodes.new('ShaderNodeEmission')
        nt.links.new(diff.outputs[0], rgb.inputs[0]); nt.links.new(rgb.outputs[0], ramp.inputs[0])
        noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 7; noise.inputs['Detail'].default_value = 8
        coord = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(coord.outputs['Object'], noise.inputs['Vector'])
        wear = nt.nodes.new('ShaderNodeValToRGB'); wear.color_ramp.interpolation = 'CONSTANT'
        wear.color_ramp.elements[0].color = (1, 1, 1, 1); wear.color_ramp.elements[1].position = .7; wear.color_ramp.elements[1].color = (.8, .76, .72, 1)
        both = nt.nodes.new('ShaderNodeMix'); both.data_type = 'RGBA'; both.blend_type = 'MULTIPLY'; both.inputs['Factor'].default_value = 1
        nt.links.new(noise.outputs['Fac'], wear.inputs[0])
        nt.links.new(ramp.outputs[0], next(i for i in both.inputs if i.identifier == 'A_Color'))
        nt.links.new(wear.outputs[0], next(i for i in both.inputs if i.identifier == 'B_Color'))
        nt.links.new(next(o_ for o_ in both.outputs if o_.identifier == 'Result_Color'), b)
        nt.links.new(next(o_ for o_ in mix.outputs if o_.identifier == 'Result_Color'), em.inputs[0])
        nt.links.new(em.outputs[0], out_.inputs[0])
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        obj.data.materials.append(outline)
        mod = obj.modifiers.new('outline', 'SOLIDIFY')
        mod.thickness, mod.offset, mod.use_flip_normals, mod.use_rim = size * .002, 1, True, False
        mod.material_offset = len(obj.data.materials) - 1


def render(root, name, size, out):
    scene = bpy.context.scene
    try: scene.render.engine = 'BLENDER_EEVEE'
    except TypeError: scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x, scene.render.resolution_y = 1536, 1024
    scene.render.film_transparent = True
    scene.render.image_settings.file_format, scene.render.image_settings.color_mode = 'PNG', 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('preview') if not scene.world else scene.world
    scene.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (.05, .06, .09, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
    key = bpy.data.objects.new('preview key', bpy.data.lights.new('preview key', 'SUN')); scene.collection.objects.link(key)
    key.data.energy, key.data.color = 3.2, (1, .93, .82); key.rotation_euler = (math.radians(50), math.radians(-25), math.radians(140))
    fill = bpy.data.objects.new('preview fill', bpy.data.lights.new('preview fill', 'SUN')); scene.collection.objects.link(fill)
    fill.data.energy, fill.data.color = .8, (.6, .75, 1); fill.rotation_euler = (math.radians(110), 0, math.radians(-40))
    cam = bpy.data.objects.new('preview camera', bpy.data.cameras.new('preview camera')); scene.collection.objects.link(cam)
    cam.data.type, cam.data.ortho_scale = 'ORTHO', size
    scene.camera = cam
    bpy.context.view_layer.update()
    pts = [obj.matrix_world @ Vector(c) for obj in root.children_recursive if obj.type == 'MESH' for c in obj.bound_box]
    middle = Vector([(min(q[i] for q in pts) + max(q[i] for q in pts)) / 2 for i in range(3)])
    for suffix, az, el in (('preview', 55, 30), ('reverse', -125, 28)):
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        cam.location = middle + d * 40
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        right = (-d).cross(Vector((0, 0, 1))).normalized(); up = right.cross(-d)
        key.rotation_euler = (-right * .55 + up * .7 + d * .45).normalized().to_track_quat('Z', 'Y').to_euler()
        fill.rotation_euler = (right * .6 - up * .25 + d * .2).normalized().to_track_quat('Z', 'Y').to_euler()
        scene.render.filepath = str(out / f'{name}-{suffix}.png')
        bpy.ops.render.render(write_still=True)


def build(name, fn, category, size, out, preview=True, sockets_=None, dress=None):
    """build one model: the .blend with every part, the merged glb, its stats and the previews.
    dress(p, root) adds parts for the previews only, after the export"""
    reset()
    p = palette()
    root = empty(name.replace('-', '_'))
    root['category'], root['forward_axis'], root['export_up_axis'] = category, '+x', '+y'
    fn(p, root)
    if sockets_:
        for slot, pos in sockets_.items(): socket(root, slot, slot.rstrip('1'), pos)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f'{name}.blend'))
    consolidate_all(root)
    export(root, out / f'{name}.glb')
    info = {'name': name, 'category': category, 'triangles': stats(root), 'bytes': (out / f'{name}.glb').stat().st_size}
    if dress: dress(p, root)
    if preview:
        toonify(size)
        render(root, name, size, out)
    return info
