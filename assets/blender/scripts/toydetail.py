"""make toy seams, hollow nozzles, windows and pipe clamps."""

import math

import bmesh
from mathutils import Matrix

import paintkit as kit
import toykit as toy


def tube(name, at, radius, bore, length, material, root, axis='X'):
    mesh = bmesh.new()
    rings = []
    for r, z in ((radius, -length / 2), (radius, length / 2),
            (bore, length / 2), (bore, -length / 2)):
        rings.append([mesh.verts.new((r * math.cos(i * math.tau / 24),
            r * math.sin(i * math.tau / 24), z)) for i in range(24)])
    for a, b in zip(rings, rings[1:] + rings[:1]):
        for i in range(24):
            mesh.faces.new((a[i], a[(i + 1) % 24], b[(i + 1) % 24], b[i]))
    turn = {'X': Matrix.Rotation(math.pi / 2, 3, 'Y'),
        'Y': Matrix.Rotation(math.pi / 2, 3, 'X'), 'Z': Matrix.Identity(3)}[axis]
    bmesh.ops.rotate(mesh, verts=mesh.verts, cent=(0, 0, 0), matrix=turn)
    bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    return kit.link(name, mesh, material, root, (.12, 2), at=at)


def bolt(name, at, radius, material, root, axis='Z'):
    return kit.barrel(name, at, radius, radius * .6, material, root,
        axis, sides=8, round_=radius * .12)


def window(name, at, radius, p, root, axis='Y'):
    toy.drum(name + ' frame', at, radius, .8, p['red'], root, axis)
    offset = {'X': (-.6, 0, 0), 'Y': (0, -.6, 0), 'Z': (0, 0, .6)}[axis]
    lens = tuple(a + b for a, b in zip(at, offset))
    toy.drum(name + ' lit lens', lens, radius * .69, .25, p['glow'], root, axis)


def seam(name, obj, axes, width=.4, depth=.45):
    import bpy
    bpy.context.view_layer.objects.active = obj
    for modifier in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.context.view_layer.update()
    dimensions = tuple(obj.dimensions)
    for axis, positions in axes:
        for position in positions:
            for face in (i for i in range(3) if i != axis):
                for side in (-1, 1):
                    size = [dimensions[i] + 2 for i in range(3)]
                    size[axis], size[face] = width, depth * 2
                    at = list(obj.location)
                    at[axis] = position
                    at[face] += side * dimensions[face] / 2
                    cutter = kit.block(name + ' cutter', at, size, obj.data.materials[0], obj.parent, 0)
                    modifier = obj.modifiers.new(name, 'BOOLEAN')
                    modifier.operation, modifier.solver = 'DIFFERENCE', 'EXACT'
                    modifier.object = cutter
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    bpy.data.objects.remove(cutter, do_unlink=True)


def clamps(name, points, radius, p, root):
    for index, (at, axis) in enumerate(points):
        kit.ring(name + ' clamp ' + str(index), at, radius + .35,
            .55 if radius < 3 else 1.1, p['red'], root, axis)


def pipe(name, points, radius, p, root):
    return kit.pipe(name, points, radius, p['green'], root, corner=radius * 2, sides=12)


def finish(root):
    """smooth curved faces and keep the broad panels flat."""
    import bpy
    for obj in root.children_recursive:
        if obj.type != 'MESH':
            continue
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        mesh = obj.data
        mesh.set_sharp_from_angle(angle=math.radians(40))
        for face in mesh.polygons:
            face.use_smooth = True
        modifier = obj.modifiers.new('panel normals', 'WEIGHTED_NORMAL')
        modifier.keep_sharp = True
        modifier.weight = 50


def clips(root, p):
    """give each socket a rim and four visible latches."""
    for socket in list(root.children_recursive):
        if not socket.name.startswith('socket_'):
            continue
        mount = kit.empty('socket trim ' + socket['slot'], socket.parent, socket.location)
        mount.rotation_euler = socket.rotation_euler.copy()
        kit.ring('socket milk rim', (0, 0, .8), 3.35, .45, p['milk'], mount, 'Z')
        for x, y in ((-3.7, 0), (3.7, 0), (0, -3.7), (0, 3.7)):
            kit.block('socket latch', (x, y, .8), (1.5, 1.5, 1.4), p['butter'], mount, .3, 1)
