#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包本地资料整合
把本地能拿到的豆包内容整理成博客页：
1. 上传的 JavaWeb 手写笔记（txt，转义后原样呈现）
2. MBTI 连续人格空间研究管线（html，原样嵌入）
3. 豆包 agent 会话（trajectory 还原的 md）

注意：豆包「主聊天」在网页端、需账号登录，本地拿不到，只能等用户导出。
"""
import os
import re
import html as htmlmod

ROOT = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(ROOT, "articles")
DOUBAO_CHATS = "/Users/hua/Doubao/chats"
AGENT_RAW = os.path.join(ROOT, "raw_exports", "doubao_agent_raw")

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<link rel="stylesheet" href="../assets/style.css" />
<script id="meta" type="application/json">
{meta}
</script>
</head>
<body>
<header class="site-header"><div class="container">
<h1 class="site-title">科研博客</h1>
<p class="site-subtitle">H&amp;E → IHC 虚拟染色 · 学习记录与知识库</p>
<nav class="site-nav"><a href="../index.html#articles">文章</a><a href="../index.html#threads">研究方向</a></nav>
</div></header>
<article class="article">
<h1>{title}</h1>
<div class="meta">{meta_line}</div>
{body}
<a class="back-link" href="../index.html#articles">← 返回首页</a>
</article>
<footer class="site-footer"><div class="container"><span>用 WorkBuddy 搭建 · 静态博客</span></div></footer>
<script src="../assets/blog.js" defer></script>
</body>
</html>
"""


def write_page(fname, title, category, tags, summary, meta_line, body):
    import json
    meta = json.dumps(
        {"title": title, "date": "2026-10-24", "tags": tags, "category": category, "summary": summary},
        ensure_ascii=False, indent=2,
    )
    page = PAGE.format(title=htmlmod.escape(title), meta=meta, meta_line=meta_line, body=body)
    with open(os.path.join(ART, fname), "w", encoding="utf-8") as f:
        f.write(page)
    print("已生成 articles/" + fname)


def javaweb_notes():
    path = os.path.join(DOUBAO_CHATS, "2026-09-13", "new-chat", "Javaweb手写笔记全文本.txt")
    if not os.path.exists(path):
        print("找不到 JavaWeb 笔记:", path)
        return
    with open(path, encoding="utf-8", errors="replace") as f:
        txt = f.read()
    esc = htmlmod.escape(txt)
    body = (
        '<div class="note"><span class="tag">来源</span>'
        '这是我上传到豆包的 <b>JavaWeb 手写笔记全文本</b>（2026-09-13），原样保留、未删改。'
        '笔记里的 HTML 代码已做转义显示，方便直接读。原始文件：'
        '<code>/Users/hua/Doubao/chats/2026-09-13/new-chat/</code>。</div>'
        f'<div class="notes">{esc}</div>'
    )
    write_page(
        "doubao-javaweb-notes.html",
        "JavaWeb 手写笔记（课程学习存档）",
        "学习笔记",
        ["JavaWeb", "HTML", "课程笔记", "豆包"],
        "我上传到豆包的 JavaWeb 手写笔记全文本，从 HTML 基础、标签、表单到后面的 Web 开发，是我课程学习的原始存档，一条未删。",
        "学习笔记 · 豆包上传 · 2026-09-13 · 1732 行",
        body,
    )


def mbti_pipeline():
    path = os.path.join(DOUBAO_CHATS, "2026-09-14", "new-chat", "mbti_pipeline_overview.html")
    if not os.path.exists(path):
        print("找不到 MBTI 管线:", path)
        return
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    # 去掉外层 <html>，只保留内部 div（自包含、行内样式）
    inner = raw
    inner = re.sub(r"^\s*<html[^>]*>", "", inner)
    inner = re.sub(r"</html>\s*$", "", inner)
    body = (
        '<div class="note"><span class="tag">来源</span>'
        '这是我做的一个研究项目——<b>MBTI 连续人格空间与分布建模</b>的阶段总览图，'
        '从豆包上传记录里原样恢复。核心链路 X → Z_attr → Z_neural → P(Z|M) → P(A|S,Z)，'
        '中间设 6 道阶段闸门，每一步不达标就不往下走。完整的数学结构与方案在下面的 agent 会话存档里。</div>'
        f'<div class="embed-frame">{inner}</div>'
    )
    write_page(
        "doubao-mbti-pipeline.html",
        "MBTI 连续人格空间研究管线（阶段总览）",
        "研究",
        ["MBTI", "人格建模", "VAE", "研究设计", "豆包"],
        "我设计的一个研究项目：把 MBTI 从 16 类离散类型扩展成连续人格空间，X→Z→P(Z|M)→P(A|S,Z) 六道阶段闸门。这是阶段总览图，从豆包上传记录恢复。",
        "研究 · 豆包上传 · 2026-09-14",
        body,
    )


def agent_sessions():
    files = sorted(
        f for f in os.listdir(AGENT_RAW) if f.endswith(".md") and not f.startswith("_")
    ) if os.path.isdir(AGENT_RAW) else []
    if not files:
        print("没有豆包 agent 会话 md")
        return
    import json
    index_items = []
    for fn in files:
        with open(os.path.join(AGENT_RAW, fn), encoding="utf-8", errors="replace") as f:
            content = f.read()
        # 简单转义呈现
        esc = htmlmod.escape(content)
        title = fn.replace("doubao_", "豆包会话 ").replace(".md", "")
        slug = "agent_" + fn.replace(".md", ".html")
        body = (
            '<div class="note"><span class="tag">来源</span>'
            '豆包 agent 模式会话还原（本地 trajectory 日志）。原样保留。</div>'
            f'<div class="notes">{esc}</div>'
        )
        write_page(
            slug, title, "资料库", ["豆包", "agent会话"], title,
            "资料库 · 豆包 agent 会话", body,
        )
        index_items.append((title, slug))
    # 汇总说明
    lst = "".join(f'<li><a href="{s}">{htmlmod.escape(t)}</a></li>' for t, s in index_items)
    body = (
        '<div class="note"><span class="tag">说明</span>'
        '豆包 <b>agent 模式</b>的会话缓存在本地留了 trajectory 日志，我能从这里还原出你的研究长提示'
        '（其中一份是完整的「MBTI 连续人格空间建模 v0.2」方案，带五层数学结构）。'
        '下面是每个会话的还原存档。</div>'
        f'<ul class="article-list">{lst}</ul>'
        '<div class="note"><span class="tag">待补充</span>'
        '豆包的<b>主聊天记录</b>在网页端、需要你的账号登录，我本机拿不到。'
        '要用「AI导出鸭」批量导出成 Markdown 丢进 <code>raw_exports/</code>，我就能自动解析归类进来。</div>'
    )
    write_page(
        "doubao-agent-sessions.html",
        "豆包 agent 会话存档",
        "资料库",
        ["豆包", "agent会话", "MBTI"],
        "从豆包 agent 模式本地 trajectory 日志还原的研究会话存档，含 MBTI 连续人格空间建模的完整方案。",
        "资料库 · 豆包 agent 会话",
        body,
    )


if __name__ == "__main__":
    javaweb_notes()
    mbti_pipeline()
    agent_sessions()
    print("豆包本地资料整合完成。")
