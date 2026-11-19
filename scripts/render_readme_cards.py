#!/usr/bin/env python3
"""Draw the animated SVG cards for the profile README from data/contributions.json.
STATIC=1 renders the final frame (no animation) for screenshots."""
import base64, json, os, datetime as dt
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DARK = os.environ.get("THEME") == "dark"
OUT = os.path.join(ROOT, "cards", "dark") if DARK else os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"
os.makedirs(OUT, exist_ok=True)

INK, BLUE, BG, CARD, MUTED, FAINT = "#0f1115", "#2563eb", "#f7f8fa", "#ffffff", "#5b6472", "#9aa3af"
STROKE, BAR = "rgba(15,17,21,.10)", "#cfd8e6"
GREEN, AMBER = "#16a34a", "#d97706"
LEVELS = ["#e8edf5", "#bfd4fb", "#8ab1f7", "#4f86ef", "#2563eb"]
if DARK:
    INK, BLUE, BG, CARD, MUTED, FAINT = "#f0f6fc", "#4f8cff", "#0d1117", "#161b22", "#9198a1", "#6e7681"
    STROKE, BAR = "rgba(240,246,252,.14)", "#30363d"
    LEVELS = ["#1f2733", "#1d3a73", "#2a5bc4", "#3b82f6", "#79a8ff"]

def font_css():
    css = ""
    for w in (400, 700):
        b64 = base64.b64encode(open(os.path.join(ROOT, "fonts", f"inter-{w}.woff"), "rb").read()).decode()
        css += f"@font-face{{font-family:'Inter';font-weight:{w};src:url(data:font/woff;base64,{b64}) format('woff')}}"
    return css

FONT = font_css()
BASE = (FONT + f"text{{font-family:'Inter',-apple-system,'Segoe UI',sans-serif}}"
        ".mono{font-family:'Courier New',monospace}")
ANIM = """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{transform:scale(1.12)}100%{opacity:1;transform:scale(1)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes swing{0%{opacity:0;transform:translateY(40px) rotate(-5deg)}65%{opacity:1;transform:translateY(-6px) rotate(1deg)}100%{opacity:1;transform:none}}
@keyframes pulse{0%{opacity:.5;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(4px)}}
@keyframes fade{from{opacity:0}to{opacity:1}}
.a{opacity:0;transform-box:fill-box}
.rise{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
.pop{animation:pop .5s cubic-bezier(.2,.7,.2,1) both;transform-origin:center}
.bar{transform-origin:bottom;animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.swing{animation:swing .9s cubic-bezier(.2,.8,.2,1) both;transform-origin:bottom left}
.ring{transform-origin:center;animation:pulse 2.4s ease-out 1.4s infinite}
.arrow{animation:nudge 2s ease-in-out infinite}
.fade{animation:fade .6s ease both}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.a{opacity:1!important}}
"""
STATIC_CSS = "*{animation:none!important}.a{opacity:1!important}"

def svg(w, h, body, extra_css=""):
    css = BASE + (STATIC_CSS if STATIC else ANIM) + extra_css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f"<style>{css}</style>{body}</svg>")

def save(name, s):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(s)

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def card(w, h, fill=CARD, stroke=None, r=18):
    stroke = stroke or STROKE
    return f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'

# ---------- data ----------
days = json.load(open(os.path.join(ROOT, "data", "contributions.json")))
days = [d for d in days if d["date"] <= dt.date.today().isoformat()]
total = sum(d["contributionCount"] for d in days)
active = sum(1 for d in days if d["contributionCount"] > 0)
busiest = max(days, key=lambda d: d["contributionCount"])
best_streak = cur = 0
for d in days:
    cur = cur + 1 if d["contributionCount"] > 0 else 0
    best_streak = max(best_streak, cur)
months = OrderedDict()
for d in days:
    k = d["date"][:7]
    months[k] = months.get(k, 0) + d["contributionCount"]
months = list(months.items())[-12:]
repo_count = int(os.environ.get("REPO_COUNT", "19"))


def ascii_portrait(cols=50):
    from PIL import Image, ImageOps, ImageChops
    im = Image.open(os.path.join(ROOT, "assets", "portrait.png")).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop(box)
    rows = max(1, round(cols * im.size[1] / im.size[0] * 0.77))
    g = ImageOps.autocontrast(im.convert("L").resize((cols, rows), Image.LANCZOS), cutoff=1)
    ramp = " .:-=+*#%@"
    out = []
    for y in range(rows):
        line = "".join(ramp[min(len(ramp)-1, int(((255 - g.getpixel((x, y))) / 255) ** 1.3 * len(ramp)))] for x in range(cols))
        out.append(line.rstrip())
    return out

# ---------- hero ----------
W = 900
art = ascii_portrait()
HH = 350
hero = card(W, HH, CARD, STROKE, 22)
hero += f'<text class="mono a rise" x="48" y="78" font-size="13" fill="{BLUE}" letter-spacing="3" style="animation-delay:.1s">BUILDER · FOUNDER</text>'
hero += f'<text class="a rise" x="48" y="152" font-size="68" font-weight="700" fill="{INK}" letter-spacing="-2.5" style="animation-delay:.25s">Sam</text>'
hero += f'<text class="a rise" x="48" y="224" font-size="68" font-weight="700" fill="url(#shine)" letter-spacing="-2.5" style="animation-delay:.4s">Schnopp</text>'
hero += f'<text class="a rise" x="50" y="262" font-size="17" fill="{MUTED}" style="animation-delay:.6s">I ship apps, trading bots and odd little tools, fast.</text>'
hero += f'<text class="a rise" x="50" y="286" font-size="14" fill="{FAINT}" style="animation-delay:.7s">MIS at Westfield State · samschnopp.dev</text>'
lh = 6.6
ax = W - 64 - 50 * 5.0
ay = (HH - len(art) * lh) / 2 + 4
for i, row in enumerate(art):
    hero += (f'<text class="mono a fade" xml:space="preserve" x="{ax:.1f}" y="{ay + i*lh:.1f}" font-size="8.3" fill="{INK}" '
             f'style="animation-delay:{0.5 + i*0.028:.3f}s">{esc(row)}</text>')
defs = (f'<defs><linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="260" y2="0">'
        f'<stop offset="0" stop-color="{INK}"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="{INK}"/>'
        + ('' if STATIC else '<animateTransform attributeName="gradientTransform" type="translate" values="-300 0;420 0;420 0" keyTimes="0;.45;1" dur="6s" begin="1.4s" repeatCount="indefinite"/>')
        + '</linearGradient></defs>')
save("hero.svg", svg(W, HH, defs + hero))

# ---------- blue contribution graph ----------
cell, gap = 13, 3
weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
gw = len(weeks) * (cell + gap) + 80
body = card(W, 210, CARD)
body += f'<text x="30" y="40" font-size="15" font-weight="700" fill="{INK}">{total} contributions in the last year</text>'
mx = max([d["contributionCount"] for d in days] + [1])
x0, y0 = (W - len(weeks) * (cell + gap)) / 2, 68
for wi, wk in enumerate(weeks):
    for di, d in enumerate(wk):
        c = d["contributionCount"]
        lvl = 0 if c == 0 else min(4, 1 + int(3 * (c - 1) / max(mx - 1, 1) + .5))
        delay = round(.3 + wi * .02, 2)
        body += (f'<rect class="a pop" x="{x0 + wi*(cell+gap):.1f}" y="{y0 + di*(cell+gap)}" width="{cell}" height="{cell}" rx="3" '
                 f'fill="{LEVELS[lvl]}" style="animation-delay:{delay}s"/>')
save("graph.svg", svg(W, 210, body))

# ---------- monthly bars ----------
body = card(W, 240, CARD)
body += f'<text x="30" y="40" font-size="15" font-weight="700" fill="{INK}">Contributions by month</text>'
stat = (f"{active} active days · longest streak {best_streak} · busiest day {busiest['contributionCount']} "
        f"({dt.date.fromisoformat(busiest['date']).strftime('%b %-d') if os.name != 'nt' else dt.date.fromisoformat(busiest['date']).strftime('%b %d').replace(' 0', ' ')})")
body += f'<text x="{W-30}" y="40" font-size="13" fill="{MUTED}" text-anchor="end">{stat}</text>'
top = max((v for _, v in months), default=1) or 1
best = max(months, key=lambda m: m[1])[0] if months else ""
bw = (W - 60) / max(len(months), 1)
for i, (k, v) in enumerate(months):
    h = max(4, 120 * v / top)
    x = 30 + i * bw + bw * .18
    fill = BLUE if k == best else BAR
    delay = round(.2 + i * .07, 2)
    body += f'<rect class="a bar" x="{x:.1f}" y="{180-h:.1f}" width="{bw*.64:.1f}" height="{h:.1f}" rx="6" fill="{fill}" style="animation-delay:{delay}s"/>'
    label = dt.date.fromisoformat(k + "-01").strftime("%b")
    body += f'<text x="{x + bw*.32:.1f}" y="206" font-size="12" fill="{FAINT}" text-anchor="middle">{label}</text>'
    if k == best:
        body += f'<text class="a pop" x="{x + bw*.32:.1f}" y="{172-h:.1f}" font-size="14" font-weight="700" fill="{BLUE}" text-anchor="middle" style="animation-delay:1.2s">{v}</text>'
save("months.svg", svg(W, 240, body))

# ---------- repo cards ----------
REPOS = [
    ("cabin-scout", "Free self-hosted whitetail scouting board: map, trail cams, wind and scent predictions.", "JavaScript", "https://github.com/Gizzer77/cabin-scout"),
    ("Tracker", "Crypto whale tracker to see what the big wallets are doing, live.", "JavaScript", "https://github.com/Gizzer77/Tracker"),
    ("Stream_chat", "Stream chat aggregator that puts every platform's chat in one place.", "JavaScript", "https://github.com/Gizzer77/Stream_chat"),
]
def wrap(text, n):
    out, line = [], ""
    for wd in text.split():
        if len(line) + len(wd) + 1 > n:
            out.append(line); line = wd
        else:
            line = (line + " " + wd).strip()
    return out + [line]
for i, (name, desc, lang, _) in enumerate(REPOS):
    w, h = 290, 170
    b = card(w, h, CARD)
    b += f'<text x="24" y="42" font-size="18" font-weight="700" fill="{INK}">{esc(name)}</text>'
    for j, ln in enumerate(wrap(desc, 36)[:3]):
        b += f'<text x="24" y="{72 + j*20}" font-size="13" fill="{MUTED}">{esc(ln)}</text>'
    b += f'<circle cx="30" cy="146" r="5" fill="{BLUE}"/><text x="42" y="150" font-size="12" fill="{MUTED}">{lang}</text>'
    b += f'<text class="arrow" x="{w-40}" y="152" font-size="18" fill="{BLUE}">→</text>'
    save(f"repo{i+1}.svg", svg(w, h, f'<g class="a rise" style="animation-delay:{2.3 + i*.15}s">{b}</g>'))

print("rendered cards:", sorted(os.listdir(OUT)))
