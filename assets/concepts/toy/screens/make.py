# the toy look: schematic screens and the ui kit, as svg and png, one set per palette.
# run from the theseus folder: python3 assets/concepts/toy/screens/make.py [palette]
import math, random, sys, os, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1600, 900

# a role per colour, so a screen reads the same in every palette
# mild pastels; meadow (soft red on green) first, toybox (sam's colours) next. candy and arcade went: too much contrast
PALETTES = {
    'meadow':    dict(space='#1d2e2a', deep='#13201d', panel='#2a403a', panel2='#34504a', line='#4d6e65',
                      coral='#ec8f84', mustard='#f2dc9a', mint='#a9dfb2', teal='#7fbf98', pink='#f5b3a8',
                      cream='#fbf6ec', cyan='#d6f5c9', lilac='#b9cfc4', ink='#13201d', grey='#8fa69c'),
    # sam's colours, sampled from his toy frames: indigo space, coral, amber, sea green, teal, cream
    'toybox':    dict(space='#1a0e5c', deep='#120845', panel='#2a1d72', panel2='#35278a', line='#4d3fa6',
                      coral='#e8664e', mustard='#efb23a', mint='#5fc4a2', teal='#2da5a0', pink='#ef7fa8',
                      cream='#f3e8d0', cyan='#8ff0e6', lilac='#b6a8e6', ink='#120845', grey='#8f86c0'),
    'lagoon':    dict(space='#173238', deep='#0f2226', panel='#22454c', panel2='#2b555d', line='#437880',
                      coral='#f4a3bd', mustard='#ffd9b3', mint='#9fe6df', teal='#6cc6c9', pink='#e98fb0',
                      cream='#f7fbfa', cyan='#c9f4f0', lilac='#b3d3d4', ink='#0f2226', grey='#86a7a9'),
    'postcard':  dict(space='#1e2638', deep='#141a28', panel='#2b354d', panel2='#35415d', line='#4f5d80',
                      coral='#e8857f', mustard='#f3dfa4', mint='#9cc6ea', teal='#6f9fd1', pink='#f1aaa6',
                      cream='#fbf5ec', cyan='#cfe3f7', lilac='#b6c0d8', ink='#141a28', grey='#8a95ad'),
    'dusk':      dict(space='#2a2438', deep='#1e1a29', panel='#3a3250', panel2='#463d60', line='#62577f',
                      coral='#f0a894', mustard='#f2dca6', mint='#b8e0c8', teal='#9a8fd0', pink='#e7a9c8',
                      cream='#faf6f2', cyan='#d9d2f2', lilac='#bdb3d6', ink='#1e1a29', grey='#958cae'),
    'sherbet':   dict(space='#141c4a', deep='#0c1235', panel='#222d6b', panel2='#2c3a85', line='#4558b0',
                      coral='#ffb38a', mustard='#fff1a8', mint='#9df2c8', teal='#5cc99d', pink='#c7b3ff',
                      cream='#fffaf0', cyan='#9ff3ff', lilac='#aab6f0', ink='#0c1235', grey='#8a95c8'),
    'bubblegum': dict(space='#0c2a2e', deep='#061a1d', panel='#12403f', panel2='#175250', line='#237270',
                      coral='#ff8ad8', mustard='#ffe066', mint='#7dffcf', teal='#6ec8ff', pink='#8b5cf6',
                      cream='#f7fffb', cyan='#7dffcf', lilac='#a9d8d0', ink='#061a1d', grey='#7fa8a4'),
}
NAMES = {
    'meadow': [ 'soft red', 'butter', 'pastel green', 'sage', 'rose', 'haze', 'milk', 'forest' ],
    'toybox': [ 'coral', 'amber', 'sea green', 'teal', 'rose', 'lilac', 'cream', 'indigo' ],
    'lagoon': [ 'pink', 'peach', 'aqua', 'deep aqua', 'rose', 'mist', 'foam', 'lagoon' ],
    'postcard': [ 'soft red', 'butter', 'soft blue', 'blue', 'blush', 'haze', 'paper', 'slate' ],
    'dusk': [ 'peach', 'butter', 'pistachio', 'lavender', 'orchid', 'mist', 'milk', 'dusk' ],
    'sherbet': [ 'peach', 'butter', 'mint', 'sage', 'lavender', 'haze', 'milk', 'midnight' ],
    'bubblegum': [ 'pink', 'banana', 'mint', 'sky', 'grape', 'sea', 'foam', 'deep teal' ],
}
C = {}
PAL = ''
FONT = "Arial Rounded MT Bold, Nunito, Arial, sans-serif"


def darken(hexc, k=.72):
    h = hexc.lstrip('#')
    return '#' + ''.join(f'{int(int(h[i:i + 2], 16) * k):02x}' for i in (0, 2, 4))


class Dark(dict):
    def __missing__(self, key): return darken(C[key])


DARK = Dark()


def esc(t): return str(t).replace('&', '&amp;').replace('<', '&lt;')


def text(x, y, t, size=22, fill=None, weight=500, anchor='start', ls=0, op=1):
    fill = fill or C['cream']
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}">{esc(t)}</text>'


def block(x, y, w, h, fill, r=6, lip=5, dark=None, hi=False, stroke=None):
    """a toy block: the face on a darker lip. small corners, no shine."""
    r = min(r, 8)
    d = dark or darken(fill)
    s = f'<rect x="{x}" y="{y + lip}" width="{w}" height="{h}" rx="{r}" fill="{d}"/>'
    return s + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="3"' if stroke else '') + '/>'


def btn(x, y, w, h, label, fill, fg=None, size=26):
    return block(x, y, w, h, fill) + text(x + w / 2, y + h / 2 + size * .36, label, size, fg or C['ink'], 700, 'middle')


def panel(x, y, w, h, title=None, fill=None):
    s = block(x, y, w, h, fill or C['panel'], r=26, lip=8, dark=DARK['panel'], hi=False, stroke=C['line'])
    if title: s += text(x + 26, y + 44, title, 26, C['cream'], 700)
    return s


def chip(x, y, t, fill, fg=None, size=20, w=None):
    w = w or len(str(t)) * size * .55 + 30
    return block(x, y, w, size + 16, fill, r=(size + 16) / 2, lip=4, hi=False) + text(x + w / 2, y + size * .95, t, size, fg or C['ink'], 700, 'middle')


def stars(n=180, seed=3, y0=0, y1=H):
    r = random.Random(seed)
    return ''.join(f'<circle cx="{r.random() * W:.0f}" cy="{r.uniform(y0, y1):.0f}" r="{r.choice([1, 1, 1.4, 2, 2.6]):.1f}" fill="{r.choice([C["cream"], C["lilac"], C["cyan"]])}" opacity="{r.uniform(.25, .8):.2f}"/>' for _ in range(n))


def icon(kind, x, y, s=40):
    """bright flat icons on a round toy base."""
    k = s / 40
    g = f'<g transform="translate({x},{y}) scale({k})">'
    body = {
        'reactor': f'<circle r="11" fill="{C["mint"]}"/><ellipse rx="19" ry="7" fill="none" stroke="{C["cyan"]}" stroke-width="4"/><ellipse rx="19" ry="7" fill="none" stroke="{C["cyan"]}" stroke-width="4" transform="rotate(60)"/><ellipse rx="19" ry="7" fill="none" stroke="{C["cyan"]}" stroke-width="4" transform="rotate(-60)"/>',
        'cruise': f'<path d="M-16 -10 h20 l12 10 l-12 10 h-20 z" fill="{C["cream"]}"/><path d="M-16 -7 l-8 7 l8 7 z" fill="{C["coral"]}"/><circle cx="-24" cy="0" r="5" fill="{C["mustard"]}"/>',
        'maneuver': f'<path d="M0 -20 l7 9 h-4 v8 h8 v-4 l9 7 l-9 7 v-4 h-8 v8 h4 l-7 9 l-7 -9 h4 v-8 h-8 v4 l-9 -7 l9 -7 v4 h8 v-8 h-4 z" fill="{C["lilac"]}"/>',
        'cargo': f'<rect x="-17" y="-15" width="34" height="30" rx="5" fill="{C["mustard"]}"/><rect x="-17" y="-4" width="34" height="6" fill="{DARK["mustard"]}"/><rect x="-4" y="-15" width="8" height="30" fill="{C["coral"]}"/>',
        'utility': f'<path d="M0 18 v-22" stroke="{C["cream"]}" stroke-width="5"/><path d="M-15 -4 a15 15 0 0 1 30 0" fill="none" stroke="{C["pink"]}" stroke-width="5"/><path d="M-9 -4 a9 9 0 0 1 18 0" fill="none" stroke="{C["pink"]}" stroke-width="5"/><circle cy="-6" r="4" fill="{C["cyan"]}"/>',
        'fuel': f'<path d="M0 -19 C10 -6 14 2 14 7 a14 14 0 0 1 -28 0 C-14 2 -10 -6 0 -19 z" fill="{C["teal"]}"/><circle cx="-5" cy="6" r="4" fill="#fff" opacity=".5"/>',
        'power': f'<path d="M4 -20 l-14 22 h9 l-4 18 l15 -24 h-9 z" fill="{C["mustard"]}"/>',
        'coin': f'<circle r="17" fill="{C["mustard"]}"/><circle r="12" fill="none" stroke="{DARK["mustard"]}" stroke-width="3"/><text y="7" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="800" fill="{DARK["mustard"]}">₢</text>',
        'mail': f'<rect x="-18" y="-12" width="36" height="25" rx="4" fill="{C["cream"]}"/><path d="M-18 -10 l18 13 l18 -13" fill="none" stroke="{C["coral"]}" stroke-width="4"/>',
        'clock': f'<circle r="17" fill="{C["lilac"]}"/><path d="M0 -10 v10 l7 5" stroke="{C["ink"]}" stroke-width="4" fill="none" stroke-linecap="round"/>',
        'crate': f'<rect x="-16" y="-16" width="32" height="32" rx="6" fill="{C["coral"]}"/><path d="M-16 -16 l32 32 M16 -16 l-32 32" stroke="{DARK["coral"]}" stroke-width="4"/>',
        'ore': f'<path d="M-16 8 l6 -18 l12 -4 l12 10 l-4 14 z" fill="{C["grey"]}"/><path d="M-6 -6 l6 4 l-3 6 z" fill="{C["cyan"]}"/>',
        'food': f'<circle r="15" fill="{C["mint"]}"/><path d="M0 -15 q8 -8 12 -2" stroke="{C["teal"]}" stroke-width="4" fill="none"/>',
        'meds': f'<rect x="-16" y="-16" width="32" height="32" rx="9" fill="{C["cream"]}"/><path d="M0 -9 v18 M-9 0 h18" stroke="{C["coral"]}" stroke-width="6" stroke-linecap="round"/>',
        'gas': f'<rect x="-11" y="-17" width="22" height="34" rx="11" fill="{C["pink"]}"/><rect x="-4" y="-21" width="8" height="6" fill="{C["cream"]}"/>',
        'chip': f'<rect x="-13" y="-13" width="26" height="26" rx="4" fill="{C["teal"]}"/><path d="M-8 -18 v5 M0 -18 v5 M8 -18 v5 M-8 13 v5 M0 13 v5 M8 13 v5" stroke="{C["cream"]}" stroke-width="3"/>',
        'ship': f'<path d="M-18 -8 h22 q14 0 16 8 q-2 8 -16 8 h-22 z" fill="{C["cream"]}"/><circle cx="8" cy="0" r="4" fill="{C["teal"]}"/><circle cx="-24" cy="-4" r="4" fill="{C["cyan"]}" opacity=".7"/><circle cx="-29" cy="2" r="3" fill="{C["lilac"]}" opacity=".6"/>',
        'station': f'<circle r="15" fill="{C["coral"]}"/><rect x="-6" y="-24" width="12" height="11" rx="3" fill="{C["cream"]}"/><rect x="11" y="-4" width="11" height="9" rx="3" fill="{C["mint"]}"/><circle cx="-5" cy="4" r="3" fill="{DARK["coral"]}"/>',
    }[kind]
    return g + body + '</g>'


def badge(kind, x, y, r=30, fill=None):
    return f'<circle cx="{x}" cy="{y + 5}" r="{r}" fill="{DARK["panel2"]}"/><circle cx="{x}" cy="{y}" r="{r}" fill="{fill or C["panel2"]}" stroke="{C["line"]}" stroke-width="3"/>' + icon(kind, x, y, r * 1.15)


def counter(x, y, kind, value, of=None, w=250):
    s = block(x, y, w, 64, C['panel'], r=32, lip=6, dark=DARK['panel'], hi=False, stroke=C['line'])
    s += icon(kind, x + 34, y + 32, 36)
    s += text(x + 64, y + 42, value, 30, C['cream'], 700)
    if of: s += text(x + 64 + len(str(value)) * 16 + 8, y + 42, f'/ {of}', 22, C['grey'], 500)
    return s


def bar(x, y, w, v, fill, h=16, ghost=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{C["deep"]}"/>'
    if ghost is not None: s += f'<rect x="{x}" y="{y}" width="{w * ghost}" height="{h}" rx="{h / 2}" fill="{fill}" opacity=".35"/>'
    return s + f'<rect x="{x}" y="{y}" width="{w * v}" height="{h}" rx="{h / 2}" fill="{fill}"/>'


def compass(x, y, r, dest_deg, value, tilt):
    """the ship's position: a badge in a ring of bearings, an arrow to the destination."""
    s = f'<circle cx="{x}" cy="{y}" r="{r + 26}" fill="{C["deep"]}" opacity=".55"/>'
    s += f'<circle cx="{x}" cy="{y}" r="{r + 14}" fill="none" stroke="{C["lilac"]}" stroke-width="2" opacity=".5"/>'
    a0 = math.radians(-90 - 40)
    s += f'<path d="M{x + (r + 14) * math.cos(a0):.1f} {y + (r + 14) * math.sin(a0):.1f} A{r + 14} {r + 14} 0 0 1 {x + (r + 14) * math.cos(math.radians(dest_deg - 90)):.1f} {y + (r + 14) * math.sin(math.radians(dest_deg - 90)):.1f}" fill="none" stroke="{C["cyan"]}" stroke-width="6" stroke-linecap="round"/>'
    for i, l in enumerate('NESW'):
        a = math.radians(i * 90 - 90)
        s += text(x + (r + 40) * math.cos(a), y + (r + 40) * math.sin(a) + 8, l, 22, C['cream'], 700, 'middle', op=.8)
    a = math.radians(dest_deg - 90)
    px, py = x + (r + 16) * math.cos(a), y + (r + 16) * math.sin(a)
    s += f'<path d="M0 -13 L11 9 L0 4 L-11 9 Z" fill="{C["mustard"]}" transform="translate({px:.1f},{py:.1f}) rotate({dest_deg})"/>'
    s += f'<circle cx="{x}" cy="{y + 6}" r="{r}" fill="{DARK["panel2"]}"/><circle cx="{x}" cy="{y}" r="{r}" fill="{C["panel2"]}" stroke="{C["ink"]}" stroke-width="5"/>'
    s += f'<path d="M{x} {y - r} A{r} {r} 0 0 1 {x + r} {y} L{x} {y} Z" fill="{C["mint"]}"/><path d="M{x} {y} L{x - r} {y} A{r} {r} 0 0 0 {x} {y + r} Z" fill="{C["teal"]}"/>'
    s += f'<g transform="translate({x},{y}) rotate({dest_deg - 45})"><path d="M0 -26 L12 14 L0 7 L-12 14 Z" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="4" stroke-linejoin="round"/></g>'
    s += chip(x + r * .35, y + r * .7, value, C['ink'], C['cream'], 20)
    s += text(x - r - 40, y + r + 56, f'∠ {tilt}°', 24, C['cream'], 600)
    return s


def frame(name, body, title=None, sub=None):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">'
    s += f'<defs><radialGradient id="glow"><stop offset="0" stop-color="{C["panel2"]}"/><stop offset="1" stop-color="{C["space"]}"/></radialGradient></defs>'
    s += f'<rect width="{W}" height="{H}" fill="{C["space"]}"/><ellipse cx="{W / 2}" cy="{H / 2}" rx="900" ry="560" fill="url(#glow)" opacity=".6"/>'
    s += stars() + body
    if title: s += text(48, 66, title, 40, C['cream'], 700) + (text(48, 100, sub, 22, C['lilac'], 500) if sub else '')
    s += '</svg>'
    path = os.path.join(OUT, f'{name}-{PAL}.svg')
    open(path, 'w').write(s)
    png(path)


# ── the ui kit ────────────────────────────────────────────────

def ui_kit():
    b = ''
    # palette
    for i, k in enumerate(['coral', 'mustard', 'mint', 'teal', 'pink', 'lilac', 'cream', 'panel']):
        b += block(48 + i * 92, 140, 76, 76, C[k], r=20) + text(86 + i * 92, 244, NAMES[PAL][i], 17, C['lilac'], 600, 'middle')
    b += text(48, 290, 'a rounded sans · chunky, lowercase, friendly', 22, C['cream'], 500)
    b += text(48, 340, 'theseus', 60, C['cream'], 800) + text(330, 340, '1,600 ₢', 60, C['mustard'], 800)
    # buttons
    b += btn(48, 380, 200, 64, 'buy 10', C['mint']) + btn(268, 380, 200, 64, 'sell 4', C['coral']) + btn(488, 380, 220, 64, 'travel ▸', C['mustard'])
    b += btn(48, 470, 120, 56, 'ok', C['cream'], size=24) + btn(188, 470, 170, 56, 'cancel', C['panel2'], C['cream'], 24) + btn(378, 470, 200, 56, 'install', C['teal'], C['cream'], 24)
    # chips and tabs
    b += chip(48, 560, 'docked', C['mint']) + chip(160, 560, 'underway', C['mustard']) + chip(296, 560, 'red alert', C['coral']) + chip(436, 560, '0.6 c', C['lilac'])
    tabs = ['port', 'market', 'hold', 'nav', 'rigging', 'comms']
    b += block(48, 630, 660, 70, C['panel'], r=35, lip=6, dark=DARK['panel'], hi=False, stroke=C['line'])
    for i, t in enumerate(tabs):
        on = i == 1
        if on: b += block(58 + i * 108, 640, 104, 50, C['cream'], r=25, lip=4, hi=False)
        b += text(110 + i * 108, 674, t, 22, C['ink'] if on else C['cream'], 700, 'middle')
    # tool bar, shapez style but ours
    b += block(48, 730, 660, 120, C['panel'], r=30, lip=8, dark=DARK['panel'], hi=False, stroke=C['line'])
    for i, k in enumerate(['reactor', 'cruise', 'maneuver', 'cargo', 'utility', 'fuel']):
        x = 108 + i * 104
        on = i == 2
        b += block(x - 40, 748, 80, 80, C['cream'] if on else C['panel2'], r=20, lip=5, hi=on, dark=DARK['cream'] if on else DARK['panel2'])
        b += icon(k, x, 786, 44) + text(x, 846, str(i + 1), 16, C['lilac'], 700, 'middle')
    # counters
    b += counter(780, 140, 'coin', '1,600') + counter(1050, 140, 'fuel', '72', '120', 280) + counter(780, 220, 'cargo', '18', '40') + counter(1050, 220, 'power', '9', '12', 280)
    # a card next to a thing
    b += panel(780, 320, 420, 380, 'sol outpost')
    b += chip(1080, 340, 'market', C['mustard'], size=18)
    for i, (k, n, p, c) in enumerate([('food', 'protein vats', '34 ₢', C['mint']), ('ore', 'iron ore', '12 ₢', C['grey']), ('meds', 'meds', '88 ₢', C['coral'])]):
        y = 400 + i * 74
        b += badge(k, 830, y + 18, 26) + text(870, y + 26, n, 24, C['cream'], 600) + chip(1100, y + 2, p, c, size=18, w=84)
    b += btn(806, 628, 170, 48, 'open', C['mustard'], size=22) + btn(990, 628, 186, 48, 'later', C['panel2'], C['cream'], 22)
    b += f'<path d="M1200 480 L1248 470 L1240 496 Z" fill="{C["panel"]}" stroke="{C["line"]}" stroke-width="3"/>'
    b += icon('station', 1300, 470, 90)
    # toast
    b += block(780, 752, 420, 74, C['mint'], r=37, lip=6) + icon('coin', 822, 789, 40) + text(856, 798, '+340 ₢  sold 10 iron ore', 24, C['ink'], 700)
    # compass and slider
    b += compass(1400, 640, 70, 62, '1.3 ly', 15)
    b += text(1240, 820, 'burn', 20, C['lilac'], 600) + bar(1300, 806, 240, .62, C['coral'], 18) + f'<circle cx="{1300 + 240 * .62}" cy="815" r="17" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="4"/>'
    b += text(1240, 868, 'toggle', 20, C['lilac'], 600) + block(1320, 846, 80, 36, C['mint'], r=18, lip=4, hi=False) + f'<circle cx="1382" cy="864" r="14" fill="{C["cream"]}"/>'
    frame('ui-kit', b, 'the toy ui kit', 'chunky blocks, bright flat icons, a rounded sans.')


# ── the iso diagram: a grid plane, seen from above at an angle ─
#
# the player turns and zooms it. flat things (the plane, tiles, paths)
# are drawn in plane units under one matrix; things that stand up
# (worlds, badges, labels) stand at their projected point.

SPRITES = os.path.join(OUT, '..', 'sprites')


class Iso:
    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, u, v, h=0):
        return self.ox + (u - v) * self.s * .866, self.oy + (u + v) * self.s * .5 - h

    def flat(self, svg):
        a, b = self.s * .866, self.s * .5
        return f'<g transform="matrix({a:.3f} {b:.3f} {-a:.3f} {b:.3f} {self.ox} {self.oy})">{svg}</g>'


NS = 'vector-effect="non-scaling-stroke"'


def plane(iso, n, fill, ink):
    x0, y0 = iso.p(n, -n)
    x1, y1 = iso.p(n, n)
    x2, y2 = iso.p(-n, n)
    side = f'<path d="M{x0} {y0} L{x1} {y1} L{x2} {y2} L{x2} {y2 + 22} L{x1} {y1 + 22} L{x0} {y0 + 22} Z" fill="{darken(fill, .6)}"/>'
    g = f'<rect x="{-n}" y="{-n}" width="{2 * n}" height="{2 * n}" rx=".5" fill="{fill}"/>'
    g += ''.join(f'<path d="M{i} {-n} V{n} M{-n} {i} H{n}" stroke="{ink}" stroke-width="1.5" {NS} opacity=".2"/>' for i in range(-n + 1, n))
    g += f'<rect x="{-n}" y="{-n}" width="{2 * n}" height="{2 * n}" rx=".5" fill="none" stroke="{ink}" stroke-width="3" {NS} opacity=".45"/>'
    return side + iso.flat(g)


def tile(iso, u, v, t, col, on=False):
    g = f'<rect x="{u - t / 2}" y="{v - t / 2}" width="{t}" height="{t}" rx="{t * .2}" fill="{col}" opacity="{.28 if on else .12}"/>'
    g += f'<rect x="{u - t / 2}" y="{v - t / 2}" width="{t}" height="{t}" rx="{t * .2}" fill="none" stroke="{C["cream"] if on else col}" stroke-width="{8 if on else 6}" {NS}/>'
    return iso.flat(g)


def route(iso, pts, col, w=.2, dots=True):
    d = 'M' + ' L'.join(f'{u} {v}' for u, v in pts)
    g = f'<path d="{d}" stroke="{darken(col, .45)}" stroke-width="{w * 1.6}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    g += f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    if dots: g += f'<path d="{d}" stroke="{C["cream"]}" stroke-width="{w * .4}" fill="none" stroke-dasharray="{w * .15} {w * 1.4}" stroke-linecap="round"/>'
    return iso.flat(g)


def sprite(name, x, y, w):
    path = os.path.join(SPRITES, name + '.png')
    if not os.path.exists(path): return None
    import base64
    data = base64.b64encode(open(path, 'rb').read()).decode()
    return f'<image href="data:image/png;base64,{data}" x="{x - w / 2}" y="{y - w * .82}" width="{w}" height="{w}"/>'


def world(x, y, r, kind, body, accent):
    """a small round world with its facility: a toy, two tones, no shine."""
    found = sprite('station-' + { 'yard': 'ship-yard', 'gas': 'gas-skimmer' }.get(kind, kind), x, y, r * 3.4)
    if found: return found
    s = f'<ellipse cx="{x}" cy="{y}" rx="{r * 1.2}" ry="{r * .48}" fill="{C["deep"]}" opacity=".45"/>'
    cy = y - r * 1.05
    top = {
        'market': f'<path d="M{x - r * .55} {cy - r * .78} a{r * .55} {r * .5} 0 0 1 {r * 1.1} 0 z" fill="{accent}"/><rect x="{x - r * .62}" y="{cy - r * .82}" width="{r * 1.24}" height="{r * .16}" rx="3" fill="{C["cream"]}"/>',
        'yard': f'<rect x="{x + r * .1}" y="{cy - r * 1.5}" width="{r * .16}" height="{r * .8}" fill="{accent}"/><rect x="{x - r * .5}" y="{cy - r * 1.5}" width="{r * .8}" height="{r * .14}" fill="{accent}"/><rect x="{x - r * .5}" y="{cy - r * 1.36}" width="{r * .06}" height="{r * .3}" fill="{C["cream"]}"/>',
        'lab': f'<path d="M{x - r * .5} {cy - r * .8} a{r * .5} {r * .55} 0 0 1 {r} 0 z" fill="{C["cyan"]}" opacity=".85"/><circle cx="{x - r * .12}" cy="{cy - r * 1.02}" r="{r * .1}" fill="{C["cream"]}"/>',
        'mine': f'<path d="M{x - r * .3} {cy - r * .8} L{x} {cy - r * 1.55} L{x + r * .3} {cy - r * .8} z" fill="{accent}"/><circle cx="{x + r * .62}" cy="{cy - r * .66}" r="{r * .16}" fill="{C["grey"]}"/>',
        'gas': f'<rect x="{x - r * .55}" y="{cy - r * 1.3}" width="{r * .34}" height="{r * .6}" rx="{r * .17}" fill="{accent}"/><rect x="{x - r * .1}" y="{cy - r * 1.42}" width="{r * .34}" height="{r * .72}" rx="{r * .17}" fill="{C["cream"]}"/><rect x="{x + r * .35}" y="{cy - r * 1.22}" width="{r * .3}" height="{r * .52}" rx="{r * .15}" fill="{accent}"/>',
        'relay': f'<rect x="{x - r * .05}" y="{cy - r * 1.6}" width="{r * .1}" height="{r * .9}" fill="{C["cream"]}"/><path d="M{x - r * .45} {cy - r * 1.45} a{r * .45} {r * .3} 0 0 0 {r * .9} 0" fill="{accent}"/><circle cx="{x}" cy="{cy - r * 1.62}" r="{r * .08}" fill="{C["cyan"]}"/>',
    }[kind]
    s += top
    s += f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{darken(body, .7)}"/><circle cx="{x - r * .14}" cy="{cy - r * .14}" r="{r * .86}" fill="{body}"/>'
    s += f'<circle cx="{x + r * .32}" cy="{cy + r * .2}" r="{r * .12}" fill="{darken(body, .75)}"/><circle cx="{x - r * .4}" cy="{cy + r * .34}" r="{r * .08}" fill="{darken(body, .75)}"/>'
    s += f'<ellipse cx="{x}" cy="{cy + r * .06}" rx="{r * 1.28}" ry="{r * .3}" fill="none" stroke="{accent}" stroke-width="{r * .1}" stroke-dasharray="{r * .5} {r * .12}"/>' if kind in ('market', 'yard') else ''
    return s


def node(x, y, kind, r=26, fill=None):
    """a round badge where a route meets a tile, as on a board game."""
    return f'<circle cx="{x}" cy="{y + 4}" r="{r}" fill="{C["deep"]}" opacity=".6"/><circle cx="{x}" cy="{y}" r="{r}" fill="{fill or C["lilac"]}"/>' + icon(kind, x, y, r * 1.2)


def rocks(seed, n=14):
    r = random.Random(seed)
    s = ''
    for _ in range(n):
        x, y, k = r.uniform(0, W), r.uniform(140, H), r.uniform(14, 46)
        s += f'<ellipse cx="{x}" cy="{y}" rx="{k}" ry="{k * .78}" fill="{darken(C["panel"], .8)}"/><ellipse cx="{x - k * .15}" cy="{y - k * .25}" rx="{k * .7}" ry="{k * .45}" fill="{C["panel2"]}"/>'
    return s


def camera_ui():
    """the player turns and zooms the plane."""
    s = ''
    for i, g in enumerate([ '⟲', '⟳', '+', '−' ]):
        s += block(1360 + (i % 2) * 64, 700 + (i // 2) * 64, 54, 54, C['panel2'], stroke=C['line']) + text(1387 + (i % 2) * 64, 737 + (i // 2) * 64, g, 30, C['cream'], 700, 'middle')
    return s


def scene(seed, n, iso):
    planet = f'<circle cx="1480" cy="40" r="210" fill="{darken(C["mint"], .5)}"/><circle cx="1500" cy="20" r="180" fill="{C["mint"]}" opacity=".55"/>'
    return planet + rocks(seed) + plane(iso, n, darken(C['teal'], .32), C['mint'])


# ── market: one good, its whole market, on the plane ──────────

def market_flow(iso, good='meds'):
    """the flow of one good round here: makers left, buyers right, routes into and out of here."""
    makers = [ ((-5, -2.5), 'gas', 'titan ring', 18, 6, C['pink'], [ (-5, -2.5), (-5, -.6), (-1.4, -.6) ]),
               ((-2.5, -5), 'yard', 'ganymede yards', 22, 3, C['teal'], [ (-2.5, -5), (-.6, -5), (-.6, -1.4) ]),
               ((-5, 1.5), 'mine', 'ember station', 30, 9, C['coral'], [ (-5, 1.5), (-5, .6), (-1.4, .6) ]) ]
    buyers = [ ((4.5, -1.5), 'relay', 'wolf reach', 112, 14, C['mustard'], [ (1.4, -.6), (4.5, -.6), (4.5, -1.5) ]),
               ((4.5, 2.5), 'market', 'mars hub', 61, 2, C['coral'], [ (1.4, .6), (4.5, .6), (4.5, 2.5) ]),
               ((1.5, 5), 'lab', 'venus lab', 74, 4, C['pink'], [ (.6, 1.4), (.6, 5), (1.5, 5) ]) ]
    b = ''
    for *_, path in makers: b += route(iso, path, C['mint'], .24)
    for _, _, _, p, _, _, path in buyers: b += route(iso, path, C['mustard'] if p > 100 else C['coral'], .16 + p / 600)
    for (u, v), *_ in makers + buyers: b += tile(iso, u, v, 2.4, C['mint'])
    b += tile(iso, 0, 0, 2.8, C['mint'], True)
    for (u, v), kind, name, p, yrs, col, _ in sorted(makers + buyers, key=lambda e: sum(e[0])):
        x, y = iso.p(u, v)
        b += world(x, y, 30, kind, col, C['cream'])
        b += chip(x - 66, y + 30, name, C['panel'], C['cream'], 16, 132)
        b += chip(x + 40, y - 78, f'{p} ₢', C['mustard'] if p > 100 else C['cream'], size=17, w=70) + chip(x + 40, y - 42, f'{yrs} y', C['lilac'], size=15, w=52)
    x, y = iso.p(0, 0)
    b += world(x, y, 40, 'market', C['coral'], C['mustard'])
    return b + node(x + 64, y - 70, good, 30, C['cream']) + chip(x - 70, y + 44, 'sol outpost · here', C['cream'], size=17, w=150)


def market_iso():
    iso = Iso(720, 470, 52)
    b = scene(11, 7, iso) + market_flow(iso)
    good = 'meds'
    # the goods to pick, and what this one does here
    b += block(48, 128, 560, 84, C['panel'], stroke=C['line'])
    for i, k in enumerate([ 'food', 'ore', 'meds', 'gas', 'chip', 'crate' ]):
        on = k == good
        b += block(62 + i * 90, 140, 70, 60, C['cream'] if on else C['panel2']) + icon(k, 97 + i * 90, 170, 36)
    b += panel(48, 640, 420, 220, 'meds · 88 ₢ here')
    b += text(72, 724, 'made at 3 stations, wanted at 3.', 20, C['lilac'], 500) + text(72, 754, 'best: wolf reach, 112 ₢, 14 years.', 20, C['cream'], 600)
    b += btn(72, 784, 180, 56, 'buy 10', C['mint'], size=24) + btn(268, 784, 176, 56, 'sell 4', C['coral'], size=24)
    b += camera_ui()
    frame('market', b, 'market', 'one good at a time: who makes it, who wants it, what it costs on the way. turn and zoom the plane.')


def cube(x, y, a, h, col):
    """a toy cube on the plane: (x, y) its foot, `a` its half width, `h` its height."""
    hx, hy = a * .866, a * .5
    top = f'M{x} {y - h - hy * 2} L{x + hx} {y - h - hy} L{x} {y - h} L{x - hx} {y - h - hy} Z'
    left = f'M{x - hx} {y - h - hy} L{x} {y - h} L{x} {y} L{x - hx} {y - hy} Z'
    right = f'M{x + hx} {y - h - hy} L{x} {y - h} L{x} {y} L{x + hx} {y - hy} Z'
    return f'<path d="{left}" fill="{darken(col, .78)}"/><path d="{right}" fill="{darken(col, .6)}"/><path d="{top}" fill="{col}"/>'


def stack(x, y, good, n, price, col):
    """a stack of n cubes, the good on top, its price below: how much, how dear."""
    s = f'<ellipse cx="{x}" cy="{y - 8}" rx="22" ry="9" fill="{C["deep"]}" opacity=".5"/>'
    s += ''.join(cube(x, y - i * 13, 16, 13, col) for i in range(n))
    return s + node(x, y - n * 13 - 44, good, 15, C['cream']) + chip(x - 30, y + 6, f'{price} ₢', col, size=15, w=60)


def market_all():
    iso = Iso(760, 450, 50)
    b = scene(17, 7, iso)
    # where, kind, name, body, the best buy (good, price, how much), the best sell
    st = [ ((-4.5, -1.5), 'gas', 'titan ring', C['pink'], ('gas', 9, 4), ('food', 46, 2)),
           ((-1.5, -4.8), 'yard', 'ganymede yards', C['teal'], ('chip', 140, 1), ('ore', 38, 3)),
           ((-5, 3), 'mine', 'ember station', C['coral'], ('ore', 12, 4), ('meds', 96, 3)),
           ((4.5, -1.5), 'relay', 'wolf reach', C['mustard'], ('crate', 30, 2), ('meds', 112, 4)),
           ((4.5, 3), 'market', 'mars hub', C['coral'], ('food', 14, 3), ('chip', 210, 2)),
           ((.8, 5.2), 'lab', 'venus lab', C['pink'], ('meds', 40, 2), ('gas', 31, 3)),
           ((0, 0), 'market', 'sol outpost · here', C['coral'], ('meds', 88, 1), ('ore', 27, 2)) ]
    for i, a in enumerate(st[:-1]):
        b += route(iso, [ (0, 0), (a[0][0], 0), a[0] ], C['line'], .1, False)
    for (u, v), *_ in st: b += tile(iso, u, v, 2.6 if (u, v) == (0, 0) else 2.4, C['mint'], (u, v) == (0, 0))
    for (u, v), kind, name, body, buy, sell in sorted(st, key=lambda e: sum(e[0])):
        x, y = iso.p(u, v)
        b += world(x, y, 26, kind, body, C['cream'])
        b += stack(x - 62, y + 4, buy[0], buy[2], buy[1], C['mint']) + stack(x + 62, y + 4, sell[0], sell[2], sell[1], C['coral'])
        b += chip(x - len(name) * 4.6 - 15, y + 44, name, C['cream'] if (u, v) == (0, 0) else C['panel'], C['ink'] if (u, v) == (0, 0) else C['cream'], 16, len(name) * 9.2 + 30)
    b += panel(48, 600, 440, 260, 'the best trades')
    for i, (g, a, pa, z, pz, y) in enumerate([ ('meds', 'venus lab', 40, 'wolf reach', 112, 9), ('ore', 'ember', 12, 'ganymede', 38, 6), ('gas', 'titan ring', 9, 'venus lab', 31, 7) ]):
        yy = 680 + i * 58
        b += node(84, yy, g, 20, C['cream']) + text(116, yy - 4, f'{a} {pa} ₢ → {z} {pz} ₢', 18, C['cream'], 700) + text(116, yy + 20, f'+{pz - pa} ₢ a unit · {y} years', 16, C['lilac'], 500)
    b += block(1150, 128, 400, 96, C['panel'], stroke=C['line'])
    b += cube(1186, 170, 14, 22, C['mint']) + text(1210, 164, 'cheapest to buy here', 18, C['cream'], 700)
    b += cube(1186, 206, 14, 22, C['coral']) + text(1210, 200, 'pays best here', 18, C['cream'], 700)
    b += text(1420, 182, 'taller: more', 16, C['lilac'], 500)
    b += camera_ui()
    frame('market-all', b, 'market · all goods', 'every station shows its best buy and its best sell. the stack is how much; the chip, the price.')


def toy_ship(x, y, ang, body, accent):
    """the player's ship, a chunky toy: a fat hull, a bubble cockpit, a trail of puffs."""
    s = f'<ellipse cx="{x}" cy="{y + 46}" rx="44" ry="14" fill="{C["deep"]}" opacity=".5"/>'
    g = ''.join(f'<circle cx="{-60 - i * 26}" cy="{(i % 2) * 6 - 3}" r="{15 - i * 3}" fill="{C["cream"]}" opacity="{.9 - i * .18}"/>' for i in range(3))
    g += f'<rect x="-56" y="-18" width="22" height="36" rx="6" fill="{darken(accent, .75)}"/>'
    g += f'<path d="M-30 -20 L-42 -40 H-22 L-6 -18 Z" fill="{accent}"/><path d="M-30 20 L-42 40 H-22 L-6 18 Z" fill="{darken(accent, .8)}"/>'
    g += f'<path d="M-40 0 C-40 -24 0 -30 22 -24 C42 -18 52 -8 52 0 C52 8 42 18 22 24 C0 30 -40 24 -40 0 Z" fill="{darken(body, .75)}"/>'
    g += f'<path d="M-40 -2 C-40 -24 0 -30 22 -24 C42 -18 52 -8 52 -2 C40 4 0 6 -40 -2 Z" fill="{body}"/>'
    g += f'<circle cx="18" cy="-6" r="12" fill="{C["cyan"]}"/><circle cx="-6" cy="4" r="5" fill="{C["mustard"]}"/><circle cx="-20" cy="4" r="5" fill="{C["mustard"]}"/>'
    return s + f'<g transform="translate({x},{y}) rotate({ang}) scale(1.3)">{g}</g>'


def market_ship():
    iso = Iso(720, 470, 52)
    b = scene(23, 7, iso) + market_flow(iso)
    x, y = iso.p(3.1, -.6)
    b += toy_ship(x, y - 56, 30, C['cream'], C['coral'])
    x += 30
    # the trade card beside the ship, its tail to the ship
    b += f'<path d="M{x + 20} {y - 80} L{x + 70} {y - 132} L{x + 104} {y - 132} Z" fill="{C["panel"]}" stroke="{C["line"]}" stroke-width="3" stroke-linejoin="round"/>'
    b += panel(x + 60, 140, 400, 290, 'meds → wolf reach')
    rows = [ ('crate', 'aboard', '10 t · bought 88 ₢'), ('coin', 'sells', '112 ₢ · +240 ₢'), ('clock', 'lands in', '14 years') ]
    for i, (k, l, v) in enumerate(rows):
        yy = 214 + i * 50
        b += icon(k, x + 96, yy, 30) + text(x + 124, yy + 7, l, 18, C['lilac'], 600) + text(x + 230, yy + 7, v, 20, C['cream'], 700)
    b += btn(x + 84, 352, 150, 52, 'follow', C['mint'], size=22) + btn(x + 246, 352, 190, 52, 'change course', C['panel2'], C['cream'], 20)
    b += panel(48, 640, 420, 220, 'the hold · 10 of 40 t')
    for i, (k, n) in enumerate([ ('meds', 10), ('food', 0), ('ore', 0) ]):
        b += block(72 + i * 128, 704, 112, 72, C['cream'] if n else C['panel2']) + icon(k, 104 + i * 128, 740, 36) + text(150 + i * 128, 750, f'{n}' if n else '·', 24, C['ink'] if n else C['grey'], 800, 'middle')
    b += text(72, 822, 'underway: the market shows the way ahead.', 18, C['lilac'], 500)
    b += camera_ui()
    frame('market-ship', b, 'market · on the way', 'the flow with our ship on its route. the trade card rides beside the ship.')


# ── comms: the ansible net, on the plane ──────────────────────

def comms_iso():
    iso = Iso(680, 400, 46)
    b = scene(23, 7, iso)
    st = { 'sol outpost': ((0, 0), 'market', C['coral']), 'mars hub': ((-4, 0), 'market', C['pink']), 'ganymede yards': ((0, -4.5), 'yard', C['teal']),
           'alpha exchange': ((4, 0), 'relay', C['mustard']), 'wolf reach': ((4, -4.5), 'relay', C['lilac']), 'sirius gate': ((0, 4.5), 'gas', C['mint']) }
    links = [ ('sol outpost', 'mars hub'), ('sol outpost', 'ganymede yards'), ('sol outpost', 'alpha exchange'), ('alpha exchange', 'wolf reach'), ('sol outpost', 'sirius gate'), ('ganymede yards', 'wolf reach') ]
    for a, z in links:
        (u1, v1), (u2, v2) = st[a][0], st[z][0]
        b += route(iso, [ (u1, v1), (u2, v1), (u2, v2) ], C['lilac'], .14)
    for name, ((u, v), kind, col) in st.items():
        b += tile(iso, u, v, 2.4, C['lilac'], name == 'sol outpost')
    for name, ((u, v), kind, col) in sorted(st.items(), key=lambda e: sum(e[1][0])):
        x, y = iso.p(u, v)
        b += world(x, y, 32 if name != 'sol outpost' else 40, kind, col, C['cream'])
        b += chip(x - 70, y + 38, name, C['panel'] if name != 'sol outpost' else C['cream'], C['cream'] if name != 'sol outpost' else C['ink'], 16, 140)
    # letters on their way, and when each lands
    for (u, v), eta, col in [ ((-2, 0), 'lands in 3 d', C['pink']), ((4, -2.4), 'lands in 4.2 y', C['mustard']), ((2, 0), 'lands in 9 h', C['mint']) ]:
        x, y = iso.p(u, v)
        b += node(x, y - 16, 'mail', 26, col) + chip(x - 56, y - 74, eta, col, size=16, w=112)
    b += panel(1150, 140, 404, 420, 'to: mars hub')
    b += text(1176, 220, 'from: grey area', 20, C['lilac'], 600)
    b += f'<rect x="1176" y="240" width="352" height="140" rx="6" fill="{C["cream"]}"/>' + text(1196, 284, 'got 40 t of meds.', 22, C['ink'], 600) + text(1196, 318, 'hold a slot for me', 22, C['ink'], 600) + text(1196, 352, 'at the yards?', 22, C['ink'], 600)
    b += icon('clock', 1194, 416, 30) + text(1220, 424, 'lands in 3 days, ship time 2 h', 19, C['cream'], 600)
    b += btn(1176, 466, 352, 60, 'send', C['pink'])
    b += panel(48, 660, 360, 200, 'station channel')
    for i, (who, msg, col) in enumerate([ ('rook', 'iron is cheap at titan', C['mint']), ('vega', 'anyone fly to wolf?', C['mustard']) ]):
        y = 726 + i * 62
        b += f'<circle cx="80" cy="{y + 12}" r="15" fill="{col}"/>' + block(104, y - 10, 286, 50, C['panel2']) + text(118, y + 10, who, 16, col, 700) + text(118, y + 32, msg, 17, C['cream'], 500)
    b += camera_ui()
    frame('comms', b, 'comms', 'the ansible net on the plane: each letter rides a link, and shows when it lands.')


# ── rigging: the modules on the plane, inside the ship's outline ─

def rigging_iso():
    iso = Iso(660, 480, 50)
    b = scene(31, 7, iso)
    hull = f'<path d="M-5 -1.6 Q-6 0 -5 1.6 L2.8 2 Q5.8 1.8 6.2 0 Q5.8 -1.8 2.8 -2 Z" fill="{C["cream"]}" opacity=".16" stroke="{C["cream"]}" stroke-width="4" {NS}/>'
    b += iso.flat(hull)
    mods = { 'power1': ((0, 0), 'reactor', 'reactor mk2', C['mint'], '+12'), 'cruise1': ((-4, 0), 'cruise', 'cruise drive mk1', C['coral'], '−6'),
             'maneuver1': ((0, -3.6), 'maneuver', 'maneuver mk1', C['lilac'], '−2'), 'cargo1': ((0, 3.6), 'cargo', 'cargo mk2 · 40 t', C['mustard'], '−1'),
             'utility1': ((4, 0), 'utility', 'empty', C['grey'], '') }
    for k, ((u, v), *_) in mods.items():
        if k != 'power1': b += route(iso, [ (0, 0), (u, 0), (u, v) ] if v else [ (0, 0), (u, v) ], C['mustard'] if k != 'utility1' else C['grey'], .22, k != 'utility1')
    for k, ((u, v), ic, name, col, pw) in mods.items():
        b += tile(iso, u, v, 2.3, col, k == 'utility1')
    for k, ((u, v), ic, name, col, pw) in sorted(mods.items(), key=lambda e: sum(e[1][0])):
        x, y = iso.p(u, v)
        found = sprite('module-' + { 'cruise': 'cruise-drive', 'utility': 'antenna' }.get(ic, ic), x, y, 120) if k != 'utility1' else None
        b += found or (f'<ellipse cx="{x}" cy="{y}" rx="44" ry="18" fill="{C["deep"]}" opacity=".45"/>' + (block(x - 36, y - 74, 72, 66, col) + icon(ic, x, y - 41, 52) if k != 'utility1' else f'<rect x="{x - 36}" y="{y - 74}" width="72" height="66" rx="6" fill="none" stroke="{C["cream"]}" stroke-width="4" stroke-dasharray="10 8"/>' + text(x, y - 26, '+', 50, C['cream'], 800, 'middle')))
        b += chip(x - 62, y + 26, k, col if k != 'utility1' else C['cream'], size=16, w=124)
        if pw: b += chip(x + 36, y - 110, f'{pw} ⚡', C['ink'], col, 16, 64)
    b += panel(48, 128, 300, 236, 'the far treasure')
    for i, (k, l, v, g, col) in enumerate([ ('power', 'power', .75, .75, C['mustard']), ('cargo', 'hold', .45, None, C['coral']), ('cruise', 'speed', .6, None, C['mint']) ]):
        y = 196 + i * 56
        b += icon(k, 82, y + 8, 30) + text(108, y + 2, l, 20, C['lilac'], 600) + bar(108, y + 14, 214, v, col, 14, g)
    b += panel(1150, 128, 404, 540, 'utility1 · empty')
    b += text(1176, 204, 'fits: utility. in your hold:', 20, C['lilac'], 500)
    for i, (n, ic, col, on) in enumerate([ ('ansible transceiver', 'mail', C['pink'], True), ('radar mk1', 'utility', C['teal'], False) ]):
        y = 226 + i * 82
        b += block(1176, y, 352, 66, C['cream'] if on else C['panel2']) + icon(ic, 1214, y + 33, 38) + text(1246, y + 42, n, 22, C['ink'] if on else C['cream'], 700)
    b += text(1176, 420, 'preview', 21, C['cream'], 700)
    for i, (l, v, g, col) in enumerate([ ('power', .9, .75, C['mustard']), ('mail range', .8, 0, C['pink']), ('speed', .58, .6, C['mint']) ]):
        y = 444 + i * 42
        b += text(1176, y + 14, l, 18, C['lilac'], 600) + bar(1290, y + 2, 230, v, col, 14, g)
    b += btn(1176, 584, 170, 56, 'install', C['mint'], size=24) + btn(1358, 584, 170, 56, 'back', C['panel2'], C['cream'], 24)
    b += camera_ui()
    frame('rigging', b, 'rigging', 'the modules on the plane, inside the ship. the reactor feeds the rest. pick a slot, try a module.')


# quick look renders the svg square; the frame is the top 16:9 of it
def png(svg):
    subprocess.run([ 'qlmanage', '-t', '-s', str(W), '-o', OUT, svg ], capture_output=True)
    from PIL import Image
    Image.open(svg + '.png').crop((0, 0, W, H)).save(svg[:-4] + '.png')
    os.remove(svg + '.png')


for PAL in sys.argv[1:] or PALETTES:
    C = PALETTES[PAL]
    DARK.clear()
    for f in (ui_kit, rigging_iso, market_iso, market_all, market_ship, comms_iso): f()
    print(PAL, 'ok')
