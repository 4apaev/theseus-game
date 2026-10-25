"""show ten role palettes on the approved cargo model."""

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit

assets = Path(__file__).resolve().parents[2]
folder = assets / 'concepts/toy/skins'
skins = json.loads((folder / 'skins.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(assets / 'blender/toy/ship-cargo.blend'))
source = bpy.data.objects['toy_ship_cargo']
original = [source, *source.children_recursive]
for index, (name, colours) in enumerate(skins.items()):
    copies = {}
    materials = {}
    for role, value in colours.items():
        material = bpy.data.materials[role].copy()
        material.name = name + ' / ' + role
        shader = material.node_tree.nodes.get('Principled BSDF')
        colour = (*kit.srgb(value), 1)
        shader.inputs['Base Color'].default_value = colour
        material.diffuse_color = colour
        if role == 'toy-glow':
            shader.inputs['Emission Color'].default_value = colour
        materials[role] = material
    for obj in original:
        copy = obj.copy()
        if obj.type == 'MESH':
            copy.data = obj.data.copy()
            for slot in copy.material_slots:
                slot.material = materials[slot.material.name]
        bpy.context.scene.collection.objects.link(copy)
        copies[obj] = copy
    for obj, copy in copies.items():
        copy.parent = copies.get(obj.parent)
    root = copies[source]
    root.name = 'skin ' + name
    root.rotation_euler = (math.radians(28), math.radians(-25), math.radians(-28))
    x, y = (index % 5 - 2) * 115, (0.5 - index // 5) * 118
    root.location = (x, y + 10, 0)
    curve = bpy.data.curves.new('label ' + name, 'FONT')
    curve.body, curve.align_x, curve.size = name, 'CENTER', 7
    label = bpy.data.objects.new('label ' + name, curve)
    bpy.context.scene.collection.objects.link(label)
    label.location = (x, y - 40, 15)
    label.data.materials.append(kit.mat('sheet label', '#f1eee4', emission=1))
    for n, role in enumerate(colours):
        chip = kit.block('swatch ' + name + ' ' + role,
            (x - 24 + n * 9.6, y - 49, 15), (8, 4, .5), materials[role], None, .5, 2)
for obj in reversed(original):
    bpy.data.objects.remove(obj, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 2560, 1152
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.world = bpy.data.worlds.new('sheet world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.015, .028, .024, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .8
light = bpy.data.objects.new('sheet key', bpy.data.lights.new('sheet key', 'SUN'))
scene.collection.objects.link(light)
light.data.energy = 2
light.rotation_euler = (math.radians(25), math.radians(-20), 0)
camera = bpy.data.objects.new('sheet camera', bpy.data.cameras.new('sheet camera'))
scene.collection.objects.link(camera)
camera.location = (0, 0, 700)
camera.data.type, camera.data.ortho_scale = 'ORTHO', 590
scene.camera = camera
scene.render.image_settings.file_format = 'WEBP'
scene.render.image_settings.quality = 95
scene.render.filepath = str(folder / 'cargo-skins.webp')
bpy.ops.render.render(write_still=True)
