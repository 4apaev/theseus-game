"""build rounded toy parts and export role colours."""

import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

import paintkit as kit
import surfacecheck

assets = Path(__file__).resolve().parents[2]
colours = {
    'red': '#e68d8b', 'green': '#a9cbb0', 'butter': '#efdc91',
    'milk': '#f1eee4', 'dark': '#294c3d', 'glow': '#d5edb4'
}


def palette():
    result = {}
    for role, value in colours.items():
        material = kit.mat('toy-' + role, value, emission=.6 if role == 'glow' else 0, rough=1)
        material.name = 'toy-' + role
        shader = material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Specular IOR Level'].default_value = 0
        result[role] = material
    return result


def ball(name, at, size, material, root):
    mesh = bmesh.new()
    bmesh.ops.create_uvsphere(mesh, u_segments=24, v_segments=12, radius=1)
    bmesh.ops.scale(mesh, vec=Vector(size), verts=mesh.verts)
    obj = kit.link(name, mesh, material, root, at=at)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def box(name, at, size, material, root):
    return kit.block(name, at, size, material, root, min(size) * .25, 3)


def drum(name, at, radius, length, material, root, axis='X'):
    return kit.barrel(name, at, radius, length, material, root, axis,
        sides=24, round_=min(radius * .2, length * .2))


def dish(name, at, radius, material, root):
    mesh = bmesh.new()
    rings = []
    for scale, z in ((.12, 0), (.5, radius * .13), (1, radius * .4),
            (1, radius * .4 + radius * .07), (.5, radius * .13 + radius * .07), (.12, radius * .07)):
        rings.append([mesh.verts.new((radius * scale * math.cos(i * math.tau / 24),
            radius * scale * math.sin(i * math.tau / 24), z)) for i in range(24)])
    for lower, upper in zip(rings, rings[1:] + rings[:1]):
        for i in range(24):
            mesh.faces.new((lower[i], lower[(i + 1) % 24], upper[(i + 1) % 24], upper[i]))
    bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    return kit.link(name, mesh, material, root, (radius * .025, 2), at=at)


def bounds(root):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(corner) for obj in root.children_recursive
        if obj.type == 'MESH' for corner in obj.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def save(root, name, limit, viewSize, subfolder=''):
    source = assets / 'blender/toy' / subfolder
    target = assets / 'exports/toy' / subfolder
    previews = assets / 'blender/renders/toy' / subfolder
    for folder in (source, target, previews):
        folder.mkdir(parents=True, exist_ok=True)
    root['units'], root['forward_axis'], root['export_up_axis'] = 'metres', '+x', '+y'
    root['surface_clearance'] = .25 if name.startswith('station') else .1
    count = kit.stats(root)
    if count > limit:
        raise ValueError(f'{name}: {count} triangles exceeds {limit}')
    surfacecheck.validate(root)
    extent = bounds(root)
    root['triangle_count'] = count
    bpy.ops.wm.save_as_mainfile(filepath=str(source / (name + '.blend')))
    kit.consolidate_all(root)
    kit.export(root, target / (name + '.glb'))
    info = {'name': name, 'triangles': kit.stats(root), 'bounds': extent,
        'units': 'metres', 'materials': ['toy-' + role for role in colours]}
    print(json.dumps(info))
    scale = min(1, 20 / viewSize)
    root.scale = (scale,) * 3
    kit.render(root, name, viewSize * scale, previews,
        'CYCLES' if root.get('detail_revision') else None)
