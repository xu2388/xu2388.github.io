#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简 Markdown -> HTML 转换器（零依赖）
只覆盖本项目用到的子集：标题、分隔线、引用块、有序/无序列表、
表格、段落、行内 **粗体** 与 `代码`。
并内嵌 <script id="meta"> 供 build_index.py 自动收录与分组。

用法：
  python3 md_to_html.py <input.md> <category> <title> <date> <tags逗号分隔> [summary]
"""
import sys
import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link rel="stylesheet" href="../assets/style.css" />
  <script id="meta" type="application/json">
  {meta_json}
  </script>
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1 class="site-title">科研博客</h1>
      <p class="site-subtitle">H&amp;E → IHC 虚拟染色 · 一年多来的问题与踩坑记录</p>
      <nav class="site-nav">
        <a href="../index.html#threads">研究方向</a>
        <a href="../index.html#articles">文章</a>
        <a href="../index.html#about">关于</a>
      </nav>
    </div>
  </header>

  <article class="article">
    <h1>{title}</h1>
    <div class="meta">{meta_line}</div>
{body}
    <a class="back-link" href="../index.html#articles">← 返回首页</a>
  </article>

  <footer class="site-footer">
    <div class="container">
      <span>用 WorkBuddy 搭建 · 静态博客，零依赖，可随意托管</span>
    </div>
  </footer>
</body>
</html>
"""


def inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def convert(md: str) -> str:
    lines = md.split("\n")
    # 去掉文档首行的顶级 # 标题（模板已用 <h1> 渲染标题，避免重复）
    while lines and lines[0].strip() == "":
        lines.pop(0)
    if lines and re.match(r"^#\s+\S", lines[0]):
        lines.pop(0)
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if re.match(r"^\s*---\s*$", line):
            out.append("<hr />")
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue
        if line.strip().startswith("|"):
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip())
                i += 1
            rows = [r for r in tbl if not re.match(r"^\|[\s:|-]+\|$", r)]
            if rows:
                out.append("<table>")
                for ri, r in enumerate(rows):
                    cells = [c.strip() for c in r.strip().strip("|").split("|")]
                    tag = "th" if ri == 0 else "td"
                    out.append(
                        "<tr>"
                        + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells)
                        + "</tr>"
                    )
                out.append("</table>")
            continue
        if re.match(r"^\s*-\s+", line):
            buf = []
            while i < n and re.match(r"^\s*-\s+", lines[i]):
                buf.append(re.sub(r"^\s*-\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ol>")
            continue
        if line.strip() == "":
            i += 1
            continue
        buf = []
        while (
            i < n
            and lines[i].strip() != ""
            and not re.match(r"^(#{1,4}\s|>\s|-\s|\d+\.\s|\s*---\s*$)", lines[i])
            and not lines[i].strip().startswith("|")
        ):
            buf.append(lines[i])
            i += 1
        if buf:
            para = " ".join(b.strip() for b in buf)
            out.append(f"<p>{inline(para)}</p>")
    return "\n".join(out)


def main():
    if len(sys.argv) < 4:
        print("用法: python3 md_to_html.py <input.md> <category> <title> [date] [tags] [summary]")
        sys.exit(1)
    inp = sys.argv[1]
    category = sys.argv[2]
    title = sys.argv[3]
    date = sys.argv[4] if len(sys.argv) > 4 else "2026-10-24"
    tags = [t.strip() for t in sys.argv[5].split(",")] if len(sys.argv) > 5 and sys.argv[5] else []
    summary = sys.argv[6] if len(sys.argv) > 6 else title
    with open(inp, encoding="utf-8") as f:
        md = f.read()
    body = convert(md)
    meta = {
        "title": title,
        "date": date,
        "tags": tags,
        "category": category,
        "summary": summary,
    }
    meta_json = json.dumps(meta, ensure_ascii=False, indent=2)
    html = TEMPLATE.format(
        title=title,
        meta_line=f"{date} · {category}",
        meta_json=meta_json,
        body=body,
    )
    out_path = os.path.join(
        ROOT, "articles", os.path.splitext(os.path.basename(inp))[0] + ".html"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成: {out_path}")


if __name__ == "__main__":
    main()
