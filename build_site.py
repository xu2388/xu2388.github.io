#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点生成器

信息架构（三层）：
    首页 index.html
      ├── 科研 research.html
      │     ├── 研究文章   articles/list-research.html
      │     ├── 论文精读   articles/list-readings.html
      │     ├── 研究笔记   articles/list-research-notes.html
      │     ├── 调研档案   articles/survey-catalog.html
      │     └── 论文导读   articles/papers-index.html
      ├── 学习 study.html
      │     ├── study/<学科>.html   （20 门学科，每门一页）
      │     └── 教程       articles/list-tutorials.html
      ├── 随笔 essays.html
      └── 搜索 search.html（标题搜索，索引 data/search-index.js）

与 AI 助手的对话存档不再进入站点，也不再参与构建。

用法：python3 build_notes.py && python3 build_site.py && python3 fix_nav.py
"""
import os
import re
import json
import glob
import time
import html as htmlmod

from fix_nav import build_header, build_footer
from site_model import (SUBJECTS, GROUP_ORDER, RESEARCH_SUBJECT,
                        subject_slug, subject_group, subject_desc, subject_sort_key)

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES = os.path.join(ROOT, "articles")
NOTES = os.path.join(ROOT, "notes")
DATA = os.path.join(ROOT, "data")

SITE_TITLE = "科研与学习档案"

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Noto+Serif+SC:wght@400;600&display=swap" />'
)


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
    items = []
    for path in sorted(glob.glob(os.path.join(ARTICLES, "*.html"))):
        base = os.path.basename(path)
        if base.startswith("list-"):
            continue
        m = re.search(r'<script id="meta" type="application/json">(.*?)</script>', read(path), re.DOTALL)
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
        mtime = os.path.getmtime(path)
        items.append({
            "title": fm["title"],
            "subject": fm.get("subject", "其他"),
            "category": fm.get("category", "课程笔记"),
            "summary": fm.get("summary", ""),
            "url": "articles/notes/" + slug,
            "file": os.path.basename(path),
            "date": time.strftime("%Y-%m-%d", time.localtime(mtime)),
            "nodate": True,   # mtime 不是写作日期，列表里不显示
        })
    items.sort(key=lambda x: x["file"])
    return items


# ------------------------------------------------------------------ 骨架
def shell(title, body, prefix="", active=None, body_class="", desc=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc or SITE_TITLE)}" />
<link rel="stylesheet" href="{prefix}assets/style.css" />
{FONT_LINK}
<script id="theme-init">try{{var t=localStorage.getItem("theme");if(!t)t=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}</script>
</head>
<body class="{body_class}">
{build_header(prefix, active)}

{body}

{build_footer(prefix)}
<script src="{prefix}assets/blog.js" defer></script>
</body>
</html>
"""


def rows(items, prefix="", limit=None):
    """板块 | 标题 | 出处 —— 索引式行列表（笔记没有可靠日期，所以不显示日期）。"""
    out = []
    for it in (items[:limit] if limit else items):
        out.append(
            f'<li><span class="d">{esc(it.get("sec", ""))}</span>'
            f'<a class="t" href="{prefix}{it["url"]}">{esc(it["title"])}</a>'
            f'<span class="s">{esc(it.get("tag", ""))}</span></li>'
        )
    return '<ul class="rows">' + "".join(out) + "</ul>"


def article_list(items, prefix="", show_tags=True):
    if not items:
        return '<p class="muted">（暂无内容）</p>'
    out = ['<ul class="article-list">']
    for it in items:
        tags = ""
        if show_tags and it.get("tags"):
            tags = "".join('<span class="tag">%s</span>' % esc(t) for t in it["tags"][:5])
        date = f'<span class="date">{it["date"]}</span>' if it.get("date") and not it.get("nodate") else ""
        out.append(
            f'<li><a href="{prefix}{it["url"]}">{esc(it["title"])}</a>{date}'
            f'{tags}<span class="desc">{esc(it.get("summary", ""))}</span></li>'
        )
    out.append("</ul>")
    return "\n".join(out)


# ------------------------------------------------------------------ 首页
def page_home(arts, notes, survey_n, paper_n):
    research = [a for a in arts if a["category"] == "研究"]
    readings = [a for a in research if "论文精读" in a["tags"]]
    res_notes = [n for n in notes if n["subject"] == RESEARCH_SUBJECT]
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]
    essays = [a for a in arts if a["category"] == "随笔"]
    tutorials = [a for a in arts if a["category"] == "学习笔记"]

    by_subject = {}
    for n in course_notes:
        by_subject.setdefault(n["subject"], []).append(n)
    group_counts = []
    for g in GROUP_ORDER:
        subs = [s for s in by_subject if subject_group(s) == g]
        if subs:
            group_counts.append((g, sum(len(by_subject[s]) for s in subs)))

    pool = []
    for a in arts:
        sec = {"研究": "科研", "随笔": "随笔", "学习笔记": "学习"}.get(a["category"])
        if not sec:
            continue
        tag = "论文精读" if "论文精读" in a["tags"] else (
            {"研究": "研究文章", "随笔": "随笔", "学习笔记": "教程"}[a["category"]])
        pool.append({"date": a["date"], "title": a["title"], "url": a["url"], "sec": sec, "tag": tag})
    for n in notes:
        pool.append({"date": n["date"], "title": n["title"], "url": n["url"], "tag": n["subject"],
                     "sec": "科研" if n["subject"] == RESEARCH_SUBJECT else "学习"})

    def pick(sec, k):
        return [x for x in sorted(pool, key=lambda x: (x["date"], x["url"]), reverse=True)
                if x["sec"] == sec][:k]

    r, s = pick("科研", 5), pick("学习", 5)
    recent = []
    for i in range(5):
        if i < len(r):
            recent.append(r[i])
        if i < len(s):
            recent.append(s[i])

    study_sub = "".join(f"<span>{esc(g)} {n}</span>" for g, n in group_counts)

    body = f"""
<main class="wrap">
  <section class="home-hero">
    <div>
      <h1>一个本科生的<br />研究记录与课程笔记</h1>
      <p class="home-lede">
        科研：研究文章、论文精读、研究笔记、调研档案。<br />
        学习：{len(by_subject)} 门学科的专业课笔记，每门一页。<br />
        按主题归档，逐层点进去就是正文。
      </p>
      <form class="home-search" action="search.html" role="search">
        <input type="search" name="q" placeholder="搜索标题" aria-label="搜索文章标题" autocomplete="off" />
        <button type="submit" aria-label="搜索">→</button>
      </form>
    </div>

    <div>
      <div class="toc-label">目录</div>
      <div class="toc-list">
        <a class="toc-item" href="research.html">
          <div class="toc-item-head"><h2>科研</h2><span class="n">{len(research)} 篇文章 · {survey_n} 份档案</span></div>
          <p>从问题、方法到自我推翻，保留原始数据与当时的判断；论文逐篇拆解，调研成批归档。</p>
          <span class="sub">研究文章 {len(research)} · 论文精读 {len(readings)} · 研究笔记 {len(res_notes)} · 论文导读 {paper_n}</span>
        </a>
        <a class="toc-item" href="study.html">
          <div class="toc-item-head"><h2>学习</h2><span class="n">{len(course_notes)} 篇笔记 · {len(by_subject)} 门学科</span></div>
          <p>专业课复习与整理，按学科成册；另有 {len(tutorials)} 篇从具体困惑出发的教程。</p>
          <span class="sub">{study_sub}</span>
        </a>
      </div>
    </div>
  </section>

  <section class="home-recent">
    <div class="sec-head"><h2>最近更新</h2><a href="search.html">搜索全部</a></div>
    {rows(recent)}
  </section>

  <section class="home-foot">
    <div>
      <h2>关于</h2>
      <p>内容来自一年多来的科研与课程学习，由我逐篇整理。<strong>原始信息不删减，思考过程原样保留</strong>，
        每条结论尽量能追到具体依据。</p>
    </div>
    <div>
      <h2>另有</h2>
      <p>随笔 {len(essays)} 篇：<a href="essays.html">自己写的科普长文</a>，讲本质，不堆术语。</p>
      <p>全站 {len(arts) + len(notes)} 条内容，可用<a href="search.html">标题搜索</a>直达。</p>
    </div>
  </section>
</main>
"""
    return shell(f"{SITE_TITLE}", body, "", None, "home",
                 "一个本科生的科研与学习档案：研究记录、论文精读、调研档案，以及按学科归档的专业课笔记。")


# ------------------------------------------------------------------ 科研
def page_research(arts, notes, survey_n, paper_n):
    research = [a for a in arts if a["category"] == "研究"]
    readings = [a for a in research if "论文精读" in a["tags"]]
    res_notes = [n for n in notes if n["subject"] == RESEARCH_SUBJECT]

    def cat(name, n, unit, desc, href, preview):
        pv = ""
        if preview:
            pv = '<div class="recent">' + "".join(f"<span>{esc(t)}</span>" for t in preview) + "</div>"
        return f"""<a class="cat" href="{href}">
  <h2>{name}</h2>
  <div><p>{desc}</p>{pv}</div>
  <span class="n">{n} {unit}</span>
</a>"""

    core = [a for a in research if "论文精读" not in a["tags"]]
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>科研</div>
  <header class="page-head">
    <h1>科研</h1>
    <div>
      <p class="lede">按内容形态分成五类：研究文章、论文精读、研究笔记、调研档案与论文导读。
        每一类点进去都是完整清单。</p>
      <p class="stat">{len(research)} 篇文章 · {len(res_notes)} 篇研究笔记 · {survey_n} 份调研档案 · {paper_n} 篇论文导读</p>
    </div>
  </header>

{cat("研究文章", len(research), "篇",
     "完整的研究记录：问题、方法、实验与自我推翻，保留原始数据与当时的判断。",
     "articles/list-research.html", [a["title"] for a in (core or research)[:2]])}
{cat("论文精读", len(readings), "篇",
     "逐篇拆解的文献：方法、结构约束与评价口径，以及和本方向的关系。",
     "articles/list-readings.html", [a["title"] for a in readings[:2]])}
{cat("研究笔记", len(res_notes), "篇",
     "研究过程中的专题笔记：概念、推导、实验设置与踩坑记录。",
     "articles/list-research-notes.html", [n["title"] for n in res_notes[:2]])}
{cat("调研档案", survey_n, "份",
     "整批文献调研的原始档案：文献地图、逐篇翻译、精读与方案审查。",
     "articles/survey-catalog.html", [])}
{cat("论文导读", paper_n, "篇",
     "读过并留档的论文清单，每篇一句话总结。",
     "articles/papers-index.html", [])}
</main>
"""
    return shell("科研 · " + SITE_TITLE, body, "", "科研", "",
                 "科研：研究文章、论文精读、研究笔记、调研档案与论文导读。")


# ------------------------------------------------------------------ 学习
def page_study(arts, notes):
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]
    tutorials = [a for a in arts if a["category"] == "学习笔记"]
    by_subject = {}
    for n in course_notes:
        by_subject.setdefault(n["subject"], []).append(n)

    groups = []
    for g in GROUP_ORDER:
        subs = [s for s in by_subject if subject_group(s) == g]
        if not subs:
            continue
        subs.sort(key=subject_sort_key)
        lis = "".join(
            f'<li><a href="study/{subject_slug(s)}.html">{esc(s)}<b>{len(by_subject[s])}</b></a></li>'
            for s in subs
        )
        total = sum(len(by_subject[s]) for s in subs)
        groups.append(f"""<section class="idx-group">
  <h2>{g}<b>{len(subs)} 门 · {total} 篇</b></h2>
  <ul class="idx">{lis}</ul>
</section>""")

    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>学习</div>
  <header class="page-head">
    <h1>学习</h1>
    <div>
      <p class="lede">按学科归档。下面每一行是一门学科，点进去是该学科的全部笔记。</p>
      <p class="stat">{len(course_notes)} 篇笔记 · {len(by_subject)} 门学科 · {len(tutorials)} 篇教程</p>
    </div>
  </header>

{"".join(groups)}

<a class="cat" href="articles/list-tutorials.html" style="margin-top:64px">
  <h2>教程</h2>
  <div><p>从一个具体困惑出发，把机制讲到能自己推一遍。</p></div>
  <span class="n">{len(tutorials)} 篇</span>
</a>
</main>
"""
    return shell("学习 · " + SITE_TITLE, body, "", "学习", "",
                 "学习：按 20 门学科归档的专业课笔记，以及成系列的教程。")


# ------------------------------------------------------------------ 学科页
def page_subject(subject, items):
    items = sorted(items, key=lambda x: x["title"])
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="../index.html">首页</a><span>/</span><a href="../study.html">学习</a><span>/</span>{esc(subject)}</div>
  <header class="list-head">
    <h1>{esc(subject)}</h1>
    <p class="lede">{esc(subject_desc(subject))} · 共 {len(items)} 篇</p>
  </header>
  {article_list(items, prefix="../", show_tags=False)}
  <a class="back-link" href="../study.html">← 返回学习</a>
</main>
"""
    return shell(f"{subject} · 学习 · {SITE_TITLE}", body, "../", "学习", "",
                 f"{subject}的全部笔记（{len(items)} 篇）。")


# ------------------------------------------------------------------ 随笔
def page_essays(essays):
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>随笔</div>
  <header class="list-head">
    <h1>随笔</h1>
    <p class="lede">自己写的科普长文，讲本质，不堆术语。</p>
  </header>
  {article_list(essays)}
  <a class="back-link" href="index.html">← 返回首页</a>
</main>
"""
    return shell("随笔 · " + SITE_TITLE, body, "", "随笔", "", "随笔与科普长文。")


# ------------------------------------------------------------------ 清单页
def page_list(title, desc, items, filename, active):
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="../index.html">首页</a><span>/</span><a href="../{("research" if active == "科研" else "study")}.html">{active}</a><span>/</span>{esc(title)}</div>
  <header class="list-head">
    <h1>{esc(title)}</h1>
    <p class="lede">{esc(desc)}　共 {len(items)} 篇</p>
  </header>
  {article_list(items, prefix="../")}
  <a class="back-link" href="../index.html">← 返回首页</a>
</main>
"""
    write(os.path.join(ARTICLES, filename),
          shell(f"{title} · {SITE_TITLE}", body, "../", active, "", desc))


# ------------------------------------------------------------------ 搜索
def page_search(by_subject, sec_counts):
    subs = "".join(
        f'<li><a href="study/{subject_slug(s)}.html">{esc(s)}<b>{len(by_subject[s])}</b></a></li>'
        for s in sorted(by_subject, key=subject_sort_key)
    )
    secs = "".join(
        f'<li><a href="{href}">{name}<b>{n}</b></a></li>'
        for name, href, n in (("科研", "research.html", sec_counts["科研"]),
                              ("学习", "study.html", sec_counts["学习"]),
                              ("随笔", "essays.html", sec_counts["随笔"]))
    )
    body = f"""
<main class="wrap"><div class="search-page">
  <h1>搜索</h1>
  <p class="lede">按标题搜索全站的文章与笔记。输入即筛选，不需要回车。</p>
  <div class="search-field">
    <input id="search-q" type="search" placeholder="输入标题关键词" autocomplete="off" aria-label="搜索标题" />
    <span class="count" id="search-count"></span>
  </div>
  <p class="search-hint">共收录 <b id="search-total">—</b> 条内容　按 <kbd>/</kbd> 可随时回到这里</p>
  <ul id="search-results" class="search-results"></ul>

  <div id="search-default" class="search-default">
    <p class="search-sec">按学科</p>
    <ul class="idx">{subs}</ul>
    <p class="search-sec">按板块</p>
    <ul class="idx">{secs}</ul>
  </div>
</div></main>
<script src="data/search-index.js"></script>
"""
    return shell("搜索 · " + SITE_TITLE, body, "", "搜索", "", "按标题搜索全站文章与笔记。")


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

    survey_n = 0
    sc = os.path.join(ARTICLES, "survey-catalog.html")
    if os.path.exists(sc):
        m = re.search(r"调研档案总目（(\d+) 份文档）", read(sc))
        survey_n = int(m.group(1)) if m else 0
    pi = os.path.join(ARTICLES, "papers-index.html")
    paper_n = read(pi).count('class="paper"') if os.path.exists(pi) else 0

    by_subject = {}
    for n in course_notes:
        by_subject.setdefault(n["subject"], []).append(n)

    write(os.path.join(ROOT, "index.html"), page_home(arts, notes, survey_n, paper_n))
    write(os.path.join(ROOT, "research.html"), page_research(arts, notes, survey_n, paper_n))
    write(os.path.join(ROOT, "study.html"), page_study(arts, notes))
    write(os.path.join(ROOT, "essays.html"), page_essays(essays))
    write(os.path.join(ROOT, "search.html"),
          page_search(by_subject, {"科研": len(research) + len(res_notes),
                                   "学习": len(course_notes) + len(tutorials),
                                   "随笔": len(essays)}))

    for subject, items in by_subject.items():
        write(os.path.join(ROOT, "study", subject_slug(subject) + ".html"),
              page_subject(subject, items))

    page_list("研究文章", "完整的研究记录：问题、方法、实验与自我推翻。", research,
              "list-research.html", "科研")
    page_list("论文精读", "逐篇拆解的文献：方法、结构约束、评价口径与和本方向的关系。", readings,
              "list-readings.html", "科研")
    page_list("研究笔记", "研究过程中的专题笔记：概念、推导、实验设置与踩坑记录。", res_notes,
              "list-research-notes.html", "科研")
    page_list("教程", "从一个具体困惑出发，把机制讲到能自己推一遍。", tutorials,
              "list-tutorials.html", "学习")
    page_list("学科笔记 · 全部",
              "按学科归档的专业课笔记，一页看完；按学科浏览见「学习」页。",
              sorted(course_notes, key=lambda n: (subject_sort_key(n["subject"]), n["title"])),
              "list-courses.html", "学习")
    page_list("随笔", "自己写的科普长文，讲本质，不堆术语。", essays, "list-essays.html", "随笔")
    page_list("调研档案", "整批文献调研的原始档案。",
              [a for a in arts if a["category"] == "调研"], "list-survey.html", "科研")
    page_list("论文导读", "读过并留档的论文清单。",
              [a for a in arts if a["category"] == "论文"], "list-papers.html", "科研")
    page_list("学习笔记 · 教程", "从具体困惑出发的教程与整理。", tutorials,
              "list-notes.html", "学习")

    # 搜索索引（.js 而不是 .json：双击本地文件打开也能用）
    idx = []
    for a in arts:
        cat = a["category"]
        if cat == "研究":
            section, group = "科研", ("论文精读" if "论文精读" in a["tags"] else "研究文章")
        elif cat == "随笔":
            section, group = "随笔", "随笔"
        elif cat in ("调研", "论文"):
            section, group = "科研", cat
        else:
            section, group = "学习", "教程"
        idx.append({"t": a["title"], "u": a["url"], "s": section, "g": group, "d": a["date"]})
    for n in notes:
        idx.append({"t": n["title"], "u": n["url"],
                    "s": "科研" if n["subject"] == RESEARCH_SUBJECT else "学习",
                    "g": n["subject"], "d": ""})
    for subject in by_subject:
        idx.append({"t": subject + " · 学科", "u": "study/" + subject_slug(subject) + ".html",
                    "s": "学习", "g": subject, "d": ""})
    idx.sort(key=lambda x: (x["s"], x["g"], x["t"]))
    write(os.path.join(DATA, "search-index.js"),
          "window.SEARCH_INDEX=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";\n")

    write(os.path.join(DATA, "nav_counts.json"),
          json.dumps({"research": len(research), "study": len(course_notes),
                      "essays": len(essays)}, ensure_ascii=False))

    print("首页 / 科研 / 学习 / 随笔 / 搜索 已重建")
    print("学科页 %d 个 · 清单页 %d 个 · 搜索索引 %d 条"
          % (len(by_subject), len(glob.glob(os.path.join(ARTICLES, "list-*.html"))), len(idx)))
    print("研究文章 %d · 论文精读 %d · 研究笔记 %d · 学科笔记 %d"
          % (len(research), len(readings), len(res_notes), len(course_notes)))


if __name__ == "__main__":
    main()
