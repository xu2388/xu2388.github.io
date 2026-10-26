#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 articles_src/*.md（完整研究文章，带 frontmatter）转成 articles/*.html 站点文章页。

frontmatter: title / date / tags(JSON 数组) / summary / category / source

页面骨架与 build_notes.py 保持一致（同一套顶栏、页脚、衬线字体），
所以这个脚本跑完不需要 fix_nav.py 再补一遍。
"""
import os
import re
import glob
import json
import html as htmlmod

from build_knowledge_base import render_md
from fix_nav import build_header, build_footer

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "articles_src")
OUT_DIR = os.path.join(ROOT, "articles")

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Noto+Serif+SC:wght@400;600&display=swap" />'
)

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{summary_j}" />
<link rel="stylesheet" href="../assets/style.css" />
{font}
<script id="meta" type="application/json">
{{"title":"{title_j}","date":"{date}","tags":{tags_j},"category":"{cat}","summary":"{summary_j}"}}
</script>
<script id="theme-init">try{{var t=localStorage.getItem("theme");if(!t)t=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}</script>
</head>
<body>
{header}
<article class="article">
<h1>{title}</h1>
<div class="meta">写于 {date} · {cat_label}</div>
{body}
<a class="back-link" href="{list_href}">← 返回{cat_label}</a>
</article>
{footer}
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
        # 去掉正文开头重复的一级标题（模板里已经渲染过一次）
        body = re.sub(r"^\s*#\s+.*?\n", "", body, count=1)
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

        CAT_LIST = {
            "研究": ("list-research.html", "研究记录", "研究"),
            "学习笔记": ("../writing.html", "写作", "写作"),
            "随笔": ("../writing.html", "写作", "写作"),
            "课程笔记": ("../notes.html", "笔记", "笔记"),
        }
        list_href, cat_label, active = CAT_LIST.get(cat, ("list-research.html", "研究记录", "研究"))
        # 带「论文精读」标签的归到精读清单
        if cat == "研究" and "论文精读" in tags:
            list_href, cat_label = "list-readings.html", "论文精读"

        page = PAGE.format(
            title=htmlmod.escape(title), title_j=j(title), date=date, cat=cat,
            tags_j=tags_j, summary_j=j(summary), body=render_md(body),
            list_href=list_href, cat_label=cat_label,
            font=FONT_LINK,
            header=build_header("../", active),
            footer=build_footer("../"),
        )
        open(os.path.join(OUT_DIR, slug), "w", encoding="utf-8").write(page)
        n += 1
    print(f"研究文章：{n} 篇 -> articles/")


if __name__ == "__main__":
    main()
