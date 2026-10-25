# the toy ui icons: flat chunky shapes, an ink outline of one weight, rounded ends.
# run from the theseus folder: python3 assets/icons/toy/ui/make.py [palette ...]
# out: svg/<name>.svg (colours as the client's --toy-* vars, meadow as fallback) and sheet-<palette>.png
import math, os, re, subprocess, sys

OUT = os.path.dirname(os.path.abspath(__file__))
# the palettes of the screens generator, read without running it
SRC = open(os.path.join(OUT, '../../../concepts/toy/screens/make.py')).read()
exec(re.search(r'PALETTES = \{.*?\n\}', SRC, re.S).group(0))

# make.py's roles by the client's names (src/content/palettes.ts)
ROLES = dict(red='coral', amber='mustard', green='mint', teal='teal', pink='pink', cream='cream',
             glow='cyan', mist='lilac', ink='ink', deep='deep', panel='panel', panel2='panel2', line='line', space='space')
SW = 3  # the one stroke weight, in a 48 px box
VARS = False


def col(role):
    hexc = PALETTES['meadow' if VARS else PAL][ROLES[role]]
    return f'var(--toy-{role}, {hexc})' if VARS else hexc


def paint(fill, stroke='ink', w=SW):
    s = f'fill:{col(fill) if fill else "none"}'
    if stroke: s += f';stroke:{col(stroke)};stroke-width:{w};stroke-linecap:round;stroke-linejoin:round'
    return f'style="{s}"'


def path(d, fill, stroke='ink'): return f'<path d="{d}" {paint(fill, stroke)}/>'


def circle(x, y, r, fill, stroke='ink'): return f'<circle cx="{x}" cy="{y}" r="{r}" {paint(fill, stroke)}/>'


def rect(x, y, w, h, r, fill, stroke='ink'): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {paint(fill, stroke)}/>'


def line(d): return f'<path d="{d}" {paint(None)}/>'


def fat(d, fill, core=4):
    """a chunky bar: an ink line, the colour inside, so the outline keeps its weight."""
    return f'<path d="{d}" {paint(None, "ink", core + 2 * SW)}/><path d="{d}" {paint(None, fill, core)}/>'


def gear(n=8, r1=17, r2=12.5):
    pts = []
    for i in range(n * 4):
        a = math.pi * 2 * i / (n * 4) - math.pi / 2
        r = r1 if i % 4 in (0, 1) else r2
        pts.append(f'{24 + r * math.cos(a):.1f} {24 + r * math.sin(a):.1f}')
    return 'M' + ' L'.join(pts) + ' Z'


# ── places ────────────────────────────────────────────────────

def port():
    return line('M24 14 V8') + circle(24, 6.5, 2.5, 'amber') + rect(33, 19, 9, 6, 2, 'red') + path('M15 25 a9 9 0 0 1 18 0 z', 'cream') + f'<ellipse cx="24" cy="32" rx="19" ry="11" {paint("green")}/>' + circle(15, 33, 2.5, 'teal', None) + circle(26, 37, 2, 'teal', None) + circle(33, 31, 1.5, 'teal', None)


def market():
    return rect(9, 18, 30, 24, 3, 'amber') + rect(18, 27, 12, 15, 2, 'cream') + rect(6, 7, 36, 12, 3, 'red') + rect(14.5, 8.5, 6, 9, 0, 'cream', None) + rect(27.5, 8.5, 6, 9, 0, 'cream', None) + rect(6, 7, 36, 12, 3, None)


def hold():
    return rect(9, 9, 15, 15, 3, 'red') + rect(23, 13, 15, 13, 3, 'green') + path('M5 22 H43 L39 42 H9 Z', 'amber') + line('M12 29 H36')


def nav():
    return path('M24 44 C14 33 9 27 9 19 a15 15 0 0 1 30 0 c0 8 -5 14 -15 25 z', 'red') + circle(24, 19, 6, 'cream')


def rigging():
    head = 'M20.5 3.7 A9 9 0 1 0 27.5 3.7 L27.5 12 L20.5 12 Z'
    return f'<g transform="rotate(45 24 24)">' + rect(19.5, 16, 9, 30, 4.5, 'teal') + path(head, 'mist') + circle(24, 39, 2, 'ink', None) + '</g>'


def comms():
    return fat('M10 15 a12 12 0 0 0 0 16 M38 15 a12 12 0 0 1 0 16', 'pink', 3) + path('M17 43 L24 21 L31 43 Z', 'mist') + line('M20.5 34 H27.5') + circle(24, 18, 5.5, 'pink')


# ── actions ───────────────────────────────────────────────────

def buy():
    return fat('M17 19 V15 a7 7 0 0 1 14 0 V19', 'mist', 3) + path('M8 18 H36 L34 42 H10 Z', 'amber') + circle(36, 35, 8.5, 'green') + line('M36 31 V39 M32 35 H40')


def sell():
    return path('M7 8 H24 L41 25 L26 40 L7 21 Z', 'red') + circle(15, 16, 3, 'cream') + circle(35, 37, 8.5, 'amber') + line('M31 37 H39')


def travel():
    ship = 'M14 24 C14 17 24 15 32 16.5 C39 18 44 21.5 44 24 C44 26.5 39 30 32 31.5 C24 33 14 31 14 24 Z'
    return circle(9, 24, 4, 'mist') + circle(4.5, 18.5, 2.5, 'mist') + path('M17 18 L13 9 H20 L25 16.5 Z', 'red') + path('M17 30 L13 39 H20 L25 31.5 Z', 'red') + path(ship, 'cream') + circle(33, 24, 3.5, 'teal')


def tray(): return rect(5, 32, 38, 10, 3, 'mist') + rect(13, 35.5, 22, 3, 1.5, 'ink', None)


def install(): return tray() + path('M18 5 H30 V16 H37 L24 30 L11 16 H18 Z', 'green')


def remove(): return tray() + path('M24 4 L37 17 H30 V28 H18 V17 H11 Z', 'red')


def send():
    return path('M5 22 L43 6 L32 41 L22 29 Z', 'cream') + path('M22 29 L43 6 L24 39 Z', 'pink')


def settings(): return path(gear(), 'mist') + circle(24, 24, 5.5, 'deep')


def menu(): return ''.join(rect(7, y, 34, 7, 3.5, 'cream') for y in (9, 20.5, 32))


def close(): return fat('M14 14 L34 34 M34 14 L14 34', 'red', 5)


def back(): return path('M6 24 L20 10 V18 H41 V30 H20 V38 Z', 'amber')


def turnLeft():
    return fat('M34.4 32 A12 12 0 1 0 12 25', 'green', 5) + path('M4.5 23 L19.5 23 L12 33 Z', 'green')


def turnRight(): return f'<g transform="matrix(-1 0 0 1 48 0)">{turnLeft()}</g>'


def lens(sign):
    return fat('M30 30 L40 40', 'mist', 5) + circle(20, 20, 14, 'glow') + fat(sign, 'green', 3)


def zoomIn(): return lens('M20 14 V26 M14 20 H26')


def zoomOut(): return lens('M14 20 H26')


# ── status ────────────────────────────────────────────────────

def credits():
    return circle(24, 24, 18, 'amber') + circle(24, 24, 12.5, None) + line('M29 19.5 A6.5 6.5 0 1 0 29 28.5 M25.5 15 L22.5 33')


def fuel():
    return path('M24 5 C34 17 38 24 38 29 a14 14 0 0 1 -28 0 C10 24 14 17 24 5 Z', 'teal') + path('M17 29 a7 7 0 0 0 7 7', None)


def power(): return path('M27 4 L11 27 H22 L19 44 L37 19 H26 Z', 'amber')


def cargo():
    return rect(7, 7, 34, 34, 5, 'red') + rect(12, 12, 24, 24, 2, 'red') + line('M12 12 L36 36 M36 12 L12 36')


def time():
    return rect(20, 3, 8, 6, 2, 'red') + circle(24, 26, 17, 'mist') + line('M24 16 V26 L31 30')


def years():
    glass = 'M14 10 H34 C34 19 26 21 26 24 C26 27 34 29 34 38 H14 C14 29 22 27 22 24 C22 21 14 19 14 10 Z'
    return path(glass, 'glow') + path('M17.5 37 C19 31.5 22 30.5 24 29.5 C26 30.5 29 31.5 30.5 37 Z', 'amber', None) + path('M18 14 H30 C29 17 26 19 24 21 C22 19 19 17 18 14 Z', 'amber', None) + path(glass, None) + rect(9, 5, 30, 6, 3, 'red') + rect(9, 37, 30, 6, 3, 'red')


def distance():
    return rect(4, 15, 40, 18, 3, 'amber') + line('M10 15 V24 M17 15 V21 M24 15 V25 M31 15 V21 M38 15 V24')


def alert():
    return path('M24 6 L43 39 H5 Z', 'amber') + rect(22, 16, 4, 13, 2, 'ink', None) + circle(24, 33.5, 2.5, 'ink', None)


GROUPS = {
    'places': [ port, market, hold, nav, rigging, comms ],
    'actions': [ buy, sell, travel, install, remove, send, settings, menu, close, back, turnLeft, turnRight, zoomIn, zoomOut ],
    'status': [ credits, fuel, power, cargo, time, years, distance, alert ],
}


def kebab(f): return re.sub(r'([A-Z])', r'-\1', f.__name__).lower()


def svg(f, size=48): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 48 48">{f()}</svg>'


def files():
    global VARS
    VARS = True
    os.makedirs(os.path.join(OUT, 'svg'), exist_ok=True)
    for f in sum(GROUPS.values(), []):
        open(os.path.join(OUT, 'svg', kebab(f) + '.svg'), 'w').write(svg(f) + '\n')
    VARS = False


# ── the sheet ─────────────────────────────────────────────────

W, H = 1600, 900
FONT = "Arial Rounded MT Bold, Nunito, Arial, sans-serif"


def text(x, y, t, size, fill, anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="700" fill="{fill}" text-anchor="{anchor}">{t}</text>'


def place(f, x, y, s): return f'<g transform="translate({x},{y}) scale({s / 48})">{f()}</g>'


def cell(f, x, y):
    s = f'<rect x="{x}" y="{y + 5}" width="88" height="88" rx="6" fill="{col("deep")}"/><rect x="{x}" y="{y}" width="88" height="88" rx="6" fill="{col("panel2")}" stroke="{col("line")}" stroke-width="2"/>'
    return s + place(f, x + 12, y + 12, 64) + text(x + 44, y + 116, kebab(f), 15, col('mist'), 'middle')


def strip(y, bg, fg):
    s = f'<rect x="48" y="{y}" width="{W - 96}" height="72" rx="6" fill="{col(bg)}"/>' + text(68, y + 44, '48 px', 18, col(fg))
    return s + ''.join(place(f, 150 + i * 49.5, y + 12, 48) for i, f in enumerate(sum(GROUPS.values(), [])))


def sheet():
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}"><rect width="{W}" height="{H}" fill="{col("space")}"/>'
    s += text(48, 66, 'toy ui icons', 40, col('cream')) + text(48, 100, f'{PAL} · one stroke weight, rounded ends, flat toy shapes', 22, col('mist'))
    y = 140
    for name, fs in GROUPS.items():
        s += text(48, y + 56, name, 22, col('cream'))
        s += ''.join(cell(f, 170 + i * 100, y) for i, f in enumerate(fs))
        y += 150
    s += strip(y + 20, 'panel', 'mist') + strip(y + 104, 'cream', 'ink')
    path = os.path.join(OUT, f'sheet-{PAL}.svg')
    open(path, 'w').write(s + '</svg>')
    png(path)


# quick look renders the svg square; the sheet is the top 16:9 of it
def png(svg):
    subprocess.run([ 'qlmanage', '-t', '-s', str(W), '-o', OUT, svg ], capture_output=True)
    from PIL import Image
    Image.open(svg + '.png').crop((0, 0, W, H)).save(svg[:-4] + '.png')
    os.remove(svg + '.png')
    os.remove(svg)


files()
for PAL in sys.argv[1:] or [ 'meadow', 'toybox', 'lagoon' ]:
    sheet()
    print(PAL, 'ok')
