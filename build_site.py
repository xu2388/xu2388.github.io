#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点生成器

信息架构：首页是一页简历，其余是它的附件。

    index.html        简历：自述 / 研究经历 / 技能 / 写作 / 档案
      ├── research.html        研究：长文、精读、研究笔记、调研档案、论文导读
      │     └── articles/list-*.html
      ├── writing.html         写作：随笔与教程
      ├── notes.html           笔记：20 门学科，每门一页 → subject/<slug>.html
      └── archive.html         索引：全站可搜索的目录

首页的所有「关于我」的事实来自 me.json（见 me.py），模板里不写死。

用法：python3 build_articles.py && python3 build_notes.py && python3 build_site.py && python3 fix_nav.py
"""
import os
import re
import json
import glob
import time
import html as htmlmod

from fix_nav import build_header, build_footer
from me import NAME, FIELD, ROLE, get
from site_model import (SUBJECTS, GROUP_ORDER, RESEARCH_SUBJECT,
                        subject_slug, subject_group, subject_desc, subject_sort_key)

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLES = os.path.join(ROOT, "articles")
NOTES = os.path.join(ROOT, "notes")
DATA = os.path.join(ROOT, "data")

SITE_TITLE = NAME

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Noto+Serif+SC:wght@400;600&display=swap" />'
)


# ------------------------------------------------------------------ 工具
def esc(s):
    return htmlmod.escape(str(s or ""))


def clip(s, n=58):
    """摘要截到一行半左右：首页只用来辨认，不必读完。
    优先在标点处断开，硬切会把「自己的」切成「自…」，读着像 bug。"""
    s = (s or "").strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    k = max(cut.rfind(p) for p in "。！？；，、：")
    if k >= n * 0.5:
        cut = cut[:k]
    return cut.rstrip("，。、；：·—- ") + "…"


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
<meta name="author" content="{esc(NAME)}" />
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


def load_csdn():
    """data/csdn.json 由 fetch_csdn.py 生成；没有这个文件就当作未接入。"""
    path = os.path.join(DATA, "csdn.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def csdn_block(csdn, limit=5):
    arts = csdn.get("articles") or []
    if not arts:
        return ('<div class="csdn-empty">'
                + '<span class="sk" style="width:88%"></span>'
                + '<span class="sk" style="width:72%"></span>'
                + '<span class="sk" style="width:81%"></span>'
                + '<span class="sk" style="width:64%"></span>'
                + '<span class="sk" style="width:76%"></span>'
                + '<p>还没有接入。把 CSDN 用户名填进 <code>me.json</code> 的 '
                '<code>csdn.user</code>，运行 <code>python3 fetch_csdn.py</code>，'
                '这里会按上面的样式列出最近 5 篇。</p></div>')

    home = csdn.get("home") or "https://blog.csdn.net/"
    total = csdn.get("total") or len(arts)
    views = sum(a.get("views") or 0 for a in arts)
    lis = "".join(
        f'<li><a href="{esc(a["url"])}" rel="noopener">{esc(a["title"])}</a>'
        f'<span>{esc(a.get("date", ""))}　{a.get("views", 0):,} 阅读</span></li>'
        for a in arts[:limit]
    )
    return (f'<ul class="csdn-list">{lis}</ul>'
            f'<p class="cv-more"><a href="{esc(home)}" rel="noopener">'
            f'CSDN 全部 {total} 篇 · 合计 {views:,} 阅读</a></p>')


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


# ------------------------------------------------------------------ 首页（简历）
def page_home(arts, notes, survey_n, paper_n):
    research = [a for a in arts if a["category"] == "研究"]
    readings = [a for a in research if "论文精读" in a["tags"]]
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]
    essays = [a for a in arts if a["category"] == "随笔"]
    tutorials = [a for a in arts if a["category"] == "学习笔记"]

    # 首屏：姓名 + 右侧联系方式（空字段不渲染）
    contact = []
    if get("place"):
        contact.append(f'<span>{esc(get("place"))}</span>')
    if get("email"):
        contact.append(f'<a href="mailto:{esc(get("email"))}">{esc(get("email"))}</a>')
    if get("github"):
        contact.append(f'<a href="{esc(get("github"))}" rel="me">GitHub</a>')
    csdn_home = (get("csdn", {}) or {}).get("home")
    if csdn_home:
        contact.append(f'<a href="{esc(csdn_home)}" rel="me">CSDN</a>')
    contact.append('<a class="no-print" href="#" onclick="window.print();return false">PDF</a>')

    role_line = " · ".join(x for x in (ROLE, FIELD) if x)

    # 自述
    statement = "".join(f"<p>{p}</p>" for p in get("statement", []))

    # 研究经历：做了什么 + 产出了什么（简历要的是证据，不是结论）
    log = []
    for t in get("timeline", []):
        out = t.get("out", "")
        out_html = f'<p class="out"><span>产出</span>{esc(out)}</p>' if out else ""
        log.append(
            f'<li><span class="when">{esc(t.get("when", ""))}</span>'
            f'<div><h3><a href="{esc(t.get("url", ""))}">{esc(t.get("title", ""))}</a></h3>'
            f'<p>{esc(t.get("note", ""))}</p>{out_html}</div></li>'
        )

    # 学习经历：课程 → 产出的映射，只留能指到具体笔记的行（简历要证据，不要课表）
    by_subject = {}
    for n in course_notes:
        by_subject.setdefault(n["subject"], []).append(n)
    study_rows = []
    for course, output, subject in get("study_map", []):
        study_rows.append(
            f'<div><dt><a href="subject/{subject_slug(subject)}.html">{esc(course)}</a></dt>'
            f'<dd>{esc(output)}</dd></div>'
        )

    # 技能：一行内联，不占整块（四块变三块 + 一行，版面才松得开）
    skills_inline = "　·　".join(
        f'<b>{esc(k)}</b>　{esc(v)}' for k, v in get("skills", [])
    )

    # 教育（org 留空则整段不出现）
    edu = ""
    if get("org"):
        edu = f"""
<section class="cv-sec">
  <h2 class="cv-label">教育</h2>
  <dl class="kv"><div><dt>{esc(ROLE)}</dt><dd>{esc(get("org"))}</dd></div></dl>
</section>"""

    # 写作（随笔在前，教程在后）
    wl = []
    for a in (essays + tutorials)[:3]:
        kind = "随笔" if a["category"] == "随笔" else "教程"
        wl.append(f'<li><a href="{a["url"]}">{esc(a["title"])}</a>'
                  f'<span class="k">{kind}</span><p>{esc(clip(a["summary"], 44))}</p></li>')

    # 全部内容：把数量当排版元素
    figs = [
        ("research.html", len(research), "研究记录"),
        ("articles/survey-catalog.html", survey_n, "调研档案"),
        ("notes.html", len(course_notes), "课程笔记"),
        ("articles/list-readings.html", len(readings), "论文精读"),
    ]
    fig_html = "".join(
        f'<li><a href="{href}"><b>{n}</b><span>{label}</span></a></li>'
        for href, n, label in figs
    )
    total = len(arts) + len(notes)

    # 站外：CSDN（没接入时不渲染这一格——骨架占位是开发态，访客看到只会以为页面坏了）
    csdn = load_csdn()
    csdn_cell = ""
    if csdn.get("articles"):
        # no-print：纸面简历不需要文章列表，联系方式里已印出 CSDN 地址
        csdn_cell = f"""
    <section class="gcell gcell-fill no-print">
      <h2 class="cv-label">站外</h2>
      {csdn_block(csdn)}
    </section>"""

    body = f"""
<main class="cv">
  <header class="cv-hero">
    <div class="cv-id">
      <h1 class="cv-name">{esc(NAME)}</h1>
      <p class="cv-role">{esc(role_line)}</p>
    </div>
    <div class="cv-contact">{"<i>·</i>".join(contact)}</div>
  </header>

  <section class="cv-sec cv-sec-first">
    <h2 class="cv-label">自述</h2>
    <div class="cv-statement">
      {statement}
    </div>
  </section>

  <div class="grid4">
    <section class="gcell gcell-tall">
      <h2 class="cv-label">研究经历</h2>
      <ol class="log">
        {"".join(log)}
      </ol>
      <p class="cv-more"><a href="process.html">六条改变过方向的判断，附当时的依据与后来的结果</a></p>
      <p class="cv-more"><a href="research.html">全部研究记录、论文精读与调研档案</a></p>
    </section>

    <section class="gcell">
      <h2 class="cv-label">学习经历</h2>
      <dl class="kv kv-study">{''.join(study_rows)}</dl>
      <p class="cv-more"><a href="notes.html">{len(course_notes)} 篇课程笔记，按 {len(by_subject)} 门学科成册</a></p>
    </section>

    <section class="gcell">
      <h2 class="cv-label">写作</h2>
      <ul class="wlist">
        {"".join(wl)}
      </ul>
      <p class="cv-more"><a href="writing.html">全部写作</a></p>
    </section>
{csdn_cell}
  </div>

  <section class="cv-sec cv-skills">
    <h2 class="cv-label">技能</h2>
    <p class="skills-line">{skills_inline}</p>
  </section>

  <section class="cv-sec cv-sec-last">
    <h2 class="cv-label">全部内容</h2>
    <ul class="figs">{fig_html}</ul>
    <p class="cv-note">另有随笔 {len(essays)} 篇、教程 {len(tutorials)} 篇。全站 {total} 条内容可检索，按 <kbd>/</kbd> 直达。</p>
  </section>
</main>
"""
    return shell(f"{NAME} · {FIELD}", body, "", None, "cv-page",
                 f"{NAME}，{role_line}。虚拟染色研究记录、论文精读与课程笔记。")


# ------------------------------------------------------------------ 研究
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
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>研究</div>
  <header class="page-head">
    <h1>研究</h1>
    <div>
      <p class="lede">一个问题的全部过程：任务怎么定义、哪里判断错了、后来改成什么。
        长文按时间保留当时的判断与原始数据，精读与调研档案作为证据链单独归档。</p>
      <p class="stat">{len(research)} 篇长文 · {len(res_notes)} 篇研究笔记 · {survey_n} 份调研档案 · {paper_n} 篇论文导读</p>
    </div>
  </header>

{cat("研究路径", 6, "条",
     "改变过研究方向的判断：当时的依据、验证方式，以及后来是否成立。失败的一并保留。",
     "process.html", [])}
{cat("研究记录", len(research), "篇",
     "完整的过程记录：问题、方法、实验与自我推翻，保留原始数据与当时的判断。",
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
    return shell(f"研究 · {SITE_TITLE}", body, "", "研究", "",
                 "研究记录、论文精读、研究笔记、调研档案与论文导读。")


# ------------------------------------------------------------------ 研究路径
def page_process(arts):
    """研究路径：六条判断的索引页。内容硬编码在此，不依赖 me.json。"""
    JUDGE = [
        # (主张, 依据, 文章编号, 文章 slug, 会话出处)
        ("用下游分割证明「生成得像」不可信",
         "分割器各有泛化差异，换一个模型结论就翻转；评价应转向基础模型对生成图的认证程度与蛋白表达统计。"
         "后改为 FID、SSIM、DAB 相关性与 H-score 分级四类口径。",
         "022", "虚拟染色问题地图", "医学图像风格迁移与虚拟染色区别"),
        ("换数据域必须重标定阈值，否则损失「在编不在岗」",
         "MLPA 的两个硬阈值（0.15 / 0.68，含 ^1.8 锐化）在 RGB 域标定；输入改成 H / DAB 双通道后数据域变了、"
         "阈值没变，监督项落在浓度分布尾部，几乎不激活。",
         "023", "换域阈值失效", "扩散生成染色浓度"),
        ("竖纹不是数据问题，是 4 像素上采样网格",
         "常量输入条纹归零、输入各向同性（方向比 0.84–1.00）、第一层竖/横增益逐位相同，"
         "而列残差主频恒为 0.25 cycles/px、块周期恒 4.00 px——根因是解码器两次 2× 上采样。",
         "024", "4像素网格伪影归因", "棋盘格伪影成因分析 · 扩散生成染色浓度"),
        ("PSNR 上升可能只是「变淡」，模型在输出平均 IHC",
         "PSNR +3.26 dB 的代价是 D/H 从 0.976 掉到 0.339；全量 796 张上真值 D/H 的 IQR 宽 0.767，"
         "模型只有 0.037——输出与输入无关，坍缩成同一种「平均染色」。",
         "025", "平均IHC表达坍缩", "扩散生成染色浓度"),
        ("频域能约束纹理尺度，不能约束空间位置",
         "「伊红能量在低频、DAB 能量在高频所以存在能量搬迁」不成立——两张图各自统计，只说明各有频率特点；"
         "且幅度谱对平移几乎不敏感，约束位置必须引入相位或空间域手段。",
         "026", "频域约束的边界", "频域 · 频域科研思路"),
        ("辅助损失会和噪声损失抢梯度，蛋白约束应走条件注入",
         "扩散主干学的是 ε，辅助损失与主损失梯度方向可能相反而互相抵消；含噪 RGB 上统计蛋白量本身不可靠。"
         "注：此条后来又被自己部分推翻（条件注入只能带进信息、带不进约束），至今未收敛。",
         "028", "条件注入还是约束引导", "扩散生成染色浓度 · 逐像素扩散解释"),
    ]
    lis = []
    for claim, why, art, slug, src in JUDGE:
        lis.append(f"""<li>
  <div>
    <h2>{esc(claim)}</h2>
    <p class="why">{esc(why)}</p>
    <p class="to">→ <a href="articles/{art}-{slug}.html">文章 {art}</a>　出处：会话《{esc(src)}》</p>
  </div>
</li>""")
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>研究路径</div>
  <header class="page-head">
    <h1>研究路径</h1>
    <div>
      <p class="lede">这条线走了两年，下面六条是途中真正改变方向的判断。
        每条都注明了当时的依据，以及后来它是否成立。</p>
      <p class="stat">六条判断 · 三份归因报告留档</p>
    </div>
  </header>

  <ol class="judge">
    {"".join(lis)}
  </ol>

  <p class="judge-side">旁支：曾考虑把 MBTI 当作评价体系做人格空间的连续建模，
    找到 MIRT 与 Q 矩阵一类心理测量学工具后搁置——与本方向无关，不影响主线。</p>
  <p class="judge-note">以上判断均来自当时的实验记录，失败的同样保留。</p>
</main>
"""
    return shell(f"研究路径 · {SITE_TITLE}", body, "", "研究", "",
                 "六条改变研究方向的判断，附当时的依据与后来的结果。")


# ------------------------------------------------------------------ 笔记
def page_notes(arts, notes):
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
            f'<li><a href="subject/{subject_slug(s)}.html">{esc(s)}<b>{len(by_subject[s])}</b></a></li>'
            for s in subs
        )
        total = sum(len(by_subject[s]) for s in subs)
        groups.append(f"""<section class="idx-group">
  <h2>{g}<b>{len(subs)} 门 · {total} 篇</b></h2>
  <ul class="idx">{lis}</ul>
</section>""")

    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>笔记</div>
  <header class="page-head">
    <h1>笔记</h1>
    <div>
      <p class="lede">按学科归档的课程笔记。这里不追求完整，只留那些当时真的没想通、
        后来逼自己重推一遍的地方。</p>
      <p class="stat">{len(course_notes)} 篇 · {len(by_subject)} 门学科</p>
    </div>
  </header>

{"".join(groups)}
</main>
"""
    return shell(f"笔记 · {SITE_TITLE}", body, "", "笔记", "",
                 "按学科归档的课程笔记。")


# ------------------------------------------------------------------ 学科页
def page_subject(subject, items):
    items = sorted(items, key=lambda x: x["title"])
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="../index.html">首页</a><span>/</span><a href="../notes.html">笔记</a><span>/</span>{esc(subject)}</div>
  <header class="list-head">
    <h1>{esc(subject)}</h1>
    <p class="lede">{esc(subject_desc(subject))} · 共 {len(items)} 篇</p>
  </header>
  {article_list(items, prefix="../", show_tags=False)}
  <a class="back-link" href="../notes.html">← 返回笔记</a>
</main>
"""
    return shell(f"{subject} · 笔记 · {SITE_TITLE}", body, "../", "笔记", "",
                 f"{subject}的全部笔记（{len(items)} 篇）。")


# ------------------------------------------------------------------ 写作
def page_writing(essays, tutorials, csdn=None):
    def group(title, desc, items):
        return f"""
  <section class="wgroup">
    <h2>{title}<b>{len(items)} 篇</b></h2>
    <p class="wdesc">{desc}</p>
    {article_list(items)}
  </section>"""

    # 站外：CSDN 全部文章（没有数据时整节不出现）
    ext = ""
    if csdn and csdn.get("articles"):
        items = csdn["articles"]
        views = sum(a.get("views") or 0 for a in items)
        lis = "".join(
            f'<li><a href="{esc(a["url"])}" rel="noopener">{esc(a["title"])}</a>'
            f'<span>{esc(a.get("date", ""))}　{a.get("views", 0):,} 阅读</span></li>'
            for a in items
        )
        ext = f"""
  <section class="wgroup">
    <h2>站外 · CSDN<b>{csdn.get("total") or len(items)} 篇</b></h2>
    <p class="wdesc">发在 CSDN 上的文章，合计 {views:,} 阅读。
      <a href="{esc(csdn.get("home", "https://blog.csdn.net/"))}" rel="noopener">去主页 →</a></p>
    <ul class="csdn-list two">{lis}</ul>
  </section>"""

    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="index.html">首页</a><span>/</span>写作</div>
  <header class="page-head">
    <h1>写作</h1>
    <div>
      <p class="lede">写给别人的东西，和写给自己的分开：这里是可以直接读的长文，
        研究过程的底稿留在「研究」里。</p>
      <p class="stat">{len(essays)} 篇随笔 · {len(tutorials)} 篇教程</p>
    </div>
  </header>
{group("随笔", "讲本质，不堆术语。", essays)}
{group("教程", "从一个具体困惑出发，把机制讲到能自己推一遍。", tutorials)}
{ext}
</main>
"""
    return shell(f"写作 · {SITE_TITLE}", body, "", "写作", "",
                 "随笔与教程：写给读者看的长文。")


# ------------------------------------------------------------------ 清单页
def page_list(title, desc, items, filename, active):
    parent = {"研究": "research", "写作": "writing", "笔记": "notes"}[active]
    body = f"""
<main class="wrap">
  <div class="crumbs"><a href="../index.html">首页</a><span>/</span><a href="../{parent}.html">{active}</a><span>/</span>{esc(title)}</div>
  <header class="list-head">
    <h1>{esc(title)}</h1>
    <p class="lede">{esc(desc)}　共 {len(items)} 篇</p>
  </header>
  {article_list(items, prefix="../")}
  <a class="back-link" href="../{parent}.html">← 返回{active}</a>
</main>
"""
    write(os.path.join(ARTICLES, filename),
          shell(f"{title} · {SITE_TITLE}", body, "../", active, "", desc))


# ------------------------------------------------------------------ 索引
def page_archive(arts, notes, by_subject, survey_n):
    research = [a for a in arts if a["category"] == "研究"]
    essays = [a for a in arts if a["category"] == "随笔"]
    tutorials = [a for a in arts if a["category"] == "学习笔记"]
    res_notes = [n for n in notes if n["subject"] == RESEARCH_SUBJECT]
    course_notes = [n for n in notes if n["subject"] != RESEARCH_SUBJECT]

    def ix(items, prefix="", kind=""):
        out = []
        for it in items:
            out.append(f'<li><a href="{prefix}{it["url"]}">{esc(it["title"])}</a>'
                       f'<span>{esc(kind)}</span></li>')
        return '<ul class="ix">' + "".join(out) + "</ul>"

    subs = sorted(by_subject, key=subject_sort_key)
    sub_ix = "".join(
        f'<li><a href="subject/{subject_slug(s)}.html">{esc(s)}</a>'
        f'<span>{len(by_subject[s])}</span></li>' for s in subs
    )

    total = len(arts) + len(notes) + len(subs)
    body = f"""
<main class="wrap"><div class="archive">
  <h1>索引</h1>
  <p class="lede">全站 {total} 条内容。可以直接搜标题，也可以顺着下面的目录翻。</p>
  <div class="search-field">
    <input id="search-q" type="search" placeholder="搜索标题" autocomplete="off" aria-label="搜索标题" />
    <span class="count" id="search-count"></span>
  </div>
  <p class="search-hint">按 <kbd>/</kbd> 可随时回到这里</p>
  <ul id="search-results" class="search-results"></ul>

  <div id="search-default">
    <section class="ix-group">
      <h2>研究<b>{len(research) + len(res_notes)}</b></h2>
      {ix(research)}
      {ix(res_notes, kind="研究笔记") if res_notes else ""}
    </section>
    <section class="ix-group">
      <h2>写作<b>{len(essays) + len(tutorials)}</b></h2>
      {ix(essays)}
      {ix(tutorials, kind="教程")}
    </section>
    <section class="ix-group">
      <h2>笔记<b>{len(course_notes)} 篇 · {len(subs)} 门</b></h2>
      <ul class="ix two">{sub_ix}</ul>
    </section>
    <section class="ix-group">
      <h2>档案</h2>
      <ul class="ix">
        <li><a href="articles/survey-catalog.html">调研档案总目</a><span>{survey_n} 份</span></li>
        <li><a href="articles/papers-index.html">论文导读</a><span></span></li>
      </ul>
    </section>
  </div>
</div></main>
<script src="data/search-index.js"></script>
"""
    return shell(f"索引 · {SITE_TITLE}", body, "", "索引", "",
                 "全站内容索引与标题搜索。")


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
    write(os.path.join(ROOT, "process.html"), page_process(arts))
    write(os.path.join(ROOT, "notes.html"), page_notes(arts, notes))
    write(os.path.join(ROOT, "writing.html"), page_writing(essays, tutorials, load_csdn()))
    write(os.path.join(ROOT, "archive.html"),
          page_archive(arts, notes, by_subject, survey_n))

    for subject, items in by_subject.items():
        write(os.path.join(ROOT, "subject", subject_slug(subject) + ".html"),
              page_subject(subject, items))

    page_list("研究记录", "完整的过程记录：问题、方法、实验与自我推翻。", research,
              "list-research.html", "研究")
    page_list("论文精读", "逐篇拆解的文献：方法、结构约束、评价口径与和本方向的关系。", readings,
              "list-readings.html", "研究")
    page_list("研究笔记", "研究过程中的专题笔记：概念、推导、实验设置与踩坑记录。", res_notes,
              "list-research-notes.html", "研究")

    # 搜索索引（.js 而不是 .json：双击本地文件打开也能用）
    idx = []
    for a in arts:
        cat = a["category"]
        if cat == "研究":
            section, group = "研究", ("论文精读" if "论文精读" in a["tags"] else "研究记录")
        elif cat == "随笔":
            section, group = "写作", "随笔"
        elif cat in ("调研", "论文"):
            section, group = "研究", cat
        else:
            section, group = "写作", "教程"
        idx.append({"t": a["title"], "u": a["url"], "s": section, "g": group, "d": a["date"]})
    for n in notes:
        idx.append({"t": n["title"], "u": n["url"],
                    "s": "研究" if n["subject"] == RESEARCH_SUBJECT else "笔记",
                    "g": n["subject"], "d": ""})
    for subject in by_subject:
        idx.append({"t": subject + " · 学科", "u": "subject/" + subject_slug(subject) + ".html",
                    "s": "笔记", "g": subject, "d": ""})
    idx.sort(key=lambda x: (x["s"], x["g"], x["t"]))
    write(os.path.join(DATA, "search-index.js"),
          "window.SEARCH_INDEX=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";\n")

    print("简历首页 / 研究 / 写作 / 笔记 / 索引 已重建")
    print("学科页 %d 个 · 清单页 %d 个 · 搜索索引 %d 条"
          % (len(by_subject), len(glob.glob(os.path.join(ARTICLES, "list-*.html"))), len(idx)))
    print("研究 %d · 精读 %d · 研究笔记 %d · 课程笔记 %d · 随笔 %d · 教程 %d"
          % (len(research), len(readings), len(res_notes), len(course_notes),
             len(essays), len(tutorials)))


if __name__ == "__main__":
    main()
