#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点生成器（取代 build_index.py）

信息架构（三级，越点越具体）：
    首页 index.html
      ├── 科研 research.html
      │     ├── 研究文章   articles/list-research.html
      │     ├── 论文精读   articles/list-readings.html
      │     ├── 研究笔记   articles/list-research-notes.html
      │     ├── 调研档案   articles/survey-catalog.html
      │     └── 论文导读   articles/papers-index.html
      ├── 学习 study.html
      │     ├── study/<学科>.html   （按 20 门学科，每门一页）
      │     ├── 教程       articles/list-tutorials.html
      │     └── 对话存档   articles/knowledge-index.html
      ├── 随笔 essays.html
      └── 搜索 search.html（标题搜索，索引 data/search-index.js）

产出：index.html / research.html / study.html / study/*.html / essays.html /
      search.html / articles/list-*.html / data/search-index.js / data/nav_counts.json

用法：python3 build_notes.py && python3 build_site.py && python3 fix_nav.py
"""
import os
import re
import json
import glob
import time
import html as htmlmod

from fix_nav import build_nav, build_foot
from site_model import (SUBJECTS, GROUP_ORDER, RESEARCH_SUBJECT,
                        subject_slug, subject_group, subject_desc, subject_sort_key)

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES = os.path.join(ROOT, "articles")
NOTES = os.path.join(ROOT, "notes")
DATA = os.path.join(ROOT, "data")

SITE_TITLE = "科研与学习档案"
SITE_SUB = "Research &amp; Study Archive"


# ------------------------------------------------------------------ 工具
def esc(s):
    return htmlmod.escape(str(s or ""))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ------------------------------------------------------------------ 采集
def collect_articles():
    """扫 articles/*.html 的内嵌 meta。"""
    items = []
    for path in sorted(glob.glob(os.path.join(ARTICLES, "*.html"))):
        base = os.path.basename(path)
        if base.startswith("list-"):
            continue
        text = read(path)
        m = re.search(r'<script id="meta" type="application/json">(.*?)</script>', text, re.DOTALL)
        if not m:
            continue
        try:
            meta = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        items.append({
            "title": meta.get("title", base),
            "date": meta.get("date", ""),
            "summary": meta.get("summary", ""),
            "tags": meta.get("tags", []),
            "category": meta.get("category", ""),
            "url": "articles/" + base,
        })
    # 日期降序；同日期按文件名升序（001 在前）
    items.sort(key=lambda x: x["url"])
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def parse_front(text):
    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for ln in m.group(1).split("\n"):
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm


def collect_notes():
    items = []
    for path in sorted(glob.glob(os.path.join(NOTES, "*.md"))):
        fm = parse_front(read(path))
        if not fm.get("title"):
            continue
        slug = os.path.splitext(os.path.basename(path))[0] + ".html"
        subject = fm.get("subject", "其他")
        mtime = os.path.getmtime(path)
        items.append({
            "title": fm["title"],
            "subject": subject,
            "category": fm.get("category", "课程笔记"),
            "summary": fm.get("summary", ""),
            "url": "articles/notes/" + slug,
            "file": os.path.basename(path),
            "mtime": mtime,
            "date": time.strftime("%Y-%m-%d", time.localtime(mtime)),
        })
    items.sort(key=lambda x: x["file"])
    return items


def count_pattern(path, pattern):
    if not os.path.exists(path):
        return 0
    m = re.search(pattern, read(path))
    return int(m.group(1)) if m else 0


# ------------------------------------------------------------------ 页面骨架
def shell(title, body, prefix="", active=None, body_class="", desc=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc or SITE_TITLE)}" />
<link rel="stylesheet" href="{prefix}assets/style.css" />
<script id="theme-init">try{{var t=localStorage.getItem("theme");if(!t)t=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}</script>
</head>
<body class="{body_class}">
<header class="site-header">
  <div class="container">
    <div class="side-brand">
      <a class="side-avatar" href="{prefix}index.html" aria-label="回到首页">RS</a>
      <div>
        <h1 class="site-title">{SITE_TITLE}</h1>
        <p class="site-subtitle">{SITE_SUB}</p>
      </div>
    </div>
    {build_nav(prefix, active)}
    {build_foot(prefix)}
  </div>
</header>

<main class="container">
{body}
</main>

<footer class="site-footer"><div class="container"><span>科研与学习档案 · 纯静态 · GitHub Pages</span></div></footer>
<script src="{prefix}assets/blog.js" defer></script>
</body>
</html>
"""


def badge(section):
    cls = {"科研": "b-research", "学习": "b-study", "随笔": "b-essay", "资料库": "b-archive"}.get(section, "b-study")
    return f'<i class="badge {cls}">{esc(section)}</i>'


def article_list(items, prefix="", show_date=True, show_tags=True, clamp=False):
    if not items:
        return '<p class="muted">（暂无内容）</p>'
    out = ['<ul class="article-list">']
    for it in items:
        title = esc(it["title"])
        date = it.get("date", "")
        tags = ""
        if show_tags and it.get("tags"):
            tags = " ".join('<span class="tag">%s</span>' % esc(t) for t in it["tags"][:5])
        date_html = f'<span class="date">{date}</span>' if (show_date and date) else ""
        out.append(
            f'<li><a href="{prefix}{it["url"]}">{title}</a>{date_html}'
            f'{tags}<span class="desc">{esc(it.get("summary", ""))}</span></li>'
        )
    out.append("</ul>")
    return "\n".join(out)


# ------------------------------------------------------------------ 首页
def page_home(arts, notes, survey_n, paper_n, kb_n):
    research = [a for a in arts if a["category"] == "研究"]
    readings = [a for a in research if "论文精读" in a["tags"]]
    res_notes = [n for n in notes if n["subject"] == RESEARCH_SUBJECT]
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]
    subjects = sorted({n["subject"] for n in course_notes}, key=subject_sort_key)
    tutorials = [a for a in arts if a["category"] == "学习笔记"]
    essays = [a for a in arts if a["category"] == "随笔"]

    # 最近更新：文章按 meta 日期、笔记按源文件修改时间，混排后取前 9 条
    pool = []
    for a in arts:
        if a["category"] == "研究":
            sec = "科研"
        elif a["category"] == "随笔":
            sec = "随笔"
        elif a["category"] == "学习笔记":
            sec = "学习"
        else:
            continue
        pool.append((a["date"], sec, a["title"], a["url"]))
    for n in notes:
        pool.append((n["date"], "科研" if n["subject"] == RESEARCH_SUBJECT else "学习",
                     n["title"], n["url"]))

    def pick(sec, k):
        return [x for x in sorted(pool, key=lambda x: (x[0], x[3]), reverse=True) if x[1] == sec][:k]

    # 科研 / 学习交替排列，避免某一天新增的笔记把首页刷成单一板块
    r, s, e = pick("科研", 4), pick("学习", 4), pick("随笔", 2)
    recent = []
    for i in range(4):
        if i < len(r):
            recent.append(r[i])
        if i < len(s):
            recent.append(s[i])
    recent += e

    def door(kind, en, name, headline, desc, rows, go):
        lis = "".join(
            f'<li><span>{esc(k)}</span><i></i><b>{v}</b></li>' for k, v in rows
        )
        return f"""<a class="door door--{kind}" href="{kind}.html">
  <div class="door-top"><span class="door-en">{en}</span><span class="door-headline">{headline}</span></div>
  <h2>{name}</h2>
  <p class="door-desc">{desc}</p>
  <ul class="door-list">{lis}</ul>
  <span class="door-go">{go} <em>→</em></span>
</a>"""

    research_door = door(
        "research", "RESEARCH", "科研",
        f'<b>{len(research)}</b> 篇文章 · <b>{survey_n}</b> 份调研档案',
        "研究记录、论文精读、调研档案与论文导读。按内容形态分层，点进去就是全文。",
        [("研究文章", len(research)), ("论文精读", len(readings)), ("研究笔记", len(res_notes)),
         ("调研档案", survey_n), ("论文导读", paper_n)],
        "进入科研",
    )
    study_door = door(
        "study", "STUDY", "学习",
        f'<b>{len(course_notes)}</b> 篇笔记 · <b>{len(subjects)}</b> 门学科',
        "按学科归档的专业课笔记，每门学科一页；另有成系列教程与全部学习对话存档。",
        [("学科笔记", len(course_notes)), ("覆盖学科", len(subjects)), ("教程", len(tutorials)),
         ("对话存档", kb_n)],
        "进入学习",
    )

    recent_lis = "".join(
        f'<li><a href="{u}">{esc(t)}</a>'
        f'<span class="recent-meta">{badge(s)}<span class="recent-date">{d}</span></span></li>'
        for d, s, t, u in recent
    )

    body = f"""
<section class="home-intro">
  <p class="eyebrow"><span class="dot"></span>ARCHIVE · 2024—2026</p>
  <h1>{SITE_TITLE}</h1>
  <p class="lede">一个本科生的科研与学习记录。内容分成 <b>科研</b> 与 <b>学习</b> 两个板块，
    每个板块再按主题、学科细分，逐层点进去就是文章。</p>
  <form class="home-search" action="search.html" role="search">
    <input type="search" name="q" placeholder="搜索文章标题…" aria-label="搜索文章标题" autocomplete="off" />
    <button type="submit" aria-label="搜索">→</button>
  </form>
</section>

<div class="doors">
{research_door}
{study_door}
</div>

<section class="recent">
  <div class="recent-head"><h2>最近更新</h2><a class="more" href="search.html">搜索全部 →</a></div>
  <ul class="recent-list">{recent_lis}</ul>
</section>

<section class="home-extra">
  <a class="extra-card" href="essays.html"><span class="extra-en">ESSAYS</span><span class="extra-name">随笔</span><span class="extra-n">{len(essays)} 篇</span></a>
  <a class="extra-card" href="articles/list-archive.html"><span class="extra-en">ARCHIVE</span><span class="extra-name">资料库</span><span class="extra-n">审计与溯源</span></a>
  <a class="extra-card" href="search.html"><span class="extra-en">SEARCH</span><span class="extra-name">搜索</span><span class="extra-n">按标题查找</span></a>
</section>

<section class="about" id="about">
  <h2>关于</h2>
  <p>内容来自我和 AI 助手（DeepSeek、豆包、WorkBuddy）一年多的科研与学习对话，由 WorkBuddy 整理。
    原则只有一条：<strong>原始信息不删减、思考过程原样保留、每条结论尽量能溯源到具体对话</strong>。</p>
  <p>纯静态站点，零依赖，托管于 GitHub Pages。新增内容：把 Markdown 放进
    <code>notes/</code>（带 frontmatter 的学科笔记）或 <code>articles_src/</code>（长文章），
    跑一遍 <code>./publish.sh</code> 即可自动收录、归类、生成学科页与搜索索引。</p>
</section>
"""
    return shell(SITE_TITLE, body, "", "首页", "home",
                 "一个本科生的科研与学习档案：科研、学习两大板块，按主题与学科细分。")


# ------------------------------------------------------------------ 科研板块
def page_research(arts, notes, survey_n, paper_n, archive_n):
    research = [a for a in arts if a["category"] == "研究"]
    readings = [a for a in research if "论文精读" in a["tags"]]
    res_notes = [n for n in notes if n["subject"] == RESEARCH_SUBJECT]

    def card(no, name, n, unit, desc, href, preview, go, tags=None):
        pv = ""
        if preview:
            pv = '<ul class="hub-preview">' + "".join(f"<li>{esc(t)}</li>" for t in preview) + "</ul>"
        elif tags:
            pv = '<div class="hub-tags">' + "".join(f'<span class="tag">{esc(t)}</span>' for t in tags) + "</div>"
        return f"""<a class="hub-card" href="{href}">
  <div class="hub-card-top"><span class="hub-kicker">{no}</span><span class="hub-n">{n}<small>{unit}</small></span></div>
  <h2>{name}</h2>
  <p class="hub-desc">{desc}</p>
  {pv}
  <span class="hub-go">{go} <em>→</em></span>
</a>"""

    core = [a for a in research if "论文精读" not in a["tags"]]
    core_preview = [a["title"] for a in (core or research)[:3]]

    cards = [
        card("01", "研究文章", len(research), "篇",
             "完整的研究记录：问题、方法、实验与自我推翻，保留原始数据与当时的判断。",
             "articles/list-research.html", core_preview, f"全部 {len(research)} 篇"),
        card("02", "论文精读", len(readings), "篇",
             "逐篇拆解的文献：方法、结构约束与评价口径，以及和本方向的关系。",
             "articles/list-readings.html",
             [a["title"] for a in readings[:3]], f"全部 {len(readings)} 篇"),
        card("03", "研究笔记", len(res_notes), "篇",
             "研究过程中的专题笔记：概念、推导、实验设置与踩坑记录。",
             "articles/list-research-notes.html",
             [n["title"] for n in res_notes[:3]], f"全部 {len(res_notes)} 篇"),
        card("04", "调研档案", survey_n, "份",
             "整批文献调研的原始档案：文献地图、逐篇翻译、精读与方案审查。",
             "articles/survey-catalog.html", [], "打开总目",
             ["文献地图", "论文翻译", "逐篇精读", "伪影归因", "方案审查"]),
        card("05", "论文导读", paper_n, "篇",
             "读过并留档的论文清单，每篇一句话总结 + 与本方向的关系。",
             "articles/papers-index.html", [], "打开导读",
             ["按主题分组", "一句话总结", "可检索清单"]),
        card("06", "资料库", archive_n, "份",
             "全量审计、覆盖率清单与原始存档说明，用于溯源核对。",
             "articles/list-archive.html", [], "打开资料库",
             ["全量审计", "覆盖率", "原始存档"]),
    ]

    body = f"""
<nav class="crumbs"><a href="index.html">首页</a> <span>/</span> 科研</nav>
<header class="hub-head hub-head--research">
  <p class="eyebrow"><span class="dot"></span>RESEARCH</p>
  <h1>科研</h1>
  <p class="lede">按内容形态分成六类：长文记录、论文精读、专题笔记、调研档案、论文导读与资料库。
    每一类点进去都是完整清单。</p>
  <div class="hub-stats">
    <span><b>{len(research)}</b> 篇文章</span>
    <span><b>{len(res_notes)}</b> 篇研究笔记</span>
    <span><b>{survey_n}</b> 份调研档案</span>
    <span><b>{paper_n}</b> 篇论文导读</span>
  </div>
</header>
<div class="hub-grid">
{"".join(cards)}
</div>
"""
    return shell("科研 · " + SITE_TITLE, body, "", "科研", "hub",
                 "科研板块：研究文章、论文精读、研究笔记、调研档案与论文导读。")


# ------------------------------------------------------------------ 学习板块
def page_study(arts, notes):
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]
    tutorials = [a for a in arts if a["category"] == "学习笔记"]
    by_subject = {}
    for n in course_notes:
        by_subject.setdefault(n["subject"], []).append(n)
    subjects = sorted(by_subject, key=subject_sort_key)

    sections = []
    for group in GROUP_ORDER:
        subs = [s for s in subjects if subject_group(s) == group]
        if not subs:
            continue
        n_total = sum(len(by_subject[s]) for s in subs)
        cards = []
        for s in subs:
            items = by_subject[s]
            latest = items[-1]["title"] if items else ""
            for pre in (s + " · ", s + "·", s + "："):
                if latest.startswith(pre):
                    latest = latest[len(pre):]
                    break
            cards.append(f"""<a class="subj-card" href="study/{subject_slug(s)}.html">
  <span class="subj-top"><span class="subj-name">{esc(s)}</span><span class="subj-n">{len(items)}</span></span>
  <span class="subj-desc">{esc(subject_desc(s))}</span>
  <span class="subj-latest">最近 · {esc(latest)}</span>
</a>""")
        sections.append(f"""<section class="subj-group">
  <div class="subj-group-head"><h2>{group}</h2><span>{len(subs)} 门学科 · {n_total} 篇</span></div>
  <div class="subj-grid">
{chr(10).join(cards)}
  </div>
</section>""")

    body = f"""
<nav class="crumbs"><a href="index.html">首页</a> <span>/</span> 学习</nav>
<header class="hub-head hub-head--study">
  <p class="eyebrow"><span class="dot"></span>STUDY</p>
  <h1>学习</h1>
  <p class="lede">按学科归档。下面每一张卡片是一门学科，点进去是该学科的全部笔记；
    教程与对话存档单独放在最后。</p>
  <div class="hub-stats">
    <span><b>{len(course_notes)}</b> 篇学科笔记</span>
    <span><b>{len(subjects)}</b> 门学科</span>
    <span><b>{len(tutorials)}</b> 篇教程</span>
  </div>
</header>

{"".join(sections)}

<section class="wide-cards">
  <a class="wide-card" href="articles/list-tutorials.html">
    <span class="wide-en">TUTORIALS</span>
    <h2>教程 <span class="n">{len(tutorials)}</span></h2>
    <p>从一个具体困惑出发，把机制讲到能自己推一遍。</p>
    <span class="hub-go">全部 {len(tutorials)} 篇 <em>→</em></span>
  </a>
  <a class="wide-card" href="articles/knowledge-index.html">
    <span class="wide-en">CONVERSATIONS</span>
    <h2>对话存档 <span class="n">368</span></h2>
    <p>DeepSeek 270 条 + 豆包 98 条学习对话，一条不丢，可溯源。</p>
    <span class="hub-go">打开存档 <em>→</em></span>
  </a>
</section>

<p class="hub-note">也可以<a href="articles/notes-index.html">在一页里看全部 {len(course_notes)} 篇学科笔记</a>（按学科分组）。</p>
"""
    return shell("学习 · " + SITE_TITLE, body, "", "学习", "hub hub--study",
                 "学习板块：按学科归档的专业课笔记、教程与学习对话存档。")


# ------------------------------------------------------------------ 学科页
def page_subject(subject, items):
    items = sorted(items, key=lambda x: x["title"])
    lis = "".join(
        f'<li><a href="../{n["url"]}">{esc(n["title"])}</a>'
        f'<span class="desc">{esc(n["summary"])}</span></li>'
        for n in items
    )
    group = subject_group(subject)
    body = f"""
<nav class="crumbs"><a href="../index.html">首页</a> <span>/</span> <a href="../study.html">学习</a> <span>/</span> {esc(subject)}</nav>
<header class="subj-head">
  <p class="eyebrow">{esc(group)}</p>
  <h1>{esc(subject)}</h1>
  <p class="lede">{esc(subject_desc(subject))} · 共 {len(items)} 篇</p>
</header>
<ul class="article-list plain">
{lis}
</ul>
<div class="subj-foot">
  <a class="back-link" href="../study.html">← 返回学习</a>
</div>
"""
    return shell(f"{subject} · 学习 · {SITE_TITLE}", body, "../", "学习", "hub hub--study",
                 f"{subject}的全部笔记（{len(items)} 篇）。")


# ------------------------------------------------------------------ 随笔
def page_essays(essays):
    body = f"""
<nav class="crumbs"><a href="index.html">首页</a> <span>/</span> 随笔</nav>
<header class="list-head">
  <p class="eyebrow"><span class="dot"></span>ESSAYS</p>
  <h1>随笔</h1>
  <p class="lede">自己写的科普长文，讲本质，不堆术语。</p>
</header>
{article_list(essays)}
"""
    return shell("随笔 · " + SITE_TITLE, body, "", "随笔", "hub", "随笔与科普长文。")


# ------------------------------------------------------------------ 通用清单页
def page_list(title, desc, items, filename, active, kicker=""):
    body = f"""
<nav class="crumbs"><a href="../index.html">首页</a> <span>/</span> <a href="../{"research" if active == "科研" else "study"}.html">{active}</a> <span>/</span> {esc(title)}</nav>
<header class="list-head">
  <p class="eyebrow">{esc(kicker or active)}</p>
  <h1>{esc(title)}</h1>
  <p class="lede">{esc(desc)}　共 {len(items)} 篇</p>
</header>
{article_list(items, prefix="../")}
<div class="subj-foot"><a class="back-link" href="../index.html">← 返回首页</a></div>
"""
    write(os.path.join(ARTICLES, filename),
          shell(f"{title} · {SITE_TITLE}", body, "../", active, "hub", desc))


# ------------------------------------------------------------------ 搜索页
def page_search(by_subject, research_n, survey_n, essays_n):
    course_n = sum(len(v) for v in by_subject.values())
    chips = "".join(
        f'<a href="study/{subject_slug(s)}.html">{esc(s)}<span>{len(by_subject[s])}</span></a>'
        for s in sorted(by_subject, key=subject_sort_key)
    )
    body = f"""
<section class="search-page">
  <p class="eyebrow"><span class="dot"></span>SEARCH</p>
  <h1>搜索</h1>
  <p class="lede">按<b>标题</b>搜索全站的文章、笔记与学科页。输入即筛选，不需要回车。</p>
  <div class="search-box">
    <input id="search-q" type="search" placeholder="输入标题关键词，例如「扩散」「TCP」「MySQL」" autocomplete="off" aria-label="搜索标题" />
    <span id="search-count" class="search-count"></span>
  </div>
  <ul id="search-results" class="search-results"></ul>
  <p id="search-hint" class="search-hint">共收录 <b id="search-total">—</b> 条内容。按 <kbd>/</kbd> 可随时回到这里。</p>

  <div id="search-default" class="search-default">
    <p class="search-sec">按板块浏览</p>
    <div class="quick-links">
      <a class="quick-link" href="research.html"><b>科研</b><span>{research_n} 篇文章 · {survey_n} 份调研档案</span></a>
      <a class="quick-link" href="study.html"><b>学习</b><span>{course_n} 篇笔记 · {len(by_subject)} 门学科</span></a>
      <a class="quick-link" href="essays.html"><b>随笔</b><span>{essays_n} 篇</span></a>
    </div>
    <p class="search-sec">全部学科</p>
    <div class="quick-chips">{chips}</div>
  </div>
</section>
<script src="data/search-index.js"></script>
"""
    return shell("搜索 · " + SITE_TITLE, body, "", "搜索", "search", "按标题搜索全站文章与笔记。")


# ------------------------------------------------------------------ 主流程
def main():
    arts = collect_articles()
    notes = collect_notes()

    research = [a for a in arts if a["category"] == "研究"]
    readings = [a for a in research if "论文精读" in a["tags"]]
    res_notes = [n for n in notes if n["subject"] == RESEARCH_SUBJECT]
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]
    tutorials = [a for a in arts if a["category"] == "学习笔记"]
    essays = [a for a in arts if a["category"] == "随笔"]
    archive = [a for a in arts if a["category"] == "资料库"]

    survey_n = count_pattern(os.path.join(ARTICLES, "survey-catalog.html"), r"调研档案总目（(\d+) 份文档）")
    paper_n = read(os.path.join(ARTICLES, "papers-index.html")).count('class="paper"') \
        if os.path.exists(os.path.join(ARTICLES, "papers-index.html")) else 0
    kb_n = len(glob.glob(os.path.join(ARTICLES, "kb", "*.html"))) + \
        len(glob.glob(os.path.join(ARTICLES, "kb-doubao", "*.html")))

    # 1) 顶层页面
    by_subject = {}
    for n in course_notes:
        by_subject.setdefault(n["subject"], []).append(n)

    write(os.path.join(ROOT, "index.html"),
          page_home(arts, notes, survey_n, paper_n, kb_n))
    write(os.path.join(ROOT, "research.html"),
          page_research(arts, notes, survey_n, paper_n, len(archive)))
    write(os.path.join(ROOT, "study.html"), page_study(arts, notes))
    write(os.path.join(ROOT, "essays.html"), page_essays(essays))
    write(os.path.join(ROOT, "search.html"),
          page_search(by_subject, len(research), survey_n, len(essays)))

    # 2) 学科页
    for subject, items in by_subject.items():
        write(os.path.join(ROOT, "study", subject_slug(subject) + ".html"),
              page_subject(subject, items))

    # 3) 各分类清单页
    page_list("研究文章", "完整的研究记录：问题、方法、实验与自我推翻。", research,
              "list-research.html", "科研", "RESEARCH")
    page_list("论文精读", "逐篇拆解的文献：方法、结构约束、评价口径与和本方向的关系。", readings,
              "list-readings.html", "科研", "READINGS")
    page_list("研究笔记", "研究过程中的专题笔记：概念、推导、实验设置与踩坑记录。", res_notes,
              "list-research-notes.html", "科研", "NOTES")
    page_list("教程", "从一个具体困惑出发，把机制讲到能自己推一遍。", tutorials,
              "list-tutorials.html", "学习", "TUTORIALS")
    page_list("学科笔记 · 全部", "按学科归档的专业课笔记，一页看完；按学科浏览见「学习」页。",
              sorted(course_notes, key=lambda n: (subject_sort_key(n["subject"]), n["title"])),
              "list-courses.html", "学习", "ALL NOTES")
    page_list("对话存档", "与 AI 助手的全部学习对话，按主题分组，可溯源。",
              [a for a in arts if a["category"] == "知识库"], "list-kb.html", "学习", "KB")
    page_list("随笔", "自己写的科普长文，讲本质，不堆术语。", essays,
              "list-essays.html", "随笔", "ESSAYS")
    page_list("调研档案", "整批文献调研的原始档案。",
              [a for a in arts if a["category"] == "调研"], "list-survey.html", "科研", "SURVEY")
    page_list("论文导读", "读过并留档的论文清单。",
              [a for a in arts if a["category"] == "论文"], "list-papers.html", "科研", "PAPERS")
    page_list("资料库", "全量审计、覆盖率清单与原始存档说明，用于溯源核对。", archive,
              "list-archive.html", "科研", "ARCHIVE")
    # 旧导航的兼容别名
    page_list("学习笔记 · 教程", "从具体困惑出发的教程与整理。", tutorials,
              "list-notes.html", "学习", "STUDY")

    # 4) 搜索索引（用 .js 而不是 .json：file:// 直接打开也能用）
    idx = []
    for a in arts:
        cat = a["category"]
        if cat == "研究":
            section, group = "科研", ("论文精读" if "论文精读" in a["tags"] else "研究文章")
        elif cat == "随笔":
            section, group = "随笔", "随笔"
        elif cat == "资料库":
            section, group = "资料库", "资料库"
        elif cat in ("调研", "论文"):
            section, group = "科研", cat
        elif cat == "知识库":
            section, group = "学习", "对话存档"
        else:
            section, group = "学习", "教程"
        idx.append({"t": a["title"], "u": a["url"], "s": section, "g": group, "d": a["date"]})
    for n in notes:
        section = "科研" if n["subject"] == RESEARCH_SUBJECT else "学习"
        idx.append({"t": n["title"], "u": n["url"], "s": section,
                    "g": n["subject"], "d": ""})
    for subject in by_subject:
        idx.append({"t": subject + " · 学科", "u": "study/" + subject_slug(subject) + ".html",
                    "s": "学习", "g": subject, "d": ""})
    idx.sort(key=lambda x: (x["s"], x["g"], x["t"]))
    write(os.path.join(DATA, "search-index.js"),
          "window.SEARCH_INDEX=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";\n")

    # 5) 侧栏徽标计数
    write(os.path.join(DATA, "nav_counts.json"), json.dumps({
        "research": len(research),
        "study": len(course_notes),
        "essays": len(essays),
    }, ensure_ascii=False))

    print("首页 / 科研 / 学习 / 随笔 / 搜索 已重建")
    print("学科页 %d 个：%s" % (len(by_subject), "、".join(by_subject)))
    print("清单页 %d 个；搜索索引 %d 条；研究文章 %d 篇 / 研究笔记 %d 篇 / 学科笔记 %d 篇"
          % (len(glob.glob(os.path.join(ARTICLES, "list-*.html"))), len(idx),
             len(research), len(res_notes), len(course_notes)))


if __name__ == "__main__":
    main()
