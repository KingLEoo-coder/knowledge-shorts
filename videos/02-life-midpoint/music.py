"""混音：公有领域配乐 + 轻音效，按 marks.json 对齐画面。

用法：python music.py marks.json track.mp3 music.wav [起始秒]
配乐来自 FreePD（CC0 公有领域），见 README。音效只保留很轻的翻页/嗖声/提示音。
需要 numpy、scipy、ffmpeg。
"""
import json
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(18)


def load(path, start, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path,
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def sfx_whoosh():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 800, 5000) * np.sin(np.pi * t / 0.5) ** 2 * 0.5


def sfx_tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 110) * 0.5


def sfx_pop():
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(700 + 500 * t / 0.15) / SR) * np.exp(-t * 30) * 0.5


def add(buf, sig, t, gain):
    i = int(t * SR)
    if i >= buf.shape[1]:
        return
    sig = sig[: buf.shape[1] - i]
    buf[:, i:i + len(sig)] += sig * gain


def main(marks_path, track, out_path, start=0.0):
    marks = json.load(open(marks_path))
    t_of = lambda name: next(m["t"] for m in marks if m["name"] == name)
    end = t_of("end")
    total = end + 0.3
    N = int(total * SR)

    music = load(track, start, total)
    if music.shape[1] < N:
        music = np.pad(music, ((0, 0), (0, N - music.shape[1])))
    music = music[:, :N]

    # 音量包络：开头淡入；“是不是有点慌？”之后压低到 25%，“别慌。”后恢复；结尾 3 秒淡出
    gain = np.ones(N)
    fi = int(1.0 * SR)
    gain[:fi] = np.linspace(0, 1, fi)
    stop = t_of("stop")
    twist = next(m["t"] for m in marks if m["name"] == "hit" and m["t"] > stop)
    a, b = int(stop * SR), int(twist * SR)
    r = int(0.4 * SR)
    gain[a:a + r] *= np.linspace(1, 0.25, r)
    gain[a + r:b] *= 0.25
    gain[b:b + 2 * r] *= np.linspace(0.25, 1, 2 * r)
    fo = int(3.0 * SR)
    gain[-fo:] *= np.linspace(1, 0, fo)
    music *= gain

    sfx = np.zeros((2, N))
    for m in marks:
        t, name = m["t"], m["name"]
        if name == "whoosh":
            add(sfx, sfx_whoosh(), t - 0.05, 0.25)
        elif name == "tick":
            add(sfx, sfx_tick(), t, 0.25)
        elif name == "pop":
            add(sfx, sfx_pop(), t, 0.25)
        elif name in ("ticks", "ticks_slow"):
            for i in range(m["n"]):
                add(sfx, sfx_tick() * 0.6, t + m["dur"] * i / m["n"], 0.25)

    mix = music * 0.85 + sfx
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    pcm = (mix.T * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out_path}: {total:.1f}s from {track} @ {start}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 0.0)
