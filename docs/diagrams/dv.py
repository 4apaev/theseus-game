# the ΔV diagrams of docs/ΔV.md, from the same formulas. run: python3 docs/diagrams/dv.py
import math
from pathlib import Path
here = Path(__file__).resolve().parent
GM, AU, DAY, VCAP = 1.32712e20, 1.495978707e11, 86400, 0.00008 * 299792458
SOL = [('icarus', .05), ('mercury', .387), ('venus', .723), ('outpost', 1.0), ('mars', 1.524), ('ganymede', 5.203), ('titan', 9.537)]
STARS = [('Sol', 1.0), ('Alpha Centauri A', 1.1), ("Barnard's star", .16), ('Wolf 359', .11), ('Sirius A', 2.06), ('Ran', .82), ('Procyon A', 1.5), ('Lalande 21185', .39), ('Ross 154', .18), ('Lacaille 9352', .49)]
pull = lambda r, m=1: m * GM / (r * AU) ** 2
vorb = lambda r, m=1: math.sqrt(m * GM / (r * AU))
cross = lambda a, m=1: math.sqrt(m * GM / a) / AU
def leg(r1, r2, a):
    d = abs(r1 - r2) * AU; pk = min(math.sqrt(a * d), VCAP)
    t = 2 * math.sqrt(d / a) if math.sqrt(a * d) <= VCAP else d / VCAP + VCAP / a
    return t / DAY, 2 * pk
print('crossing', [round(cross(a), 3) for a in (.002, .006, 31.4)])
print('from the outpost: leg days, well km/s, well days starter, well days mk2, total km/s')
for n, r in SOL:
    if n == 'outpost': continue
    t, dv = leg(1, r, .002); w = abs(vorb(r) - vorb(1))
    print(n, round(t), round(w / 1000, 1), round(w / .002 / DAY), round(w / .006 / DAY), round((dv + w) / 1000, 1))
for n, m in STARS:
    print(n, m, round(pull(1, m), 5), round(vorb(1, m) / 1000, 1), round(cross(.002, m), 2), round(cross(.006, m), 2))
for ve in (4.5, 9, 50, 100, 300):
    print('ve', ve, [round(100 * (1 - math.exp(-dv / ve)), 1) for dv in (30.7, 45.2, 64.7, 137.1)])


W, H, L, R, T, B = 680, 340, 60, 16, 44, 78
STYLE = """<style>
text { font-family: -apple-system, 'SF Pro Text', system-ui, sans-serif }
.t { font-size: 12px; fill: #2C2C2A } .m { font-size: 11px; fill: #5F5E5A }
.grid { stroke: #D3D1C7; stroke-width: .5 } .axis { stroke: #888780; stroke-width: 1 } .ink { stroke: #2C2C2A; fill: none; stroke-width: 2 } .dot { fill: #2C2C2A; stroke: #FFFFFF; stroke-width: 1.5 }
.coral { stroke: #D85A30; fill: none } .amber { stroke: #BA7517; fill: none } .teal { stroke: #1D9E75; fill: none } .purple { stroke: #534AB7; fill: none } .gray { stroke: #888780; fill: none }
.tp { fill: #3C3489 } .zone { fill: #FCEBEB } .zs { fill: #FCEBEB; stroke: #A32D2D; stroke-width: .5 } .bad { fill: #A32D2D; stroke: #FFFFFF; stroke-width: 1.5 } .tb { font-size: 11px; fill: #A32D2D }
@media (prefers-color-scheme: dark) {
  .t { fill: #F1EFE8 } .m { fill: #D3D1C7 } .grid { stroke: #444441 } .axis { stroke: #888780 } .ink { stroke: #F1EFE8 } .dot { fill: #F1EFE8; stroke: #2C2C2A }
  .tp { fill: #AFA9EC } .zone { fill: #501313 } .zs { fill: #501313; stroke: #F09595 } .bad { fill: #F09595; stroke: #2C2C2A } .tb { fill: #F09595 }
}
</style>"""
def svg(title, desc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">\n<title>{title}</title>\n<desc>{desc}</desc>\n{STYLE}\n{body}\n</svg>\n'
class Scale:
    def __init__(s, x0, x1, y0, y1, xlog=True, ylog=True):
        s.x0, s.x1, s.y0, s.y1, s.xlog, s.ylog = x0, x1, y0, y1, xlog, ylog
    def k(s, v, a, b, log): return (math.log10(v) - math.log10(a)) / (math.log10(b) - math.log10(a)) if log else (v - a) / (b - a)
    def x(s, v): return L + s.k(v, s.x0, s.x1, s.xlog) * (W - L - R)
    def y(s, v): return T + (1 - s.k(v, s.y0, s.y1, s.ylog)) * (H - T - B)
def fmt(v): return '0' if v == 0 else f'{v:g}' if v >= .001 else f'{v:.0e}'.replace('e-0', 'e-')
def axes(sc, xg, xt, yt, xl, yl):
    o = []
    for v in xg: x = sc.x(v); o.append(f'<line class="grid" x1="{x:.1f}" x2="{x:.1f}" y1="{T}" y2="{H-B}"/>')
    for v in xt: o.append(f'<text class="m" x="{sc.x(v):.1f}" y="{H-B+15}" text-anchor="middle">{fmt(v)}</text>')
    for v in yt: y = sc.y(v); o += [f'<line class="grid" x1="{L}" x2="{W-R}" y1="{y:.1f}" y2="{y:.1f}"/>', f'<text class="m" x="{L-6}" y="{y+4:.1f}" text-anchor="end">{fmt(v) if sc.ylog else yl.format(v)}</text>']
    o += [f'<line class="axis" x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}"/>', f'<text class="m" x="{W-R}" y="{H-B+15}" text-anchor="end" dy="14">{xl}</text>']
    return o
def legend(items):
    o, x = [], L
    for kind, cls, name in items:
        if kind == 'box': o.append(f'<rect class="{cls}" x="{x}" y="9" width="14" height="10" rx="2"/>')
        else: o.append(f'<line class="{cls}" stroke-width="{3 if kind == "bar" else 2}" x1="{x}" x2="{x+18}" y1="14" y2="14"' + (' stroke-dasharray="5 3"' if kind == 'dash' else '') + '/>')
        o.append(f'<text class="m" x="{x+24}" y="18">{name}</text>'); x += 30 + 6.2 * len(name)
    return o
def rug(sc, rows, bad=lambda r: False):
    o = []
    for n, r in rows:
        x = sc.x(r); cls = 'tb' if bad(r) else 'm'
        o.append(f'<line class="axis" x1="{x:.1f}" x2="{x:.1f}" y1="{H-B}" y2="{H-B+4}"/>')
        o.append(f'<text class="{cls}" x="{x:.1f}" y="{H-B+30}" text-anchor="end" transform="rotate(-35 {x:.1f} {H-B+30})">{n}</text>')
    return o
def path(sc, f, xs): return 'M' + ' L'.join(f'{sc.x(r):.1f} {sc.y(f(r)):.1f}' for r in xs)
xs = [10 ** (math.log10(.03) + i * 3 / 160) for i in range(161)]
XG = [.05, .1, .2, .5, 1, 2, 5, 10, 20]
XT = [.1, 1, 10]

# 1 · the pull against the push
sc = Scale(.03, 30, 1e-5, 100); rs = cross(.002); o = []
o.append(f'<rect class="zone" x="{L}" y="{T}" width="{sc.x(rs)-L:.1f}" height="{H-T-B}"/>')
o += axes(sc, XG, XT, [1e-5, 1e-4, 1e-3, .01, .1, 1, 10, 100], 'orbit radius, AU', '')
o.append(f'<text class="tb" x="{L+8}" y="{H-B-12}">the starter is stuck here: a − GM/r² &lt; 0</text>')
o.append(f'<path class="ink" d="{path(sc, pull, xs)}"/>')
for a, cls in ((.002, 'coral'), (.006, 'amber'), (31.4, 'teal')):
    y = sc.y(a); o.append(f'<line class="{cls}" stroke-width="2" stroke-dasharray="6 4" x1="{L}" x2="{W-R}" y1="{y:.1f}" y2="{y:.1f}"/>')
for n, r in SOL: o.append(f'<circle class="{"bad" if r < rs else "dot"}" cx="{sc.x(r):.1f}" cy="{sc.y(pull(r)):.1f}" r="4.5"/>')
o += rug(sc, SOL, lambda r: r < rs)
o += legend([('line', 'ink', 'sun pull, m/s²'), ('dash', 'coral', 'starter 0.002'), ('dash', 'amber', 'mk2 0.006'), ('dash', 'teal', 'beam 3.2 g'), ('box', 'zs', 'stuck')])
open(here / 'dv.pull.svg', 'w').write(svg('the pull against the push',
    "log-log chart of the sun's pull against orbit radius. the starter's push of 0.002 m/s² crosses the pull at 1.72 AU, so every station inside, the outpost included, lies in the stuck zone. maneuver.mk2 crosses at 0.99 AU. the beam stays above the pull everywhere.", '\n'.join(o)))

# 2 · the well as speed
sc = Scale(.03, 30, 3, 300); o = axes(sc, XG, XT, [3, 10, 30, 100, 300], 'orbit radius, AU', '')
o.append(f'<path class="ink" d="{path(sc, lambda r: vorb(r) / 1000, xs)}"/>')
yo = sc.y(vorb(1) / 1000)
o.append(f'<line class="purple" stroke-width="1" stroke-dasharray="4 4" x1="{L}" x2="{W-R}" y1="{yo:.1f}" y2="{yo:.1f}"/>')
for n, r in SOL:
    x, y = sc.x(r), sc.y(vorb(r) / 1000)
    if n != 'outpost':
        dv = abs(vorb(r) - vorb(1)) / 1000; up = y < yo
        o.append(f'<line class="purple" stroke-width="3" x1="{x:.1f}" x2="{x:.1f}" y1="{yo:.1f}" y2="{y:.1f}" opacity=".6"/>')
        o.append(f'<text class="m tp" x="{x:.1f}" y="{(y - 9) if up else (y + 18):.1f}" text-anchor="middle">{dv:.1f}</text>')
    o.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>')
o += rug(sc, SOL)
o += legend([('line', 'ink', 'orbit speed, km/s'), ('dash', 'purple', 'the outpost, 29.8'), ('bar', 'purple', 'Δv to match, km/s')])
open(here / 'dv.well.svg', 'w').write(svg('the well as speed',
    'log-log chart of orbit speed against orbit radius around the sun. bars show the speed change from the outpost at 29.8 km/s: icarus 103.4, mercury 18.1, venus 5.2, mars 5.7, ganymede 16.7, titan 20.1 km/s.', '\n'.join(o)))

# 3 · the rocket equation
sc = Scale(0, 150, 0, 100, xlog=False, ylog=False)
o = axes(sc, range(0, 151, 25), range(0, 151, 25), range(0, 101, 25), 'Δv of the leg, km/s', '{}%')
for name, dv in (('mars', 30.7), ('mercury', 45.2), ('ganymede', 64.7), ('icarus', 137.1)):
    x = sc.x(dv); o.append(f'<line class="gray" stroke-width="1" stroke-dasharray="3 3" x1="{x:.1f}" x2="{x:.1f}" y1="{T}" y2="{H-B}"/>')
    o.append(f'<text class="m" x="{x:.1f}" y="{T-6}" text-anchor="middle">{name}</text>')
EV = ((4.5, 'coral', 'chemical 4.5'), (9, 'amber', 'nuclear thermal 9'), (50, 'purple', 'fusion 50'), (100, 'teal', 'fusion 100'), (300, 'gray', 'fusion 300'))
for ve, cls, _ in EV:
    o.append(f'<path class="{cls}" stroke-width="2" d="M' + ' L'.join(f'{sc.x(dv):.1f} {sc.y(100 * (1 - math.exp(-dv / ve))):.1f}' for dv in [i * .5 for i in range(301)]) + '"/>')
o += legend([('line', c, n) for _, c, n in EV])
o.append(f'<text class="m" x="{L}" y="{H-B+44}">fuel as a share of the full mass. exhaust speed in km/s.</text>')
open(here / 'dv.rocket.svg', 'w').write(svg('the rocket equation',
    'fuel as a share of the full ship mass against the Δv of a leg, for 5 exhaust speeds. marks show the starter legs from the outpost: mars 30.7, mercury 45.2, ganymede 64.7 and icarus 137.1 km/s. at 4.5 km/s every leg needs more than 99% fuel.', '\n'.join(o)))
