# 科研与学习档案

一个本科生的科研记录与课程笔记。纯静态 HTML + CSS，**零依赖、无框架、无追踪**，
可以直接托管在 GitHub Pages / Vercel / 任意静态空间。

## 信息架构

三层，越点越具体：**首页 → 板块 → 学科/主题 → 文章**。

```
首页 index.html
├── 科研 research.html
│   ├── 研究文章     articles/list-research.html        17 篇
│   ├── 论文精读     articles/list-readings.html        10 篇
│   ├── 研究笔记     articles/list-research-notes.html  15 篇
│   ├── 调研档案     articles/survey-catalog.html       80 份
│   └── 论文导读     articles/papers-index.html         27 篇
├── 学习 study.html
│   ├── study/<学科>.html   20 门学科，每门一页（共 75 篇笔记）
│   └── 教程         articles/list-tutorials.html       5 篇
├── 随笔 essays.html
└── 搜索 search.html        按标题即时筛选（索引 data/search-index.js）
```

首页只有三件事：一句话说清这是谁的什么档案、一个标题搜索框、一份目录（科研 / 学习，
带篇数与学科分组）。不放统计条、不放轮播、不放「最新动态」。

## 设计约定

视觉概念是**一本编好的册子**（edited volume），不是产品落地页：

- 标题与正文用衬线（Noto Serif SC / 宋体），界面与元信息用无衬线；
- 近白纸底 `#f8f7f4` + 墨色字，唯一强调色是钢笔墨蓝 `#1f4e79`；
- 层级靠字号、留白与发丝线，不用卡片、投影、渐变光斑；
- 圆角只出现在代码与标签上（2–3px），其余一律直角；
- 交互克制：只有明暗主题、`/` 唤起搜索、文章页右侧目录与阅读进度。

刻意不做：粒子背景、滚动入场动画、卡片悬停位移、编号 01/02/03 的分节标记。

## 目录结构

```
科研博客/
├── index.html  research.html  study.html  essays.html  search.html   五个入口页（自动生成）
├── study/                      每门学科一页（自动生成）
├── assets/
│   ├── style.css               全站样式（明暗双主题，单强调色）
│   └── blog.js                 主题切换、移动导航、标题搜索、右侧目录、KaTeX 按需加载
├── site_model.py               学科注册表（学科名 → slug / 分组 / 一句话说明）
├── build_site.py               站点生成器：入口页、学科页、清单页、搜索索引
├── build_notes.py              notes/*.md → articles/notes/*.html
├── build_articles.py           articles_src/*.md → articles/*.html
├── fix_nav.py                  统一全站顶栏 / 页脚，按页面归属高亮板块
├── articles/                   文章页、清单页、notes/ 正文页
├── notes/                      笔记的 Markdown 源（frontmatter 的 subject 决定归到哪门学科）
├── articles_src/               长研究文章的 Markdown 源
├── survey/                     调研档案原始文件（80 份）
└── data/                       search-index.js + nav_counts.json
```

已停用、不再参与构建：`build_index.py`、`build_doubao_kb.py`、`ingest_doubao_local.py`。
`build_knowledge_base.py` 仅作为 Markdown 渲染器被引用（`render_md`）。

**与 AI 助手的对话存档不进入站点**：`articles/kb/`、`articles/kb-doubao/`、`raw_exports/`
已从仓库移除，并写进 `.gitignore`，不会再被构建或推送。

## 本地预览

```bash
cd 科研博客
python3 -m http.server 8000     # 浏览器打开 http://localhost:8000
```

直接双击 `index.html` 也能看，搜索索引是 `.js` 而不是 `.json`，`file://` 下同样可用。

## 构建

```bash
./publish.sh                    # 构建 + 提交 + 推送
```

单独构建：

```bash
python3 build_articles.py       # 如有新的 articles_src/*.md
python3 build_notes.py          # 如有新的 notes/*.md
python3 build_site.py           # 入口页 / 学科页 / 清单页 / 搜索索引
python3 fix_nav.py              # 统一顶栏（必须在 build_site 之后跑）
```

## 新增一篇内容

**学科笔记**（会同时出现在「学习 → 某学科」页和搜索里）：

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

> 分类决定归属：`研究` → 科研，`学习笔记` → 学习，`随笔` → 随笔；
> 带 `论文精读` 标签的自动进「科研 → 论文精读」。

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
