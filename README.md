# 个人主页：一页简历 + 研究档案

一个本科生的个人主页。首页是**简历**，其余页面是简历的**证据**。
纯静态 HTML + CSS，零依赖、无框架、无追踪，可直接托管在 GitHub Pages。

面向的读者是面试官，不是同行：先看简历，再决定要不要点进去。

## 信息架构

```
index.html      简历：自述 / 研究经历 / 学习经历 / 技能 / 写作 / 站外 / 全部内容
├── research.html      研究：研究记录、论文精读、研究笔记、调研档案、论文导读
│     └── articles/list-*.html
├── writing.html       写作：随笔、教程、站外 CSDN 文章
├── notes.html         笔记：20 门学科，每门一页 → subject/<slug>.html
└── archive.html       索引：全站可搜索的目录
```

首页不按「科研 / 学习」这种身份分栏，因为任何本科生都能这么分，没有信息量。
简历只回答三件事：**在追什么问题、为此做了什么、做出来的东西在哪**。

首页中段是四块并列的版面（研究经历 / 学习经历 / 技能 / 写作，另加一格站外）：
研究经历最长，跨两行，右侧叠学习经历与技能，写作与站外并排。这样四块的底边
落在同一水平线上，不会出现一大块空洞——严格 2×2 会空出 230px。

每条研究经历都写「做了什么」+「产出了什么」——没有论文时，产出就是证据：

```
2025 — 2026
失败归因：结构是在哪一层丢的
生成图有色调、无结构。把问题定位到条件注入路径与结构约束的层级……
产出  归因报告一份 · 方法精读 5 篇
```

## 改简历只改一个文件

`me.json` 是全站唯一手填的文件，模板里不写死任何个人信息：

| 字段 | 作用 |
|---|---|
| `name` / `role` / `field` | 首屏大字、身份行、顶栏品牌、`<title>` |
| `org` / `place` / `email` / `github` | 联系方式；**留空则不渲染**，页面不会出现空行 |
| `statement` | 自述两段：第一段是主张（20px 衬线），第二段是旁注（13px 无衬线） |
| `timeline` | 研究经历；每项含 `when` / `title` / `note` / `out` / `url` |
| `skills` | 技能表，`[标签, 内容]` 数组 |
| `csdn.user` | CSDN 用户名；填了才会抓文章，留空则首页「站外」一格显示占位 |

填了 `org` 会自动多出一节「教育」。改完跑一次 `python3 build_site.py && python3 fix_nav.py` 即可。

## 站外文章（CSDN）

`fetch_csdn.py` 走 CSDN 前台用的公开接口，抓标题、链接、日期、阅读量，写成
`data/csdn.json`；`build_site.py` 读它渲染首页「站外」一格（最近 5 篇）和
写作页的「站外 · CSDN」整节。

```bash
# 1) 把账号名填进 me.json 的 csdn.user（blog.csdn.net/ 后面那段）
python3 fetch_csdn.py                # 或 python3 fetch_csdn.py 你的账号
python3 build_site.py && python3 fix_nav.py
```

> **昵称不是账号名。** 接口只认地址栏里那串（本站是 `2401_87978948`），
> 不认昵称（「不想生孩子」）。把主页链接或任意一篇文章的链接当参数传进去也行，
> 脚本会从 URL 里解析出账号。

`./publish.sh` 会在构建前自动刷新一次；断网或接口改版时沿用上次的
`data/csdn.json`，不会阻断发布。抓取失败也不会把旧文件写坏。

## 打印成 PDF

首页带 `@media print`：面试时按 `⌘P` 直接出**一页** A4 黑白简历，
顶栏、页脚、搜索、跳转链接全部隐藏，链接不显示下划线。

- 纸上点不了链接，所以联系方式的网址本身会印出来（`github.com/xu2388 · blog.csdn.net/...`）；
- 站外文章在纸面只留 3 条，其余靠「CSDN 全部 N 篇」；
- 打印宽度约 695px，会落进 860px 的窄屏断点，所以打印样式里把两栏显式写了回来。

## 设计约定

视觉概念是**一本编好的册子**，不是产品落地页：

- 左侧 116px 窄栏只放小标签，正文一律对齐在同一条竖线上——这是简历与博客的分界；
- 标题与正文用衬线（Noto Serif SC / 宋体），界面与元信息用无衬线；
- 近白纸底 `#f8f7f4` + 墨色字，唯一强调色是钢笔墨蓝 `#1f4e79`；
- 层级靠字号、留白与发丝线，不用卡片、投影、渐变光斑；
- 圆角只出现在代码与标签上（2–3px），其余一律直角；
- 交互克制：明暗主题、`/` 唤起索引、文章页右侧目录与阅读进度。

刻意不做：粒子背景、滚动入场动画、卡片悬停位移、编号 01/02/03 的分节标记。

## 目录结构

```
科研博客/
├── index.html  research.html  writing.html  notes.html  archive.html   五个入口页（自动生成）
├── subject/                    每门学科一页（自动生成）
├── assets/
│   ├── style.css               全站样式（明暗双主题 + 打印样式）
│   └── blog.js                 主题切换、移动导航、标题搜索、右侧目录、KaTeX 按需加载
├── me.json                     个人信息与简历内容（唯一手填）
├── me.py                       读取 me.json
├── fetch_csdn.py               抓 CSDN 文章清单 → data/csdn.json
├── ingest_chatgpt.py           ChatGPT 导出 → raw_exports/chatgpt_export/dump/（一条对话一个 txt）
├── site_model.py               学科注册表（学科名 → slug / 分组 / 一句话说明）
├── build_site.py               站点生成器：简历首页、板块页、学科页、清单页、索引
├── build_notes.py              notes/*.md → articles/notes/*.html
├── build_articles.py           articles_src/*.md → articles/*.html
├── fix_nav.py                  统一全站顶栏 / 页脚，按页面归属高亮板块
├── articles/                   文章页、清单页、notes/ 正文页
├── notes/                      笔记的 Markdown 源（frontmatter 的 subject 决定归到哪门学科）
├── articles_src/               长研究文章的 Markdown 源
├── survey/                     调研档案原始文件（80 份）
└── data/                       search-index.js、csdn.json（抓取结果）
```

已停用：`build_index.py`、`build_doubao_kb.py`、`ingest_doubao_local.py`。
`build_knowledge_base.py` 仅作为 Markdown 渲染器被引用（`render_md`）。

**与 AI 助手的对话存档不进入站点**：`articles/kb/`、`articles/kb-doubao/`、`raw_exports/`
已从仓库移除并写进 `.gitignore`。

## 对话素材 → 文章

与 AI 助手的原始对话**不进站点**（`raw_exports/` 已 gitignore），只作为写文章的原料。
怎么从上千条对话里挑题、怎么改写成文章、哪些内容绝对不能出现，写在两份交接文档里：

| 文档 | 覆盖 |
|---|---|
| `HANDOVER-豆包对话成文交接文档.md` | 豆包 1813 条对话；文章 frontmatter、文风、去尴尬规则、构建流水线 |
| `HANDOVER-ChatGPT对话成文交接文档.md` | ChatGPT 30 条科研对话；以「判断」为单位成文、研究路径页、现状批评 |

ChatGPT 侧语料已拆好，直接读：

```bash
python3 ingest_chatgpt.py                       # 首次或换了导出文件时跑
cat raw_exports/chatgpt_export/INDEX.md         # 86 条会话清单
ls raw_exports/chatgpt_export/dump/ | grep 频域  # 按标题找
```

## 本地预览

```bash
cd 科研博客
python3 -m http.server 8000     # 浏览器打开 http://localhost:8000
```

直接双击 `index.html` 也能看：搜索索引是 `.js` 而不是 `.json`，`file://` 下同样可用。

## 构建

```bash
./publish.sh                    # 构建 + 提交 + 推送
```

单独构建：

```bash
python3 build_articles.py       # 如有新的 articles_src/*.md
python3 build_notes.py          # 如有新的 notes/*.md
python3 build_site.py           # 简历首页 / 板块页 / 学科页 / 清单页 / 索引
python3 fix_nav.py              # 统一顶栏（必须在 build_site 之后跑）
```

## 新增一篇内容

**学科笔记**（会出现在「笔记 → 某学科」页和索引里）：

```bash
# 在 notes/ 下新建 .md，frontmatter 写 title / subject / category / summary
# subject 必须与 site_model.py 里登记的学科名一致，否则会落到「其他」
python3 build_notes.py && python3 build_site.py && python3 fix_nav.py
```

**长文章 / 随笔**：

```bash
python3 md_to_html.py <你的.md> <分类:研究/随笔/学习笔记> "<标题>" "<日期>" "<标签逗号分隔>" "<一句话摘要>"
python3 build_site.py && python3 fix_nav.py
```

> 分类决定归属：`研究` → 研究页，`学习笔记` / `随笔` → 写作页；
> 带 `论文精读` 标签的自动进「研究 → 论文精读」。

## 部署到 GitHub Pages

仓库已配好自动部署（`.github/workflows/deploy.yml` + `.nojekyll`），推上去就上线：

```bash
git remote add origin https://github.com/<用户名>/<仓库名>.git
git branch -M main
git push -u origin main
```

> **推送卡在密码？** GitHub 不支持登录密码推送。"密码"要填 Personal Access Token：
> Settings → Developer settings → Tokens (classic) → 勾 `repo` → 复制 `ghp_...` 当密码。

然后仓库 → Settings → Pages → Source 选 **GitHub Actions**，等 Actions 跑完即可。
站点在 `https://<用户名>.github.io/<仓库名>/`。全站相对链接，放在子目录也不会断。
