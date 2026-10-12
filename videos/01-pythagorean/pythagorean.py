"""勾股定理的拼图证明：竖屏 1080x1920 短视频。

渲染：manim -qh pythagorean.py Pythagorean
"""
from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30
config.background_color = "#0f1420"

FONT = "WenQuanYi Zen Hei"
A_COL = "#4ade80"   # a² 绿
B_COL = "#f87171"   # b² 红
C_COL = "#60a5fa"   # c² 蓝
TRI_COL = "#fbbf24"  # 三角形 金

a, b = 3, 4
L = a + b


def T(s, size=46, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


class Pythagorean(Scene):
    def caption(self, *lines, old=None, colors=None):
        g = VGroup(*[T(l, 54) for l in lines]).arrange(DOWN, buff=0.3)
        if colors:
            for line in g:
                line.set_color_by_t2c(colors)
        if g.width > 8.2:
            g.scale_to_fit_width(8.2)
        g.move_to(DOWN * 5.6)
        if old is not None:
            self.play(FadeOut(old, shift=UP * 0.2), FadeIn(g, shift=UP * 0.2), run_time=0.6)
        else:
            self.play(FadeIn(g, shift=UP * 0.2), run_time=0.6)
        return g

    def construct(self):
        t2c = {"a²": A_COL, "b²": B_COL, "c²": C_COL}

        # 1. 开场
        title = T("勾股定理", 96).move_to(UP * 1.2)
        q = T("a² + b² = c²", 80).next_to(title, DOWN, buff=0.7)
        q.set_color_by_t2c(t2c)
        sub = T("30 秒看懂它为什么成立", 44, GREY_B).next_to(q, DOWN, buff=0.7)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(q, shift=UP * 0.3), run_time=0.8)
        self.play(FadeIn(sub), run_time=0.6)
        self.wait(1.5)
        self.play(FadeOut(VGroup(title, q, sub)), run_time=0.6)

        header = T("勾股定理", 60).move_to(UP * 6.8)
        self.play(FadeIn(header), run_time=0.5)

        # 2. 直角三角形与三个正方形
        s = 0.62
        A_, B_, C_ = np.array([0, 0, 0]), np.array([a, 0, 0]), np.array([0, b, 0])
        n = np.array([b, a, 0])
        tri = Polygon(A_, B_, C_, color=TRI_COL, fill_opacity=0.85, stroke_width=4)
        sq_a = Polygon(A_, B_, B_ + DOWN * a, A_ + DOWN * a, color=A_COL, fill_opacity=0.35)
        sq_b = Polygon(A_, C_, C_ + LEFT * b, A_ + LEFT * b, color=B_COL, fill_opacity=0.35)
        sq_c = Polygon(B_, C_, C_ + n, B_ + n, color=C_COL, fill_opacity=0.35)
        fig = VGroup(sq_a, sq_b, sq_c, tri)
        fig.scale(s, about_point=ORIGIN)
        fig.move_to(UP * 0.9)
        ra = RightAngle(Line(tri.get_vertices()[0], tri.get_vertices()[1]),
                        Line(tri.get_vertices()[0], tri.get_vertices()[2]),
                        length=0.25, color=WHITE)
        v0, v1, v2 = tri.get_vertices()
        la = T("a", 48).next_to(Line(v0, v1), DOWN, buff=0.15)
        lb = T("b", 48).next_to(Line(v0, v2), LEFT, buff=0.15)
        lc = T("c", 48).move_to((v1 + v2) / 2 + normalize(n) * 0.35)

        cap = self.caption("一个直角三角形", "两条直角边 a、b，斜边 c")
        self.play(DrawBorderThenFill(tri), Create(ra), run_time=1.2)
        self.play(FadeIn(la), FadeIn(lb), FadeIn(lc), run_time=0.6)
        self.wait(1.2)

        cap = self.caption("在三条边上各画一个正方形", old=cap)
        sa_t = T("a²", 48, A_COL).move_to(sq_a.get_center())
        sb_t = T("b²", 48, B_COL).move_to(sq_b.get_center())
        sc_t = T("c²", 48, C_COL).move_to(sq_c.get_center())
        self.play(FadeOut(VGroup(la, lb, lc)), run_time=0.3)
        for sq, lab in ((sq_a, sa_t), (sq_b, sb_t), (sq_c, sc_t)):
            self.play(DrawBorderThenFill(sq), FadeIn(lab), run_time=0.7)
        self.wait(0.6)
        cap = self.caption("定理说：绿 + 红 = 蓝", "为什么？", old=cap)
        self.wait(1.8)
        self.play(FadeOut(VGroup(fig, ra, sa_t, sb_t, sc_t)), run_time=0.6)

        # 3. 拼图：边长 a+b 的大正方形
        k = 0.88
        origin = np.array([-L * k / 2, -L * k / 2 + 0.9, 0])

        def P(x, y):
            return origin + np.array([x, y, 0]) * k

        big = Square(L * k, color=WHITE, stroke_width=5).move_to(P(L / 2, L / 2))
        cap = self.caption("画一个边长为 a+b 的大正方形", old=cap)
        self.play(Create(big), run_time=1)

        def tri_at(p0, p1, p2):
            return Polygon(P(*p0), P(*p1), P(*p2), color=TRI_COL,
                           fill_opacity=0.9, stroke_color=BLACK, stroke_width=3)

        t1 = tri_at((0, 0), (a, 0), (0, b))
        t2 = tri_at((L, 0), (L, a), (a, 0))
        t3 = tri_at((L, L), (b, L), (L, a))
        t4 = tri_at((0, L), (0, b), (b, L))
        tris = VGroup(t1, t2, t3, t4)

        cap = self.caption("放进 4 个一模一样的三角形", old=cap)
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in tris], lag_ratio=0.3), run_time=1.6)

        inner = Polygon(P(a, 0), P(L, a), P(b, L), P(0, b), color=C_COL,
                        fill_opacity=0.55, stroke_width=0)
        inner_t = T("c²", 64, C_COL).move_to(inner.get_center())
        self.bring_to_back(inner)
        cap = self.caption("中间空出的部分，正好是 c²", old=cap, colors=t2c)
        self.play(FadeIn(inner), Write(inner_t), run_time=1)
        self.wait(1.8)

        # 4. 挪动三角形
        cap = self.caption("现在只挪动三角形，不改变大小", old=cap)
        self.play(FadeOut(inner), FadeOut(inner_t), run_time=0.5)
        self.play(t1.animate.shift(UP * a * k), run_time=1)
        self.play(t3.animate.shift(LEFT * b * k), run_time=1)
        self.play(t4.animate.shift((RIGHT * a + DOWN * b) * k), run_time=1.2)
        self.wait(0.3)

        sq_a2 = Square(a * k, color=A_COL, fill_opacity=0.55, stroke_width=0).move_to(P(a / 2, a / 2))
        sq_b2 = Square(b * k, color=B_COL, fill_opacity=0.55, stroke_width=0).move_to(P(a + b / 2, a + b / 2))
        a_t = T("a²", 60, A_COL).move_to(sq_a2.get_center())
        b_t = T("b²", 64, B_COL).move_to(sq_b2.get_center())
        self.bring_to_back(sq_a2, sq_b2)
        cap = self.caption("空白变成了两块：a² 和 b²", old=cap, colors=t2c)
        self.play(FadeIn(sq_a2), FadeIn(sq_b2), Write(a_t), Write(b_t), run_time=1)
        self.wait(1.8)

        # 5. 结论
        cap = self.caption("大正方形没变，三角形没变", "所以空白面积也没变", old=cap)
        self.wait(2.2)

        board = VGroup(big, tris, sq_a2, sq_b2, a_t, b_t)
        self.play(board.animate.scale(0.6).shift(UP * 1.6), FadeOut(cap), run_time=0.8)
        eq = T("a² + b² = c²", 96).next_to(board, DOWN, buff=0.9)
        eq.set_color_by_t2c(t2c)
        box = SurroundingRectangle(eq, color=WHITE, buff=0.35, corner_radius=0.15)
        self.play(Write(eq), run_time=1.2)
        self.play(Create(box), run_time=0.6)
        self.play(Indicate(eq, scale_factor=1.08, color=None), run_time=1)
        tail = T("关注我，下次讲清另一个知识点", 40, GREY_B).move_to(DOWN * 6.3)
        self.play(FadeIn(tail), run_time=0.6)
        self.wait(2.5)
