"""set the station plots and reserve the main street."""

import math
import random


SIZES = ((24, 30, 13), (27, 19, 8), (39, 12, 9), (46, 23, 14),
    (29, 17, 11), (34, 25, 10), (41, 22, 12), (31, 18, 7),
    (43, 26, 15), (21, 16, 8))

PLOTS = {
    'outpost': ((-99, 59, 0), (-98, 8, 0), (-27, 84, 0), (43, 68, 0),
        (96, 47, 90), (37, 20, 0), (-72, -61, 0), (-20, -56, 0), (40, -69, 0), (95, -53, 0)),
    'yards': ((-99, 58, 0), (-97, 4, 0), (-29, 84, 0), (39, 69, 0),
        (98, 50, 90), (45, 17, 0), (-70, -63, 0), (-18, -55, 0), (44, -68, 0), (100, -58, 0)),
    'hub': ((-98, 61, 0), (-94, 5, 0), (-29, 84, 0), (41, 72, 0),
        (96, 39, 90), (37, 19, 0), (-70, -60, 0), (-14, -54, 0), (43, -70, 0), (98, -52, 0)),
    'lab': ((-99, 59, 0), (-94, 2, 0), (-29, 84, 0), (42, 68, 0),
        (97, 43, 90), (42, 16, 0), (-72, -57, 0), (-18, -73, 0), (43, -63, 0), (99, -55, 0)),
    'gate': ((-107, 58, 0), (-101, 6, 0), (-34, 84, 0), (43, 70, 0),
        (113, 42, 90), (48, 15, 0), (-80, -58, 0), (-20, -70, 0), (49, -64, 0), (112, -54, 0)),
    'dock': ((-99, 59, 0), (-96, 4, 0), (-29, 84, 0), (42, 69, 0),
        (99, 42, 90), (38, 14, 0), (-69, -63, 0), (-16, -53, 0), (45, -69, 0), (99, -54, 0)),
    'gas': ((-100, 59, 0), (-96, 3, 0), (-29, 84, 0), (44, 70, 0),
        (98, 41, 90), (43, 17, 0), (-72, -61, 0), (-17, -73, 0), (45, -62, 0), (100, -57, 0)),
    'mine': ((-99, 61, 0), (-97, 7, 0), (-29, 84, 0), (41, 70, 0),
        (98, 45, 90), (43, 17, 0), (-70, -62, 0), (-17, -55, 0), (43, -69, 0), (100, -55, 0)),
    'relay': ((-98, 59, 0), (-94, 2, 0), (-29, 84, 0), (41, 70, 0),
        (98, 44, 90), (40, 15, 0), (-71, -57, 0), (-17, -74, 0), (44, -62, 0), (99, -53, 0)),
}


def overlaps(a, b, gap=0):
    return a[0] < b[2] + gap and a[2] > b[0] - gap and a[1] < b[3] + gap and a[3] > b[1] - gap


def footprint(x, y, width, depth, angle=0):
    a = math.radians(angle)
    dx = (abs(math.cos(a)) * width + abs(math.sin(a)) * depth) / 2
    dy = (abs(math.sin(a)) * width + abs(math.cos(a)) * depth) / 2
    return (x - dx, y - dy, x + dx, y + dy)


def workSites(name, occupied):
    rng = random.Random(917 + sum(map(ord, name)))
    sites = []
    edge = 136 if name == 'gate' else 120
    blocked = list(occupied) + [(-120, -40, edge + 10, -24)]
    for large, width, depth, count in ((True, 28, 32, 4), (False, 16, 18, 12)):
        added = 0
        for attempt in range(12000):
            x = rng.uniform(-edge + width / 2 + 3, edge - width / 2 - 3)
            y = rng.uniform(-91 + depth / 2, 91 - depth / 2)
            area = footprint(x, y, width, depth)
            if any(overlaps(area, other, 1) for other in blocked):
                continue
            sites.append((x, y, large))
            blocked.append(area)
            added += 1
            if added == count:
                break
    if sum(large for x, y, large in sites) < 2 or len(sites) < 10:
        raise ValueError(f'{name}: too few clear work areas fit')
    return sites
