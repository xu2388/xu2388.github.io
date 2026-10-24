#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科研博客索引生成器
扫描 articles/*.html，读取每个文件内嵌的 <script id="meta"> JSON 元数据，
按 category 分组（研究 / 随笔 / 资料库）重建 index.html 的文章区。
线程地图（研究方向）保持手写不动。

用法：python3 build_index.py
"""
import json
import re
import os
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(ROOT, "articles")
INDEX_PATH = os.path.join(ROOT, "index.html")

CATEGORY_ORDER = ["研究", "课程笔记", "学习笔记", "随笔", "知识库", "论文", "资料库"]
CATEGORY_TITLE = {
    "研究": "研究文章",
    "课程笔记": "课程笔记 · 系统复习",
    "学习笔记": "学习笔记",
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


def extract_meta(html: str) -> dict | None:
    m = re.search(
        r'<script id="meta" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def collect() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for path in sorted(glob.glob(os.path.join(ARTICLES_DIR, "*.html"))):
        with open(path, encoding="utf-8") as f:
            html = f.read()
        meta = extract_meta(html)
        if not meta:
            continue
        meta["file"] = os.path.basename(path)
        cat = meta.get("category", "研究")
        grouped.setdefault(cat, []).append(meta)
    for cat in grouped:
        grouped[cat].sort(key=lambda x: x.get("date", ""), reverse=True)
    return grouped


def render_list(items: list[dict]) -> str:
    if not items:
        return '<p class="muted">（空）</p>'
    lines = ['<ul class="article-list">']
    for it in items:
        title = it.get("title", it.get("file", "未命名"))
        date = it.get("date", "")
        tags = " ".join(f'<span class="tag">{t}</span>' for t in it.get("tags", []))
        summary = it.get("summary", "")
        href = f"articles/{it['file']}"
        lines.append(
            f'  <li>\n'
            f'    <a href="{href}">{title}</a>'
            f'<span class="date">{date}</span><br />\n'
            f'    {tags}\n'
            f'    <span class="desc">{summary}</span>\n'
            f'  </li>'
        )
    lines.append("</ul>")
    return "\n".join(lines)


def render_section(cat: str, items: list[dict]) -> str:
    title = CATEGORY_TITLE.get(cat, cat)
    anchor = CATEGORY_ID.get(cat, "")
    idattr = f' id="{anchor}"' if anchor else ""
    return (
        f'<section class="block"{idattr}>\n'
        f'  <h2>{title}</h2>\n'
        f'  {render_list(items)}\n'
        f'</section>'
    )


def main():
    grouped = collect()
    sections = []
    for cat in CATEGORY_ORDER:
        if cat in grouped:
            sections.append(render_section(cat, grouped[cat]))
    # 其余未知分类补在最后
    for cat in grouped:
        if cat not in CATEGORY_ORDER:
            sections.append(render_section(cat, grouped[cat]))
    new_block = "\n".join(sections)

    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = f.read()

    # 替换从 <!-- ARTICLES_START --> 到 <!-- ARTICLES_END --> 的内容
    pattern = re.compile(
        r"<!-- ARTICLES_START -->.*?<!-- ARTICLES_END -->", re.DOTALL
    )
    if not pattern.search(idx):
        print("找不到 ARTICLES_START/END 标记，退出。")
        return
    idx = pattern.sub("<!-- ARTICLES_START -->\n" + new_block + "\n  <!-- ARTICLES_END -->", idx)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(idx)

    total = sum(len(v) for v in grouped.values())
    print(f"已更新索引：{total} 篇文章，分 {len(grouped)} 类。")
    for cat, items in grouped.items():
        print(f"  [{cat}] {len(items)} 篇")


if __name__ == "__main__":
    main()
