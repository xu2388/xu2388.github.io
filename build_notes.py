#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 notes/*.md（正式学习笔记，带 frontmatter）批量转成站点文章页。

frontmatter: title / subject / category(课程笔记|学习笔记|研究) / summary
输出：articles/notes/{slug}.html
学科索引由 build_site.py 生成（study/<学科>.html），这里只产出单篇正文页。
"""
import os
import re
import glob
import html as htmlmod

from build_knowledge_base import render_md
from site_model import subject_slug, RESEARCH_SUBJECT
from fix_nav import build_header, build_footer

ROOT = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(ROOT, "notes")
OUT_DIR = os.path.join(ROOT, "articles", "notes")

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
<link rel="stylesheet" href="../../assets/style.css" />
{font}
<script id="meta" type="application/json">
{{"title":"{title_json}","date":"{date}","tags":["{cat}","{subject}"],"category":"{cat}","summary":"{summary_json}"}}
</script>
</head>
<body>
{header}
<article class="article">
<h1>{title}</h1>
<div class="meta">{cat} · {subject}</div>
{body}
<a class="back-link" href="{back_href}">{back_text}</a>
</article>
{footer}
<script src="../../assets/blog.js" defer></script>
</body>
</html>
"""


def parse(path):
    text = open(path, encoding="utf-8").read()
    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    body = text
    if m:
        for ln in m.group(1).split("\n"):
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
        body = text[m.end():]
    return fm, body


def esc_json(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(NOTES_DIR, "*.md")))
    entries = []
    for p in files:
        fm, body = parse(p)
        if not fm.get("title"):
            continue
        title = fm["title"]
        subject = fm.get("subject", "其他")
        cat = fm.get("category", "课程笔记")
        summary = fm.get("summary", "")
        slug = os.path.splitext(os.path.basename(p))[0] + ".html"
        # 正文开头的 "# 标题" 会和模板里的 <h1> 重复，去掉一行
        body_md = re.sub(r"^\s*#\s+" + re.escape(title) + r"\s*\n+", "", body, count=1)
        active = "科研" if subject == RESEARCH_SUBJECT else "学习"
        # 笔记页在 articles/notes/ 下，返回链接要上溯两级；科研类回到科研页
        if subject == RESEARCH_SUBJECT:
            back_href, back_text = "../../research.html", "← 返回科研"
        else:
            back_href, back_text = "../../study/%s.html" % subject_slug(subject), "← 返回 %s" % subject
        page = PAGE.format(
            title=htmlmod.escape(title), title_json=esc_json(title),
            cat=cat, subject=subject, summary_json=esc_json(summary),
            date="2026-10-24",
            body=render_md(body_md),
            slug=subject_slug(subject),
            back_href=back_href, back_text=back_text,
            font=FONT_LINK,
            header=build_header("../../", active),
            footer=build_footer("../../"),
        )
        open(os.path.join(OUT_DIR, slug), "w", encoding="utf-8").write(page)
        entries.append(slug)
    print("笔记：%d 篇 -> articles/notes/" % len(entries))


if __name__ == "__main__":
    main()
