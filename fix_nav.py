#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把全站左侧目录（.site-nav）统一成同一套，并按页面所在深度改写相对路径。

为什么需要：文章页在 articles/ 下，原来导航写的是 "#research" 这种锚点，
在文章页里根本不存在对应元素，点了没反应。这个脚本按深度补 ../ 前缀。

幂等：可以反复运行。
用法：python3 fix_nav.py
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "raw_exports", "node_modules", ".github"}

# (显示名, 相对站点的路径)
NAV = [
    ("首页", "index.html"),
    ("研究文章", "index.html#research"),
    ("学习笔记", "index.html#notes"),
    ("课程笔记", "index.html#courses"),
    ("随笔", "index.html#essays"),
    ("知识库", "index.html#kb"),
    ("论文分享屋", "index.html#papers"),
    ("资料库", "index.html#archive"),
    ("关于", "index.html#about"),
]

NAV_RE = re.compile(r'<nav class="site-nav">.*?</nav>', re.DOTALL)
TITLE_RE = re.compile(r'<h1 class="site-title">.*?</h1>', re.DOTALL)
SITE_TITLE = "科研与学习档案"


def build_nav(prefix, active=None):
    parts = []
    for label, path in NAV:
        href = prefix + path
        cls = ' class="active"' if active and label == active else ""
        parts.append('<a%s href="%s">%s</a>' % (cls, href, label))
    return '<nav class="site-nav">%s</nav>' % "".join(parts)


def build_foot(prefix):
    return (
        '<div class="side-foot">'
        '<a href="%sindex.html#about">关于这个档案</a>'
        '<span>纯静态 · 零依赖 · GitHub Pages</span>'
        '</div>' % prefix
    )


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
            # 列表页按文件名高亮当前栏目（不依赖页面里已有的 class）
            active = None
            m = re.match(r"list-([a-z]+)\.html$", fn)
            if m:
                rev = {"research": "研究文章", "notes": "学习笔记", "courses": "课程笔记",
                       "essays": "随笔", "kb": "知识库", "papers": "论文分享屋", "archive": "资料库"}
                active = rev.get(m.group(1))
            elif depth == 0 and fn == "index.html":
                active = "首页"
            # 先清掉旧的侧栏页脚，保证幂等
            text = re.sub(r'<div class="side-foot">.*?</div>', "", text, flags=re.DOTALL)
            # 统一站名（各页原来叫「科研博客 · 知识库」等，不统一）
            text = TITLE_RE.sub('<h1 class="site-title">%s</h1>' % SITE_TITLE, text, count=1)
            new = NAV_RE.sub(build_nav(prefix, active) + "\n" + build_foot(prefix), text, count=1)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                changed += 1
    print("扫描 %d 个页面，改写导航 %d 个。" % (total, changed))


if __name__ == "__main__":
    main()
