#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取 me.json —— 站点里所有「关于我」的事实只在这里写一次。

build_site.py（首页简历）与 fix_nav.py（顶栏品牌、页脚）都从这里取，
所以改名字、加邮箱、改研究方向，只要动 me.json，不必碰模板。
"""
import os
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "me.json")


def _load():
    try:
        with open(PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print("!! me.json 读取失败：%s" % e)
        return {}


PROFILE = _load()


def get(key, default=""):
    v = PROFILE.get(key, default)
    return v if v not in (None, "", [], {}) else default


NAME = get("name", "hua")
FIELD = get("field", "")
ROLE = get("role", "")
