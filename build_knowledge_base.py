#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量知识库生成器
把 raw_exports/deepseek_raw/ 下每一个对话转成一个干净的「问答页」，
按主题聚合成一个可浏览的知识库索引。一条对话都不丢。

规则：
- 丢掉 ### THINK / ### REASONING（AI 内部思考，非知识内容）
- 保留「我问」和 AI 回答，还原成 问→答
- 每页链接回原始 raw 文件，保证绝对忠实

用法：python3 build_knowledge_base.py
"""
import os
import re
import glob
import html as htmlmod

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT, "raw_exports", "deepseek_raw")
INVENTORY = os.path.join(ROOT, "data", "deepseek_inventory.md")
KB_DIR = os.path.join(ROOT, "articles", "kb")
INDEX_OUT = os.path.join(ROOT, "articles", "knowledge-index.html")

TOPIC_ORDER = [
    "科研-虚拟染色",
    "科研-深度学习/模型",
    "科研-论文调研",
    "课程-编程/计算机",
    "课程-数学",
    "英语-雅思",
    "考试-学校/大创",
    "杂项/其他",
]


# ---------- 极简 markdown 渲染（标题/列表/表格/代码块/引用/粗体行内码） ----------
def inline(text: str) -> str:
    text = htmlmod.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def render_md(md: str) -> str:
    lines = md.split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        # 代码围栏
        if line.strip().startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束围栏
            out.append("<pre><code>" + htmlmod.escape("\n".join(buf)) + "</code></pre>")
            continue
        if re.match(r"^\s*---\s*$", line):
            out.append("<hr />")
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2).strip())}</h{lv}>")
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
                        "<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>"
                    )
                out.append("</table>")
            continue
        if re.match(r"^\s*[-*]\s+", line):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
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
            and not re.match(r"^(#{1,4}\s|>\s|[-*]\s|\d+\.\s|\s*---\s*$)", lines[i])
            and not lines[i].strip().startswith("|")
            and not lines[i].strip().startswith("```")
        ):
            buf.append(lines[i])
            i += 1
        if buf:
            out.append("<p>" + inline(" ".join(b.strip() for b in buf)) + "</p>")
    return "\n".join(out)


# ---------- 解析单个对话 ----------
def parse_conversation(path: str) -> dict | None:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # front matter
    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    body = text
    if m:
        for ln in m.group(1).split("\n"):
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
        body = text[m.end():]
    # 分块
    blocks = []
    cur_h, cur = None, []
    for line in body.split("\n"):
        hm = re.match(r"^###\s+(.*)$", line)
        if hm:
            if cur_h is not None:
                blocks.append((cur_h, "\n".join(cur).strip()))
            cur_h, cur = hm.group(1).strip(), []
        else:
            cur.append(line)
    if cur_h is not None:
        blocks.append((cur_h, "\n".join(cur).strip()))
    # 还原 问→答（导出格式：每轮是 [THINK, 回答, 我（提问）]）
    turns = []
    pending_ans = []

    def flush(question):
        turns.append((question, "\n\n".join(pending_ans).strip()))
        pending_ans.clear()

    for header, content in blocks:
        h = header
        if ("THINK" in h) or ("REASONING" in h) or ("思考" in h):
            continue
        is_q = ("我（提问）" in h) or ("我（问）" in h) or ("提问" in h and "DeepSeek" not in h) or (h.strip() in ("user", "User", "我"))
        if is_q:
            q = content.strip()
            # 若已有未配对回答，则这些回答属于这个问题（导出把问题放在回答后）
            flush(q)
        else:
            if content:
                pending_ans.append(content)
    # 收尾：若还有未配对回答（少数情况），并成一个轮次
    if pending_ans:
        turns.append(("（见下方回答）", "\n\n".join(pending_ans).strip()))
    return {
        "title": fm.get("title", os.path.basename(path)),
        "date": fm.get("inserted_at", "")[:10],
        "count": fm.get("message_count", "?"),
        "file": os.path.basename(path),
        "turns": turns,
    }


# ---------- 从清单拿主题 ----------
def load_inventory() -> dict[str, dict]:
    mapping = {}
    if not os.path.exists(INVENTORY):
        return mapping
    with open(INVENTORY, encoding="utf-8") as f:
        for ln in f:
            if "→" not in ln or not ln.lstrip().startswith("-"):
                continue
            left, fname = ln.split("→", 1)
            fname = fname.strip().strip("`").strip()
            idm = re.search(r"\[(\d+)\]", left)
            cnt = re.search(r"(\d+)\s*条", left)
            dt = re.search(r"(\d{4}-\d{2}-\d{2})~(\d{4}-\d{2}-\d{2}),\s*(.+)$", left.strip())
            topics = []
            if dt:
                topics = [t.strip() for t in dt.group(3).split(",") if t.strip()]
            title = left
            tm = re.search(r"\]\s*(.+?)\s*—", left)
            if tm:
                title = tm.group(1).strip()
            mapping[fname] = {
                "id": idm.group(1) if idm else "?",
                "title": title,
                "count": cnt.group(1) if cnt else "?",
                "date": dt.group(1) if dt else "",
                "topics": topics,
            }
    return mapping


PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<link rel="stylesheet" href="../../assets/style.css" />
</head>
<body>
<header class="site-header"><div class="container">
<h1 class="site-title">科研博客 · 知识库</h1>
<p class="site-subtitle">全部学习对话的问答存档 · 一条不丢</p>
<nav class="site-nav">
<a href="../../index.html">首页</a>
<a href="../knowledge-index.html">知识库索引</a>
</nav>
</div></header>
<article class="article">
<h1>{title}</h1>
<div class="meta">{date} · 主题：{topics} · {count} 条消息 · 对话编号 {cid}</div>
{body}
<p class="muted" style="margin-top:28px">原始档案：<code>raw_exports/deepseek_raw/{file}</code>（未删减，含 AI 思考过程）</p>
<a class="back-link" href="../knowledge-index.html">← 返回知识库索引</a>
</article>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../../assets/blog.js" defer></script>
</body>
</html>
"""


def render_turns(turns):
    parts = []
    for q, a in turns:
        parts.append('<div class="record"><span class="tag">我问</span>' + render_md(q) + "</div>")
        if a:
            parts.append(render_md(a))
    return "\n".join(parts)


def main():
    os.makedirs(KB_DIR, exist_ok=True)
    inv = load_inventory()
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.md")))
    entries = []  # (topics, meta, slug)
    for path in files:
        conv = parse_conversation(path)
        if not conv:
            continue
        slug = os.path.splitext(os.path.basename(path))[0] + ".html"
        info = inv.get(conv["file"], {})
        topics = info.get("topics", ["杂项/其他"])
        cid = info.get("id", "?")
        date = info.get("date", conv["date"])
        count = info.get("count", conv["count"])
        body = render_turns(conv["turns"])
        page = PAGE.format(
            title=htmlmod.escape(conv["title"]),
            date=date,
            topics="、".join(topics),
            count=count,
            cid=cid,
            file=conv["file"],
            body=body,
        )
        with open(os.path.join(KB_DIR, slug), "w", encoding="utf-8") as f:
            f.write(page)
        entries.append({"topics": topics, "title": conv["title"], "slug": slug,
                        "date": date, "count": count, "id": cid})
    # 生成索引（按主题分组）
    write_index(entries)
    print(f"已生成 {len(entries)} 个问答页 -> articles/kb/")
    print("已生成索引 -> articles/knowledge-index.html")


def write_index(entries):
    # 主题 -> [entry]
    by_topic = {t: [] for t in TOPIC_ORDER}
    for e in entries:
        for t in e["topics"]:
            by_topic.setdefault(t, []).append(e)
    sections = []
    for t in TOPIC_ORDER + [x for x in by_topic if x not in TOPIC_ORDER]:
        items = by_topic.get(t, [])
        if not items:
            continue
        items = sorted(items, key=lambda x: x["date"], reverse=True)
        lis = []
        for e in items:
            lis.append(
                f'<li><a href="kb/{e["slug"]}">{htmlmod.escape(e["title"])}</a>'
                f'<span class="date">{e["date"]} · {e["count"]}条 · #{e["id"]}</span></li>'
            )
        sections.append(
            f'<section class="block"><h2>{t}（{len(items)}）</h2>'
            f'<ul class="article-list">' + "".join(lis) + "</ul></section>"
        )
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>知识库 · 全部学习对话</title>
<link rel="stylesheet" href="../assets/style.css" />
<script id="meta" type="application/json">
{{"title":"知识库 · 全部学习对话（{len(entries)} 条）","date":"2026-10-24","tags":["知识库","全量","学习"],"category":"知识库","summary":"把 DeepSeek 全部 {len(entries)} 条对话转成可浏览的问答存档，按主题分组，一条不丢。每条都可点进去看完整我问+AI回答，并链接回未删减的原始档案。"}}
</script>
</head>
<body>
<header class="site-header"><div class="container">
<h1 class="site-title">科研博客 · 知识库</h1>
<p class="site-subtitle">全部学习对话的问答存档 · {len(entries)} 条 · 一条不丢</p>
<nav class="site-nav"><a href="../index.html">首页</a></nav>
</div></header>
<main class="container">
<nav class="crumbs"><a href="../index.html">首页</a> / 知识库 · DeepSeek 全部对话</nav>
<h1 class="list-title">知识库 · DeepSeek 全部对话</h1>
<p class="intro">这里收录了我（DeepSeek）全部 {len(entries)} 条对话，按主题分组。每条点进去是完整的「我问 + AI 回答」，并链接回未删减的原始档案。科研、课程、数学、雅思、考试、论文调研……都在。</p>
{''.join(sections)}
</main>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../assets/blog.js" defer></script>
</body>
</html>
"""
    with open(INDEX_OUT, "w", encoding="utf-8") as f:
        f.write(page)


if __name__ == "__main__":
    main()
