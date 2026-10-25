# 科研博客 · 我的虚拟染色探索之路

从我和 AI 助手（DeepSeek、豆包、WorkBuddy）一年多的科研与学习对话里，整理出来的个人博客。
纯静态 HTML + CSS，**零依赖**，可直接托管到 GitHub Pages / Vercel / 任意静态空间。

## 目录结构

```
科研博客/
├── index.html                  首页（导语 + 各栏目预览 + 「全部 N 篇」入口，自动生成）
├── assets/
│   ├── style.css               全站样式（Yilia 式浅色双栏：左侧固定目录 + 右侧内容）
│   └── blog.js                 交互增强（侧栏粒子、移动端抽屉、悬浮目录、阅读进度、公式渲染）
├── build_index.py              索引生成器：生成各栏目归档页 articles/list-*.html，并重建首页
├── fix_nav.py                  统一全站左侧目录，按页面深度改写相对路径（每次构建后跑一次）
├── md_to_html.py               Markdown → 文章页转换器（内嵌 meta，供索引收录）
├── build_articles.py           articles_src/*.md → articles/*.html（长研究文章）
├── build_notes.py              notes/*.md → articles/notes/ + 笔记索引
├── build_knowledge_base.py     DeepSeek 270 条对话 → articles/kb/
├── build_doubao_kb.py          豆包 98 条对话 → articles/kb-doubao/
├── articles/
│   ├── 001~003、008~010        研究文章（手写 / 由研究笔记升级）
│   ├── 004~007                 学习笔记 · 教程（扩散/Flow Matching、VAE、注意力、对比学习）
│   ├── list-*.html             各栏目归档页（自动生成）
│   ├── notes/                  25 篇课程与科研笔记
│   ├── kb/                     DeepSeek 270 条问答页
│   └── kb-doubao/              豆包 98 条问答页
├── notes/                      笔记的 Markdown 源（带 frontmatter）
├── articles_src/               长研究文章的 Markdown 源
├── data/                       审计与清单的 Markdown 源
└── raw_exports/                原始对话档案（未删减）
```

## 内容分层

1. **研究文章**：深度长文，保留原始数据、公式、当时的困惑和自我推翻。
2. **学习笔记 · 教程**：从具体困惑出发的教程，讲清机制并接回主线。
3. **课程与科研笔记**：大一到大二专业课复习 + 科研整理，正式书面，按学科分组。
4. **知识库**：DeepSeek 270 条 + 豆包 98 条学习对话的问答存档，可溯源到原始档案。
5. **论文分享屋 / 资料库**：论文导读清单、全量审计与溯源。

## 本地启动

```bash
cd 科研博客
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 构建流程（改完内容跑这一串）

```bash
python3 build_articles.py        # 如有新的 articles_src/*.md
python3 build_notes.py           # 如有新的 notes/*.md
python3 build_index.py           # 生成归档页 + 重建首页（含数据条）
python3 fix_nav.py               # 统一左侧目录的相对路径（必须在 build_index 之后）
```

## 新增一篇文章

```bash
# 方式一：从 Markdown 转
python3 md_to_html.py <你的.md> <分类:研究/随笔/知识库/资料库> "<标题>" "<日期>" "<标签逗号分隔>" "<一句话摘要>"

# 方式二：手写 HTML（在 <head> 里放一段 <script id="meta" type="application/json">{...}</script> 描述 title/date/tags/category/summary）

# 最后重建索引
python3 build_index.py && python3 fix_nav.py
```

## 重新生成知识库

对话放进 `raw_exports/deepseek_raw/` 后：

```bash
python3 build_knowledge_base.py   # 重建 articles/kb/ 和 knowledge-index.html
python3 build_index.py            # 刷新首页
```

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

