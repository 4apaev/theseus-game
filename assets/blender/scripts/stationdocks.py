"""add four berths and keep their approach paths clear."""

import paintkit as kit


PADS = (
    ('berth_b', 'small', -190, 140, 76, 40),
    ('berth_c', 'medium', -20, 220, 180, 76),
    ('berth_d', 'large', 0, -175, 300, 120),
    ('berth_e', 'small', -190, -280, 76, 40),
)


def add(p, root):
    from paintedstations import beam, box, panel
    old = next(obj for obj in root.children if obj.name == 'berth')
    old['size'] = 'medium'
    for name, size, x, y, length, width in PADS:
        group = kit.empty('docking platform ' + name, root, (x, y, 0))
        box('dock pressure deck', (0, 0, -1), (length, width, 2), p['tealD'], group)
        panel('dock walking surface', (0, 0, 0), (length - 2, width - 2, .2),
            p['dark'], group, '+z', 0)
        for side in (-1, 1):
            for i in range(int(length // 12)):
                px = -length / 2 + 7 + i * 12
                panel('dock edge marking', (px, side * (width / 2 - 3), 0),
                    (5, 1, .15), p['mustard'], group, '+z', .45)
                box('nav dock lamp', (px, side * (width / 2 - 1), .9),
                    (.6, .6, .4), p['lamp'], group)
        for side in (-1, 1):
            panel('dock target', (0, side * 6, 0), (10, 1, .12),
                p['cream'], group, '+z', .45)
        anchor = (-106 if x < -100 else -60, 86 if y > 0 else -86, -3)
        beam('dock support arm', anchor, (x, y, -1.5), 2.6, p['teal'], root)
        beam('dock lower brace', (anchor[0] + 10, anchor[1], -3),
            (x + length / 3, y, -1.5), 1.2, p['cream'], root)
        marker = kit.empty(name, root, (x, y, .45))
        marker['size'], marker['forward'] = size, '+x'
        marker['pad_length'], marker['pad_width'] = length, width
    validatePlan()


def validatePlan():
    for name, size, x, y, length, width in PADS:
        assert abs(y) - width / 2 > 96, name
        assert {'small': 60, 'medium': 150, 'large': 260}[size] + 10 <= length, name
        for other, _, ox, oy, ol, ow in PADS:
            if name == other:
                continue
            assert abs(y - oy) > (width + ow) / 2 + 4, (name, other)
    assert max(y + w / 2 for _, _, x, y, l, w in PADS) - min(
        y - w / 2 for _, _, x, y, l, w in PADS) < 600
