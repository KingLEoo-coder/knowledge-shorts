"""人生的中点是 18 岁：竖屏 1080x1920 短视频（画面部分）。

渲染：manim -qh --disable_caching life_midpoint.py LifeMidpoint
  STYLE=A|B|C 切换风格（A 纸本杂志，默认；B 暗夜极简；C 文艺手账）
  PREVIEW=1   半分辨率 15fps 快速预览
渲染时把关键节拍的时间写进 marks.json，music.py 读它来对齐配乐和音效。
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
if os.environ.get("PREVIEW"):
    config.pixel_width, config.pixel_height, config.frame_rate = 540, 960, 15

THEMES = {
    "A": dict(  # 纸本杂志：米白纸面 + 朱红
        bg="#F2EDE3", ink="#1C1A17", sub="#8A8378", hair="#CFC6B6", tint="#E4DCCD",
        accent="#C8432B", accent2="#2F4B5C",
        head=("Noto Serif CJK SC", SEMIBOLD), body=("Noto Serif CJK SC", NORMAL),
        label=("Noto Sans CJK SC", NORMAL), num=("Noto Serif Display", NORMAL), grain=("#000000", 0.05),
    ),
    "B": dict(  # 暗夜极简：近黑 + 暖金
        bg="#0E0E10", ink="#EDEAE4", sub="#7A7770", hair="#34333A", tint="#1C1C20",
        accent="#D9A65A", accent2="#7FA6B8",
        head=("Noto Serif CJK SC", MEDIUM), body=("Noto Serif CJK SC", NORMAL),
        label=("Noto Sans CJK SC", NORMAL), num=("Inter Display", LIGHT), grain=("#FFFFFF", 0.04),
    ),
    "C": dict(  # 文艺手账：奶油底 + 赭红
        bg="#EFE6D8", ink="#3B332B", sub="#9A8C7B", hair="#D6C9B5", tint="#E3D7C4",
        accent="#C66B4E", accent2="#6F9478",
        head=("LXGW WenKai", BOLD), body=("LXGW WenKai", NORMAL),
        label=("LXGW WenKai", NORMAL), num=("LXGW WenKai", BOLD), grain=("#5a4630", 0.05),
    ),
}
TH = THEMES[os.environ.get("STYLE", "A")]
config.background_color = TH["bg"]

TOTAL = 104.3  # 成片时长（秒），给顶部进度线用；渲染后按 marks.json 的 end 校准
LX = -3.7      # 版心左边线
RX = 3.7
CAP_Y = -5.3
LOG20 = math.log(20)
INK, SUB, HAIR, TINT, ACC, ACC2 = TH["ink"], TH["sub"], TH["hair"], TH["tint"], TH["accent"], TH["accent2"]


def T(s, size=46, color=None, role="body", **kw):
    font, weight = TH[role]
    return Text(s, font=font, weight=weight, font_size=size, color=color or INK, **kw)


def H(s, size=64, color=None):
    return T(s, size, color, "head")


def N(s, size=60, color=None):
    return T(s, size, color, "num")


def Lb(s, size=28, color=None):
    return T(s, size, color or SUB, "label")


def left(m, y):
    return m.move_to([LX, y, 0], aligned_edge=LEFT)


def fit(m, w=7.4):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def felt_frac(age):
    """从 4 岁算起，到 age 岁时走过了“感觉上”的多少（对数比例）。"""
    return math.log(age / 4) / LOG20


def year_fill(a):
    """18 岁以前用强调色，之后墨色由浅到深。"""
    if a < 18:
        return ACC, 0.92
    return INK, 0.12 + 0.6 * (a - 18) / 62


class Clock(Mobject):
    def __init__(self):
        super().__init__()
        self.t = 0.0
        self.add_updater(lambda m, dt: setattr(m, "t", m.t + dt))


class LifeMidpoint(Scene):
    # ---------- 公共元素 ----------
    def mark(self, name, **kw):
        self.marks.append({"name": name, "t": round(self.renderer.time, 3), **kw})

    def setup_page(self):
        rng = random.Random(3)
        col, op = TH["grain"]
        grain = VGroup(*[Dot([rng.uniform(-4.5, 4.5), rng.uniform(-8, 8), 0], radius=rng.uniform(0.004, 0.012),
                             color=col).set_opacity(rng.uniform(0.2, 1) * op * 6) for _ in range(1400)])
        clock = self.clock
        track = Line([LX, 7.55, 0], [RX, 7.55, 0], stroke_width=1.2, color=HAIR)
        bar = always_redraw(lambda: Line(
            [LX, 7.55, 0], [LX + max(0.001, (RX - LX) * min(clock.t / TOTAL, 1)), 7.55, 0],
            stroke_width=2.4, color=ACC))
        self.add(grain, track, bar)
        self.kicker = None

    def set_chapter(self, idx, name):
        a = Lb(idx, 28, ACC)
        b = Lb(name, 28, SUB)
        row = VGroup(a, b).arrange(RIGHT, buff=0.25)
        left(row, 6.85)
        rule = Line([LX, 6.5, 0], [RX, 6.5, 0], stroke_width=1.2, color=HAIR)
        g = VGroup(row, rule)
        if self.kicker is None:
            self.play(FadeIn(row, shift=RIGHT * 0.2), Create(rule), run_time=0.6)
        else:
            self.play(FadeOut(self.kicker[0], shift=UP * 0.2), FadeIn(row, shift=UP * 0.2), run_time=0.5)
            self.remove(self.kicker[1])
            self.add(rule)
        self.kicker = g

    def cap(self, text, t2c=None, hold=None, size=46):
        lines = text.split("\n")
        g = VGroup(*[T(l, size) for l in lines]).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        if t2c:
            for l in g:
                l.set_color_by_t2c(t2c)
        fit(g)
        g.move_to([LX, CAP_Y, 0], aligned_edge=LEFT)
        anims = [FadeIn(g, shift=UP * 0.15)]
        if self.caption is not None:
            anims.append(FadeOut(self.caption, shift=UP * 0.15))
        self.play(*anims, run_time=0.5)
        self.caption = g
        if hold:
            self.wait(hold)
        return g

    def drop_cap(self):
        if self.caption is not None:
            self.play(FadeOut(self.caption), run_time=0.35)
            self.caption = None

    # ---------- 正片 ----------
    def construct(self):
        self.marks = []
        self.caption = None
        self.clock = Clock()
        self.add(self.clock)
        self.setup_page()

        self.scene_hook()
        self.scene_calendar()
        self.scene_ratio()
        self.scene_ruler()
        self.scene_doubling()
        self.scene_progress()
        self.scene_twist()

        self.mark("end")
        with open("marks.json", "w") as f:
            json.dump(self.marks, f, ensure_ascii=False, indent=1)

    # 1. 钩子：80 岁的人生，中点在哪？
    def scene_hook(self):
        self.mark("intro")
        self.set_chapter("00", "人生的中点")
        l1 = H("假设你能活到 80 岁", 64)
        left(l1, 5.3)
        self.play(FadeIn(l1, shift=UP * 0.2), run_time=0.8)
        self.mark("pop")

        Y = -0.6
        warp = ValueTracker(0)

        def x_of(age, w):
            lin = age / 80
            lg = 0 if age <= 4 else felt_frac(age)
            return LX + (RX - LX) * ((1 - w) * lin + w * lg)

        axis = Line([LX, Y, 0], [RX, Y, 0], stroke_width=1.6, color=INK)

        def ticks():
            w = warp.get_value()
            g = VGroup()
            for a in range(0, 81):
                x = x_of(a, w)
                big = a % 20 == 0
                g.add(Line([x, Y, 0], [x, Y + (0.32 if big else 0.14), 0], stroke_width=1.2,
                           color=ACC if (w > 0.5 and a <= 18) else INK))
            for a in (0, 20, 40, 60, 80):
                g.add(N(str(a), 36, SUB).move_to([x_of(a, w), Y - 0.45, 0]))
            return g
        tk = always_redraw(ticks)
        self.play(Create(axis), FadeIn(tk), run_time=1.2)
        self.mark("sweep")

        self.cap("人生的「中点」在哪里？", {"中点": ACC})
        mid_x = (LX + RX) / 2
        pin = Line([mid_x, Y + 0.05, 0], [mid_x, Y + 1.5, 0], stroke_width=2, color=INK)
        val = ValueTracker(40)
        reading = always_redraw(lambda: VGroup(
            N(f"{round(val.get_value())}", 96, ACC if val.get_value() < 39 else INK),
            T("岁", 40, SUB)).arrange(RIGHT, buff=0.12, aligned_edge=DOWN).next_to(pin, UP, buff=0.2))
        self.mark("tick")
        self.play(Create(pin), FadeIn(reading, shift=DOWN * 0.2), run_time=0.6)
        self.cap("按日历算，是 40 岁", hold=1.0)
        self.cap("可如果按「感觉」来算——", {"感觉": ACC}, hold=0.4)
        self.mark("riser", dur=2.0)
        self.play(warp.animate.set_value(1), val.animate.set_value(18), run_time=2.0, rate_func=smooth)
        pin.set_color(ACC)
        self.mark("hit")

        # 揭晓：大号 18
        l2 = H("感觉上的人生中点，在", 64)
        fit(l2)
        left(l2, 4.25)
        big = N("18", 400, ACC)
        big.next_to(l2, DOWN, buff=0.1, aligned_edge=LEFT).shift(LEFT * 0.12)
        sui = H("岁", 90).next_to(big, RIGHT, buff=0.25, aligned_edge=DOWN).shift(UP * 0.35)
        line_grp = VGroup(axis, tk, pin, reading)
        tk.clear_updaters()
        reading.clear_updaters()
        self.play(line_grp.animate.shift(DOWN * 2.4), FadeIn(l2, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(big, shift=UP * 0.3), FadeIn(sui), run_time=0.7)
        Y2 = Y - 2.4 + 0.75
        mx = LX + (RX - LX) / 2
        half = Line([LX, Y2, 0], [mx, Y2, 0], stroke_width=4, color=ACC)
        half2 = Line([mx, Y2, 0], [RX, Y2, 0], stroke_width=4, color=HAIR)
        h1 = Lb("前 14 年", 28, ACC).next_to(half, UP, buff=0.15)
        h2 = Lb("后 62 年", 28, SUB).next_to(half2, UP, buff=0.15)
        self.play(FadeOut(VGroup(pin, reading)), Create(half), Create(half2), FadeIn(h1), FadeIn(h2), run_time=0.8)
        self.cap("前 14 年，和后 62 年，感觉一样长", {"一样长": ACC}, hold=1.6)
        self.cap("这不是玄学，是一个关于「比例」的错觉", {"比例": ACC}, hold=1.4)
        self.mark("whoosh")
        self.play(FadeOut(VGroup(l1, l2, big, sui, axis, tk, half, half2, h1, h2, self.caption), shift=UP * 0.4),
                  run_time=0.7)
        self.caption = None

    # 2. 为什么越长大，一年过得越快
    def scene_calendar(self):
        self.mark("beat_in")
        self.set_chapter("01", "为什么越活越快")
        title = H("同样是一年", 64)
        left(title, 5.3)
        self.play(FadeIn(title, shift=UP * 0.2), run_time=0.6)

        def months(y):
            cells = VGroup(*[Square(0.52, stroke_width=1.4, stroke_color=HAIR) for _ in range(12)])
            cells.arrange_in_grid(rows=2, cols=6, buff=0.1)
            cells.move_to([RX, y, 0], aligned_edge=RIGHT)
            return cells

        kid_age = VGroup(N("5", 150, ACC), T("岁", 40, SUB)).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        ad_age = VGroup(N("40", 150, ACC2), T("岁", 40, SUB)).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        left(kid_age, 2.6)
        left(ad_age, -0.9)
        kid_m = months(2.45)
        ad_m = months(-1.05)
        rule = Line([LX, 0.85, 0], [RX, 0.85, 0], stroke_width=1, color=HAIR)
        self.play(FadeIn(kid_age, shift=UP * 0.2), FadeIn(kid_m), run_time=0.6)
        self.play(Create(rule), FadeIn(ad_age, shift=UP * 0.2), FadeIn(ad_m), run_time=0.6)
        self.cap("把一年里过去的月份，一格一格涂满", hold=0.2)

        def fill(cells, n, col, each):
            return Succession(*[cells[i].animate(run_time=each, rate_func=rush_from).set_fill(col, 0.9)
                                .set_stroke(col) for i in range(n)])

        # 同样 3 秒：5 岁只走了 3 格（感觉慢），40 岁走完 12 格（感觉快）
        self.mark("ticks", n=12, dur=3.0)
        self.mark("ticks_slow", n=3, dur=3.0)
        self.play(AnimationGroup(fill(kid_m, 3, ACC, 1.0), fill(ad_m, 12, ACC2, 0.25)), run_time=3.0)
        lab1 = T("一个暑假，长得像永远", 34, ACC)
        lab2 = T("一年，一眨眼就没了", 34, ACC2)
        lab1.next_to(kid_m, DOWN, buff=0.3, aligned_edge=RIGHT)
        lab2.next_to(ad_m, DOWN, buff=0.3, aligned_edge=RIGHT)
        self.play(FadeIn(lab1, shift=UP * 0.15), run_time=0.4)
        self.play(FadeIn(lab2, shift=UP * 0.15), run_time=0.4)
        self.cap("同样 365 天，为什么感觉差这么多？", hold=1.6)
        self.play(FadeOut(VGroup(title, kid_age, ad_age, kid_m, ad_m, rule, lab1, lab2), shift=UP * 0.4),
                  run_time=0.6)

    # 3. 比例理论：1 年占人生的比例
    def scene_ratio(self):
        self.set_chapter("02", "关键是比例")
        who = Lb("1877 年 · 法国哲学家 保罗·让内", 30, SUB)
        left(who, 5.6)
        q1 = H("一段时间感觉有多长，", 60)
        q2 = H("取决于它占你人生的比例。", 60)
        quote = VGroup(q1, q2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit(quote)
        quote.move_to([LX, 4.3, 0], aligned_edge=LEFT)
        q2.set_color_by_t2c({"比例": ACC})
        self.play(FadeIn(who), run_time=0.4)
        self.play(FadeIn(q1, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(q2, shift=UP * 0.15), run_time=0.7)
        self.wait(0.6)

        def pie(n, r, center):
            g = VGroup()
            for i in range(n):
                s = AnnularSector(inner_radius=0, outer_radius=r, angle=TAU / n, start_angle=PI / 2 + i * TAU / n,
                                  stroke_color=TH["bg"], stroke_width=2 if n < 20 else 0.8)
                s.set_fill(ACC if i == 0 else TINT, 1)
                g.add(s)
            ring = Circle(radius=r, stroke_color=HAIR, stroke_width=1.2).move_to(ORIGIN)
            return VGroup(g, ring).move_to(center)

        p5 = pie(5, 1.5, [-1.95, 0.0, 0])
        p50 = pie(50, 1.5, [1.95, 0.0, 0])
        h5 = VGroup(N("5", 64), T("岁", 30, SUB)).arrange(RIGHT, buff=0.08, aligned_edge=DOWN).next_to(p5, UP, buff=0.3)
        h50 = VGroup(N("50", 64), T("岁", 30, SUB)).arrange(RIGHT, buff=0.08, aligned_edge=DOWN).next_to(p50, UP, buff=0.3)
        f5 = VGroup(T("1 年 =", 34, SUB), N("1/5", 54, ACC)).arrange(RIGHT, buff=0.15).next_to(p5, DOWN, buff=0.35)
        f50 = VGroup(T("1 年 =", 34, SUB), N("1/50", 54, ACC)).arrange(RIGHT, buff=0.15).next_to(p50, DOWN, buff=0.35)
        self.mark("tick")
        self.play(FadeIn(h5), FadeIn(p5[1]), LaggedStart(*[GrowFromCenter(s) for s in p5[0]], lag_ratio=0.15),
                  run_time=0.9)
        s0 = p5[0][0]
        self.play(s0.animate.shift(0.2 * normalize(s0.get_center() - p5.get_center())), FadeIn(f5, shift=UP * 0.15),
                  run_time=0.5)
        self.cap("5 岁时，1 年是你人生的 20%", {"20%": ACC}, hold=0.6)
        self.mark("tick")
        self.play(FadeIn(h50), FadeIn(p50[1]), LaggedStart(*[GrowFromCenter(s) for s in p50[0]], lag_ratio=0.03),
                  run_time=1.0)
        s0 = p50[0][0]
        self.play(s0.animate.shift(0.3 * normalize(s0.get_center() - p50.get_center())),
                  FadeIn(f50, shift=UP * 0.15), run_time=0.5)
        self.cap("50 岁时，1 年只占 2%", {"2%": ACC}, hold=1.2)

        # 1 段强调色 ≈ 10 段墨色
        self.play(FadeOut(VGroup(who, quote), shift=UP * 0.4),
                  VGroup(p5, p50, h5, h50, f5, f50).animate.scale(0.8).shift(UP * 3.0), run_time=0.7)
        big = Rectangle(width=RX - LX, height=0.7, stroke_width=0).set_fill(ACC, 0.92)
        left(big, -0.6)
        big_l = Lb("5 岁时的 1 年", 28, ACC).next_to(big, UP, buff=0.15, aligned_edge=LEFT)
        smalls = VGroup(*[Rectangle(width=(RX - LX - 0.9) / 10, height=0.7, stroke_width=0).set_fill(ACC2, 0.85)
                          for _ in range(10)]).arrange(RIGHT, buff=0.1)
        left(smalls, -2.3)
        sm_l = Lb("50 岁时的 10 年", 28, ACC2).next_to(smalls, UP, buff=0.15, aligned_edge=LEFT)
        self.play(GrowFromEdge(big, LEFT), FadeIn(big_l), run_time=0.7)
        self.mark("ticks", n=10, dur=1.0)
        self.play(FadeIn(sm_l), LaggedStart(*[GrowFromEdge(s, LEFT) for s in smalls], lag_ratio=0.12), run_time=1.0)
        self.cap("感觉上，5 岁的 1 年 ≈ 50 岁的 10 年", {"1 年": ACC, "10 年": ACC2}, hold=1.8)
        self.mark("whoosh")
        self.play(FadeOut(VGroup(p5, p50, h5, h50, f5, f50, big, big_l, smalls, sm_l), shift=UP * 0.4), run_time=0.6)

    # 4. 按“感觉”重画人生尺子，找到中点
    def scene_ruler(self):
        self.set_chapter("03", "重画一把人生尺子")

        # 0-3 岁：几乎没有记忆
        baby = VGroup(*[Rectangle(width=2.2, height=0.62, stroke_width=1.2, stroke_color=HAIR).set_fill(TINT, 1)
                        for _ in range(4)]).arrange(DOWN, buff=0.1)
        baby_l = VGroup(*[VGroup(N(str(i), 44, SUB), T("岁", 26, SUB)).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)
                          .next_to(baby[i], RIGHT, buff=0.3) for i in range(4)])
        bg = VGroup(baby, baby_l).move_to([-1.0, 1.4, 0])
        self.play(FadeIn(bg, shift=UP * 0.2), run_time=0.6)
        self.cap("0～3 岁的事，我们几乎都记不住", hold=1.0)
        strike = Line(baby.get_corner(DL) + LEFT * 0.2, baby.get_corner(UR) + RIGHT * 0.2, stroke_width=3, color=ACC)
        self.mark("tick")
        self.play(Create(strike), run_time=0.4)
        self.cap("所以从 4 岁算起，到 80 岁", hold=0.4)
        self.play(FadeOut(VGroup(bg, strike), shift=UP * 0.4), run_time=0.5)

        TOP, HH, X0, W = 4.55, 9.0, -1.6, 1.25
        BOT = TOP - HH
        warp = ValueTracker(0)

        def y_of(age, w):
            return TOP - HH * ((1 - w) * (age - 4) / 76 + w * felt_frac(age))

        def build():
            w = warp.get_value()
            g = VGroup()
            for a in range(4, 80):
                y1, y2 = y_of(a, w), y_of(a + 1, w)
                col, op = year_fill(a)
                r = Rectangle(width=W, height=max(y1 - y2, 0.001), stroke_width=0.8 if y1 - y2 > 0.05 else 0,
                              stroke_color=TH["bg"])
                r.set_fill(col, op).move_to([X0, (y1 + y2) / 2, 0])
                g.add(r)
            return g

        ruler = always_redraw(build)

        def labels(ages, show_when_warped):
            def f():
                w = warp.get_value()
                op = w if show_when_warped else 1 - w
                g = VGroup()
                for a in ages:
                    y = y_of(a, w)
                    g.add(Line([X0 + W / 2, y, 0], [X0 + W / 2 + 0.18, y, 0], stroke_width=1.2, color=SUB)
                          .set_opacity(op))
                    g.add(N(str(a), 32, SUB).move_to([X0 + W / 2 + 0.3, y, 0], aligned_edge=LEFT).set_opacity(op))
                return g
            return always_redraw(f)

        lab_lin = labels([4, 10, 20, 30, 40, 50, 60, 70, 80], False)
        lab_log = labels([4, 5, 6, 8, 10, 14, 18, 30, 50, 80], True)
        title = H("日历上的 76 年：每年一样长", 52)
        fit(title)
        left(title, 5.5)
        self.play(FadeIn(title, shift=UP * 0.15), Create(ruler), FadeIn(lab_lin), run_time=1.2)
        self.add(lab_log)
        self.cap("每一格是一年，日历上每格一样大", hold=0.6)

        title2 = H("感觉上的 76 年：按比例缩放", 52, ACC)
        fit(title2)
        left(title2, 5.5)
        self.cap("现在，把每一年按「它占人生的比例」缩放", {"比例": ACC}, hold=0.2)
        self.mark("riser", dur=3.0)
        self.play(warp.animate.set_value(1), FadeOut(title, shift=UP * 0.15), FadeIn(title2, shift=UP * 0.15),
                  run_time=3.0, rate_func=smooth)
        self.mark("hit_soft")
        self.cap("小时候的每一年被拉长\n长大后的每一年被压扁", {"拉长": ACC, "压扁": ACC2}, hold=1.4)

        # 中点扫描线
        self.cap("这把尺子的正中间，是几岁？", {"正中间": ACC})
        scan = ValueTracker(0.12)
        line = always_redraw(lambda: DashedLine([X0 - W / 2 - 0.25, TOP - HH * scan.get_value(), 0],
                                                [RX, TOP - HH * scan.get_value(), 0],
                                                stroke_width=1.6, color=ACC, dash_length=0.08))
        reading = always_redraw(lambda: N(f"{4 * 20 ** scan.get_value():.1f}", 150, ACC)
                                .move_to([RX, TOP - HH * scan.get_value() + 0.8, 0], aligned_edge=RIGHT))
        self.play(FadeIn(line), FadeIn(reading), run_time=0.3)
        self.mark("scan", dur=1.8)
        self.play(scan.animate.set_value(0.5), run_time=1.8, rate_func=smooth)
        self.mark("hit")
        line.clear_updaters()
        reading.clear_updaters()
        mid_y = TOP - HH / 2
        tag = Lb("正中间 ≈ 18 岁", 30, ACC).next_to(reading, DOWN, buff=0.15, aligned_edge=RIGHT)
        self.play(FadeIn(tag, shift=UP * 0.1), run_time=0.5)

        def bracket(y1, y2, x, col):
            return VGroup(Line([x, y1, 0], [x, y2, 0], stroke_width=1.6, color=col),
                          Line([x, y1, 0], [x + 0.15, y1, 0], stroke_width=1.6, color=col),
                          Line([x, y2, 0], [x + 0.15, y2, 0], stroke_width=1.6, color=col))
        bx = X0 - W / 2 - 0.3
        b1 = bracket(TOP, mid_y + 0.06, bx, ACC)
        b2 = bracket(mid_y - 0.06, BOT, bx, INK)
        t1 = VGroup(N("14", 54, ACC), T("年", 26, ACC)).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)
        t2 = VGroup(N("62", 54, INK), T("年", 26, INK)).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)
        t1.next_to(b1, LEFT, buff=0.12)
        t2.next_to(b2, LEFT, buff=0.12)
        self.mark("tick")
        self.play(Create(b1), FadeIn(t1, shift=RIGHT * 0.15), run_time=0.5)
        self.mark("tick")
        self.play(Create(b2), FadeIn(t2, shift=RIGHT * 0.15), run_time=0.5)
        self.cap("前面的 14 年，和后面的 62 年\n感觉上一样长", {"14 年": ACC, "62 年": INK})
        self.wait(2.0)
        self.mark("whoosh")
        ruler.clear_updaters()
        lab_lin.clear_updaters()
        lab_log.clear_updaters()
        self.play(FadeOut(VGroup(ruler, lab_lin, lab_log, title2, line, reading, tag, b1, b2, t1, t2), shift=UP * 0.4),
                  run_time=0.6)

    # 5. 为什么偏偏是 18：翻倍规律
    def scene_doubling(self):
        self.set_chapter("04", "为什么偏偏是 18")
        title = H("年龄每翻一倍，\n感觉上走过的路一样长", 56)
        fit(title)
        title.move_to([LX, 4.9, 0], aligned_edge=LEFT)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=0.7)

        segs = [(5, 10), (10, 20), (20, 40), (40, 80)]
        felt_y, real_y = 2.3, -0.4
        head1 = Lb("感觉上的长度", 28, ACC)
        left(head1, felt_y + 0.8)
        head2 = Lb("日历上的长度", 28, ACC2)
        left(head2, real_y + 0.8)
        felt, real, felt_l, real_l, links = VGroup(), VGroup(), VGroup(), VGroup(), VGroup()
        fw = (RX - LX) / 4
        x = LX
        for i, (a, b) in enumerate(segs):
            r = Rectangle(width=fw - 0.08, height=0.62, stroke_width=0).set_fill(ACC, 0.35 + 0.19 * i)
            r.move_to([LX + fw * (i + 0.5), felt_y, 0])
            felt.add(r)
            felt_l.add(N(f"{a}–{b}", 32, TH["bg"] if i >= 2 else INK).move_to(r))
            w = (RX - LX) * (b - a) / 75
            rr = Rectangle(width=max(w - 0.06, 0.08), height=0.62, stroke_width=0).set_fill(ACC2, 0.35 + 0.19 * i)
            rr.move_to([x + w / 2, real_y, 0])
            x += w
            real.add(rr)
            real_l.add(VGroup(N(str(b - a), 34, INK), T("年", 22, SUB)).arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
                       .next_to(rr, DOWN, buff=0.18 if i != 1 else 0.62))
            links.add(Line(r.get_bottom(), rr.get_top(), stroke_width=1, color=HAIR))
        self.play(FadeIn(head1), run_time=0.3)
        for i in range(4):
            self.mark("tick")
            self.play(GrowFromEdge(felt[i], LEFT), FadeIn(felt_l[i]), run_time=0.32)
        self.play(FadeIn(head2), Create(links), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(r, LEFT) for r in real], lag_ratio=0.35),
                  LaggedStart(*[FadeIn(l) for l in real_l], lag_ratio=0.35), run_time=1.4)
        self.cap("5～10 岁的 5 年，和 40～80 岁的 40 年\n感觉上一样长", {"5 年": ACC, "40 年": ACC2}, hold=1.8)
        self.play(FadeOut(VGroup(title, head1, head2, felt, real, felt_l, real_l, links), shift=UP * 0.4), run_time=0.5)

        # 4 ×4.5→ 18 ×4.5→ 80
        nums = VGroup(N("4", 150, INK), N("18", 150, ACC), N("80", 150, INK)).arrange(RIGHT, buff=1.15)
        nums.move_to([0, 2.8, 0])
        arcs = VGroup(*[ArcBetweenPoints(nums[i].get_top() + UP * 0.25 + RIGHT * 0.1,
                                         nums[i + 1].get_top() + UP * 0.25 + LEFT * 0.1, angle=-PI / 2.5,
                                         stroke_width=1.6, color=SUB).add_tip(tip_length=0.15, tip_width=0.12)
                        for i in range(2)])
        mul = VGroup(*[N("×4.5", 40, SUB).next_to(arcs[i], UP, buff=0.08) for i in range(2)])
        self.mark("tick")
        self.play(FadeIn(nums[0], shift=UP * 0.2), run_time=0.4)
        self.play(Create(arcs[0]), FadeIn(mul[0]), run_time=0.5)
        self.mark("pop")
        self.play(FadeIn(nums[1], shift=UP * 0.2), run_time=0.4)
        self.play(Create(arcs[1]), FadeIn(mul[1]), run_time=0.5)
        self.mark("tick")
        self.play(FadeIn(nums[2], shift=UP * 0.2), run_time=0.4)
        self.cap("4 翻 4.5 倍是 18，18 再翻 4.5 倍是 80", {"18": ACC}, hold=0.8)
        rule = Line([LX, 0.4, 0], [RX, 0.4, 0], stroke_width=1, color=HAIR)
        f1 = T("中点", 40, SUB)
        f2 = N("√(4 × 80) ≈ 17.9", 84, INK)
        f2.set_color_by_t2c({"17.9": ACC})
        formula = VGroup(f1, f2).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit(formula)
        left(formula, -1.3)
        self.mark("hit_soft")
        self.play(Create(rule), FadeIn(formula, shift=UP * 0.2), run_time=0.7)
        self.cap("这叫「几何平均数」：两端相乘，再开根号", {"几何平均数": ACC}, hold=1.8)
        self.mark("whoosh")
        self.play(FadeOut(VGroup(nums, arcs, mul, rule, formula), shift=UP * 0.4), run_time=0.5)

    # 6. 你现在走到哪了
    def scene_progress(self):
        self.set_chapter("05", "你走到哪了")
        title = H("「感觉上」的人生进度", 60)
        left(title, 5.3)
        age = ValueTracker(18)
        C = np.array([0, 0.9, 0])
        R = 2.5
        ring_bg = Circle(radius=R, stroke_width=3, color=HAIR).move_to(C)
        ring = always_redraw(lambda: Arc(radius=R, start_angle=PI / 2, angle=-TAU * max(felt_frac(age.get_value()), 1e-3),
                                         arc_center=C, stroke_width=10, color=ACC))
        pct = always_redraw(lambda: VGroup(N(f"{felt_frac(age.get_value()) * 100:.0f}", 190, INK), N("%", 70, SUB))
                            .arrange(RIGHT, buff=0.08, aligned_edge=DOWN).move_to(C + UP * 0.25))
        lbl = always_redraw(lambda: VGroup(N(f"{age.get_value():.0f}", 50, ACC), T("岁", 28, SUB))
                            .arrange(RIGHT, buff=0.06, aligned_edge=DOWN).move_to(C + DOWN * 1.25))
        self.play(FadeIn(title, shift=UP * 0.15), Create(ring_bg), FadeIn(pct), FadeIn(lbl), run_time=0.7)
        self.add(ring)
        self.cap("18 岁：已经走完一半", {"一半": ACC}, hold=0.9)
        for a, text in [(25, "25 岁：约 61%"), (30, "30 岁：约 67%，三分之二"), (40, "40 岁：约 77%")]:
            self.mark("riser", dur=0.9)
            self.play(age.animate.set_value(a), run_time=0.9, rate_func=smooth)
            self.mark("tick")
            self.cap(text, {text.split("：")[1].split("，")[0]: ACC}, hold=0.9)
        self.cap("……是不是有点慌？", hold=1.0)
        ring.clear_updaters()
        pct.clear_updaters()
        lbl.clear_updaters()
        self.mark("stop")
        self.play(FadeOut(VGroup(title, ring_bg, ring, pct, lbl)), run_time=0.5)

    # 7. 反转：时间变快，是因为新鲜事变少了
    def scene_twist(self):
        self.set_chapter("06", "反转")
        calm = H("别慌。", 150)
        left(calm, 3.0)
        self.mark("hit")
        self.play(FadeIn(calm, shift=UP * 0.2), run_time=0.5)
        self.cap("这只是一个假说，不是定律", {"假说": ACC}, hold=1.2)
        self.cap("另一种解释是：\n时间变快，是因为「新鲜事」变少了", {"新鲜事": ACC}, hold=0.6)
        self.mark("beat_in")
        self.play(FadeOut(calm, shift=UP * 0.3), run_time=0.4)

        # 重复的一周：7 个一样的格子被压成 1 格
        h1 = T("重复的一周", 40, SUB)
        left(h1, 5.4)
        days = VGroup(*[Square(0.82, stroke_width=1.4, stroke_color=HAIR).set_fill(TINT, 1) for _ in range(7)])
        days.arrange(RIGHT, buff=0.14)
        left(days, 4.4)
        self.play(FadeIn(h1), LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in days], lag_ratio=0.08), run_time=0.8)
        squashed = Square(0.82, stroke_width=1.4, stroke_color=HAIR).set_fill(TINT, 1)
        left(squashed, 4.4)
        self.mark("tick")
        self.play(ReplacementTransform(days, squashed), run_time=0.8)
        m1 = T("在记忆里只剩一格", 34, SUB).next_to(squashed, RIGHT, buff=0.35)
        self.play(FadeIn(m1), run_time=0.3)

        # 第一次旅行：7 个各不相同的形状铺开
        h2 = T("第一次去旅行的一周", 40, ACC)
        left(h2, 2.6)
        s = 0.42
        shapes = VGroup(
            Circle(radius=s, stroke_width=0).set_fill(ACC, 0.9),
            Square(2 * s * 0.9, stroke_width=0).set_fill(ACC2, 0.9),
            Triangle(stroke_width=0).scale(s * 1.1).set_fill(INK, 0.85),
            Circle(radius=s, stroke_width=2.5, color=ACC),
            Square(2 * s * 0.9, stroke_width=0).rotate(PI / 4).set_fill(ACC, 0.55),
            Annulus(inner_radius=s * 0.45, outer_radius=s, stroke_width=0).set_fill(ACC2, 0.9),
            RegularPolygon(6, stroke_width=0).scale(s).set_fill(INK, 0.5),
        ).arrange(RIGHT, buff=0.18)
        left(shapes, 1.4)
        self.play(FadeIn(h2), run_time=0.3)
        self.mark("ticks", n=7, dur=1.0)
        self.play(LaggedStart(*[GrowFromCenter(x) for x in shapes], lag_ratio=0.15), run_time=1.0)
        m2 = T("在记忆里铺满一大片", 34, ACC).next_to(shapes, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(m2), run_time=0.3)
        self.cap("大脑靠「记住了多少新东西」\n来估计时间有多长", {"新东西": ACC}, hold=2.0)
        self.play(FadeOut(VGroup(h1, squashed, m1, h2, shapes, m2), shift=UP * 0.4), run_time=0.5)

        # 结尾
        self.drop_cap()
        l1 = H("想让时间慢下来？", 64)
        left(l1, 5.3)
        l2 = H("多做一些「第一次」。", 64, ACC)
        fit(l2)
        left(l2, 4.3)
        self.play(FadeIn(l1, shift=UP * 0.15), run_time=0.6)
        self.mark("pop")
        self.play(FadeIn(l2, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)
        big = N("18", 400, ACC)
        left(big, 0.3).shift(LEFT * 0.12)
        self.play(FadeIn(big, shift=UP * 0.2), run_time=0.5)
        q = N("?", 400, INK)
        left(q, 0.3).shift(LEFT * 0.12)
        self.mark("hit")
        self.play(FadeOut(big, shift=UP * 0.3), FadeIn(q, shift=UP * 0.3), run_time=0.7)
        self.cap("你感觉中的人生中点，\n也许还远没到。", {"还远没到": ACC}, hold=2.4, size=52)
        self.mark("outro")
        self.play(FadeOut(VGroup(l1, l2, q, self.caption, self.kicker)), run_time=1.0)
        sign = Lb("知识短片 · 02", 30, SUB)
        sign.move_to(ORIGIN)
        self.play(FadeIn(sign), run_time=0.5)
        self.wait(1.2)
