#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一全站左侧目录，并按页面所在深度改写相对路径。

信息架构改成「首页 / 科研 / 学习 / 随笔 / 搜索」之后，文章页在 articles/ 下，
导航必须按深度补 ../ 前缀，且要根据页面所属板块高亮对应项。

幂等：可以反复运行。
用法：python3 fix_nav.py
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "raw_exports", "node_modules", ".github"}

# (显示名, 相对站点的路径, 计数键)
NAV = [
    ("首页", "index.html", None),
    ("科研", "research.html", "research"),
    ("学习", "study.html", "study"),
    ("随笔", "essays.html", "essays"),
    ("搜索", "search.html", None),
]

# articles/list-*.html → 所属板块
LIST_GROUP = {
    "research": "科研", "readings": "科研", "research-notes": "科研",
    "survey": "科研", "papers": "科研", "archive": "科研",
    "tutorials": "学习", "notes": "学习", "courses": "学习", "kb": "学习",
    "essays": "随笔",
}

# 文章分类 → 所属板块
CATEGORY_GROUP = {
    "研究": "科研", "调研": "科研", "论文": "科研", "资料库": "科研",
    "学习笔记": "学习", "课程笔记": "学习", "知识库": "学习",
    "随笔": "随笔",
}

THEME_INIT = ('<script id="theme-init">try{var t=localStorage.getItem("theme");'
              'if(!t)t=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";'
              'document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>')

NAV_RE = re.compile(r'<nav class="site-nav">.*?</nav>', re.DOTALL)
TITLE_RE = re.compile(r'<h1 class="site-title">.*?</h1>', re.DOTALL)
SUB_RE = re.compile(r'<p class="site-subtitle">.*?</p>', re.DOTALL)
META_RE = re.compile(r'<script id="meta" type="application/json">(.*?)</script>', re.DOTALL)
SITE_TITLE = "科研与学习档案"
SITE_SUB = "Research &amp; Study Archive"


def _load_counts():
    try:
        with open(os.path.join(ROOT, "data", "nav_counts.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def build_nav(prefix, active=None):
    counts = _load_counts()
    parts = []
    for label, path, key in NAV:
        badge = ""
        n = counts.get(key) if key else None
        if n:
            badge = '<span class="n">%d</span>' % n
        cls = ' class="active"' if active == label else ""
        parts.append('<a%s href="%s%s">%s%s</a>' % (cls, prefix, path, label, badge))
    return '<nav class="site-nav">%s</nav>' % "".join(parts)


def build_foot(prefix):
    return (
        '<div class="side-foot">'
        '<a href="%sarticles/list-archive.html">资料库 · 审计与溯源</a>'
        '<span class="fine">纯静态 · GitHub Pages</span>'
        '</div>' % prefix
    )


def active_for(relpath, text):
    """按页面相对路径判断当前板块。"""
    parts = relpath.split(os.sep)
    depth = len(parts) - 1
    fn = parts[-1]

    if depth == 0:
        return {
            "index.html": "首页", "research.html": "科研", "study.html": "学习",
            "essays.html": "随笔", "search.html": "搜索",
        }.get(fn)

    if depth == 1 and parts[0] == "study":
        return "学习"

    m = re.match(r"list-([a-z-]+)\.html$", fn)
    if m:
        return LIST_GROUP.get(m.group(1))

    if depth == 1 and parts[0] == "articles":
        meta = META_RE.search(text)
        if meta:
            try:
                cat = json.loads(meta.group(1)).get("category", "")
            except Exception:
                cat = ""
            if cat in CATEGORY_GROUP:
                return CATEGORY_GROUP[cat]

    if depth >= 2 and parts[0] == "articles":
        if parts[1] == "notes":
            meta = META_RE.search(text)
            if meta:
                try:
                    cat = json.loads(meta.group(1)).get("category", "")
                except Exception:
                    cat = ""
                if cat == "研究":
                    return "科研"
            return "学习"
        if parts[1] in ("kb", "kb-doubao"):
            return "学习"

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
            if not NAV_RE.search(text):
                continue
            active = active_for(os.path.relpath(path, ROOT), text)
            # 先清掉旧的侧栏页脚，保证幂等
            text = re.sub(r'<div class="side-foot">.*?</div>', "", text, flags=re.DOTALL)
            # 统一站名
            text = TITLE_RE.sub('<h1 class="site-title">%s</h1>' % SITE_TITLE, text, count=1)
            # 侧栏副标题各页原本各不相同，统一成站名下方的一行英文
            text = SUB_RE.sub('<p class="site-subtitle">%s</p>' % SITE_SUB, text, count=1)
            # 确保 <head> 里有主题预置脚本（避免暗色用户首帧闪白）
            if 'id="theme-init"' not in text:
                text = text.replace("</head>", THEME_INIT + "\n</head>", 1)
            new = NAV_RE.sub(build_nav(prefix, active) + "\n" + build_foot(prefix), text, count=1)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                changed += 1
    print("扫描 %d 个页面，改写导航 %d 个。" % (total, changed))


if __name__ == "__main__":
    main()
