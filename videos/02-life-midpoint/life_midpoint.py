"""人生的中点是 18 岁：竖屏 1080x1920 短视频（画面部分）。

渲染：manim -qh --disable_caching life_midpoint.py LifeMidpoint
渲染时会把关键节拍的时间写进 marks.json，music.py 读它来对齐配乐和音效。
"""
import json
import os
import math
import random

from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30
config.background_color = "#070a1c"
if os.environ.get("PREVIEW"):  # 快速预览：半分辨率、15fps
    config.pixel_width, config.pixel_height, config.frame_rate = 540, 960, 15

FONT = "Noto Sans CJK SC"
TOTAL = 101.1  # 成片时长（秒），给顶部进度条用；渲染后按 marks.json 的 end 校准

BG_TOP = "#1a1146"
BG_BOT = "#05071a"
AMBER = "#ffb547"   # 童年 / 感觉中的时间
PINK = "#ff4d8d"    # 18 / 重点
CYAN = "#4cc9f0"    # 日历时间
VIOLET = "#9b5de5"
MUTED = "#8b8fb3"
INK = "#f5f3ff"

CAP_Y = -4.9        # 字幕带中心
LOG20 = math.log(20)


def T(s, size=54, color=INK, weight=BOLD, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def glow(mob, color, layers=10, width=36, opacity=0.05):
    """叠几层越来越粗、越来越淡的描边，假装成柔光。"""
    g = VGroup()
    for i in range(1, layers + 1):
        c = mob.copy()
        c.set_fill(opacity=0)
        c.set_stroke(color, width=width * i / layers, opacity=opacity)
        g.add(c)
    return g


def age_color(f):
    """f: 0 (4 岁) → 1 (80 岁)，从琥珀到粉到紫到青。"""
    stops = [AMBER, PINK, VIOLET, CYAN]
    f = min(max(f, 0), 1) * (len(stops) - 1)
    i = min(int(f), len(stops) - 2)
    return interpolate_color(ManimColor(stops[i]), ManimColor(stops[i + 1]), f - i)


def felt_frac(age):
    """从 4 岁算起，到 age 岁时走过了“感觉上”的多少（对数比例）。"""
    return math.log(age / 4) / LOG20


class Clock(Mobject):
    def __init__(self):
        super().__init__()
        self.t = 0.0
        self.add_updater(lambda m, dt: setattr(m, "t", m.t + dt))


class LifeMidpoint(Scene):
    # ---------- 公共元素 ----------
    def mark(self, name, **kw):
        self.marks.append({"name": name, "t": round(self.renderer.time, 3), **kw})

    def setup_backdrop(self):
        bg = Rectangle(width=9.4, height=16.4, stroke_width=0)
        bg.set_fill(color=[BG_BOT, BG_TOP], opacity=1)
        bg.set_sheen_direction(UP)

        # 两团缓慢漂移的极光色块
        blobs = VGroup()
        for col, pos, r in [(VIOLET, UP * 4 + LEFT * 2, 3.2), (CYAN, DOWN * 3 + RIGHT * 2.5, 3.0)]:
            b = VGroup(*[Circle(radius=r * k / 8, stroke_width=0).set_fill(col, 0.035)
                         for k in range(1, 9)]).move_to(pos)
            blobs.add(b)
        clock = self.clock

        def drift(b, phase):
            home = b.get_center().copy()
            b.add_updater(lambda m: m.move_to(home + 0.6 * np.array(
                [math.sin(clock.t * 0.25 + phase), math.cos(clock.t * 0.2 + phase), 0])))
        drift(blobs[0], 0)
        drift(blobs[1], 2.0)

        rng = random.Random(7)
        stars = VGroup()
        for _ in range(90):
            d = Dot(point=[rng.uniform(-4.5, 4.5), rng.uniform(-8, 8), 0],
                    radius=rng.uniform(0.008, 0.028), color=WHITE)
            base, w, ph = rng.uniform(0.2, 0.8), rng.uniform(0.6, 2.2), rng.uniform(0, 6.28)
            d.add_updater(lambda m, base=base, w=w, ph=ph: m.set_opacity(
                base * (0.55 + 0.45 * math.sin(clock.t * w + ph))))
            stars.add(d)
        self.add(bg, blobs, stars)

    def setup_hud(self):
        track = Line(LEFT * 4.1, RIGHT * 4.1, stroke_width=6, color=WHITE).set_opacity(0.12)
        track.move_to(UP * 7.55)
        clock = self.clock
        bar = always_redraw(lambda: Line(
            track.get_left(),
            track.get_left() + RIGHT * max(0.001, 8.2 * min(clock.t / TOTAL, 1)),
            stroke_width=6).set_color([AMBER, PINK]))
        self.add(track, bar)
        self.chapter = None

    def set_chapter(self, idx, name):
        num = T(idx, 30, PINK, HEAVY)
        txt = T(name, 32, INK, BOLD)
        row = VGroup(num, txt).arrange(RIGHT, buff=0.22)
        pill = RoundedRectangle(corner_radius=0.3, width=row.width + 0.7, height=0.62,
                                stroke_color=WHITE, stroke_opacity=0.25, stroke_width=2)
        pill.set_fill(WHITE, 0.07)
        g = VGroup(pill, row).move_to(UP * 6.75)
        if self.chapter is None:
            self.play(FadeIn(g, shift=DOWN * 0.3), run_time=0.5)
        else:
            self.play(FadeOut(self.chapter, shift=UP * 0.3), FadeIn(g, shift=UP * 0.3), run_time=0.5)
        self.chapter = g

    def cap(self, text, t2c=None, size=54, hold=None):
        lines = text.split("\n")
        g = VGroup(*[T(l, size, INK, BOLD) for l in lines]).arrange(DOWN, buff=0.22)
        if t2c:
            for l in g:
                l.set_color_by_t2c(t2c)
        if g.width > 8.0:
            g.scale_to_fit_width(8.0)
        g.move_to(UP * CAP_Y)
        anims = [FadeIn(g, shift=UP * 0.25)]
        if self.caption is not None:
            anims.append(FadeOut(self.caption, shift=UP * 0.25))
        self.play(*anims, run_time=0.45)
        self.caption = g
        if hold:
            self.wait(hold)
        return g

    def clear_cap(self):
        if self.caption is not None:
            self.play(FadeOut(self.caption, shift=UP * 0.25), run_time=0.35)
            self.caption = None

    def flash(self, color=WHITE, opacity=0.35):
        f = Rectangle(width=9.4, height=16.4, stroke_width=0).set_fill(color, opacity)
        self.add(f)
        self.play(f.animate.set_fill(opacity=0), run_time=0.45)
        self.remove(f)

    # ---------- 正片 ----------
    def construct(self):
        self.marks = []
        self.caption = None
        self.clock = Clock()
        self.add(self.clock)
        self.setup_backdrop()
        self.setup_hud()

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
        a = T("假设你能活到", 64)
        n80 = T("80", 150, AMBER, HEAVY)
        b = T("岁", 64)
        row = VGroup(a, n80, b).arrange(RIGHT, buff=0.18, aligned_edge=DOWN).move_to(UP * 4.2)
        self.play(AddTextLetterByLetter(a), run_time=0.7)
        self.mark("pop")
        self.play(FadeIn(n80, scale=2.2), FadeIn(b), run_time=0.45)
        n80_glow = glow(n80, AMBER)
        self.play(FadeIn(n80_glow), run_time=0.3)

        # 人生进度条 0 → 80
        L, R, Y = -3.7, 3.7, -0.4
        track = RoundedRectangle(corner_radius=0.22, width=R - L, height=0.44,
                                 stroke_width=0).set_fill(WHITE, 0.08).move_to([0, Y, 0])
        fill = RoundedRectangle(corner_radius=0.22, width=R - L, height=0.44, stroke_width=0)
        fill.set_fill(color=[AMBER, PINK, CYAN], opacity=0.95).set_sheen_direction(RIGHT)
        fill.move_to([0, Y, 0])

        def x_of(age, w=0.0):
            lin = age / 80
            lg = 0 if age <= 4 else felt_frac(age)
            return L + (R - L) * ((1 - w) * lin + w * lg)

        warp = ValueTracker(0)
        ages = [0, 20, 40, 60, 80]
        ticks = VGroup()
        for ag in ages:
            tick = always_redraw(lambda ag=ag: VGroup(
                Line([x_of(ag, warp.get_value()), Y - 0.32, 0], [x_of(ag, warp.get_value()), Y - 0.5, 0],
                     stroke_width=3, color=MUTED),
                T(str(ag), 34, MUTED, BOLD).move_to([x_of(ag, warp.get_value()), Y - 0.82, 0])))
            ticks.add(tick)

        self.play(FadeIn(track), run_time=0.3)
        runner = Dot(radius=0.13, color=WHITE).move_to([L, Y + 0.62, 0])
        age_lbl = always_redraw(lambda: T(f"{round((runner.get_x() - L) / (R - L) * 80)}岁", 30, INK)
                                .next_to(runner, UP, buff=0.12))
        self.add(runner, age_lbl)
        self.mark("sweep")
        self.play(GrowFromEdge(fill, LEFT), runner.animate.set_x(R),
                  LaggedStart(*[FadeIn(t) for t in ticks], lag_ratio=0.25), run_time=1.8, rate_func=linear)
        self.play(FadeOut(runner), FadeOut(age_lbl), run_time=0.3)

        self.cap("人生的「中点」在哪？", {"中点": PINK})
        mid_x = x_of(40)
        pin = VGroup(
            Triangle(fill_opacity=1, stroke_width=0).scale(0.16).rotate(PI).set_color(INK),
            DashedLine(UP * 0.0, DOWN * 0.9, stroke_width=3, color=INK),
        ).arrange(DOWN, buff=0).move_to([mid_x, Y + 0.95, 0], aligned_edge=DOWN)
        pin.shift(DOWN * 0.7)
        q40 = T("40 岁？", 64, INK, HEAVY).next_to(pin, UP, buff=0.25)
        self.mark("tick")
        self.play(FadeIn(pin, shift=DOWN * 0.4), FadeIn(q40, shift=DOWN * 0.4), run_time=0.5)
        self.cap("按日历算，是 40 岁", {"日历": CYAN, "40": CYAN}, hold=0.9)
        self.cap("但如果按「感觉」来算——", {"感觉": AMBER}, hold=0.5)

        # 刻度向右挤，中点读数从 40 掉到 18
        val = ValueTracker(40)
        q_num = always_redraw(lambda: T(f"{round(val.get_value())} 岁", 64, PINK, HEAVY).next_to(pin, UP, buff=0.25))
        self.remove(q40)
        self.add(q_num)
        self.mark("riser", dur=1.6)
        self.play(warp.animate.set_value(1), val.animate.set_value(18), run_time=1.6, rate_func=smooth)
        self.mark("hit")
        self.flash(PINK, 0.25)

        big = T("18", 380, PINK, HEAVY).move_to(UP * 4.3)
        big_glow = glow(big, PINK, width=60, opacity=0.06)
        self.play(FadeOut(VGroup(row, n80_glow), shift=UP * 0.5),
                  FadeIn(big, scale=0.4), FadeIn(big_glow, scale=0.4), run_time=0.5)
        self.cap("你感觉到的人生，18 岁就过了一半", {"18": PINK, "一半": PINK}, hold=1.6)
        self.cap("这不是玄学，而是一个「比例」错觉", {"比例": AMBER}, hold=1.4)
        self.mark("whoosh")
        self.play(FadeOut(VGroup(big, big_glow, track, fill, ticks, pin, q_num), shift=LEFT * 2),
                  FadeOut(self.caption), run_time=0.6)
        self.caption = None

    # 2. 为什么越长大，一年过得越快
    def scene_calendar(self):
        self.mark("beat_in")
        self.set_chapter("01", "为什么越活越快")

        def calendar(month, accent):
            card = RoundedRectangle(corner_radius=0.25, width=2.7, height=3.0, stroke_width=0)
            card.set_fill("#fdfcff", 1)
            top = RoundedRectangle(corner_radius=0.25, width=2.7, height=0.75, stroke_width=0)
            top.set_fill(accent, 1).align_to(card, UP)
            top_patch = Rectangle(width=2.7, height=0.3, stroke_width=0).set_fill(accent, 1)
            top_patch.align_to(top, DOWN)
            rings = VGroup(*[Circle(radius=0.08, fill_opacity=1, color="#2b2350", stroke_width=0)
                             for _ in range(2)]).arrange(RIGHT, buff=1.2).move_to(top.get_top())
            num = T(f"{month}月", 96, "#1b1440", HEAVY).move_to(card.get_center() + DOWN * 0.3)
            return VGroup(card, top, top_patch, rings, num)

        def person(scale, col):
            head = Circle(radius=0.28, fill_opacity=1, color=col, stroke_width=0)
            body = RoundedRectangle(corner_radius=0.25, width=0.62, height=0.75, fill_opacity=1,
                                    color=col, stroke_width=0).next_to(head, DOWN, buff=0.06)
            return VGroup(head, body).scale(scale)

        kid = person(0.75, AMBER)
        adult = person(1.1, CYAN)
        kid_cal = calendar(1, AMBER)
        ad_cal = calendar(1, CYAN)
        kid_row = VGroup(VGroup(kid, T("5 岁", 46, AMBER)).arrange(DOWN, buff=0.2), kid_cal).arrange(RIGHT, buff=0.9)
        ad_row = VGroup(VGroup(adult, T("40 岁", 46, CYAN)).arrange(DOWN, buff=0.2), ad_cal).arrange(RIGHT, buff=0.9)
        kid_row.move_to(UP * 3.0)
        ad_row.move_to(DOWN * 1.1)
        self.play(LaggedStart(FadeIn(kid_row, shift=RIGHT * 0.6), FadeIn(ad_row, shift=LEFT * 0.6),
                              lag_ratio=0.3), run_time=0.8)
        self.cap("同样过一年……", hold=0.2)

        def flips(cal, accent, months, each):
            anims = []
            for m in months:
                new = T(f"{m}月", 96, "#1b1440", HEAVY).move_to(cal[4])
                anims.append(Transform(cal[4], new, run_time=each, rate_func=rush_from))
            return Succession(*anims)

        # 小孩翻 3 页（慢），大人翻 11 页（快），时长相同
        self.mark("ticks", n=11, dur=3.0)
        self.mark("ticks_slow", n=2, dur=3.0)
        self.play(AnimationGroup(flips(kid_cal, AMBER, [2, 3], 1.5),
                                 flips(ad_cal, CYAN, list(range(2, 13)), 3.0 / 11)),
                  run_time=3.0)
        lab1 = T("一个暑假，长得像永远", 40, AMBER).next_to(kid_row, DOWN, buff=0.35)
        lab2 = T("一年，一眨眼就没了", 40, CYAN).next_to(ad_row, DOWN, buff=0.35)
        self.play(FadeIn(lab1, shift=UP * 0.2), run_time=0.4)
        self.play(FadeIn(lab2, shift=UP * 0.2), run_time=0.4)
        self.cap("同样是 365 天，为什么感觉差这么多？", {"365": PINK}, hold=1.6)
        self.play(FadeOut(VGroup(kid_row, ad_row, lab1, lab2), shift=UP * 0.6), run_time=0.5)

    # 3. 比例理论：1 年占人生的比例
    def scene_ratio(self):
        self.set_chapter("02", "关键是比例")
        who = T("1877 年，法国哲学家 保罗·让内 提出：", 36, MUTED).move_to(UP * 4.9)
        q1 = T("一段时间「感觉」有多长", 60, INK, HEAVY)
        q2 = T("取决于它占你人生的比例", 60, INK, HEAVY)
        quote = VGroup(q1, q2).arrange(DOWN, buff=0.3)
        quote.scale_to_fit_width(8.2).move_to(UP * 3.4)
        q1.set_color_by_t2c({"感觉": AMBER})
        q2.set_color_by_t2c({"比例": PINK})
        self.play(FadeIn(who), run_time=0.4)
        self.play(Write(quote), run_time=1.3)
        self.wait(0.6)

        def pie(n, r, center):
            sectors = VGroup()
            for i in range(n):
                s = AnnularSector(inner_radius=0, outer_radius=r, angle=TAU / n,
                                  start_angle=PI / 2 + i * TAU / n,
                                  stroke_color=BG_BOT, stroke_width=2 if n < 20 else 1)
                s.set_fill("#3a3470" if i else AMBER, 1)
                sectors.add(s)
            return sectors.move_to(center)

        p5 = pie(5, 1.55, LEFT * 2.05 + DOWN * 0.6)
        p50 = pie(50, 1.55, RIGHT * 2.05 + DOWN * 0.6)
        h5 = T("5 岁", 46, INK).next_to(p5, UP, buff=0.35)
        h50 = T("50 岁", 46, INK).next_to(p50, UP, buff=0.35)
        f5 = T("1 年 = 1/5", 46, AMBER, HEAVY).next_to(p5, DOWN, buff=0.4)
        f50 = T("1 年 = 1/50", 46, AMBER, HEAVY).next_to(p50, DOWN, buff=0.4)
        self.mark("tick")
        self.play(FadeIn(h5), LaggedStart(*[GrowFromCenter(s) for s in p5], lag_ratio=0.15), run_time=0.9)
        self.play(p5[0].animate.shift(0.25 * (p5[0].get_center() - p5.get_center())), FadeIn(f5, shift=UP * 0.2),
                  run_time=0.5)
        self.cap("5 岁时，1 年是你人生的 20%", {"5 岁": AMBER, "20%": AMBER}, hold=0.6)
        self.mark("tick")
        self.play(FadeIn(h50), LaggedStart(*[GrowFromCenter(s) for s in p50], lag_ratio=0.03), run_time=1.0)
        self.play(p50[0].animate.shift(0.4 * (p50[0].get_center() - p50.get_center())), FadeIn(f50, shift=UP * 0.2),
                  run_time=0.5)
        self.cap("50 岁时，1 年只占 2%", {"50 岁": CYAN, "2%": AMBER}, hold=1.2)

        # 1 个琥珀块 = 10 个青色块
        self.play(FadeOut(VGroup(who, quote), shift=UP * 0.5),
                  VGroup(p5, p50, h5, h50, f5, f50).animate.shift(UP * 3.2).scale(0.85), run_time=0.6)
        big = RoundedRectangle(corner_radius=0.08, width=7.4, height=0.9, stroke_width=0).set_fill(AMBER, 1)
        big_l = T("5 岁时的 1 年", 40, "#1b1440", HEAVY).move_to(big)
        smalls = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.68, height=0.9, stroke_width=0)
                          .set_fill(CYAN, 1) for _ in range(10)]).arrange(RIGHT, buff=0.06)
        g1 = VGroup(big, big_l).move_to(DOWN * 0.9)
        smalls.move_to(DOWN * 2.6)
        eq = T("≈", 70, INK, HEAVY).move_to(DOWN * 1.75)
        sm_l = T("50 岁时的 10 年", 40, CYAN, HEAVY).next_to(smalls, DOWN, buff=0.25)
        self.play(GrowFromEdge(big, LEFT), FadeIn(big_l), run_time=0.6)
        self.mark("ticks", n=10, dur=1.0)
        self.play(FadeIn(eq), LaggedStart(*[FadeIn(s, scale=0.3) for s in smalls], lag_ratio=0.12),
                  run_time=1.0)
        self.play(FadeIn(sm_l, shift=UP * 0.2), run_time=0.3)
        self.cap("感觉上，5 岁的 1 年 ≈ 50 岁的 10 年", {"1 年": AMBER, "10 年": CYAN}, hold=1.8)
        self.mark("whoosh")
        self.play(FadeOut(VGroup(p5, p50, h5, h50, f5, f50, g1, smalls, eq, sm_l), shift=LEFT * 2), run_time=0.6)

    # 4. 按“感觉”重画人生尺子，找到中点
    def scene_ruler(self):
        self.set_chapter("03", "重画一把人生尺子")

        # 0-3 岁：几乎没有记忆
        baby = VGroup(*[RoundedRectangle(corner_radius=0.08, width=2.6, height=0.7, stroke_width=0)
                        .set_fill("#4a4670", 1) for _ in range(4)]).arrange(DOWN, buff=0.1)
        baby_l = VGroup(*[T(f"{i} 岁", 44, MUTED).next_to(baby[i], RIGHT, buff=0.3) for i in range(4)])
        bg = VGroup(baby, baby_l).move_to(UP * 1.6)
        self.play(FadeIn(bg, shift=DOWN * 0.3), run_time=0.5)
        self.cap("0～3 岁的事，我们几乎都记不住", {"0～3 岁": MUTED}, hold=1.0)
        cross = Cross(baby, stroke_width=8, stroke_color=PINK)
        self.mark("tick")
        self.play(Create(cross), run_time=0.4)
        self.cap("所以从 4 岁算起，到 80 岁", {"4 岁": AMBER, "80 岁": CYAN}, hold=0.4)
        self.play(FadeOut(VGroup(bg, cross), shift=UP * 0.5), run_time=0.4)

        TOP, H, X0, W = 5.35, 9.3, -1.0, 1.5
        BOT = TOP - H
        warp = ValueTracker(0)

        def y_of(age, w):
            lin = (age - 4) / 76
            return TOP - H * ((1 - w) * lin + w * felt_frac(age))

        def build():
            w = warp.get_value()
            g = VGroup()
            for a in range(4, 80):
                y1, y2 = y_of(a, w), y_of(a + 1, w)
                r = Rectangle(width=W, height=max(y1 - y2, 0.001), stroke_width=1.2 if y1 - y2 > 0.06 else 0,
                              stroke_color=BG_BOT)
                r.set_fill(age_color((a - 4) / 76), 1)
                r.move_to([X0, (y1 + y2) / 2, 0])
                g.add(r)
            return g

        ruler = always_redraw(build)

        lin_ages = [4, 10, 20, 30, 40, 50, 60, 70, 80]
        log_ages = [4, 5, 6, 7, 8, 10, 12, 15, 20, 30, 40, 60, 80]

        def labels(ages, visible_w):
            def f():
                w = warp.get_value()
                op = (1 - w) if visible_w == 0 else w
                g = VGroup()
                for a in ages:
                    y = y_of(a, w)
                    g.add(Line([X0 + W / 2, y, 0], [X0 + W / 2 + 0.22, y, 0], stroke_width=3,
                               color=MUTED).set_opacity(op))
                    g.add(T(f"{a}", 30, INK, BOLD).move_to([X0 + W / 2 + 0.55, y, 0]).set_opacity(op))
                return g
            return always_redraw(f)

        lab_lin = labels(lin_ages, 0)
        lab_log = labels(log_ages, 1)
        title = T("日历上的 76 年：每年一样长", 36, CYAN).move_to([0, TOP + 0.55, 0])
        self.play(FadeIn(title), Create(ruler), FadeIn(lab_lin), run_time=1.2)
        self.add(lab_log)
        self.cap("每一格是一年，日历上每格一样大", {"一样大": CYAN}, hold=0.6)

        title2 = T("感觉上的 76 年：每年按比例缩放", 36, AMBER).move_to(title)
        self.cap("现在，把每一年按「它占人生的比例」缩放", {"比例": AMBER}, hold=0.2)
        self.mark("riser", dur=3.0)
        self.play(warp.animate.set_value(1), Transform(title, title2), run_time=3.0, rate_func=smooth)
        self.mark("hit_soft")
        self.cap("小时候的每一年被「拉长」\n长大后的每一年被「压扁」", {"拉长": AMBER, "压扁": CYAN}, size=50, hold=1.4)

        # 中点扫描线
        self.cap("那么，这把尺子的正中间是几岁？", {"正中间": PINK})
        scan = ValueTracker(0.0)
        line = always_redraw(lambda: DashedLine([X0 - W / 2 - 0.4, TOP - H * scan.get_value(), 0],
                                                [X0 + W / 2 + 1.0, TOP - H * scan.get_value(), 0],
                                                stroke_width=5, color=WHITE, dash_length=0.12))
        reading = always_redraw(lambda: T(f"{4 * 20 ** scan.get_value():.1f}", 64, WHITE, HEAVY)
                                .move_to([2.95, TOP - H * scan.get_value(), 0]))
        self.add(line, reading)
        self.mark("scan", dur=1.6)
        self.play(scan.animate.set_value(0.5), run_time=1.6, rate_func=smooth)
        self.mark("hit")
        self.flash(PINK, 0.2)
        mid_y = TOP - H / 2
        eighteen = T("18 岁", 96, PINK, HEAVY).move_to([2.6, mid_y + 0.05, 0])
        eg = glow(eighteen, PINK, width=46, opacity=0.06)
        line_static = DashedLine([X0 - W / 2 - 0.4, mid_y, 0], [X0 + W / 2 + 1.0, mid_y, 0],
                                 stroke_width=6, color=PINK, dash_length=0.12)
        self.remove(line)
        self.add(line_static)
        self.play(ReplacementTransform(reading, eighteen), FadeIn(eg), run_time=0.5)

        # 上下两半
        def bracket(y1, y2, x, col):
            return VGroup(Line([x, y1, 0], [x, y2, 0], stroke_width=5, color=col),
                          Line([x, y1, 0], [x + 0.2, y1, 0], stroke_width=5, color=col),
                          Line([x, y2, 0], [x + 0.2, y2, 0], stroke_width=5, color=col))
        bx = X0 - W / 2 - 0.35
        b1 = bracket(TOP - 0.05, mid_y + 0.08, bx, AMBER)
        b2 = bracket(mid_y - 0.08, BOT + 0.05, bx, CYAN)
        t1 = VGroup(T("4→18", 34, AMBER, HEAVY), T("14 年", 40, AMBER, HEAVY)).arrange(DOWN, buff=0.08) \
            .next_to(b1, LEFT, buff=0.12)
        t2 = VGroup(T("18→80", 34, CYAN, HEAVY), T("62 年", 40, CYAN, HEAVY)).arrange(DOWN, buff=0.08) \
            .next_to(b2, LEFT, buff=0.12)
        self.mark("tick")
        self.play(Create(b1), FadeIn(t1, shift=RIGHT * 0.2), run_time=0.5)
        self.mark("tick")
        self.play(Create(b2), FadeIn(t2, shift=RIGHT * 0.2), run_time=0.5)
        self.cap("前面的 14 年，和后面的 62 年\n感觉上一样长", {"14 年": AMBER, "62 年": CYAN}, size=52)
        everything = VGroup(ruler, lab_lin, lab_log, title, line_static, eighteen, eg, b1, b2, t1, t2)
        self.play(everything.animate.scale(1.04, about_point=[0, mid_y, 0]), run_time=1.8, rate_func=smooth)
        self.wait(0.6)
        self.mark("whoosh")
        ruler.clear_updaters()
        lab_lin.clear_updaters()
        lab_log.clear_updaters()
        self.play(FadeOut(everything, shift=DOWN * 0.8), run_time=0.6)

    # 5. 为什么偏偏是 18：翻倍规律
    def scene_doubling(self):
        self.set_chapter("04", "为什么偏偏是 18")
        self.cap("规律：年龄每「翻一倍」\n感觉上走过的路一样长", {"翻一倍": PINK}, size=52)

        L, R = -3.8, 3.8
        segs = [(5, 10), (10, 20), (20, 40), (40, 80)]
        felt_y, real_y = 2.6, -0.6
        head1 = T("感觉上的长度", 38, AMBER).move_to([0, felt_y + 1.0, 0])
        head2 = T("日历上的长度", 38, CYAN).move_to([0, real_y + 1.0, 0])
        felt, real, felt_l, real_l, links = VGroup(), VGroup(), VGroup(), VGroup(), VGroup()
        fw = (R - L) / 4
        x = L
        for i, (a, b) in enumerate(segs):
            r = RoundedRectangle(corner_radius=0.08, width=fw - 0.08, height=1.0, stroke_width=0)
            r.set_fill(age_color(i / 3), 1).move_to([L + fw * (i + 0.5), felt_y, 0])
            felt.add(r)
            felt_l.add(T(f"{a}→{b}", 32, "#1b1440", HEAVY).move_to(r))
            w = (R - L) * (b - a) / 75
            rr = RoundedRectangle(corner_radius=0.06, width=max(w - 0.06, 0.1), height=0.8, stroke_width=0)
            rr.set_fill(age_color(i / 3), 1).move_to([x + w / 2, real_y, 0])
            x += w
            real.add(rr)
            real_l.add(T(f"{b - a} 年", 32, INK, BOLD).next_to(rr, DOWN, buff=0.2 if i != 1 else 0.7))
            links.add(DashedLine(r.get_bottom(), rr.get_top(), stroke_width=2, color=WHITE).set_opacity(0.35))
        self.play(FadeIn(head1), run_time=0.3)
        for i in range(4):
            self.mark("tick")
            self.play(GrowFromEdge(felt[i], LEFT), FadeIn(felt_l[i]), run_time=0.32)
        self.play(FadeIn(head2), Create(links), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(r, LEFT) for r in real], lag_ratio=0.35),
                  LaggedStart(*[FadeIn(l) for l in real_l], lag_ratio=0.35), run_time=1.4)
        self.cap("5→10 岁的 5 年，和 40→80 岁的 40 年\n感觉上一样长", {"5 年": AMBER, "40 年": CYAN}, size=50,
                 hold=1.8)
        self.play(FadeOut(VGroup(head1, head2, felt, real, felt_l, real_l, links), shift=UP * 0.6), run_time=0.5)

        # 4 ×4.5→ 18 ×4.5→ 80
        nodes = VGroup()
        for n, col in [("4", AMBER), ("18", PINK), ("80", CYAN)]:
            c = Circle(radius=0.85, stroke_color=col, stroke_width=6).set_fill(col, 0.12)
            t = T(n, 80, col, HEAVY).move_to(c)
            nodes.add(VGroup(c, t))
        nodes.arrange(RIGHT, buff=1.2).move_to(UP * 1.9)
        arcs = VGroup(*[CurvedArrow(nodes[i].get_top() + UP * 0.1, nodes[i + 1].get_top() + UP * 0.1,
                                    angle=-PI / 2.2, color=WHITE, stroke_width=4) for i in range(2)])
        mul = VGroup(*[T("×4.5", 40, INK, HEAVY).next_to(arcs[i], UP, buff=0.1) for i in range(2)])
        self.mark("tick")
        self.play(FadeIn(nodes[0], scale=0.5), run_time=0.35)
        self.play(Create(arcs[0]), FadeIn(mul[0]), run_time=0.5)
        self.mark("pop")
        self.play(FadeIn(nodes[1], scale=0.5), run_time=0.35)
        self.play(Create(arcs[1]), FadeIn(mul[1]), run_time=0.5)
        self.mark("tick")
        self.play(FadeIn(nodes[2], scale=0.5), run_time=0.35)
        self.cap("4 翻 4.5 倍是 18，18 再翻 4.5 倍就是 80", {"18": PINK, "4.5": AMBER}, size=50, hold=0.8)
        formula = T("中点 = √(4 × 80) ≈ 17.9", 66, INK, HEAVY)
        formula.scale_to_fit_width(8.0).move_to(DOWN * 1.4)
        formula.set_color_by_t2c({"17.9": PINK})
        fglow = glow(formula, PINK, width=30, opacity=0.035)
        self.mark("hit_soft")
        self.play(FadeIn(formula, shift=UP * 0.3), FadeIn(fglow), run_time=0.6)
        self.cap("「几何平均数」：两端相乘，再开根号", {"几何平均数": PINK}, hold=1.8)
        self.mark("whoosh")
        self.play(FadeOut(VGroup(nodes, arcs, mul, formula, fglow), shift=LEFT * 2), run_time=0.5)

    # 6. 你现在走到哪了
    def scene_progress(self):
        self.set_chapter("05", "你走到哪了")
        age = ValueTracker(18)
        C = UP * 1.6
        ring_bg = Circle(radius=2.3, stroke_width=26, color=WHITE).set_stroke(opacity=0.08).move_to(C)

        def arc():
            p = felt_frac(age.get_value())
            return Arc(radius=2.3, start_angle=PI / 2, angle=-TAU * max(p, 0.001), arc_center=C,
                       stroke_width=26).set_color(age_color(p))
        ring = always_redraw(arc)
        pct = always_redraw(lambda: T(f"{felt_frac(age.get_value()) * 100:.0f}%", 120, INK, HEAVY)
                            .move_to(C + UP * 0.25))
        lbl = always_redraw(lambda: T(f"{age.get_value():.0f} 岁", 46, MUTED, BOLD).move_to(C + DOWN * 0.95))
        head = T("「感觉上」的人生进度", 42, INK).move_to(C + UP * 3.25)
        self.play(FadeIn(head), Create(ring_bg), FadeIn(pct), FadeIn(lbl), run_time=0.6)
        self.add(ring)
        self.cap("18 岁：已经走完一半", {"18 岁": PINK, "一半": PINK}, hold=0.9)
        for a, text, t2c in [(25, "25 岁：约 61%", {"61%": PINK}),
                             (30, "30 岁：约 67%，三分之二", {"67%": PINK}),
                             (40, "40 岁：约 77%", {"77%": PINK})]:
            self.mark("riser", dur=0.9)
            self.play(age.animate.set_value(a), run_time=0.9, rate_func=smooth)
            self.mark("tick")
            self.cap(text, t2c, hold=0.9)
        self.cap("……是不是有点慌？", hold=1.0)
        ring.clear_updaters()
        pct.clear_updaters()
        lbl.clear_updaters()
        self.mark("stop")
        self.play(FadeOut(VGroup(head, ring_bg, ring, pct, lbl), scale=0.8), run_time=0.5)

    # 7. 反转：时间变快，是因为新鲜事变少了
    def scene_twist(self):
        self.set_chapter("06", "反转")
        calm = T("别慌。", 140, INK, HEAVY).move_to(UP * 2.4)
        self.mark("hit")
        self.play(FadeIn(calm, scale=1.6), run_time=0.4)
        self.cap("这只是一个假说，不是定律", {"假说": AMBER}, hold=1.2)
        self.cap("心理学的另一种解释：\n时间变快，是因为「新鲜事」变少了", {"新鲜事": PINK}, size=50, hold=0.6)
        self.mark("beat_in")
        self.play(FadeOut(calm, shift=UP * 0.5), run_time=0.4)

        # 重复的一周：7 格灰块被压成 1 格
        h1 = T("重复的一周", 42, MUTED).move_to(UP * 4.4)
        days = VGroup(*[RoundedRectangle(corner_radius=0.08, width=1.0, height=1.0, stroke_width=0)
                        .set_fill("#55517a", 1) for _ in range(7)]).arrange(RIGHT, buff=0.12).move_to(UP * 3.2)
        self.play(FadeIn(h1), LaggedStart(*[FadeIn(d, scale=0.5) for d in days], lag_ratio=0.1), run_time=0.8)
        squashed = RoundedRectangle(corner_radius=0.08, width=1.0, height=1.0, stroke_width=0).set_fill("#55517a", 1)
        squashed.move_to(days)
        self.mark("tick")
        self.play(ReplacementTransform(days, squashed), run_time=0.7)
        m1 = T("在记忆里只剩一格", 38, MUTED).next_to(squashed, DOWN, buff=0.3)
        self.play(FadeIn(m1), run_time=0.3)

        # 第一次旅行：7 个各不相同的彩色形状铺满一整排
        h2 = T("第一次去旅行的一周", 42, AMBER).move_to(DOWN * 0.1)
        shapes = VGroup(
            Star(5, outer_radius=0.48, color=AMBER, fill_opacity=1),
            Circle(radius=0.42, color=PINK, fill_opacity=1),
            Triangle(color=CYAN, fill_opacity=1).scale(0.5),
            Square(0.8, color=VIOLET, fill_opacity=1).rotate(PI / 4),
            RegularPolygon(6, color="#7ae582", fill_opacity=1).scale(0.45),
            Star(7, outer_radius=0.48, color=CYAN, fill_opacity=1),
            Circle(radius=0.42, color=AMBER, fill_opacity=1),
        ).arrange(RIGHT, buff=0.2).move_to(DOWN * 1.4)
        for s in shapes:
            s.set_stroke(width=0)
        self.play(FadeIn(h2), run_time=0.3)
        self.mark("ticks", n=7, dur=1.0)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in shapes], lag_ratio=0.15), run_time=1.0)
        self.play(LaggedStart(*[s.animate(rate_func=there_and_back).scale(1.25) for s in shapes], lag_ratio=0.1),
                  run_time=0.8)
        m2 = T("在记忆里铺满一大片", 38, AMBER).next_to(shapes, DOWN, buff=0.35)
        self.play(FadeIn(m2), run_time=0.3)
        self.cap("大脑用「记住了多少新东西」\n来估计时间有多长", {"新东西": PINK}, size=52, hold=1.8)
        self.play(FadeOut(VGroup(h1, squashed, m1, h2, shapes, m2), shift=UP * 0.6), run_time=0.5)

        # 结尾
        l1 = T("想让时间慢下来？", 72, INK, HEAVY).move_to(UP * 3.4)
        l2 = T("多做一些「第一次」", 80, AMBER, HEAVY)
        l2.scale_to_fit_width(8.2).move_to(UP * 1.8)
        l2g = glow(l2, AMBER, width=34, opacity=0.04)
        self.clear_cap()
        self.play(FadeIn(l1, shift=UP * 0.3), run_time=0.5)
        self.mark("pop")
        self.play(FadeIn(l2, scale=1.3), FadeIn(l2g), run_time=0.5)
        self.wait(1.0)

        big = T("18", 300, PINK, HEAVY).move_to(DOWN * 1.4)
        bg_ = glow(big, PINK, width=55, opacity=0.06)
        self.play(FadeIn(big), FadeIn(bg_), run_time=0.4)
        q = T("?", 300, AMBER, HEAVY).move_to(big)
        qg = glow(q, AMBER, width=55, opacity=0.06)
        self.mark("hit")
        self.play(Transform(big, q), Transform(bg_, qg), run_time=0.7)
        self.cap("你感觉中的人生中点\n也许还远没到", {"人生中点": PINK, "还远没到": AMBER}, size=56, hold=2.4)
        self.mark("outro")
        self.play(FadeOut(VGroup(l1, l2, l2g, big, bg_, self.caption, self.chapter)), run_time=1.0)
        sign = T("知识短片 · 02", 36, MUTED).move_to(DOWN * 0.2)
        self.play(FadeIn(sign), run_time=0.5)
        self.wait(1.2)
