# 豆包对话 → 博客文章 · 交接文档

> 本文档面向接手此任务的 AI agent。目标是：把已抓取的 **1785 条豆包对话**（科研 + 学习两大板块），
> 整理成对外展示的个人博客文章，**符合博客既有文风与工程规范**。
>
> 阅读顺序建议：先读「一、这是什么」，再读「二、数据在哪」，
> 然后重点读「四、写作规范」（这是最容易出错、也是最影响成品质量的部分），
> 最后按「五、执行流程」动手。

---

## 〇、地址速查（绝对路径，复制即用）

### 博客本体

| 用途 | 绝对路径 |
|---|---|
| **博客仓库根目录**（所有构建命令都在这里执行） | `/Users/hua/Desktop/科研博客` |
| 写研究长文 → 放这里 | `/Users/hua/Desktop/科研博客/articles_src/` |
| 写系统笔记 → 放这里 | `/Users/hua/Desktop/科研博客/notes/` |
| 调研档案（已有 80 份，通常不动） | `/Users/hua/Desktop/科研博客/survey/` |
| 构建后的网页成品 | `/Users/hua/Desktop/科研博客/articles/` |
| 首页（`index.html`，构建时自动重写，勿手改） | `/Users/hua/Desktop/科研博客/index.html` |
| 样式与脚本（KaTeX 公式渲染在 `assets/blog.js`） | `/Users/hua/Desktop/科研博客/assets/` |
| 发布脚本（一键构建+提交+推送） | `/Users/hua/Desktop/科研博客/publish.sh` |

### 豆包对话原料（**不在博客仓库里**，在另一个目录）

| 用途 | 绝对路径 |
|---|---|
| **完整原始对话（1813 个 md，写文章的原料）** | `/Users/hua/Desktop/pspstain/doubao_export/raw/` |
| 链接清单（1791 条元信息） | `/Users/hua/Desktop/pspstain/doubao_export/doubao_all_share_links_1791.json` |
| 抓取状态（补跑时靠它跳过已完成） | `/Users/hua/Desktop/pspstain/doubao_export/fetch_state.json` |
| 抓取器（纯 HTTP，无需浏览器与登录，支持断点续跑） | `/Users/hua/Desktop/pspstain/doubao_export/fetch_share_pages.py` |
| Kimi 导出任务（持续产出新链接） | `/Users/hua/Documents/kimi/tasks/2026-10-24/18-08-19-ea27a2c9/state/state.json` |

> **注意**：原料在 `~/Desktop/pspstain/`，**不在** `~/Desktop/科研博客/` 里。
> 两个目录都要用到：原料在 pspstain，成文写进科研博客。

### 本地预览

```bash
cd /Users/hua/Desktop/科研博客
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

线上地址（推送后约 1 分钟生效）：**https://xu2388.github.io**

---

## 一、这是什么

### 1.1 项目背景

作者是一位研究生，主线研究方向是 **H&E → IHC 虚拟染色**（用深度学习把 H&E 病理切片
直接生成对应的 IHC 免疫组化染色，省试剂省人力）。一年多来在豆包 / DeepSeek 等 AI 助手上
积累了上千条科研与学习对话，这些对话构成了博客的原始素材。

博客定位：**个人学术博客**，两大内容板块——

| 板块 | 内容 | 主要产出目录 |
|---|---|---|
| **科研** | 虚拟染色主线的方法研究、论文精读、调研档案 | `articles_src/`、`survey/` |
| **学习** | 专业课复习、编程/算法/英语等系统笔记、教程 | `notes/`、`articles/`（004-007） |

### 1.2 博客现状（截至本交接）

- 已上线：https://xu2388.github.io
- 仓库：`~/Desktop/科研博客`（git，远程 `git@github.com:xu2388.github.io.git`，分支 `main`）
- 已有内容：**8 篇研究文章**（`articles_src/`，编号 008-015）、**25 篇系统笔记**（`notes/`）、
  **DeepSeek 270 条 + 豆包 98 条**问答存档（`articles/kb/`、`articles/kb-doubao/`）、
  **80 份调研档案**（`survey/`）、论文分享屋、资料库审计清单。
- **缺口**：豆包侧只入了 98 条（早先小批量），全量 1785 条中绝大多数**尚未**成文。

### 1.3 核心原则（务必遵守）

1. **不替读者做价值判断**——哪些对话值得成文、归到哪个板块，由 AI 自己读内容判断。
   仓库里**没有也不需要**自动分类器；用 `ls` / `grep` 按标题和正文内容自行检索即可。
2. **对外展示的约束优先于信息完整**——口语、寒暄、跑题、私人信息一律不进文章。
3. **忠实于源材料**——数值、公式、超参不得编造；不确定处显式标注。
4. **过程保留，措辞打磨**——博客定位是"个人探索记录"，允许保留真实困惑与自我推翻，
   但要用书面语重写，不是删掉过程。

---

## 二、数据在哪

### 2.1 两处数据源的区别（最容易搞混的地方）

| | 完整原始档案 | 博客仓库内副本 |
|---|---|---|
| **路径** | `~/Desktop/pspstain/doubao_export/raw/` | `~/Desktop/科研博客/raw_exports/doubao_share_raw/` |
| **文件数** | **1813**（1785 个会话 + 28 个重名补充） | **102**（早先小批量，98 个会话） |
| **命名** | `对话标题.md` | `NNN_对话标题.md`（带序号） |
| **用途** | **写文章的原料，从这里读** | 供 `build_doubao_kb.py` 生成网页问答页 |

两套内容通过 front matter 里的 `conv_id` 一一对应，**已核对无缺口**（旧集 98 ⊂ 新集 1785）。

### 2.2 全量原始档案格式

`~/Desktop/pspstain/doubao_export/raw/` 下每个文件：

```markdown
---
title: 实现最小可运行的H&E→IHC浓度空间Diffusion
msg_count: 30
url: https://www.doubao.com/thread/a104400209e3e
conv_id: 38441506454520835
---

### 我（提问）
（用户原话）

### 豆包（回答）
（AI 原话）
```

正文完全未删减，保留对话原貌。

### 2.3 配套文件（都在 `~/Desktop/pspstain/doubao_export/`）

| 文件 | 用途 |
|---|---|
| `raw/` | **1813 个原始对话 md（主原料）** |
| `doubao_all_share_links_1791.json` | 1791 条会话的元信息（id / title / 消息数 / 分享链接） |
| `doubao_all_share_links_1791.md` | 同上，表格版 |
| `fetch_state.json` | 抓取状态（done / failed），**补跑抓取时靠它跳过已完成** |
| `fetch_share_pages.py` | 抓取器（纯 HTTP，无需浏览器与登录），支持断点续跑 |
| `doubao_missing_207.md` | 早先缺链接的 207 条会话（含失败原因） |
| `README.md` / `api_reference.md` | 豆包会话枚举与分享链接生成的原始方案说明 |

**链接来源**（持续增长）：`~/Documents/kimi/tasks/2026-10-24/18-08-19-ea27a2c9/state/state.json`
——Kimi 的导出任务仍在跑，会不断产生新会话与新链接。

### 2.4 检索方式（不需要任何自建索引）

文件名即对话标题，直接用 shell：

```bash
cd ~/Desktop/pspstain/doubao_export/raw

# 按标题找
ls | grep -i "虚拟染色"

# 按正文内容找（这是最有效的手段）
grep -l "扩散模型" *.md
grep -l "InstanceNorm" *.md

# 看某个对话有多少内容（消息数在 front matter 里）
wc -c 某文件.md

# 读一条完整对话
cat 某文件.md
```

> **注意**：不要一次性 `cat` 全目录或用 `grep -rn` 扫全文，1813 个文件共 63 MB，
> 会触发内存限制被系统杀掉。**一次只处理一个文件**，或用 `grep -l` 先筛出候选再逐个读。

---

## 三、博客工程规范

> 本章所有相对路径都相对于仓库根目录 `/Users/hua/Desktop/科研博客`。
> 比如 `articles_src/015-xxx.md` 的完整路径是
> `/Users/hua/Desktop/科研博客/articles_src/015-xxx.md`。

### 3.1 两种文章源文件，**用途不同，别混用**

#### A. `articles_src/NNN-标题.md` → 研究文章（长文）

- 归入「研究 / 调研 / 论文」栏目，适合**深度主题**：方法剖析、论文精读、实践教程。
- 页面上出现于 `articles/NNN-标题.html`，进入 `articles/list-research.html` 等归档页。

front matter：

```markdown
---
title: 从零实现浓度空间扩散基线 M0：H&E→IHC 虚拟染色的最小可行实践
date: 2026-10-25
tags: ["虚拟染色","扩散模型","浓度域","Beer-Lambert","实践教程"]
category: 研究
summary: 100-200 字摘要，会出现在列表页与首页预览。
source: notes/M0实现笔记.md
---
```

- `date` 决定归档排序（新的在前）；`tags` 必须是 **JSON 数组**；`category` 决定进哪个栏目。
- 可选 `category`：`研究` / `调研` / `课程笔记` / `学习笔记` / `随笔` / `知识库` / `论文` / `资料库`。
- 正文第一行的 `# 标题` 会被构建脚本自动剥离（模板已渲染），保留无害但可省。

#### B. `notes/标题.md` → 系统笔记（按学科分组）

- 归入「课程笔记 / 学习笔记」栏目，适合**知识点覆盖**：一门课、一个技术栈的完整复习。
- 页面上出现于 `articles/notes/标题.html`，按 `subject` 分组进 `articles/notes-index.html`。

front matter：

```markdown
---
title: 循环神经网络语言模型（RNN-LM）详解
subject: 深度学习/神经网络
category: 课程笔记
source: 013_循环神经网络语言模型（RNN-LM）详解.md
summary: 一句话说明这篇覆盖了什么。
---
```

- `subject` 决定学科分组，**必须**从 `build_notes.py` 的 `SUBJECT_ORDER` 里选，
  否则会掉进「其他」组：
  `计算机网络`、`数据库/MySQL`、`JavaWeb`、`数据结构与算法`、`深度学习/神经网络`、
  `大数据技术`、`信号与系统`、`数字图像处理`、`高等数学/最优化`、`大学物理`、
  `英语/雅思`、`思政/毛概/近代史`、`虚拟染色/科研`、`其他`。
- `source` 指向 `raw_exports/doubao_share_raw/` 里的文件名（带 `NNN_` 前缀），
  页面底部会自动生成「原始对话」回链。**该文件必须真实存在**，否则回链 404。
  - 写新笔记时，若目标对话在 `raw/` 里有但 `raw_exports/doubao_share_raw/` 里没有，
    先按旧命名规则拷过去：`cp raw/<标题>.md raw_exports/doubao_share_raw/NNN_<标题>.md`。
  - 一篇笔记来自多条对话时，写成 `source: 010_甲.md（另含 011_乙.md）` 即可，
    构建脚本会拆成多个回链（已支持）。

### 3.2 Markdown 渲染能力（`build_knowledge_base.render_md`）

**支持**：`#`~`####` 标题、``` 代码围栏、`>` 引用、`|` 表格、`-`/`*` 列表、`1.` 有序列表、
`---` 分隔线、行内 `` `code` ``、`**粗体**`、`*斜体*`、图片 `![]()`。

**不支持**：脚注、任务列表、内嵌 HTML、表格内的换行。

两个必须注意的坑：

1. **连续非空行会被合并成一个 `<p>`**。要让公式、代码、表格独立成块，前后必须留空行。
2. **公式走 KaTeX，站点已集成**（`assets/blog.js` 的 `initMath()`，按需从 CDN 加载，
   取不到则原样显示）。写法：
   - 行内公式：`$x = \frac{a}{b}$`
   - 独立公式：`$$...$$` 单独成段，前后留空行
   - `ignoredTags` 包含 `pre`/`code`，所以**代码块里的 `$` 不会被误解析**。

### 3.3 构建流水线

```bash
cd ~/Desktop/科研博客

python3 build_articles.py        # articles_src/*.md → articles/*.html
python3 build_notes.py           # notes/*.md → articles/notes/ + articles/notes-index.html
python3 build_knowledge_base.py  # DeepSeek 270 条 → articles/kb/
python3 build_doubao_kb.py       # 豆包 → articles/kb-doubao/ + articles/doubao-index.html
python3 build_index.py           # 生成 list-*.html 归档页 + 重建首页 + 数据条
python3 fix_nav.py               # 统一全站左侧导航的相对路径（**必须在 build_index 之后**）
```

或一键（构建 + 提交 + 推送 + GitHub Pages 自动部署）：

```bash
cd ~/Desktop/科研博客 && ./publish.sh "新增 XXX 若干篇"
```

发布后约 1 分钟上线 https://xu2388.github.io ，部署进度看
https://github.com/xu2388/xu2388.github.io/actions 。

### 3.4 索引与首页的自动行为

- `build_index.py` 扫描 `articles/*.html` 里的 `<script id="meta">` JSON，按 `category` 自动归栏，
  **新文章不需要手动登记**，构建完就在归档页里。
- 首页每栏预览条数写死在 `build_index.py` 的 `PREVIEW_N`（研究 3、学习笔记 3、知识库 2…）。
  **新文章进不了首页预览是正常现象**，点「全部 N 篇 →」进归档页即可，不要为此改代码。
- `data/nav_counts.json` 由 `build_index.py` 自动生成，供 `fix_nav.py` 使用，不要手改。
- 首页大分组是「科研 / 学习 / 随笔」三组，映射关系在 `build_index.py` 的 `GROUPS`。

### 3.5 编号规则

`articles_src/` 用 `NNN-标题.md` 编号，**当前已占用 008-015**（007 及以下早前已用）。

> **开工前必须先 `ls articles_src/`**，取最大编号 +1。
> 曾发生两个文件都叫 `011-` 的撞号事故，导致一个被覆盖。

---

## 四、写作规范（对外展示，最重要）

> 对标文件（读一遍就知道目标文风）：
> `articles_src/008-浓度空间Diffusion.md`、`013-PSPStain语义保持精读.md`、
> `015-浓度空间扩散M0实践.md`、`notes/浓度空间Diffusion.md`。

### 4.1 语气与人称

- 全文用**书面学术语**，人称用「本文」「作者」，**不用「你/我/咱」的对话体**。
- 禁：口语缩写、「牛逼」「绝了」、emoji、网络梗、「照抄就行别问为什么」这类随口一说。
- 禁：对着 AI 说话的语气（「你听懂了吗」「你觉得呢」「如你所见」）。
- 允许并鼓励：**克制的第一人称**表达真实研究经历（「笔者」「实验进行到第 3 天仍未……」），
  这是个人博客的特色，不要抹平。

### 4.2 去尴尬处理（作者明确要求）

原始对话里有大量「私事 / 随手问 / 跑题」内容，进文章前必须清理：

| 类别 | 处理 |
|---|---|
| 寒暄、语气词、单字母回信（「d」「嗯」「好」） | 整条删除 |
| 跑题提问（快递查询、穿搭、算命、显卡价格、感情话题） | 整条删除 |
| 私人路径与账号（`/root/autodl-tmp/...`、服务器 IP、API key） | 泛化为「项目目录」「远程实例」；**密钥类一律不得出现** |
| 引用链接里的中间格式（`kimi-cite://xxx`） | 换成干净 URL 或正式出处；换不了就删 |
| 自嘲、情绪化吐槽、抱怨 | 改写为客观陈述；确有必要保留的转述为「当时面临的主要困难是……」 |
| 中途的自我重复、无关的图片占位 | 删除；`[图片]` 占位符在成文时也要清理 |

**保留**（这些是文章的含金量）：

- 作者自己提出的**精妙类比**（如用「去雾」解释扩散模型）——这是教程的亮点，
  保留并书面化，比空讲机制强得多。
- 体现真实性的细节：「单卡 RTX 4060」「AutoDL 实例经常关机」「远程调试断点续训」这类。
- **研究过程的真实痕迹**：困惑、试错、自我推翻、方案取舍。博客定位是探索记录，
  不要把过程磨光成结论。
- 具体的报错信息、数值波动等**真实证据**（脱敏后）。

### 4.3 结构

研究文章推荐骨架（可按主题调整，但要有明确层次）：

```
摘要 / 一句话概括（可用引用块突出）
一、背景与问题（为什么这事值得做）
二、方法设计（原理 + 公式 + 关键取舍）
三、实现与实验（配置、张量形状、评测设置）
四、结果与判据（指标 / 消融 / 失败案例）
五、局限与下一步（诚实标注未完成的部分）
参考文献（作者、标题、期刊/会议、年份、链接）
```

系统笔记推荐骨架：

```
概述 → 核心概念 → 逐点展开（分节 + 公式 + 表格）→ 常见误区 → 总结要点
```

- 章节用 `## 二、xxx` 的中文数字编号（现有文章一致）。
- **公式**用 `$...$` / `$$...$$`，前后留空行；**代码**用 ``` 围栏。
- **表格**用于方法对比、指标对照、参数表——现有精读文章大量用表，可读性显著更好。
- 论文精读类文章开头用引用块给出「论文 / 作者 / 发表 / 代码 / 方法名缩写」信息块，
  格式照抄 `013-PSPStain语义保持精读.md`。

### 4.4 诚实性

- **数值必须来自源材料**：指标、超参、公式、张量形状与源对话一致。
  不确定就写「约」「第一版采用」，**绝不编造**。
- 未完成的实验要写明：「截至合成数据探针阶段指标达 0.99；真实数据判定实验尚未完成」，
  不能把阶段性结果说成结论。
- 引用他人工作要标明出处；不确定的作者/年份不要硬写。

### 4.5 摘要（summary）

- 100-200 字，**信息密度高**：包含结论或核心方法，不要写「本文介绍了……」的空话。
- 出现在列表页和首页预览，是读者决定点不点进来的唯一依据。
- 现有范例：
  > 以比尔-朗伯定律为物理基础，把 H&E 与 IHC 分解为染料浓度图，仅在 DAB 浓度通道上做条件扩散并以 H/E 浓度作为干净条件，最后经染色矩阵回投重建 IHC RGB，据此设计可判定该路线是否成立的最小基线 M0。

### 4.6 常见错误清单

- ❌ 出现「你」「我们」等对话人称
- ❌ 保留跑题内容、快递/穿搭/算命
- ❌ 暴露本地路径、服务器地址、密钥
- ❌ 编造或"大约化"具体数值
- ❌ 公式前后不留空行（会被并进段落）
- ❌ `tags` 写成 YAML 列表（必须是 JSON 数组，否则解析失败静默丢弃）
- ❌ 忘记检查编号撞车
- ❌ 新文章没进首页预览就去改 `PREVIEW_N`（正常现象，不用管）

---

## 五、执行流程

### 5.1 标准循环（一次做一篇或一组）

```
1. 选题    → 用 ls/grep 在 raw/ 里按关键词搜标题与正文，读几条候选
2. 通读    → cat 完整对话，确认信息量与可公开性
3. 定位    → 决定放 articles_src/（研究长文）还是 notes/（系统笔记）
4. 写作    → 按第四节规范重写；建 src 文件，front matter 齐全，避开编号撞车
5. 构建    → python3 build_articles.py / build_notes.py → build_index.py → fix_nav.py
6. 验收    → 打开生成的 HTML 看排版；确认进了对应归档页
7. 提交    → git add -A && git commit（发布用 ./publish.sh）
```

### 5.2 选题建议（不设硬指标，凭判断）

优先挑选：
- **信息密度高**——长对话（消息数多）通常含完整推导、反复追问、方案迭代。
- **能自圆其说**——AI 的回答构成一套完整解释，可以独立成篇。
- **踩过真实的坑**——有失败、有对比、有"后来发现不对"的转折，是最有价值的部分。
- **可公开**——无隐私、无敏感、无尴尬。

可以整条忽略的：寒暄、单问单答、纯工具杂事、纯情绪闲聊。

### 5.3 建议的推进顺序

按投入产出比：

1. **科研主线**（虚拟染色相关，raw/ 里 `ls | grep -i "染色\|stain\|扩散\|论文"`）
   → 写成 `articles_src/` 的研究长文。这是博客的立身之本，最能体现水平。
2. **深度方法对话**（如 `实现最小可运行的H&E→IHC浓度空间Diffusion`，30 条，
   已产出示范文章 `015`）→ 同上。
3. **课程系统笔记**（`计算机网络`、`数据结构与算法`、`MySQL`、`JavaWeb`、`信号与系统`、
   `大数据技术`等，各有长对话）→ 写成 `notes/`，归入对应 `subject`。
4. **英语 / 思政 / 数学**长对话 → 同样进 `notes/`。

### 5.4 批量灌入问答存档（可选，非必需）

若想把 1785 条对话都做成可浏览的问答页：

```bash
cd ~/Desktop/科研博客
cp ~/Desktop/pspstain/doubao_export/raw/*.md raw_exports/doubao_share_raw/
python3 build_doubao_kb.py    # 生成 articles/kb-doubao/ + articles/doubao-index.html
python3 build_index.py && python3 fix_nav.py
```

**注意**：
- 全量 1813 条一次性构建**会因资源限制被系统中断**（实测 300 条约 17 秒，
  1813 条会超时被杀）。需要**分批**：先把文件按 300 条一批分次拷入，
  每批跑一次 `build_doubao_kb.py`（该脚本只扫目录、不清空既有产物，可反复增量执行）。
- 体积代价：`raw_exports/` 会从 23 MB 涨到约 86 MB，`articles/kb-doubao/` 约 60 MB+。
  这些会随 git push 全部公开。**动手前先问作者是否愿意公开**，
  或者把 `raw_exports/` 加入 `.gitignore`（当前仓库**没有** `.gitignore`）。
- 归档页的分类由 `build_doubao_kb.py` 的 `CAT_KW` 关键词表决定，
  **该分类只影响问答页的分组标签，不影响文章质量**。

---

## 六、已知坑清单（踩过的，别再踩）

| 坑 | 现象 | 处理 |
|---|---|---|
| **编号撞车** | 两个文件都叫 `011-xxx.md`，后者覆盖前者 | 每次新建前 `ls articles_src/` |
| **source 回链 404** | 笔记底部「原始对话」链接打不开 | `source` 指向的文件必须存在于 `raw_exports/doubao_share_raw/`；不存在就 cp 过去 |
| **source 多来源写法** | 旧版本会把 `010_x.md（另含 011_y.md）` 整串当文件名 → 回链 404 | **已修复**（2026-10-25 改 `build_notes.py`，现在自动拆分成多个链接）。仍建议只写一个文件名 |
| **公式与段落粘连** | 公式和正文连成一段 | 公式块前后必须空行 |
| **`tags` 解析失败** | 文章在列表页没有标签 | `tags` 必须是 JSON 数组 `["a","b"]` |
| **全量构建被杀** | 1813 条一次构建，进程 SIGTERM | 分批，每批约 300 条 |
| **grep 全目录爆内存** | 进程被 kill | 一次只读一个文件；先用 `grep -l` 筛候选 |
| **git index.lock 残留** | `git status` 报 `unable to unlink .git/index.lock` | 删除 `~/Desktop/科研博客/.git/index.lock` 后重试 |
| **文章进不了首页预览** | 新文章不在首页前 3 条 | 正常现象，进归档页即可，不要改 `PREVIEW_N` |
| **旧假设作废** | 曾以为"公式以 LaTeX 原文显示" | **错**。站点已接 KaTeX，`$...$` 会正常渲染 |

---

## 七、当前未提交改动

交接时工作区有未提交内容（`git status`）：

- 新增：`articles_src/015-浓度空间扩散M0实践.md` + `articles/015-浓度空间扩散M0实践.html`
  （示范文章，来源对话《实现最小可运行的H&E→IHC浓度空间Diffusion》）
- 修改：多篇已生成 HTML、`index.html`、`list-*.html`、`data/nav_counts.json`
- 新增：`raw_exports/doubao_share_raw/013_循环神经网络语言模型（RNN-LM）详解.md`
  （补齐 RNN-LM 笔记的回链目标）

> 这些**尚未 commit**。接手者可以先 `git status` 确认，再决定是提交还是回退。

---

## 八、一句话总结

> 原料在 `~/Desktop/pspstain/doubao_export/raw/`（1813 个对话 md，文件名即标题，
> 用 `grep -l` 搜正文）；成文守 `articles_src/`（研究长文）或 `notes/`（系统笔记）
> 两套 front matter 规范；**文风照抄 `013`/`015` 两篇现有文章**，
> 对外展示的去尴尬规则见第四节；构建跑 `build_articles/build_notes → build_index → fix_nav`，
> 发布 `./publish.sh`；开工前先 `ls articles_src/` 避让编号。
