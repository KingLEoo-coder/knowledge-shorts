"""用代码合成配乐和音效（无任何外部素材），按 marks.json 里的节拍对齐画面。

用法：python music.py marks.json music.wav
需要 numpy、scipy。
"""
import json
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
BPM = 96
BEAT = 60 / BPM
rng = np.random.default_rng(18)


def note(name):
    """'A3' → Hz"""
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3,
             "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    pitch, octave = name[:-1], int(name[-1])
    return 440 * 2 ** ((names[pitch] + (octave - 4) * 12) / 12)


def env(n, a, r, sustain=1.0):
    e = np.ones(n) * sustain
    na, nr = int(a * SR), int(r * SR)
    na, nr = min(na, n), min(nr, n)
    e[:na] = np.linspace(0, sustain, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=SR, output="sos"), x)


def hp(x, hz, order=2):
    return sosfilt(butter(order, hz, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def add(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: buf.shape[1] - i]
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    buf[0, i:i + len(sig)] += sig * gain * l * 1.414
    buf[1, i:i + len(sig)] += sig * gain * r * 1.414


# ---------- 乐器 ----------
def pad_voice(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        ff = f * 2 ** (det / 12)
        for h in range(1, 7):
            s += np.sin(2 * np.pi * ff * h * t + rng.uniform(0, 6)) / h
    s = lp(s, 1400)
    return s * env(n, 0.6, 0.8) * 0.06


def pluck(f, dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    return s * np.exp(-t * 7) * env(n, 0.004, 0.05)


def bass(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.tanh(1.6 * np.sin(2 * np.pi * f * t)) + 0.3 * np.sin(2 * np.pi * f / 2 * t)
    return lp(s, 500) * env(n, 0.01, 0.12) * np.exp(-t * 1.2)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) + 0.15 * rng.standard_normal(n) * np.exp(-t * 120)


def clap():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 900, 3500) * np.exp(-t * 22)
    return s * 0.8


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (18 if open_ else 80)) * 0.5


# ---------- 音效 ----------
def sfx_impact(soft=False):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 32 + 90 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    noise = lp(rng.standard_normal(n), 2500) * np.exp(-t * 9) * 0.5
    shimmer = sum(np.sin(2 * np.pi * note(x) * t) for x in ("A5", "E6", "A6")) * np.exp(-t * 2.5) * 0.08
    s = boom + noise + shimmer
    return s * (0.5 if soft else 1.0)


def sfx_riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = int(0.05 * SR)
    for i in range(0, n, seg):  # 分段带通，中心频率逐段升高
        c = 400 + 5000 * k[i] ** 2
        out[i:i + seg] = bp(noise[i:i + seg + 0], c * 0.7, min(c * 1.4, 18000))[: len(out[i:i + seg])]
    tone = np.sin(2 * np.pi * np.cumsum(200 + 700 * k ** 2) / SR) * 0.25
    return (out * 0.6 + tone) * k ** 1.5


def sfx_whoosh():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 500, 4000) * np.sin(np.pi * t / 0.6) ** 2
    return s * 0.7


def sfx_tick():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90) * 0.6


def sfx_pop():
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    f = 500 + 500 * t / 0.18
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 25) * 0.8


def reverb(x, secs=1.8, mix=0.25):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.5)
    ir = lp(ir, 5000)
    ir /= np.abs(ir).sum() ** 0.5 * 6
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix


# ---------- 编曲 ----------
CHORDS = [  # Am – F – C – G，每个和弦一小节（4 拍）
    ("A2", ["A3", "C4", "E4", "A4"]),
    ("F2", ["F3", "A3", "C4", "F4"]),
    ("C3", ["G3", "C4", "E4", "G4"]),
    ("G2", ["G3", "B3", "D4", "G4"]),
]
ARP = [0, 1, 2, 3, 2, 1, 2, 3]


def main(marks_path, out_path):
    marks = json.load(open(marks_path))
    end = next(m["t"] for m in marks if m["name"] == "end")
    first_hit = next(m["t"] for m in marks if m["name"] == "hit")
    stop = next(m["t"] for m in marks if m["name"] == "stop")
    twist_hit = next(m["t"] for m in marks if m["name"] == "hit" and m["t"] > stop)
    outro = next(m["t"] for m in marks if m["name"] == "outro")
    total = end + 0.3
    N = int(total * SR)
    music = np.zeros((2, N))
    drums = np.zeros((2, N))
    sfx = np.zeros((2, N))

    t0 = first_hit  # 节拍网格对齐到第一次 “18” 出现的瞬间
    first_beat = -int(t0 / BEAT) - 1
    last_beat = int((total - t0) / BEAT) + 1
    for b in range(first_beat, last_beat):
        t = t0 + b * BEAT
        bar = b // 4
        root, tones = CHORDS[bar % 4]
        in_intro = t < first_hit
        in_break = stop <= t < twist_hit + 4 * BEAT
        in_outro = t >= outro

        if b % 4 == 0 and t + 4 * BEAT > 0:  # 每小节起一组 pad
            for x in tones:
                add(music, pad_voice(note(x), 4 * BEAT + 0.8), t, gain=0.9 if not in_break else 0.6,
                    pan=rng.uniform(-0.4, 0.4))
        # 琶音：八分音符，高八度
        for k in range(2):
            tt = t + k * BEAT / 2
            if tt < 0:
                continue
            idx = ARP[(b % 4) * 2 + k]
            f = note(tones[idx]) * 2
            g = 0.10 if in_intro else 0.13
            if in_break:
                g = 0.09
            add(music, pluck(f), tt, gain=g, pan=(-0.35 if k == 0 else 0.35))
        if in_intro or in_outro and t > outro + 2 * BEAT:
            continue
        if not in_break:
            add(music, bass(note(root), BEAT * 0.95), t, gain=0.32)
        # 鼓：拐点前半段只有底鼓，beat_in 之后全上
        if in_break and t < twist_hit:
            continue
        light = in_break
        if b % 2 == 0:
            add(drums, kick(), t, gain=0.55 if not light else 0.35)
        if b % 2 == 1 and t > 14.5 and not light:
            add(drums, clap(), t, gain=0.22, pan=0.1)
        if not light:
            add(drums, hat(), t + BEAT / 2, gain=0.18, pan=0.3)
            if b % 8 == 7:
                add(drums, hat(True), t + BEAT / 2, gain=0.15, pan=-0.3)

    # 断点：stop → 第二次 hit 之间整体静音，制造“停顿”
    fade_n = int(0.25 * SR)
    a, b_ = int(stop * SR), int(twist_hit * SR)
    for buf in (music, drums):
        buf[:, a:a + fade_n] *= np.linspace(1, 0, fade_n)
        buf[:, a + fade_n:b_] = 0
    # 结尾淡出
    o = int(outro * SR)
    fade = np.ones(N)
    fade[o:] = np.linspace(1, 0, N - o) ** 1.5
    music *= fade
    drums *= fade
    # 开头淡入
    fi = int(1.2 * SR)
    music[:, :fi] *= np.linspace(0, 1, fi)

    for m in marks:
        t, name = m["t"], m["name"]
        if name == "hit":
            add(sfx, sfx_impact(), t, 0.75)
        elif name == "hit_soft":
            add(sfx, sfx_impact(soft=True), t, 0.6)
        elif name == "riser":
            d = m.get("dur", 1.5)
            add(sfx, sfx_riser(d), t, 0.35)
        elif name == "whoosh":
            add(sfx, sfx_whoosh(), t - 0.05, 0.4)
        elif name == "tick":
            add(sfx, sfx_tick(), t, 0.35)
        elif name == "pop":
            add(sfx, sfx_pop(), t, 0.4)
        elif name == "scan":
            add(sfx, sfx_riser(m["dur"]), t, 0.3)
        elif name in ("ticks", "ticks_slow"):
            n, d = m["n"], m["dur"]
            for i in range(n):
                add(sfx, sfx_tick() * (0.7 if name == "ticks" else 1.0), t + d * (i + 1) / (n + 1) if name == "ticks_slow"
                    else t + d * i / n, 0.3, pan=(-0.3 if name == "ticks_slow" else 0.3))

    music = np.stack([reverb(music[0], mix=0.3), reverb(music[1], mix=0.3)])
    sfx = np.stack([reverb(sfx[0], mix=0.15), reverb(sfx[1], mix=0.15)])
    mix = music * 0.9 + drums * 0.8 + sfx
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)  # 软限幅
    mix /= np.abs(mix).max() / 0.89
    pcm = (mix.T * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out_path}: {total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
