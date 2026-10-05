# 02 · 人生的中点是 18 岁

竖屏 1080×1920，30fps，约 2 分钟，带配乐和轻音效，无旁白（中英双语字幕驱动）。

## 版本

- v1：粗黑体 + 霓虹发光，显得廉价。
- v2：纸本杂志排版（米白纸面 + 朱红 + 宋体），配乐是代码合成的，被反馈"有点阴间"。
- **v3（当前）**：参考抖音作品《opus家族史》（Vibe知识大赏）的纪录片做法重做——每一段都是一幅完整的"画面场景"，
  上面叠左上角的章节标题和居中的中英双语字幕；配乐换成公有领域（CC0）的现成曲目，不再自己合成。

## 视觉风格

- 场景底图全部由 `scenery.py` 用 numpy + Pillow 程序化绘制（水墨山水、四季山野、烛光书桌、旧纸、立轴、各时段天色），
  渲染时缓慢推镜（Ken Burns），场景之间交叉淡化，叠加萤火、花瓣、落叶、雪花、浮尘等粒子。
- 字体：思源宋体（Noto Serif CJK SC）做标题和字幕，英文用 Noto Serif 斜体。
- 色彩：米白纸 `#EFE8DA`、墨 `#1C1A17`、唯一强调色朱红 `#C8432B`，朱红印章做点睛。
- 字幕版式：中文一行 + 细线红菱形分隔 + 英文斜体一行；左上角是红色短线 + 章节标题 + 小字副标题。
- 暗场景底部有一层渐变压暗，保证浅色字幕在雪景和晴空上也看得清。

## 讲了什么

| 段落 | 内容 | 画面 |
|---|---|---|
| 开场 | 活到 80 岁，人生中点在哪？ | 水墨远山、朱红落日、浮尘；标题"人生的中点" + 印章 |
| 5 岁 vs 40 岁 | 小时候一个暑假像永远，长大后一年一眨眼 | 夏夜山野萤火；40 岁时春夏秋冬快速轮转两遍，花瓣、萤火、落叶、雪花随季节切换 |
| 1877 | 保罗·让内的比例理论：1 年占 5 岁人生的 1/5，占 50 岁人生的 1/50 | 烛光书桌，泛黄手稿上画出两个饼图 |
| 一幅立轴 | 把 4～80 岁画成一幅立轴，按"感觉"重新丈量，正中间是 18 岁 | 立轴展开，刻度从等距变成对数，红色虚线扫到中点，盖"十八"印；14 年 vs 62 年 |
| 为什么是 18 | 年龄每翻一倍，感觉上的路一样长；中点 = √(4×80) ≈ 17.9 | 毛笔笔触（感觉长度，一样长）对照朱红细线（日历年数，越来越长） |
| 折成一天 | 把感觉中的一生折成一天：18 岁正午，30 岁下午四点，40 岁西斜，60 岁入夜 | 天色从清晨到夜晚，太阳沿弧线落下，大号时钟走字 |
| 反转 | "别慌"，这只是假说；另一种解释是新鲜事变少了 | 光秃梅枝 = 重复的日子；每个"第一次"开出一朵梅花 |
| 结尾 | 你感觉中的中点也许还远没到，多做一些"第一次" | 回到水墨山水 |

## 文件

- `scenery.py`：生成 `assets/` 里的全部底图（约 30 秒）。
- `life_midpoint.py`：Manim 画面源码；渲染时把节拍（转场、计数、出现）写进 `marks.json`。
- `music.py`：混音脚本，读 `marks.json`，把配乐淡入淡出、在"是不是有点慌？"到"别慌。"之间压低音量，并在转场处叠很轻的嗖声 / 提示音（音效由代码生成）。
- `marks.json`：本次渲染的节拍表。
- `life_midpoint.mp4`：成片。

## 重新渲染

```bash
# 依赖：manim、numpy、scipy、Pillow、ffmpeg；字体：apt install fonts-noto-cjk fonts-noto-core
python scenery.py                                                   # 生成 assets/
manim --disable_caching -q h life_midpoint.py LifeMidpoint          # 画面 + marks.json
python music.py marks.json "From Page to Practice.mp3" music.wav    # 混音
ffmpeg -i media/videos/life_midpoint/1920p30/LifeMidpoint.mp4 -i music.wav \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart life_midpoint.mp4
PREVIEW=1 manim --disable_caching -q l life_midpoint.py LifeMidpoint   # 快速预览（540×960，15fps）
```

## 配乐与版权

- 曲目：**"From Page to Practice"**，作曲 Bryan Teoh，2020 年。
- 来源：[FreePD.com](https://freepd.com)，经 GitHub 上的 CC0 音乐合集
  [SoundSafari/CC0-1.0-Music](https://github.com/SoundSafari/CC0-1.0-Music)（`freepd.com/From Page to Practice.mp3`）获取。
- 许可：作者声明献给公有领域（文件元数据："This piece was composed and dedicated to the Public Domain in 2020."），
  FreePD 曲库按 CC0 1.0 发布，可商用、可用于社交媒体，无需署名（这里仍注明作者以示感谢）。
- 音频文件本身没有放进仓库，按上面的路径下载即可重新混音。
- 转场的嗖声和提示音由 `music.py` 用 numpy 生成，无第三方素材。

## 事实与出处

- 比例理论：法国哲学家 Paul Janet（保罗·让内）1877 年提出，一段时间的主观长度与当时年龄成反比（"Janet's law"）。参见 [arXiv:2310.05945](https://arxiv.org/pdf/2310.05945) 对该模型的综述。
- "从 4 岁算起"：童年失忆，多数人最早的连续记忆约在 3～4 岁。4 岁和 80 岁都是取整的假设，换起点终点中点会变（比如从 3 岁算是 √240≈15.5）。
- "折成一天"里的时刻按同一模型换算：时刻 = 24 × ln(年龄/4) / ln(20)，18 岁≈12:00，30 岁≈16:09，40 岁≈18:27，60 岁≈21:42。
- 这是一个**假说**而非定律，实证研究结论不一；"新鲜经历越少、记忆越稀疏、回想时觉得时间越快"是心理学里另一种常见解释，片中以"另一种解释"呈现。

## 参考

- 抖音《opus家族史》（Vibe知识大赏）：借鉴它"每段一幅完整场景 + 中英双语字幕 + 左上章节标题"的纪录片节奏，没有使用其中任何素材。
- 做 v1/v2 时看过的 GitHub 视频 skill：[anything2explainer](https://github.com/Vincentwei1021/anything2explainer)、[video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft)、[manim-skill](https://github.com/Yusuke710/manim-skill)、[3brown1blue](https://github.com/AmitSubhash/3brown1blue)、[OpenMontage](https://github.com/calesthio/OpenMontage)。
