# the morning brief as a page: <date>.facts.json (collect.py) + <date>.words.json (claude)
# → brief.html, and a markdown copy <date>.md. run: python3 render.py [date]
import base64, json, math, sys
from datetime import date, datetime, timedelta
from html import escape as esc
from pathlib import Path

here  = Path(__file__).resolve().parent
day   = sys.argv[ 1 ] if len(sys.argv) > 1 else str(date.today())
facts = json.loads((here / f'{ day }.facts.json').read_text())
words = json.loads((here / f'{ day }.words.json').read_text())
font  = base64.b64encode((here / 'fraunces-latin-600-normal.woff2').read_bytes()).decode()

W, BASE, LIFT = 840, 128, 86
t0, t1 = (datetime.fromisoformat(facts[ k ]) for k in ('since', 'until'))
night  = t1.replace(hour=0, minute=0)
dawn   = t1.replace(hour=6, minute=0)
cuts   = [ t0, max(t0, min(night, t1)), max(t0, min(dawn, t1)), t1 ]


# 3 acts, a third of the width each: evening, night, morning
def x(t):
    for i in range(3):
        a, b = cuts[ i ], cuts[ i + 1 ]
        if t <= b or i == 2:
            k = 0 if b <= a else min(1, max(0, (t - a) / (b - a)))
            return i * W / 3 + k * W / 3


def bumps():
    for r in facts[ 'runs' ]:
        a, b = (x(datetime.fromisoformat(r[ k ])) for k in ('start', 'end'))
        jobs = len(r[ 'done' ]) + len(r[ 'built' ]) / 2
        yield (a + b) / 2, max(30, (b - a) / 2), min(1, .25 + .05 * jobs), 'run', r
    for c in facts[ 'commits' ]:
        yield x(datetime.fromisoformat(c[ "at" ])), 16, .2, 'commit', c


marks = list(bumps())
lift  = lambda px: min(1, sum(w * math.exp(-((px - cx) / hw) ** 2) for cx, hw, w, *_ in marks))
y     = lambda px: BASE - LIFT * lift(px)
line  = ' '.join(f'{ px },{ y(px):.1f}' for px in range(0, W + 1, 4))


def dot(cx, kind, r):
    if kind == 'commit':
        return f'<circle cx="{ cx:.0f}" cy="{ y(cx):.1f}" r="5" fill="#B4B3A8"/>'
    size = 6 + min(7, (len(r[ 'done' ]) + len(r[ 'built' ]) / 2) / 2)
    fill = '#2E2C27' if r[ 'done' ] or r[ 'built' ] else '#B4B3A8'
    return f'<circle cx="{ cx:.0f}" cy="{ y(cx):.1f}" r="{ size:.0f}" fill="{ fill }"/>'


moon = '<path d="M338 18a14 14 0 1 0 10 24a11 11 0 1 1 -10 -24z" fill="none" stroke="#2E2C27" stroke-width="1.6"/>'
sun  = f'<path d="M778 { BASE }a22 22 0 0 1 44 0" fill="#C6613F"/>' + ''.join(
    f'<line x1="{ 800 + 30 * math.cos(a):.1f}" y1="{ BASE - 30 * math.sin(a):.1f}" x2="{ 800 + 38 * math.cos(a):.1f}" y2="{ BASE - 38 * math.sin(a):.1f}" stroke="#C6613F" stroke-width="2" stroke-linecap="round"/>'
    for a in (math.pi * k / 6 for k in range(1, 6)))
svg = (f'<svg viewBox="0 0 { W } 170" role="img" aria-label="the night as a line: dots are sam\'s runs and commits">'
       f'{ moon }{ sun }<polyline points="{ line }" fill="none" stroke="#2E2C27" stroke-width="2" stroke-linejoin="round"/>'
       + ''.join(dot(cx, kind, r) for cx, _, _, kind, r in marks) + '</svg>')

hm   = lambda t: f'{ t:%H:%M}'
span = lambda a, b: f'{ a:%a} { hm(a) } – { hm(b) }' if a.date() != b.date() else f'{ hm(a) } – { hm(b) }'
acts = ''.join(f'<li><b>{ span(cuts[ i ], cuts[ i + 1 ]) }</b><p>{ esc(words[ "acts" ][ i ]) }</p></li>' for i in range(3))


def items(rows):
    def title(r):
        t = esc(r[ 'title' ])
        return f'<a href="{ esc(r[ "href" ]) }">{ t }</a>' if r.get('href', '').startswith('https://') else t
    return '<ol class="items">' + ''.join(f'<li><b>{ title(r) }</b><p>{ esc(r[ "text" ]) }</p></li>' for r in rows) + '</ol>'


lists = (f'<section><h2>Needs you</h2>{ items(words[ "needs" ]) }</section>' if words[ 'needs' ] else '') + \
        (f'<section><h2>Done since the last brief</h2>{ items(words[ "done" ]) }</section>' if words[ 'done' ] else '')
if not lists:
    lists = '<p class="calm">Nothing needs you this morning.</p>'

repos = ''.join(f'<li><b>{ n }</b> · { r[ "branch" ] } · { r[ "uncommitted" ] } uncommitted · { r[ "unpushed" ] } unpushed</li>' for n, r in facts[ 'repos' ].items())
q     = facts[ 'queue' ]
queue = f'{ q[ "total" ] } jobs: { len(q[ "❎" ]) } open, { len(q[ "♻️" ]) } in progress, { len(q[ "⛔" ]) } blocked.'
usage = ''.join(f'<li><b>{ u[ 1 ] }</b> of { u[ 3 ] } h · resets { u[ 6 ] } { u[ 7 ] }</li>' for u in facts[ 'usage' ])

page = f'''<title>Theseus Morning Brief</title>
<style>
/* two bands: the night drawn on a wash, then the lists on paper. one serif, the headline. */
@font-face {{ font-family: Fraunces; font-weight: 600; src: url(data:font/woff2;base64,{ font }) format('woff2') }}
:root {{ --wash: #F9F9F7; --bg: #FCFCFB; --ink: #2E2C27; --soft: #6B6A63; --grey: #B4B3A8; --hair: #E4E3DC; --edge: #E1E1DF; --clay: #C6613F;
         --sans: -apple-system, "Segoe UI", sans-serif; --serif: Fraunces, Georgia, serif; color-scheme: light }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.55 var(--sans) }}
header, main {{ padding-inline: 16px }}
header {{ background: var(--wash); border-bottom: 1px solid var(--edge); padding-block: 40px 32px }}
main {{ padding-block: 32px 56px }}
header > *, main > * {{ max-width: 860px; margin-inline: auto }}
.date {{ color: var(--soft); font-size: 13px; margin-block: 0 8px }}
h1 {{ font: 600 40px/1.15 var(--serif); margin-block: 0 20px; text-wrap: balance }}
svg {{ display: block; width: 100%; height: auto }}
.acts {{ list-style: none; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); margin-block: 8px 0 }}
.acts li {{ padding-inline: 16px; border-left: 1px solid var(--hair); min-width: 0 }}
.acts li:first-child {{ border: 0; padding-left: 0 }}
.acts b {{ font-size: 13px; font-variant-numeric: tabular-nums }}
.acts p, .items p {{ color: var(--soft); margin-block: 4px 0 }}
section {{ display: grid; gap: 8px; margin-block-end: 32px }}
h2 {{ font: 600 15px var(--sans); margin: 0 }}
.items {{ list-style: none; padding: 0; margin: 0; counter-reset: n; display: grid; gap: 16px }}
.items li {{ counter-increment: n; display: grid; grid-template-columns: 24px 1fr; min-width: 0 }}
.items li::before {{ content: counter(n); color: var(--grey); font-variant-numeric: tabular-nums }}
.items li > * {{ grid-column: 2 }}
.items a {{ color: inherit; text-decoration-color: var(--grey) }}
.facts {{ list-style: none; padding: 0; margin: 0; color: var(--soft); display: grid; gap: 4px; font-variant-numeric: tabular-nums }}
.facts b {{ color: var(--ink); font-weight: 500 }}
.calm {{ color: var(--soft) }}
@media (max-width: 640px) {{
    h1 {{ font-size: 30px }}
    .acts {{ grid-template-columns: 1fr; gap: 12px }}
    .acts li {{ border-left: 0; border-top: 1px solid var(--hair); padding: 12px 0 0 }}
    .acts li:first-child {{ border: 0; padding-top: 0 }}
}}
</style>
<header>
    <p class="date">{ t1:%A · %B} { t1.day } { t1.year }</p>
    <h1>{ esc(words[ "headline" ]) }</h1>
    { svg }
    <ol class="acts">{ acts }</ol>
</header>
<main>
    { lists }
    <section><h2>Repos</h2><ul class="facts">{ repos }</ul></section>
    <section><h2>Sam</h2><ul class="facts"><li>{ queue }</li>{ usage }</ul></section>
</main>
'''
(here / 'brief.html').write_text(page)

md = [ f'{ t1:%A %d %B %Y} · morning brief', '=' * 32, '', words[ 'headline' ], '' ]
md += [ f'- **{ span(cuts[ i ], cuts[ i + 1 ]) }** · { words[ "acts" ][ i ] }' for i in range(3) ]
for head, key in (('needs you', 'needs'), ('done since the last brief', 'done')):
    if words[ key ]:
        md += [ '', f'## { head }', '' ] + [ f'{ i }. **{ r[ "title" ] }** · { r[ "text" ] }' for i, r in enumerate(words[ key ], 1) ]
md += [ '', '## repos', '' ] + [ f'- { n } · { r[ "branch" ] } · { r[ "uncommitted" ] } uncommitted · { r[ "unpushed" ] } unpushed' for n, r in facts[ 'repos' ].items() ]
md += [ '', '## sam', '', f'- { queue }' ] + [ f'- { u[ 1 ] } of { u[ 3 ] } h · resets { u[ 6 ] } { u[ 7 ] }' for u in facts[ 'usage' ] ]
(here / f'{ day }.md').write_text('\n'.join(md) + '\n')
print(here / 'brief.html')
