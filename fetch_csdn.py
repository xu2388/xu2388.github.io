#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 CSDN 的文章清单，写成 data/csdn.json 供 build_site.py 读取。

用法：
    python3 fetch_csdn.py                  # 读 me.json 里的 csdn.user
    python3 fetch_csdn.py xu2388           # 直接指定用户名
    python3 fetch_csdn.py --limit 40       # 只取最近 40 篇

CSDN 前台页面用的就是这个接口（community/home-api/v1/get-business-list），
返回标题、链接、发布日期、阅读量、摘要，不需要登录。接口若改版，脚本会报错
并保留旧数据，不会把 data/csdn.json 写坏。

只抓「公开的博客文章」，不抓专栏/问答/资源。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ME = os.path.join(ROOT, "me.json")
OUT = os.path.join(ROOT, "data", "csdn.json")

API = ("https://blog.csdn.net/community/home-api/v1/get-business-list"
       "?page={page}&size=100&businessType=blog&orderby=&noMore=false"
       "&year=&month=&username={user}")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def parse_user(raw):
    """三种写法都认：用户名、主页链接、任意一篇文章的链接。

    昵称不是账号名——「不想生孩子」是昵称，地址栏里那串 2401_xxxx 才是账号，
    接口只认账号。文章链接里也带着账号，所以贴文章链接一样能解析出来。
    """
    raw = (raw or "").strip()
    m = re.search(r"csdn\.net/([^/?#]+)", raw)
    if m:
        return urllib.parse.unquote(m.group(1))
    return raw.rstrip("/").split("/")[-1]


def load_me():
    try:
        with open(ME, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.exit("!! 读不到 me.json：%s" % e)


def fetch_page(user, page):
    url = API.format(page=page, user=urllib.parse.quote(user))
    req = urllib.request.Request(url, headers=dict(HEADERS, Referer="https://blog.csdn.net/" + user))
    with urllib.request.urlopen(req, timeout=25) as r:
        payload = json.loads(r.read().decode("utf-8"))
    if payload.get("code") != 200:
        raise RuntimeError("接口返回 %s：%s" % (payload.get("code"), payload.get("message")))
    return payload.get("data") or {}


def main():
    argv = [a for a in sys.argv[1:]]
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        del argv[i:i + 2]

    me = load_me()
    cfg = me.get("csdn") or {}
    user = parse_user(argv[0] if argv else cfg.get("user") or "")
    if not user:
        sys.exit("!! 还没填 CSDN 用户名。\n"
                 "   把 me.json 里 csdn.user 改成你的用户名（blog.csdn.net/ 后面那段），\n"
                 "   或者直接跑：python3 fetch_csdn.py 你的用户名")

    print("抓取 %s 的文章列表 …" % user)
    articles, total, page = [], 0, 1
    while True:
        try:
            data = fetch_page(user, page)
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError, TimeoutError) as e:
            print("!! 第 %d 页失败：%s" % (page, e))
            if not articles:
                sys.exit("!! 一条都没抓到，保留原有 data/csdn.json 不动。")
            break

        total = data.get("total") or total
        batch = data.get("list") or []
        if not batch:
            break
        for it in batch:
            articles.append({
                "title": (it.get("title") or "").strip(),
                "url": it.get("url") or "",
                "date": it.get("formatTime") or (it.get("postTime") or "")[:10].replace("-", "."),
                "views": it.get("viewCount") or 0,
                "digest": (it.get("description") or "").strip()[:120],
            })
        print("  第 %d 页 +%d 篇（累计 %d / %s）" % (page, len(batch), len(articles), total or "?"))
        if (total and len(articles) >= total) or (limit and len(articles) >= limit) or len(batch) < 100:
            break
        page += 1
        time.sleep(0.6)                            # 别把人家接口打急了

    if not articles:
        sys.exit("!! %s 名下没有抓到文章。\n"
                 "   最常见的原因是填了昵称：接口只认地址栏里的账号名\n"
                 "   （blog.csdn.net/ 后面那串），不认昵称。\n"
                 "   把主页链接或任意一篇文章的链接直接当参数传进来也行：\n"
                 "     python3 fetch_csdn.py https://blog.csdn.net/你的账号\n"
                 "   原有 data/csdn.json 未被改动。" % user)

    if limit:
        articles = articles[:limit]

    home = cfg.get("home") or ("https://blog.csdn.net/%s" % user)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        "user": user,
        "home": home,
        "total": total or len(articles),
        "count": len(articles),
        "fetched": time.strftime("%Y-%m-%d %H:%M"),
        "articles": articles,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    views = sum(a["views"] for a in articles)
    print("\n写入 %s" % os.path.relpath(OUT, ROOT))
    print("  %d 篇 · 合计阅读 %s" % (len(articles), format(views, ",")))
    if articles:
        print("  最新：%s（%s）" % (articles[0]["title"], articles[0]["date"]))
    print("\n接着跑：python3 build_site.py && python3 fix_nav.py")


if __name__ == "__main__":
    main()
