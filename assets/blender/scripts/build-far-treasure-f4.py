"""rebuild the original hull with the shared surface check."""

import importlib.util
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paintkit as kit
import surfacecheck


def build():
    script = Path(__file__).with_name('build-far-treasure-b.py')
    spec = importlib.util.spec_from_file_location('comparison', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fleet = module.fleetParts()
    assets = Path(__file__).resolve().parents[2]
    source, exports, renders = [assets / path for path in
        ('blender/painted', 'exports/painted', 'blender/renders/painted')]
    kit.reset()
    p, root = kit.palette(), kit.empty('far_treasure')
    root['metres_per_unit'] = 7.2
    root['category'], root['forward_axis'], root['export_up_axis'] = 'painted', '+x', '+y'
    fleet['far_treasure'](p, root)
    for slot, at in fleet['FAR_SOCKETS'].items():
        kit.socket(root, slot, slot.rstrip('1'), at)
    surfacecheck.validate(root, 7.2)
    bpy.ops.wm.save_as_mainfile(filepath=str(source / 'far-treasure.blend'))
    kit.consolidate_all(root)
    kit.export(root, exports / 'far-treasure.glb')
    fleet['fit'](fleet['STARTER'])(p, root)
    kit.toonify(14)
    kit.render(root, 'far-treasure', 14, renders)


build()
