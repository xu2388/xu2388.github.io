# 科研与学习档案

从我和 AI 助手（DeepSeek、豆包、WorkBuddy）一年多的科研与学习对话里，整理出来的个人主页。
纯静态 HTML + CSS，**零依赖**，可直接托管到 GitHub Pages / Vercel / 任意静态空间。

## 信息架构

三层，越点越具体：**首页 → 板块 → 学科/主题 → 文章**。

```
首页 index.html
├── 科研 research.html
│   ├── 研究文章     articles/list-research.html        18 篇
│   ├── 论文精读     articles/list-readings.html        10 篇
│   ├── 研究笔记     articles/list-research-notes.html  15 篇
│   ├── 调研档案     articles/survey-catalog.html       80 份
│   └── 论文导读     articles/papers-index.html         27 篇
├── 学习 study.html
│   ├── study/<学科>.html   20 门学科，每门一页
│   ├── 教程         articles/list-tutorials.html
│   └── 对话存档     articles/knowledge-index.html
├── 随笔 essays.html
└── 搜索 search.html        按标题即时筛选（索引 data/search-index.js）
```

配色上两个板块各有主色：**科研 = 青（teal）**，**学习 = 琥珀（amber）**，
侧栏当前项、卡片描边、链接高亮都跟着板块走，翻页时不会分不清自己在哪。

## 目录结构

```
科研博客/
├── index.html                  首页（两扇门 + 最近更新 + 关于，自动生成）
├── research.html               科研板块页（自动生成）
├── study.html                  学习板块页：20 门学科的卡片网格（自动生成）
├── essays.html                 随笔（自动生成）
├── search.html                 搜索页（自动生成，数据来自 data/search-index.js）
├── study/                      每门学科一页（自动生成）
├── assets/
│   ├── style.css               全站样式（左侧固定目录 + 右侧内容，明暗双主题）
│   └── blog.js                 交互增强（侧栏搜索、标题搜索、抽屉导航、悬浮目录、公式渲染）
├── site_model.py               学科注册表（学科名 → URL slug / 分组 / 一句话说明）
├── build_site.py               站点生成器：首页、板块页、学科页、清单页、搜索索引
├── fix_nav.py                  统一全站左侧目录 + 按页面归属高亮板块（每次构建后跑一次）
├── md_to_html.py               Markdown → 文章页转换器（内嵌 meta，供索引收录）
├── build_articles.py           articles_src/*.md → articles/*.html（长研究文章）
├── build_notes.py              notes/*.md → articles/notes/ + 笔记索引
├── build_knowledge_base.py     DeepSeek 270 条对话 → articles/kb/
├── build_doubao_kb.py          豆包 98 条对话 → articles/kb-doubao/
├── articles/
│   ├── 001~021                 研究文章与论文精读
│   ├── 004~007                 学习笔记 · 教程（扩散/Flow Matching、VAE、注意力、对比学习）
│   ├── list-*.html             各分类清单页（自动生成）
│   ├── notes/                  学科笔记正文页（自动生成）
│   ├── kb/                     DeepSeek 270 条问答页
│   └── kb-doubao/              豆包 98 条问答页
├── notes/                      笔记的 Markdown 源（带 frontmatter，subject 决定归到哪门学科）
├── articles_src/               长研究文章的 Markdown 源
├── data/                       审计清单 + search-index.js + nav_counts.json
└── raw_exports/                原始对话档案（未删减）
```

## 内容分层

1. **科研**：研究文章（长文，保留原始数据与自我推翻）、论文精读、研究笔记、调研档案、论文导读。
2. **学习**：按 20 门学科归档的专业课笔记（每门一页）、系列教程、全部学习对话存档。
3. **随笔 / 资料库**：科普长文；全量审计与溯源。

## 本地启动

```bash
cd 科研博客
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 构建流程（改完内容跑这一串）

```bash
./publish.sh            # 构建 + 提交 + 推送，一条命令
```

单独构建时：

```bash
python3 build_articles.py        # 如有新的 articles_src/*.md
python3 build_notes.py           # 如有新的 notes/*.md
python3 build_knowledge_base.py  # 如需重建 DeepSeek 对话
python3 build_doubao_kb.py       # 如需重建豆包对话
python3 build_site.py            # 首页 / 板块页 / 学科页 / 清单页 / 搜索索引
python3 fix_nav.py               # 统一左侧目录的相对路径（必须在 build_site 之后）
```

## 新增一篇内容

**学科笔记**（会同时出现在「学习 → 某学科」页和搜索里）：

```bash
# 在 notes/ 下新建 .md，frontmatter 里写清 title / subject / category / summary
# subject 必须和 site_model.py 里登记的学科名一致，否则会落到「其他」
python3 build_notes.py && python3 build_site.py && python3 fix_nav.py
```

**长文章 / 随笔**：

```bash
python3 md_to_html.py <你的.md> <分类:研究/随笔/学习笔记/资料库> "<标题>" "<日期>" "<标签逗号分隔>" "<一句话摘要>"
python3 build_site.py && python3 fix_nav.py
```

> 分类决定它归到哪个板块、哪张卡片：`研究` → 科研，`学习笔记` → 学习，`随笔` → 随笔。
> 带 `论文精读` 标签的会自动进「科研 → 论文精读」这一栏。

## 部署到 GitHub Pages

仓库已配好自动部署（`.github/workflows/deploy.yml` + `.nojekyll`）。推送到 GitHub 后自动上线：

```bash
# 1. 在 GitHub 上新建一个空仓库（不要勾选 README / .gitignore / License）
#    命名小技巧：
#      · 想用根域名 https://<你的用户名>.github.io/  → 仓库名必须叫 "<你的用户名>.github.io"
#      · 随便起名（如 research-blog）                → 站点在 https://<你的用户名>.github.io/research-blog/
#    （两种都行，本站全是相对链接，子目录也不会断链）

# 2. 绑定远程并推送（把 <你的用户名> <仓库名> 换成你的）
cd 科研博客
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git branch -M main
git push -u origin main
```

> **推送时卡在密码？** GitHub 早已不支持用登录密码推送。用户名填你的 GitHub 用户名，"密码"要填一个 **Personal Access Token（PAT）**：GitHub → 右上头像 → Settings → Developer settings → Tokens (classic) → Generate new token → 勾选 `repo` 权限 → 复制那串 `ghp_...` 当密码用。嫌麻烦也可以装个 **GitHub Desktop**，图形界面点几下就推送，不用碰命令行和 token。

```bash
# 3. GitHub 仓库页面 → Settings → Pages → Source 选 "GitHub Actions"（保存）
#    然后到 Actions 标签页，看 "Deploy to GitHub Pages" 跑完（约 1 分钟），
#    站点就上线在：
#      https://<你的用户名>.github.io/<仓库名>/
```

之后每次改完内容，`git push` 一次就会自动重新部署。所有链接都是相对路径，放在仓库子目录下也能正常跳转。

> **关于 `raw_exports/`（17M 原始对话存档）**：它会随仓库一起被推上去，技术上能通过直接猜 URL 访问到，但网站里没有任何链接指向它。如果你不想让它公开，告诉我，我可以把它从发布内容里摘掉（本地仍保留）。
