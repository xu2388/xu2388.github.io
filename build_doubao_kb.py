#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 raw_exports/doubao_share_raw/*.md 转成可浏览的问答页 + 豆包索引。
格式与 build_knowledge_base 一致：### 我（提问）/ ### 豆包（回答）。
按标题关键词自动归类。输出到 articles/kb-doubao/ + articles/doubao-index.html。
"""
import os, re, glob, html as htmlmod
from build_knowledge_base import render_md

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT, "raw_exports", "doubao_share_raw")
KB_DIR = os.path.join(ROOT, "articles", "kb-doubao")
INDEX_OUT = os.path.join(ROOT, "articles", "doubao-index.html")

CAT_ORDER = ["科研·虚拟染色", "科研·论文调研", "课程·计算机", "课程·数学/物理", "课程·英语", "思政·人文", "杂项/其他"]
CAT_KW = {
    "科研·虚拟染色": ["染色", "虚拟染色", "病理", "分割", "h&e", "ihc", "hist", "dclgan", "扩散", "flow", "gan",
                    "unet", "多尺度", "注意力", "vae", "clip", "controlnet", "生成", "图像处理", "傅里叶",
                    "对比学习", "重参数", "医学图像", "虚拟", "stain", "pspstain", "配准", "错位"],
    "科研·论文调研": ["论文", "调研", "解读", "baseline", "模型介绍", "实验", "研究方法", "相关研究"],
    "课程·计算机": ["计算机网络", "javaweb", "java", "mysql", "大数据", "信号与系统", "算法", "蓝桥杯",
                 "rnn", "操作系统", "数据库", "编程", "数据结构", "网页", "前端", "linux", "python",
                 "软件", "计组", "计算机组成", "编译"],
    "课程·数学/物理": ["数学", "高数", "线代", "概率", "物理", "微积分", "最优化", "离散"],
    "课程·英语": ["英语", "雅思", "词汇", "六级", "四级", "语法", "作文"],
    "思政·人文": ["思政", "毛概", "近代史", "马克思", "历史", "人文", "形势与政策", "国家安全"],
}

def classify(title, extra=""):
    tl = title.lower()
    for cat in CAT_ORDER[:-1]:
        if any(kw.lower() in tl for kw in CAT_KW[cat]):
            return [cat]
    # 标题没命中，看首条提问内容
    el = (extra or "").lower()
    for cat in CAT_ORDER[:-1]:
        if any(kw.lower() in el for kw in CAT_KW[cat]):
            return [cat]
    return ["杂项/其他"]

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
    return fm, blocks

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
<h1 class="site-title">科研博客 · 豆包知识库</h1>
<p class="site-subtitle">豆包学习与科研对话存档 · 一条不丢</p>
<nav class="site-nav">
<a href="../../index.html">首页</a>
<a href="../doubao-index.html">豆包索引</a>
</nav>
</div></header>
<article class="article">
<h1>{title}</h1>
<div class="meta">{topics} · {count} 条消息 · 来源：豆包分享</div>
{body}
<p class="muted" style="margin-top:28px">原始档案：<code>raw_exports/doubao_share_raw/{file}</code>　·　分享链接：<a href="{url}">{url}</a></p>
<a class="back-link" href="../doubao-index.html">← 返回豆包索引</a>
</article>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../../assets/blog.js" defer></script>
</body>
</html>
"""

def main():
    os.makedirs(KB_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.md")))
    entries = []
    for path in files:
        fm, blocks = parse(path)
        if not blocks:
            continue
        title = fm.get("title") or os.path.splitext(os.path.basename(path))[0]
        body_parts = []
        for h, content in blocks:
            if not content.strip():
                continue
            c = htmlmod.unescape(content)  # 解 &gt; &lt; &amp;
            if "我（提问）" in h or h.strip() in ("user", "我"):
                body_parts.append('<div class="record"><span class="tag">我问</span>' + render_md(c) + "</div>")
            else:
                body_parts.append(render_md(c))
        if not body_parts:
            continue
        # 首条提问用于分类兜底
        extra = ""
        for h, content in blocks:
            if "我（提问）" in h and content.strip():
                extra = content.strip()
                break
        topics = classify(title, extra)
        slug = os.path.splitext(os.path.basename(path))[0] + ".html"
        page = PAGE.format(
            title=htmlmod.escape(title),
            topics="、".join(topics),
            count=fm.get("msg_count", "?"),
            body="\n".join(body_parts),
            file=os.path.basename(path),
            url=fm.get("url", "#"),
        )
        open(os.path.join(KB_DIR, slug), "w", encoding="utf-8").write(page)
        entries.append({"title": title, "slug": slug, "topics": topics,
                        "count": fm.get("msg_count", "?"), "n": os.path.basename(path)[:3]})
    write_index(entries)
    print(f"豆包知识库：{len(entries)} 页 -> articles/kb-doubao/ ; 索引 -> articles/doubao-index.html")

def write_index(entries):
    by = {t: [] for t in CAT_ORDER}
    for e in entries:
        for t in e["topics"]:
            by.setdefault(t, []).append(e)
    secs = []
    for t in CAT_ORDER + [x for x in by if x not in CAT_ORDER]:
        items = by.get(t, [])
        if not items:
            continue
        items.sort(key=lambda x: x["n"])
        lis = "".join(
            f'<li><a href="kb-doubao/{e["slug"]}">{htmlmod.escape(e["title"])}</a>'
            f'<span class="date">{e["count"]} 条</span></li>' for e in items
        )
        secs.append(f'<section class="block"><h2>{t}（{len(items)}）</h2><ul class="article-list">{lis}</ul></section>')
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>豆包知识库 · 学习与科研对话</title>
<link rel="stylesheet" href="../assets/style.css" />
<script id="meta" type="application/json">
{{"title":"豆包知识库 · 学习与科研对话（{len(entries)} 条）","date":"2026-10-24","tags":["知识库","豆包","全量","学习"],"category":"知识库","summary":"豆包（Doubao）全部 {len(entries)} 条学习与科研对话的问答存档，按主题分组，一条不丢。每条可点进去看完整我问+AI回答，并附原始分享链接。"}}
</script>
</head>
<body>
<header class="site-header"><div class="container">
<h1 class="site-title">科研博客 · 豆包知识库</h1>
<p class="site-subtitle">豆包学习与科研对话 · {len(entries)} 条 · 一条不丢</p>
<nav class="site-nav"><a href="../index.html">首页</a><a href="knowledge-index.html">DeepSeek 知识库</a></nav>
</div></header>
<main class="container">
<nav class="crumbs"><a href="../index.html">首页</a> / 豆包知识库 · 学习与科研对话</nav>
<h1 class="list-title">豆包知识库 · 学习与科研对话</h1>
<p class="intro">这里收录我豆包账号里的 {len(entries)} 条学习与科研对话（从分享链接还原），按主题分组。每条点进去是完整的「我问 + 豆包回答」。虚拟染色、论文调研、计算机课程、思政……都在。</p>
{''.join(secs)}
</main>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../assets/blog.js" defer></script>
</body>
</html>
"""
    open(INDEX_OUT, "w", encoding="utf-8").write(page)

if __name__ == "__main__":
    main()
