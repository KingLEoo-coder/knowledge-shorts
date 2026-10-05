# 02 · 人生的中点是 18 岁

竖屏 1080×1920，30fps，约 1 分 44 秒，带配乐和音效，无旁白（字幕驱动）。

## 视觉风格（v2：纸本杂志）

第一版用了粗黑体、霓虹色、发光和卡通图标，显得廉价。v2 改成杂志排版的思路：

- 米白纸面 `#F2EDE3` + 细颗粒，墨色 `#1C1A17`，唯一强调色朱红 `#C8432B`，日历时间用灰蓝 `#2F4B5C` 做对照。
- 标题和字幕用思源宋体（Noto Serif CJK SC），小标签用思源黑体 Regular，数字用 Noto Serif Display。
- 版心左对齐（左右边距 0.8 单位），顶部是章节编号 + 细分隔线，最上方一条细进度线。
- 不用发光、星空、渐变彩虹、卡通图标；人物和日历改成数字 + 月份格子，尺子用朱红 / 墨色深浅。
- `STYLE=B` 可切到暗夜极简（近黑 + 暖金），`STYLE=C` 切到文艺手账（霞鹜文楷）。三套样帧在 `style/` 里。

## 讲了什么

| 段落 | 内容 | 主要画面 |
|---|---|---|
| 开场 | 活到 80 岁，人生中点在哪？日历上是 40，感觉上是 18 | 人生进度条，刻度向右挤压，中点读数从 40 掉到 18 |
| 01 为什么越活越快 | 同样一年，5 岁和 40 岁感觉完全不同 | 两组 12 格月份同时涂色：5 岁只涂 3 格，40 岁涂满 12 格 |
| 02 关键是比例 | 让内（1877）的比例理论：1 年占 5 岁人生的 1/5，占 50 岁人生的 1/50 | 两个饼图；1 段朱红 ≈ 10 段灰蓝 |
| 03 重画一把人生尺子 | 从有记忆的 4 岁算到 80 岁，按"感觉长度"重画，正中间是 18 岁 | 76 格竖尺子从等宽变形成对数刻度，扫描线读数停在 17.9 |
| 04 为什么偏偏是 18 | 年龄每翻一倍，感觉上一样长；4×4.5=18，18×4.5≈80；中点 = √(4×80) | 感觉长度 vs 日历长度对照条；×4.5 跳跃 |
| 05 你走到哪了 | 18 岁 50%，25 岁 61%，30 岁 67%，40 岁 77% | 环形进度 |
| 06 反转 | 这只是假说；另一种解释是"新鲜事"变少了，重复的日子在记忆里被压缩 | 7 个相同格子压成 1 格 vs 7 个不同形状铺开；18 变成 ? |

## 文件

- `life_midpoint.py`：Manim 画面源码。渲染时把关键节拍（重音、转场、计数）写进 `marks.json`。
- `music.py`：配乐和音效合成器，读 `marks.json` 让鼓点、重音、上升音、翻页声对齐画面。
- `marks.json`：本次渲染的节拍表。
- `life_midpoint.mp4`：成片。

## 重新渲染

```bash
# 依赖：manim、numpy、scipy；字体：apt install fonts-noto-cjk fonts-noto-core（B/C 风格另需 fonts-inter、fonts-lxgw-wenkai）
manim --disable_caching -q h life_midpoint.py LifeMidpoint      # 画面 + marks.json
python music.py marks.json music.wav                              # 配乐
ffmpeg -i media/videos/life_midpoint/1920p30/LifeMidpoint.mp4 -i music.wav \
  -c:v copy -c:a aac -b:a 192k -shortest life_midpoint.mp4
PREVIEW=1 manim --disable_caching -q l life_midpoint.py LifeMidpoint   # 快速预览（540×960，15fps）
```

## 配乐与版权

配乐和全部音效都由 `music.py` 用 numpy 现场合成（84 BPM，Am–F–C–G 弦乐垫 + 钢琴琶音 + 轻底鼓和沙锤 + 冲击/上升/嗖声/翻页声），不含任何采样或外部素材，没有第三方版权，可用于社交媒体发布。

## 事实与出处

- 比例理论：法国哲学家 Paul Janet（保罗·让内）1877 年提出，一段时间的主观长度与当时年龄成反比（"Janet's law"）。参见 [arXiv:2310.05945](https://arxiv.org/pdf/2310.05945) 对该模型的综述。
- "从 4 岁算起"：童年失忆，多数人最早的连续记忆约在 3～4 岁。4 岁和 80 岁都是取整的假设，换起点终点中点会变（比如从 3 岁算是 √240≈15.5）。
- 这是一个**假说**而非定律，实证研究结论不一；"新鲜经历越少、记忆越稀疏、回想时觉得时间越快"是心理学里另一种常见解释，片中以"另一种解释"呈现。

## 参考的开源项目

做这支片前在 GitHub 上看了几个给 AI 编程助手用的视频制作 skill，借鉴了它们的做法（没有复制代码或素材）：

- [Vincentwei1021/anything2explainer](https://github.com/Vincentwei1021/anything2explainer)：Remotion 讲解视频 skill。借鉴：每个镜头一个发光主角、元素入场后要有持续动作、章节进度条和胶囊 HUD、数字换成可感知的尺度、结尾回扣。
- [Vincentwei1021/video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft)：反"PPT 式"的运镜和节拍对齐思路。
- [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill)、[AmitSubhash/3brown1blue](https://github.com/AmitSubhash/3brown1blue)：Manim 版的同类 skill。
- [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)：完整的智能体视频生产流水线（需要 TTS / 生图等外部服务）。
