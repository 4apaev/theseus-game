"""reject coplanar faces with different materials before export."""

import itertools
import math
from collections import defaultdict


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def normal(points):
    a, b = subtract(points[1], points[0]), subtract(points[2], points[0])
    cross = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    length = math.sqrt(dot(cross, cross))
    return tuple(v / length for v in cross) if length > 1e-12 else None


def projectedOverlap(a, b, axis):
    axes = [i for i in range(3) if i != axis]
    a, b = [[(p[axes[0]], p[axes[1]]) for p in poly] for poly in (a, b)]
    for poly in (a, b):
        for p, q in zip(poly, poly[1:] + poly[:1]):
            edge = (p[1] - q[1], q[0] - p[0])
            length = math.hypot(*edge)
            if length < 1e-12:
                continue
            pa, pb = [[dot(v, edge) / length for v in points] for points in (a, b)]
            if min(max(pa), max(pb)) - max(min(pa), min(pb)) <= 1e-7:
                return False
    return True


def conflict(a, b, tolerance):
    if a['object'] == b['object'] and a['face'] == b['face']:
        return False
    if a['material'] == b['material']:
        return False
    if dot(a['normal'], b['normal']) < 1 - 1e-10:
        return False
    origin, direction = a['points'][0], a['normal']
    if max(abs(dot(subtract(p, origin), direction)) for p in b['points']) > tolerance + 1e-8:
        return False
    return projectedOverlap(a['points'], b['points'], max(range(3), key=lambda i: abs(direction[i])))


def cells(face, tolerance, cellSize):
    ranges = []
    for axis in range(3):
        low = min(p[axis] for p in face['points']) - tolerance
        high = max(p[axis] for p in face['points']) + tolerance
        ranges.append(range(math.floor(low / cellSize), math.floor(high / cellSize) + 1))
    return itertools.product(*ranges)


def overlaps(faces, tolerance=1e-5, cellSize=8, limit=80):
    grid, prior, failures = defaultdict(list), [], set()
    for face in faces:
        face['normal'] = normal(face['points'])
        if face['normal'] is None:
            continue
        positions = list(cells(face, tolerance, cellSize))
        direction = tuple(math.floor(v * 1000) for v in face['normal'])
        keys = [(position, direction) for position in positions]
        neighbors = itertools.product(*(range(v - 1, v + 2) for v in direction))
        candidates = {index for neighbor in neighbors for position in positions
            for index in grid.get((position, neighbor), ())}
        for index in candidates:
            other = prior[index]
            pair = tuple(sorted((face['object'], other['object'])))
            if pair not in failures and conflict(face, other, tolerance):
                failures.add(pair)
                if len(failures) >= limit:
                    return sorted(failures)
        index = len(prior)
        prior.append(face)
        for key in keys:
            grid[key].append(index)
    return sorted(failures)


def triangles(root):
    import bpy
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in root.children_recursive:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            points = [tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices]
            for triangle in mesh.loop_triangles:
                slot = triangle.material_index
                material = evaluated.material_slots[slot].material if slot < len(evaluated.material_slots) else None
                yield {'object': obj.name, 'face': triangle.polygon_index,
                    'material': material.name_full if material else None,
                    'points': [points[i] for i in triangle.vertices]}
        finally:
            evaluated.to_mesh_clear()


def validate(root, metresPerUnit=1):
    failures = overlaps(triangles(root), 1e-5 / metresPerUnit, 8 / metresPerUnit)
    if failures:
        pairs = '\n'.join(f'  {a} / {b}' for a, b in failures)
        raise ValueError('coplanar overlapping faces with different materials:\n' + pairs)
