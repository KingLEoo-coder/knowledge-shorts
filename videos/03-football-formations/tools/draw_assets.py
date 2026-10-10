"""Code-drawn assets for video 03 (football formations), 1920x1080.

Writes into ../assets/code/:
  formations.json      player coordinates for every formation (for animating dots)
  *.svg                ivory "tactics board" stills, one per beat
  preview/*.png        PNG previews + contact sheet (needs cairosvg + Noto fonts)

Coordinates: x 0 = own goal line -> 1 = opponent goal line, y 0 = top touchline -> 1 = bottom.
Player ids are stable across formations (0 = GK, then back->front, top->bottom),
so tweening id N from one formation to the next moves the dots naturally.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "code")

PAPER = "#F2EDE3"
INK = "#1C1A17"
RED = "#C8432B"
SLATE = "#2F4B5C"
MUTED = "#8A8378"
SERIF = "'Noto Serif CJK SC','Source Han Serif SC','Songti SC',serif"
DISPLAY = "'Noto Serif Display','Noto Serif',Georgia,serif"
SANS = "'Noto Sans CJK SC','PingFang SC',sans-serif"

W, H = 1920, 1080


def rows(*lines):
    """Build a formation from rows back->front: each row is (x, [y, ...])."""
    pts = [(0.045, 0.5)]
    for x, ys in lines:
        for y in ys:
            pts.append((x, y))
    return pts


def spread(n, lo=0.12, hi=0.88):
    if n == 1:
        return [0.5]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


FORMATIONS = {
    "1-1-8": dict(name="1-1-8", year="1872", team="英格兰", note="八个前锋，带球冲锋",
                  pts=rows((0.22, [0.5]), (0.40, [0.5]),
                           (0.64, [0.1, 0.34, 0.58, 0.82]), (0.72, [0.22, 0.46, 0.66, 0.9]))),
    "2-2-6": dict(name="2-2-6", year="1872", team="苏格兰", note="少两个前锋，开始传球",
                  pts=rows((0.20, [0.32, 0.68]), (0.40, [0.3, 0.7]), (0.68, spread(6, 0.1, 0.9)))),
    "2-3-5": dict(name="2-3-5", year="1880s", team="金字塔", note="The Pyramid",
                  pts=rows((0.20, [0.32, 0.68]), (0.40, [0.2, 0.5, 0.8]), (0.68, spread(5, 0.08, 0.92)))),
    "WM": dict(name="W-M  3-2-2-3", year="1925", team="阿森纳 · 查普曼", note="中场退成第三个后卫",
               pts=rows((0.20, [0.2, 0.5, 0.8]), (0.36, [0.36, 0.64]), (0.54, [0.36, 0.64]),
                        (0.72, [0.1, 0.5, 0.9]))),
    "HUN-1953": dict(name="匈牙利 1953", year="1953", team="匈牙利", note="中锋回撤",
                     pts=rows((0.20, [0.2, 0.5, 0.8]), (0.36, [0.36, 0.64]), (0.50, [0.5]),
                              (0.70, [0.1, 0.38, 0.62, 0.9]))),
    "4-2-4": dict(name="4-2-4", year="1958", team="巴西", note="四后卫站成一条线",
                  pts=rows((0.22, spread(4, 0.14, 0.86)), (0.42, [0.38, 0.62]), (0.66, spread(4, 0.1, 0.9)))),
    "catenaccio": dict(name="链式防守  1-4-3-2", year="1960s", team="意大利 · 国际米兰", note="后卫线后再放一个自由人",
                       pts=rows((0.12, [0.5]), (0.24, spread(4, 0.14, 0.86)), (0.40, [0.25, 0.5, 0.75]),
                                (0.60, [0.38, 0.62]))),
    "total": dict(name="全攻全守  4-3-3", year="1974", team="荷兰", note="位置随时互换",
                  pts=rows((0.26, spread(4, 0.12, 0.88)), (0.46, [0.28, 0.5, 0.72]), (0.68, [0.12, 0.5, 0.88]))),
    "4-4-2-press": dict(name="4-4-2 压迫", year="1989", team="AC 米兰 · 萨基", note="两条线一起前压",
                        pts=rows((0.40, spread(4, 0.18, 0.82)), (0.52, spread(4, 0.18, 0.82)), (0.64, [0.4, 0.6]))),
    "4-3-3": dict(name="4-3-3 传控", year="2009", team="巴塞罗那", note="用传球控制比赛",
                  pts=rows((0.26, spread(4, 0.12, 0.88)), (0.46, [0.3, 0.5, 0.7]), (0.70, [0.12, 0.5, 0.88]))),
    "3-2-5": dict(name="3-2-5", year="2023", team="现代强队（进攻时）", note="边后卫内收，前面五个人",
                  pts=rows((0.32, [0.25, 0.5, 0.75]), (0.48, [0.4, 0.6]), (0.74, spread(5, 0.08, 0.92)))),
    "4-4-2": dict(name="4-4-2", year="", team="读法示例", note="后卫 – 中场 – 前锋",
                  pts=rows((0.24, spread(4, 0.14, 0.86)), (0.46, spread(4, 0.14, 0.86)), (0.68, [0.38, 0.62]))),
}


# ---------------------------------------------------------------- primitives
def svg_open(extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>'
            f'<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1 L9 5 L0 9" fill="none" stroke="{RED}" stroke-width="1.6"/></marker>'
            f'<marker id="arrInk" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 1 L9 5 L0 9" fill="none" stroke="{INK}" stroke-width="1.6"/></marker>'
            f'{extra_defs}</defs>'
            f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')


def text(x, y, s, size=28, fill=INK, family=SERIF, anchor="start", weight=400, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>')


class Pitch:
    """A pitch drawn with hairlines inside rect (x, y, w, h); 105 x 68 m."""

    def __init__(self, x, y, w, h=None):
        self.x, self.y, self.w = x, y, w
        self.h = h if h else w * 68 / 105

    def p(self, px, py):
        return self.x + px * self.w, self.y + py * self.h

    def m(self, mx, my):  # metres -> canvas
        return self.x + mx / 105 * self.w, self.y + my / 68 * self.h

    def draw(self, opacity=0.55):
        s = self.w / 105
        x, y, w, h = self.x, self.y, self.w, self.h
        g = [f'<g fill="none" stroke="{INK}" stroke-opacity="{opacity}" stroke-width="2">',
             f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>',
             f'<line x1="{x + w / 2}" y1="{y}" x2="{x + w / 2}" y2="{y + h}"/>',
             f'<circle cx="{x + w / 2}" cy="{y + h / 2}" r="{9.15 * s}"/>']
        for side in (0, 1):
            bx = x if side == 0 else x + w - 16.5 * s
            g.append(f'<rect x="{bx}" y="{y + (34 - 20.16) * s}" width="{16.5 * s}" height="{40.32 * s}"/>')
            gx = x if side == 0 else x + w - 5.5 * s
            g.append(f'<rect x="{gx}" y="{y + (34 - 9.16) * s}" width="{5.5 * s}" height="{18.32 * s}"/>')
            arc_x = x + 16.5 * s if side == 0 else x + w - 16.5 * s
            sweep = 1 if side == 0 else 0
            dy = 7.3 * s
            g.append(f'<path d="M{arc_x} {y + h / 2 - dy} A{9.15 * s} {9.15 * s} 0 0 {sweep} {arc_x} {y + h / 2 + dy}"/>')
        g.append('</g>')
        cx, cy = x + w / 2, y + h / 2
        g.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{INK}" fill-opacity="{opacity}"/>')
        return "".join(g)


class VPitch(Pitch):
    """Same pitch stood upright (attacking upward), used where the shape must read as letters (W-M)."""

    def __init__(self, cx, y, h):
        self.h, self.w = h, h * 68 / 105
        self.x, self.y = cx - self.w / 2, y

    def p(self, px, py):
        return self.x + py * self.w, self.y + (1 - px) * self.h

    def draw(self, opacity=0.55):
        s = self.h / 105
        x, y, w, h = self.x, self.y, self.w, self.h
        g = [f'<g fill="none" stroke="{INK}" stroke-opacity="{opacity}" stroke-width="2">',
             f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>',
             f'<line x1="{x}" y1="{y + h / 2}" x2="{x + w}" y2="{y + h / 2}"/>',
             f'<circle cx="{x + w / 2}" cy="{y + h / 2}" r="{9.15 * s}"/>']
        for by in (y, y + h - 16.5 * s):
            g.append(f'<rect x="{x + (34 - 20.16) * s}" y="{by}" width="{40.32 * s}" height="{16.5 * s}"/>')
        for gy in (y, y + h - 5.5 * s):
            g.append(f'<rect x="{x + (34 - 9.16) * s}" y="{gy}" width="{18.32 * s}" height="{5.5 * s}"/>')
        g.append('</g>')
        return "".join(g)


def dots(pitch, pts, color=INK, r=15, mirror=False, gk_color=MUTED, highlight=(), hl_color=RED, labels=None):
    out = []
    for i, (px, py) in enumerate(pts):
        if mirror:
            px = 1 - px
        cx, cy = pitch.p(px, py)
        c = gk_color if i == 0 else (hl_color if i in highlight else color)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{c}"/>')
        if labels and i in labels:
            out.append(text(cx, cy + 6, labels[i], size=15, fill=PAPER, family=SANS, anchor="middle"))
    return "".join(out)


def links(pitch, pts, color=RED, width=2, opacity=0.6, dash=""):
    """Connect consecutive players in the same row, then rows to each other (shape outline)."""
    out = []
    rows_ = {}
    for i, (px, py) in enumerate(pts[1:], 1):
        rows_.setdefault(round(px, 2), []).append(pitch.p(px, py))
    keys = sorted(rows_)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    for k in keys:
        r = sorted(rows_[k], key=lambda t: t[1])
        for a, b in zip(r, r[1:]):
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                       f'stroke="{color}" stroke-width="{width}" stroke-opacity="{opacity}"{d}/>')
    return "".join(out)


def board(pitch=None):
    pitch = pitch or Pitch(330, 150, 1260)
    return pitch, svg_open() + pitch.draw()


def save(name, body):
    path = os.path.join(OUT, name + ".svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "</svg>")
    return path


# ---------------------------------------------------------------- beats
def formation_board(key, highlight=(), shape=False, extra=""):
    f = FORMATIONS[key]
    pitch, s = board()
    if shape:
        s += links(pitch, f["pts"])
    s += dots(pitch, f["pts"], highlight=highlight)
    s += f'<g opacity="0.9">{extra}</g>'
    return s


def number_reading():
    f = FORMATIONS["4-4-2"]
    pitch, s = board()
    s += dots(pitch, f["pts"])
    cols = [(0.24, "4", "后卫", "defenders"), (0.46, "4", "中场", "midfielders"), (0.68, "2", "前锋", "forwards")]
    for x, n, zh, en in cols:
        cx, _ = pitch.p(x, 0)
        s += f'<line x1="{cx}" y1="{pitch.y + pitch.h + 18}" x2="{cx}" y2="{pitch.y + pitch.h + 40}" stroke="{RED}" stroke-width="2"/>'
        s += text(cx, pitch.y + pitch.h + 92, n, size=56, fill=RED, family=DISPLAY, anchor="middle")
        s += text(cx - 6, pitch.y - 22, zh, size=26, anchor="end")
        s += text(cx + 6, pitch.y - 22, en, size=18, fill=MUTED, family=DISPLAY, anchor="start", extra='font-style="italic"')
    gx, gy = pitch.p(0.045, 0.5)
    s += text(gx, gy + 48, "门将不计", size=20, fill=MUTED, anchor="middle")
    return s


def match_1872():
    """Two half boards side by side: England 1-1-8 vs Scotland 2-2-6, with Scotland's passing chain."""
    s = svg_open()
    for i, key in enumerate(["1-1-8", "2-2-6"]):
        p = Pitch(150 + i * 840, 230, 780)
        s += p.draw(0.5)
        f = FORMATIONS[key]
        s += dots(p, f["pts"], r=12, color=INK if i == 0 else RED)
        s += text(p.x, p.y - 30, f["team"], size=34)
        s += text(p.x + p.w, p.y - 30, f["name"], size=44, family=DISPLAY, anchor="end", fill=RED if i else INK)
        if i == 1:  # passing chain
            chain = [f["pts"][2], f["pts"][4], f["pts"][7], f["pts"][9]]
            d = "M" + " L".join(f"{p.p(*q)[0]:.1f} {p.p(*q)[1]:.1f}" for q in chain)
            s += f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="8 7" marker-end="url(#arr)"/>'
        else:  # dribble swarm arrow
            a = p.p(0.70, 0.5)
            s += f'<path d="M{a[0]:.1f} {a[1]:.1f} q60 -30 120 0" fill="none" stroke="{INK}" stroke-width="2.5" marker-end="url(#arrInk)"/>'
    s += text(W / 2, 880, "0 : 0", size=96, family=DISPLAY, anchor="middle")
    return s


def pyramid():
    f = FORMATIONS["2-3-5"]
    pitch, s = board()
    pts = f["pts"]
    # triangle outline: back pair -> outer forwards
    a, b = pitch.p(*pts[1]), pitch.p(*pts[2])
    c, d = pitch.p(*pts[6]), pitch.p(*pts[10])
    s += (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{c[0]:.1f} {c[1]:.1f} L{d[0]:.1f} {d[1]:.1f} L{b[0]:.1f} {b[1]:.1f} Z" '
          f'fill="{RED}" fill-opacity="0.06" stroke="{RED}" stroke-width="2" stroke-opacity="0.7"/>')
    s += links(pitch, pts, opacity=0.35)
    s += dots(pitch, pts)
    return s


def offside_1925():
    """Before / after panels. Attacker (red) needs N defenders between him and the goal line."""
    s = svg_open()
    for i, (n, title) in enumerate([(3, "1925 年以前：需要 3 名防守方"), (2, "1925 年起：只需 2 名")]):
        p = Pitch(150 + i * 840, 260, 780)
        s += p.draw(0.45)
        # attacker running in behind, defending team on right half
        gk = p.m(103, 34)
        s += f'<circle cx="{gk[0]:.1f}" cy="{gk[1]:.1f}" r="12" fill="{MUTED}"/>'
        if n == 3:
            defs = [(80, 20), (86, 46), (80, 34)]
            line_x = 80
        else:
            defs = [(86, 20), (78, 46)]
            line_x = 78
        for mx, my in defs:
            q = p.m(mx, my)
            s += f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="12" fill="{INK}"/>'
        lx, _ = p.m(line_x, 0)
        s += (f'<line x1="{lx:.1f}" y1="{p.y}" x2="{lx:.1f}" y2="{p.y + p.h}" stroke="{RED}" '
              f'stroke-width="2.5" stroke-dasharray="10 8"/>')
        att = p.m(line_x + 3 if n == 2 else line_x - 3, 30)
        s += f'<circle cx="{att[0]:.1f}" cy="{att[1]:.1f}" r="12" fill="{RED}"/>'
        s += text(p.x, p.y - 34, title, size=30, fill=RED if i else INK)
        s += text(p.x + p.w, p.y + p.h + 60, "越位线 · offside line", size=20, fill=MUTED, anchor="end")
    return s


def goals_chart():
    s = svg_open()
    data = [("1924–25", 1192), ("1925–26", 1703)]
    base, top = 860, 260
    scale = (base - top) / 1800
    for i, (season, g) in enumerate(data):
        x = 700 + i * 360
        h = g * scale
        c = INK if i == 0 else RED
        s += f'<rect x="{x}" y="{base - h:.1f}" width="160" height="{h:.1f}" fill="{c}" fill-opacity="{0.85 if i else 0.75}"/>'
        s += text(x + 80, base - h - 28, f"{g:,}", size=64, family=DISPLAY, anchor="middle", fill=c)
        s += text(x + 80, base + 52, season, size=28, family=DISPLAY, anchor="middle", fill=MUTED)
    s += f'<line x1="620" y1="{base}" x2="1300" y2="{base}" stroke="{INK}" stroke-width="2"/>'
    s += text(1320, 420, "+511", size=72, family=DISPLAY, fill=RED)
    s += text(1320, 466, "英格兰顶级联赛 · 全季进球", size=24, fill=MUTED)
    return s


def wm_letters():
    f = FORMATIONS["WM"]
    pitch = VPitch(W / 2, 70, 940)
    s = svg_open() + pitch.draw()
    p = [pitch.p(*q) for q in f["pts"]]
    # M = back three + two halves ; W = two inside forwards + front three
    m = [p[1], p[4], p[2], p[5], p[3]]
    w = [p[8], p[6], p[9], p[7], p[10]]
    for poly, c in ((m, SLATE), (w, RED)):
        d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in poly)
        s += f'<path d="{d}" fill="none" stroke="{c}" stroke-width="3" stroke-linejoin="round" stroke-opacity="0.8"/>'
    s += dots(pitch, f["pts"], highlight=(2,))
    a = pitch.p(0.40, 0.5)
    b = pitch.p(0.22, 0.5)
    s += (f'<path d="M{a[0] + 40:.1f} {a[1]:.1f} Q{a[0] + 90:.1f} {(a[1] + b[1]) / 2:.1f} {b[0] + 30:.1f} {b[1] - 8:.1f}" '
          f'fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="6 6" marker-end="url(#arr)"/>')
    s += text(pitch.x + pitch.w + 60, pitch.y + 120, "W", size=120, family=DISPLAY, fill=RED)
    s += text(pitch.x + pitch.w + 60, pitch.y + pitch.h - 40, "M", size=120, family=DISPLAY, fill=SLATE)
    return s


def wembley_1953():
    """Hungary (red) attacking right; Hidegkuti drops deep, England's centre-half follows, space opens."""
    pitch, s = board()
    hun = FORMATIONS["HUN-1953"]["pts"]
    s += dots(pitch, hun, color=RED, gk_color=MUTED)
    # England WM defending the right goal (ink), mirrored back three
    eng = [(0.955, 0.5), (0.80, 0.2), (0.62, 0.5), (0.80, 0.8), (0.66, 0.36), (0.66, 0.64)]
    for i, (x, y) in enumerate(eng):
        cx, cy = pitch.p(x, y)
        c = MUTED if i == 0 else INK
        s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="15" fill="{c}"/>'
    # centre-half dragged from 0.80 to 0.62
    a, b = pitch.p(0.80, 0.5), pitch.p(0.63, 0.5)
    s += f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="15" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>'
    s += f'<line x1="{a[0] - 18:.1f}" y1="{a[1]:.1f}" x2="{b[0] + 22:.1f}" y2="{b[1]:.1f}" stroke="{INK}" stroke-width="2" marker-end="url(#arrInk)"/>'
    # the hole
    hx, hy = pitch.p(0.83, 0.5)
    s += (f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="120" ry="150" fill="{RED}" fill-opacity="0.12" '
          f'stroke="{RED}" stroke-opacity="0.6" stroke-dasharray="6 6"/>')
    # inside forwards running into the hole
    for y0 in (0.38, 0.62):
        p0 = pitch.p(0.70, y0)
        s += (f'<path d="M{p0[0] + 18:.1f} {p0[1]:.1f} Q{hx - 40:.1f} {(p0[1] + hy) / 2:.1f} {hx - 10:.1f} {hy + (y0 - 0.5) * 120:.1f}" '
              f'fill="none" stroke="{RED}" stroke-width="2.5" marker-end="url(#arr)"/>')
    # Hidegkuti label
    hk = pitch.p(0.50, 0.5)
    s += text(hk[0], hk[1] - 30, "9", size=26, family=DISPLAY, anchor="middle", fill=RED)
    s += text(W / 2, 1010, "3 : 6", size=64, family=DISPLAY, anchor="middle")
    return s


def catenaccio():
    f = FORMATIONS["catenaccio"]
    pitch, s = board()
    lib = pitch.p(*f["pts"][1])
    line_l, line_r = pitch.p(0.24, 0.1), pitch.p(0.24, 0.9)
    s += (f'<rect x="{lib[0] - 30:.1f}" y="{line_l[1]:.1f}" width="60" height="{line_r[1] - line_l[1]:.1f}" rx="30" '
          f'fill="{SLATE}" fill-opacity="0.08" stroke="{SLATE}" stroke-opacity="0.6" stroke-width="2"/>')
    s += dots(pitch, f["pts"], highlight=(1,), hl_color=SLATE)
    s += text(lib[0], line_l[1] - 18, "自由人 libero", size=22, fill=SLATE, anchor="middle")
    return s


def total_football():
    f = FORMATIONS["total"]
    pitch, s = board()
    pts = f["pts"]
    # rotation loops: full-back <-> winger, centre-back stepping up, CF dropping
    swaps = [(1, 8), (4, 10), (3, 6), (9, 7)]
    for a, b in swaps:
        A, B = pitch.p(*pts[a]), pitch.p(*pts[b])
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2 - 70
        s += (f'<path d="M{A[0]:.1f} {A[1]:.1f} Q{mx:.1f} {my:.1f} {B[0]:.1f} {B[1]:.1f}" fill="none" stroke="{RED}" '
              f'stroke-width="2" stroke-opacity="0.75" marker-end="url(#arr)" marker-start="url(#arr)"/>')
    s += dots(pitch, pts, color=RED)
    return s


def press_442():
    f = FORMATIONS["4-4-2-press"]
    pitch, s = board()
    ball = pitch.p(0.66, 0.30)
    for r, op in ((150, 0.15), (105, 0.3), (65, 0.55)):
        s += f'<circle cx="{ball[0]:.1f}" cy="{ball[1]:.1f}" r="{r}" fill="none" stroke="{RED}" stroke-opacity="{op}" stroke-width="2"/>'
    s += f'<circle cx="{ball[0]:.1f}" cy="{ball[1]:.1f}" r="13" fill="{SLATE}"/>'
    # compact block shading between the two lines
    a, b = pitch.p(0.38, 0.14), pitch.p(0.54, 0.86)
    s += f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{b[1] - a[1]:.1f}" fill="{INK}" fill-opacity="0.05"/>'
    s += links(pitch, f["pts"], color=INK, opacity=0.35)
    s += dots(pitch, f["pts"])
    s += f'<path d="M{a[0] - 80:.1f} {pitch.y + pitch.h + 40:.1f} h140" stroke="{RED}" stroke-width="2.5" marker-end="url(#arr)"/>'
    return s


def passing_web():
    f = FORMATIONS["4-3-3"]
    pitch, s = board()
    pts = f["pts"]
    pairs = [(1, 2), (2, 3), (3, 4), (1, 5), (2, 5), (2, 6), (3, 6), (3, 7), (4, 7), (5, 6), (6, 7), (5, 8),
             (6, 9), (7, 10), (6, 8), (6, 10), (5, 9), (7, 9), (8, 9), (9, 10), (0, 2), (0, 3)]
    for a, b in pairs:
        A, B = pitch.p(*pts[a]), pitch.p(*pts[b])
        w = 1.5 + 2.5 * ((a * 7 + b * 3) % 5) / 4
        s += f'<line x1="{A[0]:.1f}" y1="{A[1]:.1f}" x2="{B[0]:.1f}" y2="{B[1]:.1f}" stroke="{RED}" stroke-width="{w:.1f}" stroke-opacity="0.45"/>'
    s += dots(pitch, pts, highlight=(6,))
    return s


def full_circle():
    """2-3-5 (1880s) and 3-2-5 (today) side by side, front five highlighted."""
    s = svg_open()
    for i, key in enumerate(["2-3-5", "3-2-5"]):
        p = Pitch(150 + i * 840, 250, 780)
        s += p.draw(0.45)
        f = FORMATIONS[key]
        s += dots(p, f["pts"], r=12, highlight=range(6, 11))
        fx, _ = p.p(0.7, 0)
        s += (f'<rect x="{fx - 40:.1f}" y="{p.y + 10:.1f}" width="80" height="{p.h - 20:.1f}" rx="40" fill="none" '
              f'stroke="{RED}" stroke-width="2" stroke-dasharray="6 6"/>')
        s += text(p.x, p.y - 34, ["1880s", "今天"][i], size=34, family=DISPLAY if i == 0 else SERIF)
        s += text(p.x + p.w, p.y - 34, f["name"], size=48, family=DISPLAY, anchor="end", fill=RED)
    s += text(W / 2, 880, "前面的五个人，几乎一模一样", size=30, anchor="middle", fill=MUTED)
    return s


def family_tree():
    """Ink stem left->right through time; branches up/down end in vermilion blossoms."""
    s = svg_open()
    y0 = 560
    s += (f'<path d="M120 {y0 + 20} C 500 {y0 - 10}, 900 {y0 + 25}, 1300 {y0} S 1700 {y0 - 15}, 1800 {y0 - 5}" '
          f'fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>')
    nodes = [  # x, side(-1 up / +1 down), length, year, label, en
        (170, -1, 150, "1872", "1-1-8 · 2-2-6", "the charge"),
        (380, 1, 170, "1880s", "2-3-5 金字塔", "the pyramid"),
        (580, -1, 210, "1925", "W-M", "third back"),
        (780, 1, 150, "1953", "回撤中锋", "deep-lying 9"),
        (960, -1, 170, "1958", "4-2-4", "back four"),
        (1130, 1, 230, "1960s", "链式防守", "catenaccio"),
        (1260, -1, 240, "1974", "全攻全守", "total football"),
        (1430, 1, 160, "1989", "压迫 4-4-2", "the press"),
        (1590, -1, 180, "2009", "传控 4-3-3", "possession"),
        (1760, 1, 200, "今天", "3-2-5", "full circle"),
    ]
    for i, (x, side, L, yr, label, en) in enumerate(nodes):
        t = (x - 120) / 1680
        ys = y0 + 20 - 25 * t + 10 * math.sin(t * 6)
        ex, ey = x + 40 * (1 if i % 2 else -1) * 0.6, ys + side * L
        cx, cy = x - side * 10, ys + side * L * 0.5
        s += (f'<path d="M{x:.1f} {ys:.1f} Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{INK}" '
              f'stroke-width="{4.5 - 1.5 * (L / 240):.1f}" stroke-linecap="round"/>')
        last = i == len(nodes) - 1
        r = 15 if last else 10
        s += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r}" fill="{RED}"/>'
        for k in range(5):  # tiny petals
            ang = k * 2 * math.pi / 5
            s += f'<circle cx="{ex + math.cos(ang) * r * 1.1:.1f}" cy="{ey + math.sin(ang) * r * 1.1:.1f}" r="{r * 0.55:.1f}" fill="{RED}" fill-opacity="0.55"/>'
        yfam = DISPLAY if yr[0].isdigit() else SERIF
        if side < 0:  # year / label / english stacked above the blossom
            s += text(ex, ey - 96, yr, size=18, family=yfam, anchor="middle", fill=MUTED)
            s += text(ex, ey - 62, label, size=26, anchor="middle")
            s += text(ex, ey - 34, en, size=16, family=DISPLAY, anchor="middle", fill=MUTED, extra='font-style="italic"')
        else:  # label / year / english below
            s += text(ex, ey + 52, label, size=26, anchor="middle")
            s += text(ex, ey + 80, yr, size=18, family=yfam, anchor="middle", fill=MUTED)
            s += text(ex, ey + 106, en, size=16, family=DISPLAY, anchor="middle", fill=MUTED, extra='font-style="italic"')
    # dashed arc: today -> 1880s pyramid
    s += (f'<path d="M1760 {y0 + 330} C 1500 {y0 + 470}, 700 {y0 + 470}, 400 {y0 + 330}" fill="none" stroke="{RED}" '
          f'stroke-width="2" stroke-dasharray="8 8" stroke-opacity="0.7" marker-end="url(#arr)"/>')
    # vertical seal title like the reference's 家谱 tag
    s += text(1835, 120, "阵", size=46, anchor="middle")
    s += text(1835, 172, "型", size=46, anchor="middle")
    s += text(1835, 224, "家", size=46, anchor="middle")
    s += text(1835, 276, "谱", size=46, anchor="middle")
    s += f'<rect x="1816" y="300" width="38" height="38" fill="none" stroke="{RED}" stroke-width="2"/>'
    s += text(1835, 325, "11", size=16, family=DISPLAY, anchor="middle", fill=RED)
    return s


def title_card():
    s = svg_open()
    s += text(W / 2, 360, "T H E   S H A P E   O F   E L E V E N", size=22, family=DISPLAY, anchor="middle", fill=MUTED)
    s += text(W / 2, 560, "十一人", size=190, anchor="middle", weight=600)
    s += f'<line x1="760" y1="630" x2="1160" y2="630" stroke="{RED}" stroke-width="2"/>'
    s += text(W / 2, 690, "足球阵型 150 年", size=40, anchor="middle")
    s += text(W / 2, 740, "A short history of football formations", size=24, family=DISPLAY, anchor="middle",
              fill=MUTED, extra='font-style="italic"')
    # eleven dots under the title as the signature motif
    for i in range(11):
        s += f'<circle cx="{W / 2 - 200 + i * 40}" cy="820" r="7" fill="{RED if i == 5 else INK}"/>'
    return s


BEATS = {
    "00-title-card": title_card,
    "01-how-to-read-4-4-2": number_reading,
    "02-1872-england-vs-scotland": match_1872,
    "03-1880s-pyramid-2-3-5": pyramid,
    "04-1925-offside-rule": offside_1925,
    "05-1925-goals-chart": goals_chart,
    "06-1925-wm-letters": wm_letters,
    "07-1953-wembley-deep-nine": wembley_1953,
    "08-1958-4-2-4": lambda: formation_board("4-2-4", highlight=(1, 2, 3, 4), shape=True),
    "09-1960s-catenaccio": catenaccio,
    "10-1974-total-football": total_football,
    "11-1989-press-4-4-2": press_442,
    "12-2009-passing-web-4-3-3": passing_web,
    "13-today-3-2-5": lambda: formation_board("3-2-5", highlight=range(6, 11), shape=True),
    "14-full-circle-2-3-5-vs-3-2-5": full_circle,
    "15-family-tree": family_tree,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {k: dict(v, pts=[[round(x, 4), round(y, 4)] for x, y in v["pts"]]) for k, v in FORMATIONS.items()}
    with open(os.path.join(OUT, "formations.json"), "w", encoding="utf-8") as f:
        json.dump(dict(coords="x: own goal 0 -> opponent goal 1; y: top 0 -> bottom 1; id 0 = GK",
                       order=["1-1-8", "2-2-6", "2-3-5", "WM", "HUN-1953", "4-2-4", "catenaccio", "total",
                              "4-4-2-press", "4-3-3", "3-2-5"],
                       formations=data), f, ensure_ascii=False, indent=1)
    paths = [save(k, fn()) for k, fn in BEATS.items()]
    if "--png" in sys.argv:
        import cairosvg
        from PIL import Image, ImageDraw, ImageFont
        prev = os.path.join(OUT, "preview")
        os.makedirs(prev, exist_ok=True)
        thumbs = []
        for p in paths:
            png = os.path.join(prev, os.path.basename(p)[:-4] + ".png")
            cairosvg.svg2png(url=p, write_to=png, output_width=W, output_height=H)
            thumbs.append(png)
        tw, th, cols = 480, 270, 4
        rows_n = math.ceil(len(thumbs) / cols)
        sheet = Image.new("RGB", (cols * tw, rows_n * (th + 30)), PAPER)
        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 18)
        dr = ImageDraw.Draw(sheet)
        for i, png in enumerate(thumbs):
            im = Image.open(png).convert("RGB").resize((tw, th))
            x, y = (i % cols) * tw, (i // cols) * (th + 30)
            sheet.paste(im, (x, y))
            dr.text((x + 8, y + th + 4), os.path.basename(png)[:-4], fill=INK, font=font)
        sheet.save(os.path.join(prev, "_contact-sheet.png"))


if __name__ == "__main__":
    main()
