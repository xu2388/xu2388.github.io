#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 articles_src/*.md（完整研究文章，带 frontmatter）转成 articles/*.html 站点文章页。
frontmatter: title / date / tags(JSON 数组) / summary / category / source
"""
import os, re, glob, json, html as htmlmod
from build_knowledge_base import render_md

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "articles_src")
OUT_DIR = os.path.join(ROOT, "articles")

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<link rel="stylesheet" href="../assets/style.css" />
<script id="meta" type="application/json">
{{"title":"{title_j}","date":"{date}","tags":{tags_j},"category":"{cat}","summary":"{summary_j}"}}
</script>
</head>
<body>
<header class="site-header">
  <div class="container">
    <h1 class="site-title">科研博客</h1>
    <p class="site-subtitle">H&amp;E → IHC 虚拟染色 · 研究文章</p>
    <nav class="site-nav">
      <a href="../index.html#threads">研究方向</a>
      <a href="../index.html#articles">文章</a>
      <a href="../index.html#about">关于</a>
    </nav>
  </div>
</header>
<article class="article">
<h1>{title}</h1>
<div class="meta">{date} · 研究文章 · 整理自研究笔记</div>
{body}
<a class="back-link" href="../index.html#articles">← 返回首页</a>
</article>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../assets/blog.js" defer></script>
</body>
</html>
"""

def j(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.md")))
    n = 0
    for p in files:
        text = open(p, encoding="utf-8").read()
        fm = {}
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        body = text
        if m:
            for ln in m.group(1).split("\n"):
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    fm[k.strip()] = v.strip()
            body = text[m.end():]
        title = fm.get("title", os.path.splitext(os.path.basename(p))[0])
        date = fm.get("date", "2026-10-24")
        cat = fm.get("category", "研究")
        summary = fm.get("summary", "")
        try:
            tags = json.loads(fm.get("tags", "[]"))
        except Exception:
            tags = []
        tags_j = json.dumps(tags, ensure_ascii=False)
        slug = os.path.splitext(os.path.basename(p))[0] + ".html"
        page = PAGE.format(
            title=htmlmod.escape(title), title_j=j(title), date=date, cat=cat,
            tags_j=tags_j, summary_j=j(summary), body=render_md(body),
        )
        open(os.path.join(OUT_DIR, slug), "w", encoding="utf-8").write(page)
        n += 1
    print(f"研究文章：{n} 篇 -> articles/")

if __name__ == "__main__":
    main()
