#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 ChatGPT 官方导出（zip 或 conversations.json）拆成一条对话一个 txt，供人工/AI 阅读与 grep。

用法：
    python3 ingest_chatgpt.py                      # 用默认的桌面 zip
    python3 ingest_chatgpt.py /path/to/export.zip
    python3 ingest_chatgpt.py /path/to/conversations.json

产出（全部在 raw_exports/chatgpt_export/，该目录已被 .gitignore 忽略，不进仓库）：
    dump/<会话id前8位>_<标题>.txt   一条对话一个文件，按时间排序，只保留 user/assistant 正文
    INDEX.md                        全部会话清单（日期 / 条数 / 字数 / 文件名），先看这个
    index.json                      同上，机器可读

为什么要有这个脚本：
    ChatGPT 的 conversations.json 是「树」而不是「线性对话」（mapping 里每个节点有 parent/children），
    且顺序字段不可靠；直接按 dict 顺序读会得到乱序对话。这里按 message.create_time 排序后落盘，
    保证人读到的顺序就是当时的实际发生顺序。
"""
import json
import os
import re
import sys
import zipfile
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "raw_exports", "chatgpt_export")
DUMP = os.path.join(OUT, "dump")
DEFAULT_ZIP = os.path.expanduser(
    "~/Desktop/ChatGPT的对话/"
    "f5d32b71bb12762308c2c844968db9b4cc96e1cc6c7f29151f1e7d18d2c64cd3"
    "-2026-10-24-05-10-53-b663bbd98bdd48dba17b4a593a890377.zip"
)


def load_conversations(path):
    """接受 zip 或裸 json，返回 list。"""
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            with z.open("conversations.json") as f:
                return json.load(f)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def part_text(msg):
    """把 message.content.parts 压成纯文本。图片与工具产物只留占位，避免把 base64 写进文件。"""
    ct = msg.get("content") or {}
    out = []
    for p in ct.get("parts") or []:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict):
            if p.get("content_type") == "image_asset_pointer":
                out.append("[图片]")
            else:
                # 有些节点是 {"content_type": "...", "text": "..."} 之类
                t = p.get("text")
                out.append(t if isinstance(t, str) else "[非文本内容]")
    return "\n".join(x for x in out if x).strip()


def safe_name(title, cid):
    t = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", title or "untitled").strip("_")[:48]
    return f"{cid[:8]}_{t}.txt"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    if not os.path.exists(path):
        sys.exit(f"找不到导出文件：{path}")

    convs = load_conversations(path)
    os.makedirs(DUMP, exist_ok=True)

    index = []
    for c in convs:
        nodes = sorted(
            c.get("mapping", {}).values(),
            key=lambda m: (m.get("message") or {}).get("create_time") or 0,
        )
        blocks, n_user, n_asst, chars = [], 0, 0, 0
        for m in nodes:
            msg = m.get("message")
            if not msg:
                continue
            role = (msg.get("author") or {}).get("role")
            if role not in ("user", "assistant"):
                continue
            t = part_text(msg)
            if not t:
                continue
            ts = msg.get("create_time") or 0
            stamp = datetime.datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else ""
            blocks.append(f"\n### {role} {stamp}\n{t}")
            chars += len(t)
            n_user += role == "user"
            n_asst += role == "assistant"
        if not blocks:
            continue

        title = c.get("title") or "(无题)"
        cid = c.get("id") or "unknown"
        created = c.get("create_time") or 0
        day = datetime.datetime.fromtimestamp(created).strftime("%Y-%m-%d") if created else "????-??-??"
        fn = safe_name(title, cid)

        head = (
            f"# {title}\n\n"
            f"> 会话 id：{cid}\n"
            f"> 起始日期：{day}　消息：user {n_user} / assistant {n_asst}　字数：{chars}\n"
            f"> 来源：ChatGPT 官方导出 conversations.json\n"
        )
        with open(os.path.join(DUMP, fn), "w", encoding="utf-8") as f:
            f.write(head + "\n".join(blocks) + "\n")

        index.append(
            {
                "date": day,
                "title": title,
                "id": cid,
                "user": n_user,
                "assistant": n_asst,
                "chars": chars,
                "file": fn,
            }
        )

    index.sort(key=lambda x: (x["date"], -x["chars"]))
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)

    lines = [
        "# ChatGPT 导出 · 会话清单",
        "",
        f"共 {len(index)} 条会话，按起始日期排序。文件都在同目录 `dump/` 下。",
        "",
        "| 日期 | 条数 | 字数 | 标题 | 文件 |",
        "|---|---|---|---|---|",
    ]
    for it in index:
        lines.append(
            f"| {it['date']} | {it['user']} | {it['chars']:,} | {it['title']} | `{it['file']}` |"
        )
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"完成：{len(index)} 条会话 -> {DUMP}")
    print(f"清单：{os.path.join(OUT, 'INDEX.md')}")


if __name__ == "__main__":
    main()
