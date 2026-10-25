#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科研博客索引生成器

做三件事：
1. 扫描 articles/*.html，读取内嵌的 <script id="meta"> JSON 元数据；
2. 为每个栏目生成独立的归档页 articles/list-<id>.html（完整列表）；
3. 重建首页的文章区：每个栏目只放前 N 条 + 「全部 N 篇 →」链接，
   并刷新首页的数据条（<!-- STATS_START --> ... <!-- STATS_END -->）。

用法：python3 build_index.py
"""
import json
import re
import os
import glob
import html as htmlmod

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(ROOT, "articles")
INDEX_PATH = os.path.join(ROOT, "index.html")

CATEGORY_ORDER = ["研究", "课程笔记", "学习笔记", "随笔", "知识库", "论文", "资料库"]
CATEGORY_TITLE = {
    "研究": "研究文章",
    "课程笔记": "课程与科研笔记",
    "学习笔记": "学习笔记 · 教程",
    "随笔": "随笔 · 科普",
    "知识库": "知识库 · 全部学习对话",
    "论文": "论文分享屋",
    "资料库": "资料库 · 审计与清单",
}
CATEGORY_ID = {
    "研究": "research",
    "课程笔记": "courses",
    "学习笔记": "notes",
    "随笔": "essays",
    "知识库": "kb",
    "论文": "papers",
    "资料库": "archive",
}
CATEGORY_DESC = {
    "研究": "虚拟染色主线的完整研究文章：问题、方法、实验与自我推翻，保留原始数据与结论。",
    "课程笔记": "把专业课复习与科研对话整理成的系统笔记，按学科分组，正式书面整理。",
    "学习笔记": "从具体困惑出发的教程：扩散与 Flow Matching、VAE、注意力、对比学习与 CLIP。",
    "随笔": "自己写的科普长文，讲本质而不是堆术语。",
    "知识库": "与 AI 助手的全部学习对话存档，按主题分组，每条可溯源到原始档案。",
    "论文": "调研过的虚拟染色 / 病理影像论文导读，按主题分组，每篇一句话总结。",
    "资料库": "全量审计、清单与原始存档说明，用于溯源核对。",
}
# 首页每个栏目预览几条
PREVIEW_N = {"研究": 3, "课程笔记": 1, "学习笔记": 3, "随笔": 2, "知识库": 2, "论文": 1, "资料库": 2}


def extract_meta(text: str):
    m = re.search(r'<script id="meta" type="application/json">(.*?)</script>', text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def collect():
    grouped = {}
    for path in sorted(glob.glob(os.path.join(ARTICLES_DIR, "*.html"))):
        base = os.path.basename(path)
        if base.startswith("list-"):
            continue
        with open(path, encoding="utf-8") as f:
            meta = extract_meta(f.read())
        if not meta:
            continue
        meta["file"] = base
        cat = meta.get("category", "研究")
        grouped.setdefault(cat, []).append(meta)
    for cat in grouped:
        # 先按文件名升序（001 → 002 → …），再按日期降序（稳定排序），
        # 这样同一天的文章保持编号顺序，而不是被文件名倒序打乱。
        items = sorted(grouped[cat], key=lambda x: x.get("file", ""))
        items.sort(key=lambda x: x.get("date", ""), reverse=True)
        grouped[cat] = items
    return grouped


def render_list(items, href_prefix=""):
    if not items:
        return '<p class="muted">（暂无内容）</p>'
    out = ['<ul class="article-list">']
    for it in items:
        title = htmlmod.escape(it.get("title", it.get("file", "未命名")))
        date = it.get("date", "")
        tags = " ".join('<span class="tag">%s</span>' % htmlmod.escape(str(t)) for t in it.get("tags", []))
        summary = htmlmod.escape(it.get("summary", ""))
        href = href_prefix + it["file"]
        out.append(
            '<li>\n'
            '  <a href="%s">%s</a><span class="date">%s</span><br />\n'
            '  %s\n'
            '  <span class="desc">%s</span>\n'
            '</li>' % (href, title, date, tags, summary)
        )
    out.append("</ul>")
    return "\n".join(out)


def site_header(title, subtitle, nav_items):
    nav = "".join('<a href="%s">%s</a>' % (h, t) for t, h in nav_items)
    return (
        '<header class="site-header"><div class="container">\n'
        '<h1 class="site-title">%s</h1>\n'
        '<p class="site-subtitle">%s</p>\n'
        '<nav class="site-nav">%s</nav>\n'
        '</div></header>' % (htmlmod.escape(title), htmlmod.escape(subtitle), nav)
    )


LIST_NAV = [
    ("首页", "../index.html"),
    ("研究文章", "list-research.html"),
    ("学习笔记", "list-notes.html"),
    ("课程笔记", "list-courses.html"),
    ("随笔", "list-essays.html"),
    ("知识库", "list-kb.html"),
    ("论文分享屋", "list-papers.html"),
    ("资料库", "list-archive.html"),
]


def write_list_page(cat, items):
    anchor = CATEGORY_ID.get(cat, "misc")
    title = CATEGORY_TITLE.get(cat, cat)
    desc = CATEGORY_DESC.get(cat, "")
    body = render_list(items, href_prefix="")
    hdr = site_header("科研博客 · " + title, "%s · %d 篇" % (title, len(items)), LIST_NAV)
    hdr = hdr.replace('<a href="list-%s.html">' % anchor, '<a class="active" href="list-%s.html">' % anchor)
    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>%(title)s · 我的科研与学习档案</title>
<link rel="stylesheet" href="../assets/style.css" />
</head>
<body>
%(header)s
<main class="container">
<nav class="crumbs"><a href="../index.html">首页</a> / %(title)s</nav>
<h1 class="list-title">%(title)s</h1>
<p class="list-sub">%(desc)s　共 %(n)d 篇</p>
%(body)s
</main>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客 · 托管于 GitHub Pages</span></div></footer>
<script src="../assets/blog.js" defer></script>
</body>
</html>
""" % {
        "title": htmlmod.escape(title),
        "header": hdr,
        "desc": htmlmod.escape(desc),
        "n": len(items),
        "body": body,
    }
    path = os.path.join(ARTICLES_DIR, "list-%s.html" % anchor)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return os.path.basename(path)


def render_home_section(cat, items):
    anchor = CATEGORY_ID.get(cat, "")
    title = CATEGORY_TITLE.get(cat, cat)
    n = len(items)
    preview_n = PREVIEW_N.get(cat, 3)
    # 首页预览里跳过标题无信息量的存档条目（如「豆包会话 38441…」），
    # 它们仍保留在归档页里。
    pool = [it for it in items if not it.get("title", "").startswith("豆包会话 ")]
    if len(pool) < preview_n:
        pool = items
    preview = pool[:preview_n]
    more = ""
    if n > preview_n:
        more = '<a class="more" href="articles/list-%s.html">全部 %d 篇 →</a>' % (anchor, n)
    head = (
        '<div class="block-head">\n'
        '  <h2>%s<span class="count">%d</span></h2>\n'
        '  %s\n'
        '</div>' % (htmlmod.escape(title), n, more)
    )
    return '<section class="block" id="%s">\n%s\n%s\n</section>' % (anchor, head, render_list(preview, href_prefix="articles/"))


def compute_stats(grouped):
    notes = len(glob.glob(os.path.join(ARTICLES_DIR, "notes", "*.html")))
    kb = len(glob.glob(os.path.join(ARTICLES_DIR, "kb", "*.html"))) + len(
        glob.glob(os.path.join(ARTICLES_DIR, "kb-doubao", "*.html"))
    )
    papers = 0
    pidx = os.path.join(ARTICLES_DIR, "papers-index.html")
    if os.path.exists(pidx):
        with open(pidx, encoding="utf-8") as f:
            papers = f.read().count('class="paper"')
    research = len(grouped.get("研究", []))
    tutorials = len(grouped.get("学习笔记", []))
    return [
        (research, "篇 · 研究文章"),
        (notes + tutorials, "篇 · 笔记与教程"),
        (kb, "条 · 学习对话存档"),
        (papers, "篇 · 论文导读"),
    ]


def main():
    grouped = collect()
    ordered = [c for c in CATEGORY_ORDER if c in grouped] + [c for c in grouped if c not in CATEGORY_ORDER]

    # 1) 每个栏目生成归档页
    made = []
    for cat in ordered:
        made.append(write_list_page(cat, grouped[cat]))

    # 2) 首页栏目区
    sections = [render_home_section(cat, grouped[cat]) for cat in ordered]
    new_block = "\n".join(sections)

    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = f.read()

    pattern = re.compile(r"<!-- ARTICLES_START -->.*?<!-- ARTICLES_END -->", re.DOTALL)
    if not pattern.search(idx):
        print("找不到 ARTICLES_START/END 标记，退出。")
        return
    idx = pattern.sub("<!-- ARTICLES_START -->\n" + new_block + "\n  <!-- ARTICLES_END -->", idx)

    # 3) 数据条
    stats = compute_stats(grouped)
    stat_html = "\n".join(
        '      <div class="stat"><span class="stat-num">%s</span><span class="stat-label">%s</span></div>' % (n, l)
        for n, l in stats
    )
    sp = re.compile(r"<!-- STATS_START -->.*?<!-- STATS_END -->", re.DOTALL)
    if sp.search(idx):
        idx = sp.sub("<!-- STATS_START -->\n" + stat_html + "\n      <!-- STATS_END -->", idx)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(idx)

    total = sum(len(v) for v in grouped.values())
    print("已更新：首页 %d 个栏目，归档页 %d 个，条目共 %d。" % (len(ordered), len(made), total))
    for cat in ordered:
        print("  [%s] %d 篇（首页预览 %d）" % (cat, len(grouped[cat]), min(PREVIEW_N.get(cat, 3), len(grouped[cat]))))


if __name__ == "__main__":
    main()
