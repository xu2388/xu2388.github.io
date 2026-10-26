#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一全站顶栏与页脚，并按页面归属高亮当前板块。

导航四项对应四种「东西」而不是四种「身份」：
    研究 research.html   做过的事（长文 + 精读 + 调研档案）
    写作 writing.html    写给别人看的东西（随笔、教程）
    笔记 notes.html      课程笔记，按学科成册（附录性质）
    索引 archive.html    全站可搜索的目录

幂等：可以反复运行。
用法：python3 fix_nav.py
"""
import os
import re
import json

from me import NAME

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "raw_exports", "node_modules", ".github"}

# (显示名, 相对站点的路径)
NAV = [
    ("研究", "research.html"),
    ("写作", "writing.html"),
    ("笔记", "notes.html"),
    ("索引", "archive.html"),
]

# articles/list-*.html → 所属板块
LIST_GROUP = {
    "research": "研究", "readings": "研究", "research-notes": "研究",
    "survey": "研究", "papers": "研究",
    "tutorials": "写作", "essays": "写作",
    "notes": "笔记", "courses": "笔记",
}

# 文章分类 → 所属板块
CATEGORY_GROUP = {
    "研究": "研究", "调研": "研究", "论文": "研究", "资料库": "研究",
    "随笔": "写作", "学习笔记": "写作", "教程": "写作",
    "课程笔记": "笔记", "知识库": "笔记",
}

THEME_INIT = ('<script id="theme-init">try{var t=localStorage.getItem("theme");'
              'if(!t)t=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";'
              'document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>')

HEADER_RE = re.compile(r'<header class="(?:site-header|topbar)">.*?</header>', re.DOTALL)
FOOTER_RE = re.compile(r'<footer class="site-footer">.*?</footer>', re.DOTALL)
META_RE = re.compile(r'<script id="meta" type="application/json">(.*?)</script>', re.DOTALL)

SITE_SUB = "2024—2026 · 研究档案"


def build_header(prefix, active=None):
    links = "".join(
        '<a%s href="%s%s">%s</a>' % (' class="active"' if active == label else "", prefix, path, label)
        for label, path in NAV
    )
    return (
        '<header class="topbar">\n'
        '  <div class="topbar-inner">\n'
        '    <a class="brand" href="%sindex.html">%s</a>\n'
        '    <nav class="topnav">%s</nav>\n'
        '    <button class="nav-btn" type="button" aria-label="打开导航" aria-expanded="false">目录</button>\n'
        '  </div>\n'
        '</header>' % (prefix, NAME, links)
    )


def build_footer(prefix):
    return (
        '<footer class="site-footer"><div class="wrap">'
        '<span>%s · %s</span>'
        '<span><a href="%sarchive.html">索引</a> · 纯静态 · GitHub Pages</span>'
        '</div></footer>' % (NAME, SITE_SUB, prefix)
    )


def active_for(relpath, text):
    """按页面相对路径判断当前板块。"""
    parts = relpath.split(os.sep)
    depth = len(parts) - 1
    fn = parts[-1]

    if depth == 0:
        return {
            "research.html": "研究", "writing.html": "写作",
            "notes.html": "笔记", "archive.html": "索引",
        }.get(fn)

    if depth == 1 and parts[0] == "subject":
        return "笔记"

    m = re.match(r"list-([a-z-]+)\.html$", fn)
    if m:
        return LIST_GROUP.get(m.group(1))

    if parts[0] == "articles":
        if depth >= 2 and parts[1] == "notes":
            meta = META_RE.search(text)
            cat = ""
            if meta:
                try:
                    cat = json.loads(meta.group(1)).get("category", "")
                except Exception:
                    cat = ""
            return CATEGORY_GROUP.get(cat, "笔记")
        meta = META_RE.search(text)
        cat = ""
        if meta:
            try:
                cat = json.loads(meta.group(1)).get("category", "")
            except Exception:
                cat = ""
        if cat in CATEGORY_GROUP:
            return CATEGORY_GROUP[cat]

    return None


def main():
    changed = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel = os.path.relpath(dirpath, ROOT)
        depth = 0 if rel == "." else len(rel.split(os.sep))
        prefix = "../" * depth
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            total += 1
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if not HEADER_RE.search(text) and not FOOTER_RE.search(text):
                continue
            active = active_for(os.path.relpath(path, ROOT), text)
            # 主题预置脚本（避免暗色用户首帧闪白）
            if 'id="theme-init"' not in text:
                text = text.replace("</head>", THEME_INIT + "\n</head>", 1)
            if HEADER_RE.search(text):
                text = HEADER_RE.sub(build_header(prefix, active), text, count=1)
            if FOOTER_RE.search(text):
                text = FOOTER_RE.sub(build_footer(prefix), text, count=1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            changed += 1
    print("扫描 %d 个页面，统一顶栏 %d 个。" % (total, changed))


if __name__ == "__main__":
    main()
