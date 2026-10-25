"""check the station plans before the external blender build."""

import json
import sys
from pathlib import Path


project = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project / 'assets/blender/scripts'))
import stationlayout as layout


def plannedAreas(plots):
    areas = [(-71, 15, 7, 76), (-113, -88, -99, -74)]
    for i, ((x, y, angle), (w, d, h)) in enumerate(zip(plots, layout.SIZES)):
        area = layout.footprint(x, y, w + 3, d + 4, angle)
        if i == 3:
            area = area[:2] + (area[2] + 15, area[3])
        areas.append(area)
    return areas


def check(name, plots):
    areas = plannedAreas(plots)
    edge = 136 if name == 'gate' else 120
    street = (-120, -40, edge + 10, -24)
    for i, area in enumerate(areas):
        assert -edge < area[0] < area[2] < edge, (name, i, 'deck width')
        assert -94 < area[1] < area[3] < 94, (name, i, 'deck depth')
        assert not layout.overlaps(area, street), (name, i, 'street')
        assert not any(layout.overlaps(area, other) for other in areas[i + 1:]), (name, i, 'hall overlap')
    sites = layout.workSites(name, areas)
    for x, y, large in sites:
        area = layout.footprint(x, y, 28 if large else 16, 32 if large else 18)
        assert not any(layout.overlaps(area, other) for other in areas + [street]), (name, 'work overlap')
        areas.append(area)
    return {'kit': name, 'distinct_hall_sizes': len(set(layout.SIZES)),
        'work_areas': len(sites), 'large_work_areas': sum(site[2] for site in sites),
        'status': 'plan checks passed; blender bounds and renders remain'}


reports = [check(name, plots) for name, plots in layout.PLOTS.items()]
assert len(set(layout.SIZES)) == len(layout.SIZES)
scratch = project / 'agents/sam/scratch'
scratch.mkdir(exist_ok=True)
(scratch / 'station-layout-validation.json').write_text(json.dumps(reports, indent=4) + '\n')
print(json.dumps(reports, indent=4))
