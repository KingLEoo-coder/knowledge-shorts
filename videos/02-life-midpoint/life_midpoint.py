"""人生的中点是 18 岁：竖屏 1080x1920 纪录片式短视频（画面部分）。

先跑 scenery.py 生成 assets/ 里的底图，再渲染：
  manim -qh --disable_caching life_midpoint.py LifeMidpoint
  PREVIEW=1 半分辨率 15fps 快速预览
渲染时把关键节拍写进 marks.json，music.py 读它来对齐配乐和音效。
"""
import json
import math
import os
import random

from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30
config.background_color = "#EFE8DA"
if os.environ.get("PREVIEW"):
    config.pixel_width, config.pixel_height, config.frame_rate = 540, 960, 15

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

INK = "#1C1A17"
SUB = "#8A8378"
HAIR = "#CFC6B6"
RED = "#C8432B"
IVORY = "#F4EEE2"
IVORY_SUB = "#D8CDB8"
SERIF = "Noto Serif CJK SC"
LATIN = "Noto Serif"
LOG20 = math.log(20)


def zh(s, size=44, color=INK, weight=NORMAL):
    return Text(s, font=SERIF, font_size=size, color=color, weight=weight)


def en(s, size=24, color=SUB):
    return Text(s, font=LATIN, font_size=size, color=color, slant=ITALIC)


def img(name):
    return ImageMobject(os.path.join(ASSETS, name))


def felt_frac(age):
    return math.log(age / 4) / LOG20


def seal(text="十八", size=1.0):
    """朱红印章：红底白字，略微倾斜。"""
    box = Square(size, stroke_width=0).set_fill(RED, 0.95)
    inner = Square(size * 0.86, stroke_color="#F6E9DC", stroke_width=2)
    chars = VGroup(*[Text(c, font=SERIF, weight=BOLD, font_size=int(64 * size), color="#F6E9DC") for c in text])
    if len(text) == 2:
        chars.arrange(DOWN, buff=0.02)
    chars.scale_to_fit_height(size * 0.72)
    return VGroup(box, inner, chars).rotate(-0.06)


def brush(points, w0, w1, color=INK, opacity=0.92):
    """一段两头粗细不同的墨笔：沿折线做左右偏移，围成多边形。"""
    pts = [np.array(p, dtype=float) for p in points]
    n = len(pts)
    left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        d = b - a
        nrm = np.array([-d[1], d[0], 0]) / (np.linalg.norm(d) + 1e-9)
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append(p + nrm * w)
        right.append(p - nrm * w)
    return Polygon(*left, *right[::-1], stroke_width=0).set_fill(color, opacity)


def blossom(r=0.16, color=RED):
    petals = VGroup(*[Circle(radius=r * 0.62, stroke_width=0).set_fill(color, 0.92)
                      .move_to([r * 0.7 * math.cos(k * TAU / 5 + PI / 2), r * 0.7 * math.sin(k * TAU / 5 + PI / 2), 0])
                      for k in range(5)])
    core = Circle(radius=r * 0.3, stroke_width=0).set_fill("#7A1F14", 1)
    dots = VGroup(*[Dot([r * 0.5 * math.cos(k * TAU / 7), r * 0.5 * math.sin(k * TAU / 7), 0], radius=r * 0.06,
                        color="#F2D9A0") for k in range(7)])
    return VGroup(petals, core, dots)


class Clock(Mobject):
    def __init__(self):
        super().__init__()
        self.t = 0.0
        self.add_updater(lambda m, dt: setattr(m, "t", m.t + dt))


class Particles(VGroup):
    """飘落/漂浮的粒子：petal 花瓣、leaf 落叶、snow 雪、firefly 萤火、dust 尘埃。"""

    def __init__(self, kind, n=40, seed=1, area=(-4.6, 4.6, -8.2, 8.2)):
        super().__init__()
        rng = random.Random(seed)
        self.kind = kind
        self.area = area
        self.state = []
        for _ in range(n):
            x, y = rng.uniform(area[0], area[1]), rng.uniform(area[2], area[3])
            if kind == "petal":
                m = Ellipse(width=0.16, height=0.09, stroke_width=0).set_fill("#E9A3A0", 0.85)
                v = (rng.uniform(0.15, 0.5), rng.uniform(-0.9, -0.4))
            elif kind == "leaf":
                m = Ellipse(width=0.18, height=0.08, stroke_width=0).set_fill(rng.choice(["#C8642B", "#D9922F", "#9E3B22"]), 0.9)
                v = (rng.uniform(-0.2, 0.4), rng.uniform(-1.4, -0.7))
            elif kind == "snow":
                m = Dot(radius=rng.uniform(0.02, 0.05), color=WHITE).set_opacity(0.9)
                v = (rng.uniform(-0.15, 0.15), rng.uniform(-0.9, -0.4))
            elif kind == "firefly":
                m = Dot(radius=rng.uniform(0.025, 0.045), color="#FFE7A0")
                v = (rng.uniform(-0.15, 0.15), rng.uniform(-0.08, 0.15))
            else:  # dust
                m = Dot(radius=rng.uniform(0.01, 0.025), color="#6B635A").set_opacity(0.35)
                v = (rng.uniform(-0.08, 0.08), rng.uniform(0.02, 0.12))
            m.move_to([x, y, 0])
            self.add(m)
            self.state.append([v[0], v[1], rng.uniform(0, 6.28), rng.uniform(1, 3)])
        self.add_updater(Particles.step)

    @staticmethod
    def step(self, dt):
        x0, x1, y0, y1 = self.area
        for m, st in zip(self.submobjects, self.state):
            st[2] += dt * st[3]
            dx = st[0] + 0.25 * math.sin(st[2]) * (self.kind in ("petal", "leaf", "snow"))
            m.shift([dx * dt, st[1] * dt, 0])
            if self.kind in ("petal", "leaf"):
                m.rotate(dt * st[3] * 0.8)
            if self.kind == "firefly":
                m.set_opacity(0.35 + 0.65 * max(0, math.sin(st[2])))
            p = m.get_center()
            if p[1] < y0:
                m.move_to([p[0], y1, 0])
            elif p[1] > y1:
                m.move_to([p[0], y0, 0])
            if p[0] < x0:
                m.move_to([x1, p[1], 0])
            elif p[0] > x1:
                m.move_to([x0, p[1], 0])


class LifeMidpoint(Scene):
    # ---------- 公共元素 ----------
    def mark(self, name, **kw):
        self.marks.append({"name": name, "t": round(self.renderer.time, 3), **kw})

    def _swap(self, name, run_time, drift, rate_func=smooth, extra=(), match=True):
        new = img(name).scale_to_fit_height(16.4)
        if self.bg is not None and match:
            new.scale(self.bg.height / 16.4)
        self.add(new)
        self.bring_to_back(new)
        if self.bg is None:
            self.play(FadeIn(new), *extra, run_time=run_time)
        else:
            old = self.bg
            self.bring_to_back(old)
            self.play(FadeOut(old), *extra, run_time=run_time, rate_func=rate_func)
            old.clear_updaters()
            self.remove(old)
        new.add_updater(lambda m, dt: m.scale(1 + drift * dt))
        self.bg = new

    def set_bg(self, name, run_time=1.0, drift=0.012):
        self._swap(name, run_time, drift, match=False)  # 新场景从原始大小开始慢推

    def kicker(self, title, sub="", dark=False):
        col = IVORY if dark else INK
        line = Line(LEFT * 0.35, RIGHT * 0.35, stroke_width=2.5, color=RED)
        t = zh(title, 34, col, BOLD)
        top = VGroup(line, t).arrange(RIGHT, buff=0.22)
        if sub:
            s = zh(sub, 22, IVORY_SUB if dark else SUB)
            g = VGroup(top, s).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            s.align_to(t, LEFT)
        else:
            g = top
        g.move_to([-3.75, 6.95, 0], aligned_edge=UL)
        anims = [FadeIn(g, shift=RIGHT * 0.15)]
        if self.kick is not None:
            anims.append(FadeOut(self.kick))
        self.play(*anims, run_time=0.6)
        self.kick = g

    def sub(self, zh_text, en_text, dark=False, t2c=None, hold=1.5, y=-5.7, size=42):
        a = zh(zh_text, size, IVORY if dark else INK)
        if t2c:
            a.set_color_by_t2c(t2c)
        if a.width > 8.2:
            a.scale_to_fit_width(8.2)
        dia = Square(0.07, stroke_width=0).set_fill(RED, 1).rotate(PI / 4)
        hc = IVORY_SUB if dark else HAIR
        div = VGroup(Line(LEFT * 0.5, ORIGIN, stroke_width=1, color=hc), dia,
                     Line(ORIGIN, RIGHT * 0.5, stroke_width=1, color=hc)).arrange(RIGHT, buff=0.08)
        b = en(en_text, 23, IVORY_SUB if dark else SUB)
        if b.width > 8.0:
            b.scale_to_fit_width(8.0)
        g = VGroup(a, div, b).arrange(DOWN, buff=0.16).move_to([0, y, 0])
        if self.subtitle is not None:
            self.play(FadeOut(self.subtitle), run_time=0.25)
        self.play(FadeIn(g, shift=UP * 0.1), run_time=0.45)
        self.subtitle = g
        if hold:
            self.wait(hold)
        return g

    def scrim(self):
        """暗场底部的渐变压暗，保证浅色字幕在亮背景（雪、晴空）上也看得清。"""
        a = np.linspace(0, 1, 256) ** 1.6 * 150
        arr = np.zeros((256, 4, 4), dtype=np.uint8)
        arr[:, :, 3] = a[:, None].astype(np.uint8)
        m = ImageMobject(arr).stretch_to_fit_width(9.4).stretch_to_fit_height(6.5)
        return m.move_to([0, -8.1 + 3.25, 0])

    def drop_sub(self):
        if self.subtitle is not None:
            self.play(FadeOut(self.subtitle), run_time=0.4)
            self.subtitle = None

    def clear_layer(self, *mobs, run_time=0.6):
        mobs = [m for m in mobs if m is not None]
        for m in mobs:
            m.clear_updaters()
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        if self.kick in mobs:
            self.kick = None
        if self.subtitle in mobs:
            self.subtitle = None

    # ---------- 正片 ----------
    def construct(self):
        self.marks = []
        self.bg = None
        self.kick = None
        self.subtitle = None
        self.clock = Clock()
        self.add(self.clock)

        self.s0_opening()
        self.s1_seasons()
        self.s2_janet()
        self.s3_scroll()
        self.s4_doubling()
        self.s5_day()
        self.s6_blossom()
        self.s7_ending()

        self.mark("end")
        with open("marks.json", "w") as f:
            json.dump(self.marks, f, ensure_ascii=False, indent=1)

    # 0. 开场：水墨山水
    def s0_opening(self):
        self.mark("intro")
        self.set_bg("ink_landscape.png", run_time=1.5)
        dust = Particles("dust", 40, seed=2)
        self.add(dust)
        self.sub("如果你能活到 80 岁，", "If you were to live to eighty,", t2c={"80": RED}, hold=1.4)
        self.sub("你觉得，人生的中点在哪里？", "where would the midpoint of your life be?", hold=1.8)
        self.drop_sub()
        title = zh("人生的中点", 96, INK, BOLD)
        tag = en("On the Felt Midpoint of a Life", 26)
        g = VGroup(title, tag).arrange(DOWN, buff=0.3).move_to([0, -4.9, 0])
        st = seal("中点", 0.8).next_to(title, RIGHT, buff=0.25).shift(UP * 0.15)
        self.mark("pop")
        self.play(FadeIn(title, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(tag), FadeIn(st, scale=1.4), run_time=0.6)
        self.wait(1.6)
        self.mark("whoosh")
        self.clear_layer(title, tag, st, dust)

    # 1. 5 岁的夏天 vs 40 岁的四季
    def s1_seasons(self):
        self.set_bg("field_summer.png", run_time=1.0)
        flies = Particles("firefly", 28, seed=4, area=(-4.6, 4.6, -7.5, 0))
        shade = self.scrim()
        self.add(shade, flies)
        self.kicker("5 岁", "一个夏天", dark=True)
        self.sub("小时候，一个暑假长得像永远。", "As a child, one summer felt like forever.", dark=True, hold=3.2)
        self.clear_layer(flies, run_time=0.5)

        self.kicker("40 岁", "一整年", dark=True)
        self.sub("长大后，一年一眨眼就过去了。", "As an adult, a year is gone in a blink.", dark=True, hold=0)
        order = [("field_spring.png", "petal"), ("field_summer.png", "firefly"), ("field_autumn.png", "leaf"),
                 ("field_winter.png", "snow")] * 2
        parts = None
        self.mark("ticks", n=8, dur=5.6)
        for i, (name, kind) in enumerate(order):
            if parts is not None:
                parts.clear_updaters()
                self.remove(parts)
            parts = Particles(kind, 36, seed=10 + i)
            self.add(parts)
            self.bring_to_front(self.kick, self.subtitle)
            self._swap(name, 0.25, 0.012, rate_func=linear)
            self.bring_to_front(shade, parts, self.kick, self.subtitle)
            self.wait(0.45)
        self.sub("同样是 365 天，为什么感觉差这么多？", "Same 365 days. Why do they feel so different?", dark=True,
                 t2c={"365": "#F2B39A"}, hold=1.8)
        self.mark("whoosh")
        self.clear_layer(parts, shade, self.kick, self.subtitle)

    # 2. 1877 年，让内的比例理论
    def s2_janet(self):
        self.set_bg("desk.png", run_time=1.0, drift=0.006)
        glow = img("candle_glow.png").scale_to_fit_height(16.4)
        clock = self.clock
        glow.add_updater(lambda m: m.set_opacity(0.75 + 0.25 * math.sin(clock.t * 7.3) * math.sin(clock.t * 3.1)))
        self.add(glow)
        self.kicker("1877", "法国 · 哲学家 保罗·让内", dark=True)
        page = img("aged_page.png").scale_to_fit_width(6.2).rotate(0.03).move_to([-0.6, 0.9, 0])
        self.play(FadeIn(page, shift=UP * 0.6), run_time=1.0)
        head = Text("Paul Janet, 1877", font=LATIN, slant=ITALIC, font_size=40, color="#3A2A1C")
        head.move_to(page.get_top() + DOWN * 0.8).rotate(0.03)
        rule = Line(LEFT * 2.2, RIGHT * 2.2, stroke_width=1.2, color="#7A6450").next_to(head, DOWN, buff=0.25).rotate(0.03)
        self.play(Write(head), Create(rule), run_time=1.2)
        self.sub("1877 年，法国哲学家保罗·让内提出：", "In 1877, the French philosopher Paul Janet proposed:",
                 dark=True, hold=1.0)
        self.sub("一段时光感觉有多长，取决于它占你人生的比例。",
                 "how long a span of time feels depends on its share of your life.", dark=True,
                 t2c={"比例": "#F2B39A"}, size=38, hold=1.2)

        def pie(n, r, center):
            g = VGroup()
            for i in range(n):
                s = AnnularSector(inner_radius=0, outer_radius=r, angle=TAU / n, start_angle=PI / 2 + i * TAU / n,
                                  stroke_color="#3A2A1C", stroke_width=1.6 if n < 20 else 0.6)
                s.set_fill(RED if i == 0 else "#3A2A1C", 0.85 if i == 0 else 0.0)
                g.add(s)
            return g.move_to(center)
        c5 = page.get_center() + LEFT * 1.45 + DOWN * 0.3
        c50 = page.get_center() + RIGHT * 1.45 + DOWN * 0.3
        p5, p50 = pie(5, 1.05, c5), pie(50, 1.05, c50)
        l5 = Text("5 岁 · 1/5", font=SERIF, font_size=30, color="#3A2A1C").next_to(p5, DOWN, buff=0.35)
        l50 = Text("50 岁 · 1/50", font=SERIF, font_size=30, color="#3A2A1C").next_to(p50, DOWN, buff=0.35)
        self.mark("tick")
        self.play(Create(p5), FadeIn(l5), run_time=1.0)
        self.mark("tick")
        self.play(Create(p50), FadeIn(l50), run_time=1.2)
        self.sub("5 岁时，一年是人生的五分之一；50 岁时，只有五十分之一。",
                 "At five, a year is a fifth of your life. At fifty, a fiftieth.", dark=True, size=36, hold=2.2)
        self.mark("whoosh")
        self.clear_layer(page, head, rule, p5, p50, l5, l50, glow, self.kick, self.subtitle)

    # 3. 立轴：按感觉重新丈量 4～80 岁
    def s3_scroll(self):
        self.set_bg("paper.png", run_time=1.0, drift=0.004)
        self.kicker("一幅立轴", "4 岁 → 80 岁")
        X, TOP, HGT, WID = -0.6, 5.3, 9.4, 3.4
        painting = img("scroll_painting.png")
        painting.stretch_to_fit_width(WID).stretch_to_fit_height(HGT).move_to([X, TOP - HGT / 2, 0])
        mount = Rectangle(width=WID + 0.7, height=HGT + 1.1, stroke_width=0).set_fill("#D8CCB4", 1)
        mount.move_to([X, TOP - HGT / 2 + 0.15, 0])
        border = Rectangle(width=WID + 0.08, height=HGT + 0.08, stroke_color="#A89878", stroke_width=1.5)
        border.move_to(painting)
        top_rod = RoundedRectangle(corner_radius=0.08, width=WID + 1.2, height=0.22, stroke_width=0).set_fill("#4A3324", 1)
        top_rod.move_to([X, mount.get_top()[1], 0])
        bot_rod = RoundedRectangle(corner_radius=0.1, width=WID + 1.5, height=0.3, stroke_width=0).set_fill("#3A2618", 1)
        body = Group(mount, painting, border)
        bottom_y = mount.get_bottom()[1]
        full_h = body.height
        body.stretch_to_fit_height(0.05, about_edge=UP)
        bot_rod.move_to([X, top_rod.get_center()[1] - 0.2, 0])
        self.play(FadeIn(top_rod), FadeIn(bot_rod), FadeIn(body), run_time=0.5)
        self.mark("whoosh")
        self.play(body.animate.stretch_to_fit_height(full_h, about_edge=UP),
                  bot_rod.animate.move_to([X, bottom_y, 0]), run_time=2.0, rate_func=smooth)
        self.sub("把 4～80 岁，画成一幅立轴。", "Paint the years from four to eighty as one hanging scroll.", hold=1.0)

        warp = ValueTracker(0)
        x_tick = X + WID / 2 + 0.6

        def y_of(age, w):
            return TOP - HGT * ((1 - w) * (age - 4) / 76 + w * felt_frac(age))

        def ticks(ages, show_warped):
            def f():
                w = warp.get_value()
                op = w if show_warped else 1 - w
                g = VGroup()
                for a in ages:
                    y = y_of(a, w)
                    c = RED if a == 18 else INK
                    g.add(Line([x_tick - 0.12, y, 0], [x_tick + 0.12, y, 0], stroke_width=1.5, color=c).set_opacity(op))
                    g.add(Text(str(a), font=LATIN, font_size=28, color=c)
                          .move_to([x_tick + 0.25, y, 0], aligned_edge=LEFT).set_opacity(op))
                return g
            return always_redraw(f)
        lin = ticks([4, 10, 20, 30, 40, 50, 60, 70, 80], False)
        log = ticks([4, 5, 6, 8, 10, 14, 18, 30, 50, 80], True)
        spine = Line([x_tick, TOP, 0], [x_tick, TOP - HGT, 0], stroke_width=1, color=SUB)
        self.play(Create(spine), FadeIn(lin), run_time=0.8)
        self.add(log)
        self.sub("按日历，每一年一样长。", "By the calendar, every year is the same length.", hold=1.0)
        self.sub("可如果按「感觉」重新丈量——", "But if we measure by feeling instead—", t2c={"感觉": RED}, hold=0.2)
        self.mark("whoosh")
        self.play(warp.animate.set_value(1), run_time=3.0, rate_func=smooth)
        self.sub("小时候的年被拉长，长大后的年被压扁。", "childhood years stretch, and adult years shrink.", hold=1.4)

        mid = TOP - HGT / 2
        scan = ValueTracker(TOP)
        line = always_redraw(lambda: DashedLine([X - WID / 2 - 0.3, scan.get_value(), 0], [x_tick + 0.15, scan.get_value(), 0],
                                                stroke_width=2, color=RED, dash_length=0.1))
        self.add(line)
        self.play(scan.animate.set_value(mid), run_time=1.6, rate_func=smooth)
        line.clear_updaters()
        lin.clear_updaters()
        log.clear_updaters()
        stamp = seal("十八", 1.35).move_to([x_tick + 1.55, mid - 1.1, 0])
        self.mark("pop")
        self.play(FadeIn(stamp, scale=1.6), run_time=0.35, rate_func=rush_into)
        self.sub("正中间，是 18 岁。", "The exact middle is eighteen.", t2c={"18": RED}, hold=1.2)

        def bracket(y1, y2, x, col):
            return VGroup(Line([x, y1, 0], [x, y2, 0], stroke_width=1.6, color=col),
                          Line([x, y1, 0], [x + 0.14, y1, 0], stroke_width=1.6, color=col),
                          Line([x, y2, 0], [x + 0.14, y2, 0], stroke_width=1.6, color=col))
        bx = X - WID / 2 - 0.55
        b1, b2 = bracket(TOP, mid + 0.06, bx, RED), bracket(mid - 0.06, TOP - HGT, bx, INK)
        t1 = VGroup(Text("14", font=LATIN, font_size=40, color=RED), zh("年", 22, RED)).arrange(DOWN, buff=0.05).next_to(b1, LEFT, buff=0.08)
        t2 = VGroup(Text("62", font=LATIN, font_size=40, color=INK), zh("年", 22, INK)).arrange(DOWN, buff=0.05).next_to(b2, LEFT, buff=0.08)
        self.mark("tick")
        self.play(Create(b1), FadeIn(t1), run_time=0.5)
        self.mark("tick")
        self.play(Create(b2), FadeIn(t2), run_time=0.5)
        self.sub("前面的 14 年，和后面的 62 年，感觉一样长。",
                 "The first fourteen years feel as long as the sixty-two that follow.",
                 t2c={"14": RED}, size=38, hold=2.4)
        self.mark("whoosh")
        self.clear_layer(body, top_rod, bot_rod, spine, lin, log, line, stamp, b1, b2, t1, t2, self.kick, self.subtitle)

    # 4. 翻倍规律
    def s4_doubling(self):
        self.kicker("为什么是 18", "翻倍的规律")
        rows = [(5, 10), (10, 20), (20, 40), (40, 80)]
        L, Wf = -3.2, 5.0
        group = VGroup()
        self.sub("规律是：年龄每翻一倍，感觉上走过的路一样长。",
                 "The rule: each time your age doubles, the felt distance is the same.", size=36, hold=0)
        for i, (a, b) in enumerate(rows):
            y = 4.2 - i * 1.75
            label = Text(f"{a}–{b} 岁", font=SERIF, font_size=32, color=INK).move_to([L, y + 0.45, 0], aligned_edge=LEFT)
            felt = brush([[L, y, 0], [L + Wf * 0.5, y + 0.04, 0], [L + Wf, y - 0.02, 0]], 0.26, 0.1, INK, 0.88)
            real_w = 6.4 * (b - a) / 40
            real = Line([L, y - 0.42, 0], [L + real_w, y - 0.42, 0], stroke_width=4, color=RED)
            rl = zh(f"日历上 {b - a} 年", 20, RED).next_to(real, RIGHT, buff=0.15)
            if i == 3:
                rl.next_to(real, DOWN, buff=0.12, aligned_edge=RIGHT)
            self.mark("tick")
            self.play(FadeIn(label), GrowFromEdge(felt, LEFT), run_time=0.45)
            self.play(Create(real), FadeIn(rl), run_time=0.45)
            group.add(label, felt, real, rl)
        self.wait(1.4)
        self.sub("黑色是感觉上的长度，一样长；红色是日历上的年数，越来越长。",
                 "Black: felt length, always equal. Red: calendar years, ever longer.", size=34, hold=2.2)
        self.play(group.animate.set_opacity(0.07), run_time=0.6)
        f = Text("√(4 × 80) ≈ 17.9", font=LATIN, font_size=96, color=INK)
        f.scale_to_fit_width(7.4).move_to([0, 1.0, 0])
        f[-4:].set_color(RED)
        self.mark("pop")
        self.play(FadeIn(f, shift=UP * 0.2), run_time=0.8)
        self.sub("所以从 4 岁到 80 岁，中点是两端相乘再开方：约 18 岁。",
                 "So from four to eighty, the midpoint is the geometric mean: about eighteen.", size=34, hold=2.4)
        self.mark("whoosh")
        self.clear_layer(group, f, self.kick, self.subtitle)

    # 5. 把一生折成一天
    def s5_day(self):
        self.set_bg("sky_dawn.png", run_time=1.0, drift=0.006)
        sun = img("sun_glow.png").scale_to_fit_height(6.0)
        hour = ValueTracker(6.0)

        def sun_pos(h):
            u = min(max((h - 6) / 14, 0), 1)  # 6 点日出，20 点日落
            return [-3.6 + 7.2 * u, -3.4 + 5.6 * math.sin(PI * u), 0]
        sun.move_to(sun_pos(6))
        sun.add_updater(lambda m: m.move_to(sun_pos(hour.get_value())))
        shade = self.scrim()
        self.add(sun, shade)

        def hhmm(h):
            m = int(round(h * 60)) % (24 * 60)
            return f"{m // 60:02d}:{m % 60:02d}"
        clock_txt = always_redraw(lambda: Text(hhmm(hour.get_value()), font=LATIN, font_size=130, color=IVORY)
                                  .move_to([0, 4.3, 0]))
        self.sub("把感觉中的一生，折成一天。", "Fold your felt lifetime into a single day.", dark=True, hold=0.6)
        self.play(FadeIn(clock_txt), run_time=0.6)

        stops = [(18, "sky_noon.png", "18 岁，正午。", "Eighteen: high noon."),
                 (30, "sky_afternoon.png", "30 岁，下午四点。", "Thirty: four in the afternoon."),
                 (40, "sky_sunset.png", "40 岁，太阳已经西斜。", "Forty: the sun is already low."),
                 (60, "sky_dusk.png", "60 岁，天快黑了。", "Sixty: night is falling.")]
        for age, sky_name, z, e in stops:
            h = 24 * felt_frac(age)
            self.mark("whoosh")
            self._swap(sky_name, 1.6, 0.006, extra=[hour.animate.set_value(h)])
            self.bring_to_front(sun, shade, clock_txt)
            if self.kick is not None:
                self.bring_to_front(self.kick)
            if self.subtitle is not None:
                self.bring_to_front(self.subtitle)
            self.kicker(f"{age} 岁", f"感觉上的一天 · {hhmm(h)}", dark=True)
            self.mark("tick")
            self.sub(z, e, dark=True, hold=1.0)
        self.sub("……是不是有点慌？", "…feeling a little anxious?", dark=True, hold=1.0)
        self.mark("stop")
        self.clear_layer(sun, shade, clock_txt, self.kick, self.subtitle)

    # 6. 反转：每个第一次，开一朵梅花
    def s6_blossom(self):
        self.set_bg("paper.png", run_time=0.8, drift=0.004)
        calm = zh("别慌。", 120, INK, BOLD).move_to([0, 2.0, 0])
        self.mark("hit")
        self.play(FadeIn(calm, shift=UP * 0.2), run_time=0.6)
        self.sub("这只是一个假说，不是定律。", "It's only a hypothesis, not a law.", hold=1.0)
        self.sub("另一种解释是：时间变快，是因为新鲜事变少了。",
                 "Another explanation: time speeds up because fewer things are new.", t2c={"新鲜事": RED}, size=38, hold=0.6)
        self.mark("beat_in")
        self.play(FadeOut(calm), run_time=0.5)
        self.kicker("一根梅枝", "记忆的样子")

        trunk_pts = [[-4.2, -3.6, 0], [-2.8, -2.9, 0], [-1.6, -1.8, 0], [-0.3, -1.1, 0], [0.9, 0.2, 0], [2.0, 1.2, 0],
                     [3.0, 2.6, 0], [3.6, 4.2, 0]]
        segs = VGroup()
        for i in range(len(trunk_pts) - 1):
            w0 = 0.34 - 0.04 * i
            segs.add(brush([trunk_pts[i], trunk_pts[i + 1]], w0, w0 - 0.04))
        twigs = [(1, [-2.2, -1.0, 0]), (3, [-0.9, 0.6, 0]), (4, [0.2, 1.8, 0]), (5, [2.9, 0.4, 0]), (6, [2.0, 3.6, 0])]
        twig_m = VGroup(*[brush([trunk_pts[i], (np.array(trunk_pts[i]) + np.array(p)) / 2 + np.array([0.1, 0.05, 0]), p],
                                0.1, 0.03) for i, p in twigs])
        bare = zh("重复的日子", 26, SUB).move_to([-3.0, -4.3, 0])
        self.play(LaggedStart(*[FadeIn(s, scale=0.9) for s in segs], lag_ratio=0.35), run_time=2.0)
        self.play(FadeIn(bare), run_time=0.4)
        self.sub("重复的日子，在记忆里只剩一段光秃秃的枝。", "Repeated days leave only a bare branch in memory.",
                 size=38, hold=0.8)
        self.play(LaggedStart(*[FadeIn(t) for t in twig_m], lag_ratio=0.2), run_time=1.0)

        firsts = [([-2.2, -1.0, 0], "第一次远行"), ([-0.9, 0.6, 0], "第一次登台"), ([0.2, 1.8, 0], "第一次学会一门手艺"),
                  ([2.9, 0.4, 0], "第一次看极光"), ([2.0, 3.6, 0], "第一次……"), ([3.6, 4.2, 0], "")]
        flowers = VGroup()
        petals = Particles("petal", 18, seed=8)
        self.add(petals)
        self.sub("而每一个「第一次」，都会开出一朵花。", "But every first time blooms into a flower.",
                 t2c={"第一次": RED}, hold=0)
        for p, label in firsts:
            fl = blossom(0.24).move_to(p)
            items = [GrowFromCenter(fl)]
            if label:
                lb = zh(label, 24, RED).next_to(fl, DOWN if label == "第一次看极光" else LEFT, buff=0.15)
                items.append(FadeIn(lb))
                flowers.add(lb)
            flowers.add(fl)
            self.mark("pop")
            self.play(*items, run_time=0.55)
        self.wait(0.8)
        self.sub("花开得越多，回头看，时光就越长。", "The more it blossoms, the longer life feels looking back.",
                 hold=2.4)
        self.mark("whoosh")
        self.clear_layer(segs, twig_m, bare, flowers, petals, self.kick, self.subtitle)

    # 7. 结尾
    def s7_ending(self):
        self.set_bg("ink_landscape.png", run_time=1.2)
        dust = Particles("dust", 40, seed=3)
        self.add(dust)
        self.sub("你感觉中的人生中点，也许还远没到。", "Perhaps the midpoint you feel hasn't come yet.", hold=2.0)
        self.sub("多做一些「第一次」。", "Do more things for the first time.", t2c={"第一次": RED}, hold=2.0)
        self.mark("outro")
        self.drop_sub()
        end = VGroup(zh("知识短片 · 02", 30, SUB), seal("中点", 0.6)).arrange(RIGHT, buff=0.3).move_to([0, -5.6, 0])
        self.play(FadeIn(end), run_time=0.8)
        self.wait(1.8)
        self.clear_layer(dust)
