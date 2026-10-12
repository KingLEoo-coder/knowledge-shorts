# knowledge-shorts

用代码生成的动画（[Manim Community](https://www.manim.community/)）把概念和知识讲清楚的竖屏短视频（1080×1920），面向社交媒体投放。

## 视频列表

| 编号 | 主题 | 时长 | 文件 |
| --- | --- | --- | --- |
| 01 | 勾股定理：拼图证明 | 40 秒 | [源码](videos/01-pythagorean/pythagorean.py) · [成片](videos/01-pythagorean/pythagorean.mp4) |

## 本地渲染

```bash
# 需要 Pango/Cairo 开发库（Debian/Ubuntu）：sudo apt-get install libpango1.0-dev libcairo2-dev pkg-config
python3 -m venv venv
venv/bin/pip install manim
cd videos/01-pythagorean
../../venv/bin/manim -qh pythagorean.py Pythagorean
```

画幅在脚本里固定为 1080×1920、30fps。脚本不依赖 LaTeX，中文字幕使用「文泉驿正黑」（WenQuanYi Zen Hei），本机没有这个字体时可以改脚本里的 `FONT`。
