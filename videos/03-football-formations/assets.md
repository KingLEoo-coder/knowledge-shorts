# 素材清单 · 《十一人》

素材库目录（你本地 `Claude零号工地/03-football-formations/素材库/`）：

```
素材库/
  代码绘制/        C00–C15 战术板、图表、家谱（SVG 原件 + PNG 预览）+ formations.json
  AI生图/          G01–G10 场景画（待生成，提示词见下）
  公有领域图片/    F01–F05 老照片、版画（下载后附 来源与许可.txt）
  配乐/            6 首 CC0 候选曲
  参考片拆解/      三个参考片的截图拼版
```

版权原则：只用 ① 代码自己画的 ② AI 生成且不含真人肖像、队徽、商标的 ③ 公有领域或 CC0 / CC BY / CC BY-SA 的图片（后两种在片尾署名）④ CC0 配乐。**不用**比赛录像、转播截图、新闻社照片、俱乐部队徽。

---

## C · 代码绘制（已完成，16 张）

由 `tools/draw_assets.py` 生成，1920×1080，米白纸 + 朱红 + 宋体，和项目风格一致。SVG 可以直接放进 HyperFrames 合成里做动画（每个点都是独立的 `<circle>`）。

| 编号 | 文件 | 用在 | 内容 |
|---|---|---|---|
| C00 | 00-title-card | S02 / S13 | 片名卡「十一人」 |
| C01 | 01-how-to-read-4-4-2 | S03 | 4-4-2 读法，标注 4 / 4 / 2、门将不计 |
| C02 | 02-1872-england-vs-scotland | S04 | 1-1-8 对 2-2-6，传球虚线，0 : 0 |
| C03 | 03-1880s-pyramid-2-3-5 | S05 | 2-3-5 与金字塔三角 |
| C04 | 04-1925-offside-rule | S06 | 越位 3 人 → 2 人对比 |
| C05 | 05-1925-goals-chart | S06 | 进球 1192 → 1703 柱状图 |
| C06 | 06-1925-wm-letters | S06 | 竖放球场，连线成 W 和 M |
| C07 | 07-1953-wembley-deep-nine | S07 | 9 号回撤、中卫被拉出、身后空当 |
| C08 | 08-1958-4-2-4 | S08 | 4-2-4，后四人连成直线 |
| C09 | 09-1960s-catenaccio | S09 | 门闩：自由人在后卫线后 |
| C10 | 10-1974-total-football | S09 | 全攻全守：换位弧线 |
| C11 | 11-1989-press-4-4-2 | S10 | 两条线前压，圆环套住持球点 |
| C12 | 12-2009-passing-web-4-3-3 | S10 | 传球网 |
| C13 | 13-today-3-2-5 | S11 | 3-2-5，前五人点红 |
| C14 | 14-full-circle-2-3-5-vs-3-2-5 | S11 | 1880s 与今天并排 |
| C15 | 15-family-tree | S12 | 阵型家谱 |
| — | formations.json | 所有战术板 | 11 种阵型的球员坐标。球员编号在各阵型间固定，做补间动画时点会自然移动到新位置 |

还需要在 HyperFrames 里用代码做的动态部分（不是图片）：年份角标的数字滚动、点在阵型之间的补间、越位线移动、柱状图生长、家谱逐朵开花、纸面推入转场。

---

## G · AI 生图（10 张，待生成）

云端没有生图服务；你 Mac 上 HyperFrames 的生图需要登录 HeyGen 命令行工具，目前没装也没登录，所以先写好提示词。你可以用即梦、豆包、可灵或 Midjourney 生成，存成 `素材库/AI生图/G01.png` 这样的名字。

**统一风格后缀**（每条都接在后面，保证十张图像同一套片子）：

> 中文：电影感油画质感，柔和低饱和的暖色调，细腻胶片颗粒，构图留白，16:9 宽画幅，画面中不要出现任何文字、标志、队徽，人物只出现远景剪影，不画清晰的脸。
>
> English: painterly cinematic illustration, soft muted palette, fine film grain, generous negative space, wide 16:9, no text, no logos, no crests, people only as distant silhouettes with no detailed faces --ar 16:9

| 编号 | 镜头 | 中文提示词 | English prompt |
|---|---|---|---|
| G01 | S01 冷开场 | 清晨薄雾中的空旷草地球场，前景一只旧的棕色皮革足球，带缝线，草上有露水，低机位，远处球门模糊 | an old brown leather football with laces resting on dewy grass, empty pitch in morning mist, low camera angle, blurred goalposts in the distance |
| G02 | S04 备用 | 1872 年苏格兰格拉斯哥的板球场上举行的足球赛，维多利亚时代，穿长裤戴帽子的球员挤成一团追着球跑，围观的人戴高礼帽，阴天，像旧报纸木刻版画再上淡淡的棕褐色 | Victorian football match on a cricket ground in Glasgow 1872, players in caps and long trousers swarming after the ball, spectators in top hats, overcast sky, styled like a 19th-century newspaper wood engraving tinted sepia |
| G03 | S05 | 1880 年代英格兰北部工业小镇的球场，远处纺织厂烟囱冒烟，红砖排屋，黄昏，看台是木头栏杆，人群剪影 | 1880s football ground in a northern English mill town, smoking chimneys and red-brick terraced houses behind, dusk, wooden railings, crowd silhouettes |
| G04 | S06 | 1920 年代的木书桌上摊开一本旧规则书，旁边一支钢笔和一盏黄铜台灯，暖光，背景暗，书页上不要有可读文字 | an open old rulebook on a 1920s wooden desk, fountain pen and brass desk lamp, warm lamplight, dark background, pages without legible text |
| G05 | S07 | 1953 年 11 月伦敦温布利球场，两座白色圆顶塔楼在浓雾中若隐若现，看台上人头攒动成剪影，灰冷色调，潮湿 | Wembley stadium in November 1953, the two white domed towers half-hidden in thick fog, crowded terraces as silhouettes, cold grey tones, damp air |
| G06 | S08 | 1958 年瑞典夏日傍晚的露天球场，看台边一排白桦树，金色斜阳，草地很绿，远处的观众剪影 | open-air stadium in Sweden on a summer evening 1958, a row of birch trees by the stand, golden low sun, deep green grass, distant crowd silhouettes |
| G07 | S09 左 | 1960 年代米兰夜晚的大型混凝土球场，外墙有螺旋坡道，灯塔照明，深蓝冷色调，地面湿润反光 | a huge concrete stadium in Milan at night in the 1960s, spiral ramps on the outside, floodlight towers, deep cold blue tones, wet ground reflections |
| G08 | S09 右 | 1974 年夏天的现代主义球场，帐篷式透明屋顶，看台上一片橙色，明亮午后，轻快 | 1974 summer, modernist stadium with a tent-like transparent roof, stands filled with orange, bright afternoon, airy and light |
| G09 | S10 | 清晨的训练场，草地上整齐摆着一排排橙色标志桶，薄雾，远处的球员剪影在列队移动 | training pitch at early morning, rows of orange cones laid out in a tight grid, light mist, distant player silhouettes moving in formation |
| G10 | S13 结尾 | 傍晚中国城市居民楼之间的小块水泥球场，墙上用粉笔画了球门，几个孩子剪影在争论谁守门，一只旧皮球在地上，暖色路灯刚亮 | a small concrete pitch between apartment blocks in a Chinese city at dusk, a goal drawn in chalk on a wall, a few children as silhouettes arguing over who plays in goal, an old football on the ground, warm streetlights just turning on |

如果不想用 AI 图，S01、S05、S07、S13 这几张也能用代码画成简化的纸本风场景（像第二支的水墨远山那样），告诉我就行。

---

## F · 公有领域 / 开放许可图片（已下载 7 张可用）

在 `素材库/公有领域图片/`，每张的页面链接、作者、许可和片尾署名都在 `来源与许可.txt`。下载前逐张通过维基共享资源的接口核对过许可。

| 编号 | 用在 | 内容 | 许可 | 备注 |
|---|---|---|---|---|
| F01 | S04 | 1872 年英格兰对苏格兰比赛版画（William Ralston） | 公有领域 | 只有 506×665，做成画面里的“老报纸卡片”，不要铺满全屏，背景用 G02 |
| F03a | S07 | 1953 年匈牙利“黄金一代”合影 | CC BY-SA 3.0，片尾署名 Erky-Nagy Tibor / FORTEPAN | |
| F03b | S07 | 1953-11-25 匈牙利队在温布利赛前列队 | CC BY-SA 3.0，片尾署名 FORTEPAN | 2968px 清晰，可全屏；画面里没有双塔，双塔用 G05 |
| F04 | S09 右 | 1974 年世界杯决赛 | CC0（Bert Verhoeff / Anefo） | |
| F05 | S06 | 查普曼肖像 | 公有领域 | 只有 300×356，只能做小卡片 |
| F06 | S05 | 普雷斯顿 1888–89 首届联赛冠军队 | 公有领域 | 2685px，可全屏 |
| F07 | S04 前可选 | 1863-12-05《Bell's Life in London》报道足总成立会议的报纸版面 | 公有领域 | 长条图，适合做竖向滚动的“翻报纸”镜头 |
| ~~F02~~ | — | 1871 年英格兰橄榄球队合影 | 公有领域 | **不要用**：是橄榄球队，不是足球队 |

没找到开放许可的：1950 年代温布利双塔照片（用 G05 生图代替），以及 1958 巴西、1960 年代国际米兰、萨基米兰、瓜迪奥拉巴萨、今天的强队。这几站在分镜里本来就用代码战术板 + AI 场景，不需要你另外找。如果你有授权图库（视觉中国、Getty 等），可以给这几站各补一张真实照片。

CC BY-SA 的两张（F03a、F03b）要求片尾署名，并且严格说衍生作品也要用相同许可。短视频里通常的做法是片尾写清署名和许可；如果你介意，S07 只用 G05 生图也完全可以。

---

## 配乐 · CC0 候选（已下载）

全部来自 FreePD（CC0 公有领域，可商用、不需署名，片尾注明更好），经 [SoundSafari/CC0-1.0-Music](https://github.com/SoundSafari/CC0-1.0-Music) 镜像获取。我听不到音频，请你试听后选一首。

| 文件 | 作者 | 时长 | 备注 |
|---|---|---|---|
| Inventing Flight.mp3 | Bryan Teoh | 2:22 | 和第二支配乐同一作者，时长最接近本片 |
| Novus Initium.mp3 | Alexander Nakarada | 2:43 | 标题意为“新的开始” |
| Infinite Wonder.mp3 | Kevin MacLeod | 3:10 | |
| Travelers Notebook.mp3 | FreePD | 2:03 | 偏短，可循环或剪 |
| Nostalgic Piano.mp3 | FreePD | 3:16 | 怀旧钢琴 |
| Journey of Hope.mp3 | Alexander Nakarada | 5:49 | 需要剪辑 |

**另一个选项（仅限自己看）：** 参考片里那首《若如初见 (Slowed)》，已从参考视频里提取到 `Claude零号工地/music/若如初见-slowed.m4a`（2:13，混有原视频的音效）。它有版权，只能私用，不能发布；视频要发出去就换回上面的 CC0 曲目。

---

## 字体

和本机 HyperFrames 环境一致：Noto Serif CJK SC（中文）、Noto Serif Display（年份数字、英文斜体）。已装在 `~/Library/Fonts`。
