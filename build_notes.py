#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 notes/*.md（正式学习笔记，带 frontmatter）批量转成站点文章页 + 学科索引。
frontmatter: title / subject / category(课程笔记|学习笔记|研究) / source(原始对话文件名) / summary
输出：articles/notes/{slug}.html ；articles/notes-index.html
"""
import os, re, glob, html as htmlmod
from build_knowledge_base import render_md

ROOT = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(ROOT, "notes")
OUT_DIR = os.path.join(ROOT, "articles", "notes")
INDEX_OUT = os.path.join(ROOT, "articles", "notes-index.html")

SUBJECT_ORDER = ["计算机网络", "数据库/MySQL", "JavaWeb", "数据结构与算法", "深度学习/神经网络",
                 "大数据技术", "信号与系统", "数字图像处理", "高等数学/最优化", "大学物理",
                 "英语/雅思", "思政/毛概/近代史", "虚拟染色/科研", "其他"]

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

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<link rel="stylesheet" href="../../assets/style.css" />
<script id="meta" type="application/json">
{{"title":"{title_json}","date":"2026-10-24","tags":["{cat}","{subject}"],"category":"{cat}","summary":"{summary_json}"}}
</script>
</head>
<body>
<header class="site-header"><div class="container">
<h1 class="site-title">科研博客</h1>
<p class="site-subtitle">课程复习与科研 · 系统学习笔记</p>
<nav class="site-nav">
<a href="../../index.html#threads">研究方向</a>
<a href="../../index.html#articles">文章</a>
<a href="../notes-index.html">笔记索引</a>
</nav>
</div></header>
<article class="article">
<h1>{title}</h1>
<div class="meta">{cat} · {subject} · 整理自豆包对话 {source}</div>
{body}
<p class="muted" style="margin-top:28px">原始对话：<a href="../kb-doubao/{source_html}">{source}</a></p>
<a class="back-link" href="../notes-index.html">← 返回笔记索引</a>
</article>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../../assets/blog.js" defer></script>
</body>
</html>
"""

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
        source = fm.get("source", "")
        summary = fm.get("summary", "")
        slug = os.path.splitext(os.path.basename(p))[0] + ".html"
        source_html = source[:-3] + ".html" if source.endswith(".md") else source
        page = PAGE.format(
            title=htmlmod.escape(title), title_json=esc_json(title),
            cat=cat, subject=subject, summary_json=esc_json(summary),
            body=render_md(body), source=htmlmod.escape(source), source_html=htmlmod.escape(source_html),
        )
        open(os.path.join(OUT_DIR, slug), "w", encoding="utf-8").write(page)
        entries.append({"title": title, "slug": slug, "subject": subject, "cat": cat,
                        "summary": summary, "order": os.path.basename(p)})
    # 索引
    by = {}
    for e in entries:
        by.setdefault(e["subject"], []).append(e)
    def subj_key(s):
        return (SUBJECT_ORDER.index(s) if s in SUBJECT_ORDER else 99, s)
    secs = []
    for subj in sorted(by, key=subj_key):
        items = sorted(by[subj], key=lambda x: x["order"])
        lis = "".join(
            f'<li><a href="notes/{e["slug"]}">{htmlmod.escape(e["title"])}</a>'
            f'<span class="desc">{htmlmod.escape(e["summary"])}</span></li>' for e in items)
        secs.append(f'<section class="block"><h2>{subj}（{len(items)}）</h2><ul class="article-list">{lis}</ul></section>')
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>学习笔记 · 课程复习与科研整理</title>
<link rel="stylesheet" href="../assets/style.css" />
<script id="meta" type="application/json">
{{"title":"学习笔记 · 课程复习与科研整理（{len(entries)} 篇）","date":"2026-10-24","tags":["课程笔记","学习","复习"],"category":"课程笔记","summary":"把大一大二专业课复习与科研对话整理成的系统学习笔记，按学科分组，正式书面整理，完整覆盖知识点。"}}
</script>
</head>
<body>
<header class="site-header"><div class="container">
<h1 class="site-title">科研博客 · 学习笔记</h1>
<p class="site-subtitle">课程复习与科研 · {len(entries)} 篇系统笔记</p>
<nav class="site-nav"><a href="../index.html">首页</a><a href="knowledge-index.html">DeepSeek 知识库</a><a href="doubao-index.html">豆包知识库</a></nav>
</div></header>
<main class="container">
<nav class="crumbs"><a href="../index.html">首页</a> / 课程与科研笔记</nav>
<h1 class="list-title">课程与科研笔记</h1>
<p class="intro">这里把豆包对话里的大一大二专业课复习、以及科研讨论，逐条整理成系统、正式的学习笔记，按学科分组，完整覆盖知识点与结论。</p>
{''.join(secs)}
</main>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../assets/blog.js" defer></script>
</body>
</html>
"""
    open(INDEX_OUT, "w", encoding="utf-8").write(page)
    print(f"笔记：{len(entries)} 篇 -> articles/notes/ ; 索引 -> articles/notes-index.html")

if __name__ == "__main__":
    main()
