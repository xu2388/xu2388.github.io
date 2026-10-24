# 科研博客 · 我的虚拟染色探索之路

从我和 AI 助手（DeepSeek、豆包、WorkBuddy）一年多的科研与学习对话里，整理出来的个人博客。
纯静态 HTML + CSS，**零依赖**，可直接托管到 GitHub Pages / Vercel / 任意静态空间。

## 目录结构

```
科研博客/
├── index.html                  首页（研究方向地图 + 分类文章列表，自动生成）
├── assets/style.css            全站样式
├── build_index.py              首页索引生成器（扫 articles/*.html 的 meta，按类分组重建首页）
├── md_to_html.py               Markdown → 文章页转换器（内嵌 meta，供索引收录）
├── build_knowledge_base.py     全量知识库生成器（把 270 条对话转成问答页）
├── articles/                   文章页
│   ├── 001-虚拟染色主线.html        （研究，手写深度文）
│   ├── 002-逐像素跨图不可迁移.html  （研究，手写深度文）
│   ├── 深度学习到底在干什么*.html   （随笔，作者原文）
│   ├── knowledge-index.html        （知识库索引，按 8 主题分组）
│   ├── source_audit.html           （资料库：全量资料源审计）
│   ├── deepseek_inventory.html     （资料库：270 条对话全量清单）
│   └── kb/                          （270 个对话问答页，一条不丢）
├── data/                       审计与清单的 Markdown 源
└── raw_exports/
    ├── deepseek_raw/           270 个对话的原始 Markdown 档案（未删减，含 AI 思考过程）
    └── doubao_agent_raw/       豆包 agent 会话还原
```

## 内容三层

1. **研究文章**：我手写的高质量深度文，保留原始数据、公式、当时的困惑和自我推翻。
2. **随笔**：我自己写的科普。
3. **知识库**：DeepSeek 全部 270 条学习对话的问答存档，按主题浏览，每条可溯源到未删减原始档案。

## 本地启动

```bash
cd 科研博客
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 新增一篇文章

```bash
# 方式一：从 Markdown 转
python3 md_to_html.py <你的.md> <分类:研究/随笔/知识库/资料库> "<标题>" "<日期>" "<标签逗号分隔>" "<一句话摘要>"

# 方式二：手写 HTML（在 <head> 里放一段 <script id="meta" type="application/json">{...}</script> 描述 title/date/tags/category/summary）

# 最后重建首页索引
python3 build_index.py
```

## 重新生成知识库

对话放进 `raw_exports/deepseek_raw/` 后：

```bash
python3 build_knowledge_base.py   # 重建 articles/kb/ 和 knowledge-index.html
python3 build_index.py            # 刷新首页
```
