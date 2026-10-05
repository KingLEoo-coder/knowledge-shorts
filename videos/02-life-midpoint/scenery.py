"""用 numpy + Pillow 画场景底图（全部程序生成，无外部素材）。

python scenery.py  → assets/*.png
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(2026)


# ---------- 噪声工具 ----------
def noise2d(w, h, scale, octaves=4, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gw, gh = max(2, int(w / scale * 2 ** o)), max(2, int(h / scale * 2 ** o))
        g = Image.fromarray((r.random((gh, gw)) * 255).astype(np.uint8))
        out += np.asarray(g.resize((w, h), Image.BICUBIC), np.float32) / 255 * amp
        tot += amp
        amp *= 0.5
    return out / tot


def ridge(n, base, rough, seed, octaves=6):
    """一条山脊线：n 个点的高度（像素，越大越靠下）。"""
    r = np.random.default_rng(seed)
    y = np.zeros(n)
    amp = rough
    for o in range(octaves):
        k = 2 ** o * 2
        pts = r.normal(0, 1, k + 3)
        xs = np.linspace(0, k + 2, n)
        y += np.interp(xs, np.arange(k + 3), pts) * amp
        amp *= 0.55
    return base + y


def vgrad(h, w, stops):
    """竖直渐变。stops: [(位置0-1, (r,g,b)), ...]"""
    t = np.linspace(0, 1, h)[:, None]
    img = np.zeros((h, w, 3), np.float32)
    ps = [s[0] for s in stops]
    for c in range(3):
        img[:, :, c] = np.interp(t, ps, [s[1][c] for s in stops])
    return img


def grain(img, amt=6, seed=1):
    r = np.random.default_rng(seed)
    return img + r.normal(0, amt, img.shape[:2])[:, :, None]


def vignette(img, strength=0.35, power=2.2):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return img * (1 - strength * d[:, :, None] ** power)


def save(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))


def save_rgba(rgb, alpha, name):
    a = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    im = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), a])
    Image.fromarray(im, "RGBA").save(os.path.join(OUT, name))


# ---------- 宣纸 ----------
def paper(w=W, h=H, base=(239, 232, 218), seed=3):
    img = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    blot = noise2d(w, h, 260, 5, seed) - 0.5
    img += blot[:, :, None] * 22
    fib = noise2d(w, h, 6, 2, seed + 1) - 0.5
    img += fib[:, :, None] * 8
    img = grain(img, 3.5, seed)
    return img


# ---------- 水墨山 ----------
def ink_layer(w, h, top, rough, ink, seed, mist=260, texture=True):
    """返回 (rgb, alpha)：一层山，墨色从山脊往下渐淡成雾。"""
    ys = ridge(w, top, rough, seed)
    yy = np.arange(h)[:, None]
    depth = yy - ys[None, :]
    inside = depth > 0
    fade = np.clip(1 - depth / mist, 0, 1) ** 1.3
    edge = np.clip(depth / 4, 0, 1)
    a = inside * fade * edge
    if texture:
        tex = noise2d(w, h, 18, 3, seed + 7)
        streak = noise2d(w, h, 60, 2, seed + 9)
        a *= 0.65 + 0.55 * tex * streak
    a = np.clip(a, 0, 1)
    rgb = np.ones((h, w, 3), np.float32) * np.array(ink, np.float32)
    return rgb, a


def compose(base, layers):
    out = base.copy()
    for rgb, a in layers:
        out = out * (1 - a[:, :, None]) + rgb * a[:, :, None]
    return out


def ink_landscape():
    base = paper()
    layers = []
    specs = [  # top(px), roughness, ink color, mist length, blur
        (760, 110, (150, 148, 142), 360, 6),
        (920, 130, (110, 108, 104), 320, 3),
        (1100, 140, (70, 68, 66), 300, 1),
        (1300, 110, (34, 33, 32), 280, 0),
    ]
    for i, (top, rough, ink, mist, blur) in enumerate(specs):
        rgb, a = ink_layer(W, H, top, rough, ink, 40 + i, mist)
        if blur:
            a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur)),
                           np.float32) / 255
        layers.append((rgb, a))
        save_rgba(rgb, a, f"ink_layer{i}.png")
    out = compose(base, layers)
    # 淡朱红的太阳
    sun = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sun).ellipse([700, 360, 860, 520], fill=255)
    sun = np.asarray(sun.filter(ImageFilter.GaussianBlur(2)), np.float32)[:, :, None] / 255 * 0.55
    out = out * (1 - sun) + np.array([200, 80, 60]) * sun
    out = compose(out, layers[1:])  # 太阳在远山后面
    save(vignette(out, 0.25), "ink_landscape.png")
    save(vignette(base, 0.25), "paper.png")


def scroll_painting(w=560, h=1500):
    """立轴里的画心：竖长构图，峰峦从上到下层层叠叠。"""
    base = paper(w, h, (232, 222, 200), 11)
    layers = []
    for i, top in enumerate([200, 520, 840, 1120]):
        ink = [(176, 170, 160), (140, 135, 126), (98, 94, 88), (48, 46, 44)][i]
        rgb, a = ink_layer(w, h, top, 45 + 12 * i, ink, 80 + i, 250)
        layers.append((rgb, a))
    out = compose(base, layers)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for y, x0, x1 in [(1395, 120, 260), (1420, 300, 470), (1445, 90, 200), (1470, 260, 420)]:
        d.line([(x0, y), (x1, y)], fill=(120, 116, 108), width=2)
    d.polygon([(330, 1370), (420, 1370), (405, 1382), (345, 1382)], fill=(40, 38, 36))  # 小舟
    d.line([(372, 1370), (372, 1335)], fill=(40, 38, 36), width=2)
    out = np.asarray(im, np.float32)
    save(out, "scroll_painting.png")


# ---------- 山野四季 ----------
SEASONS = {
    "summer": dict(sky=[(0, (36, 52, 92)), (0.35, (214, 120, 84)), (0.55, (246, 196, 128)), (1, (250, 226, 170))],
                   hills=[(196, 128, 104), (150, 92, 86), (98, 62, 70), (52, 34, 44)], sun=(255, 228, 170)),
    "spring": dict(sky=[(0, (122, 160, 196)), (0.5, (226, 214, 214)), (1, (246, 232, 224))],
                   hills=[(170, 186, 168), (128, 156, 128), (92, 124, 96), (52, 78, 60)], sun=(255, 246, 230)),
    "autumn": dict(sky=[(0, (70, 74, 110)), (0.45, (220, 140, 80)), (1, (240, 200, 140))],
                   hills=[(196, 140, 96), (176, 102, 62), (130, 66, 44), (70, 36, 30)], sun=(255, 214, 150)),
    "winter": dict(sky=[(0, (110, 128, 150)), (0.5, (190, 198, 206)), (1, (224, 228, 232))],
                   hills=[(206, 212, 220), (180, 188, 198), (150, 158, 170), (236, 238, 242)], sun=(250, 250, 250)),
}


def field(name):
    s = SEASONS[name]
    img = vgrad(H, W, s["sky"])
    clouds = noise2d(W, H, 300, 5, 5)
    img += ((clouds - 0.5) * 30)[:, :, None] * np.linspace(1, 0.2, H)[:, None, None]
    # 太阳 + 光晕
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - 560) ** 2 + (yy - 1020) ** 2)
    glow = np.exp(-d / 260)[:, :, None]
    img = img * (1 - 0.6 * glow) + np.array(s["sun"]) * 0.6 * glow
    disk = np.clip((70 - d) / 3, 0, 1)[:, :, None]
    img = img * (1 - disk) + np.array(s["sun"]) * disk
    layers = []
    for i, (top, col) in enumerate(zip([1080, 1220, 1400, 1600], s["hills"])):
        ys = ridge(W, top, 40 + 20 * i, 200 + i, octaves=5)
        a = (np.arange(H)[:, None] > ys[None, :]).astype(np.float32)
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 + (3 - i))),
                       np.float32) / 255
        rgb = np.ones((H, W, 3), np.float32) * np.array(col, np.float32)
        shade = noise2d(W, H, 120, 4, 300 + i)[:, :, None]
        rgb = rgb * (0.9 + 0.2 * shade)
        layers.append((rgb, a))
    img = compose(img, layers)
    save(vignette(grain(img, 4, 9), 0.4), f"field_{name}.png")


# ---------- 烛光书桌 ----------
def desk():
    img = vgrad(H, W, [(0, (18, 12, 9)), (0.62, (40, 26, 16)), (0.64, (70, 44, 26)), (1, (40, 24, 14))])
    wood = noise2d(W, H, 400, 3, 21)
    lines = np.sin(np.linspace(0, 1, H)[:, None] * 260 + wood * 18)
    mask = (np.arange(H) > H * 0.63)[:, None]
    img += (lines * 7 * mask)[:, :, None]
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - 860) ** 2 + (yy - 900) ** 2)
    glow = np.exp(-d / 420)[:, :, None]
    img = img + np.array([255, 170, 90]) * 0.55 * glow
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    for x0, y0, x1, col in [(60, 1100, 420, (54, 34, 24)), (90, 1040, 400, (74, 30, 26)), (70, 985, 380, (40, 46, 50))]:
        dr.rectangle([x0, y0, x1, y0 + 58], fill=col)  # 一摞旧书
        dr.line([(x0 + 10, y0 + 29), (x1 - 10, y0 + 29)], fill=tuple(int(c * 1.4) for c in col), width=2)
    dr.rectangle([830, 960, 890, 1215], fill=(222, 206, 176))  # 蜡烛
    dr.ellipse([826, 950, 894, 972], fill=(236, 222, 194))
    dr.polygon([(860, 860), (875, 920), (860, 948), (845, 920)], fill=(255, 226, 150))  # 火焰
    dr.ellipse([848, 905, 872, 945], fill=(255, 246, 210))
    dr.ellipse([780, 1205, 940, 1235], fill=(90, 70, 50))  # 烛台
    img = np.asarray(im, np.float32)
    save(vignette(grain(img, 5, 13), 0.55, 1.6), "desk.png")
    # 烛光（单独一层，用来闪烁）
    g = np.exp(-d / 160)
    save_rgba(np.ones((H, W, 3)) * np.array([255, 200, 120]), g * 0.7, "candle_glow.png")


def aged_page(w=760, h=980):
    img = paper(w, h, (226, 210, 178), 31)
    yy, xx = np.mgrid[0:h, 0:w]
    e = np.minimum(np.minimum(xx, w - xx), np.minimum(yy, h - yy)) / 60
    burn = np.clip(1 - e, 0, 1)[:, :, None] ** 1.5
    img = img * (1 - 0.45 * burn) + np.array([120, 80, 40]) * 0.45 * burn
    spots = noise2d(w, h, 90, 4, 33)
    img -= (np.clip(spots - 0.68, 0, 1) * 50)[:, :, None]
    save(img, "aged_page.png")


# ---------- 天色（人生的一天） ----------
SKIES = {  # 名字: (渐变, 太阳位置 y, 太阳颜色)
    "dawn": ([(0, (40, 46, 84)), (0.55, (190, 140, 150)), (0.8, (246, 196, 160)), (1, (250, 220, 190))], 1260, (255, 220, 190)),
    "noon": ([(0, (70, 128, 190)), (0.6, (150, 196, 228)), (1, (214, 230, 238))], 420, (255, 252, 240)),
    "afternoon": ([(0, (78, 124, 176)), (0.6, (180, 196, 206)), (1, (236, 220, 190))], 760, (255, 240, 210)),
    "sunset": ([(0, (52, 56, 100)), (0.45, (206, 110, 90)), (0.75, (244, 170, 100)), (1, (250, 210, 150))], 1180, (255, 210, 140)),
    "dusk": ([(0, (14, 18, 40)), (0.6, (60, 50, 90)), (0.85, (150, 90, 100)), (1, (190, 120, 100))], 1500, (230, 140, 110)),
}


def sky(name):
    stops, sy, sc = SKIES[name]
    img = vgrad(H, W, stops)
    cl = noise2d(W, H, 260, 5, 51)
    img += ((cl - 0.55).clip(0) * 60)[:, :, None]
    # 地面剪影：远山 + 水面
    ys = ridge(W, 1560, 30, 61, 5)
    a = (np.arange(H)[:, None] > ys[None, :]).astype(np.float32)
    dark = np.array(stops[0][1]) * 0.45
    img = img * (1 - a[:, :, None]) + dark * a[:, :, None]
    save(vignette(grain(img, 3.5, 7), 0.35), f"sky_{name}.png")


def sun_glow(size=900):
    yy, xx = np.mgrid[0:size, 0:size]
    d = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2)
    a = np.exp(-d / 110) * 0.75 + np.clip((50 - d) / 3, 0, 1)
    save_rgba(np.ones((size, size, 3)) * 255, np.clip(a, 0, 1), "sun_glow.png")


if __name__ == "__main__":
    ink_landscape()
    scroll_painting()
    for k in SEASONS:
        field(k)
    desk()
    aged_page()
    for k in SKIES:
        sky(k)
    sun_glow()
    print(sorted(os.listdir(OUT)))
