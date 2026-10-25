#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""博客成文稿合规体检：文风禁词 / 隐私泄漏 / 渲染器坑 / front matter。
用法: python3 /tmp/lint_blog.py <文件或目录> ...
不改任何文件，只报告。
"""
import sys, os, re, glob

def _load_subjects():
    """直接从 build_notes.py 取 SUBJECT_ORDER，避免校验清单与真实分组漂移。"""
    src = "/Users/hua/Desktop/科研博客/build_notes.py"
    try:
        m = re.search(r"SUBJECT_ORDER\s*=\s*\[(.*?)\]", open(src, encoding="utf-8").read(), re.S)
        if m:
            return set(re.findall(r'"([^"]+)"', m.group(1)))
    except OSError:
        pass
    return {"计算机网络","数据库/MySQL","JavaWeb","数据结构与算法","深度学习/神经网络","大数据技术",
            "信号与系统","数字图像处理","高等数学/最优化","大学物理","英语/雅思","思政/毛概/近代史",
            "虚拟染色/科研","其他"}

SUBJECTS = _load_subjects()
CATS = {"研究","调研","课程笔记","学习笔记","随笔","知识库","论文","资料库"}

BANNED = [
    (r"(?<![一单双多])我们", "对话人称「我们」"),
    (r"(?<![你与])你们", "对话人称「你们」"),
    (r"[咱俺]们?", "口语人称"),
    (r"^\s*[dD]\s*$", "单字母回信"),
    (r"\[图片\]|\[图\]|【图片】", "图片占位符"),
    (r"<\s*canvas[_ ]?command|<\s*/\s*canvas", "工具 XML 标签"),
    (r"kimi-cite://", "中间格式引用"),
    (r"/root/|autodl|D:\\\\|C:\\\\|E:\\\\", "私人路径"),
    (r"(api[_ ]?key|token|secret|password|passwd)\s*[:=]\s*\S", "疑似密钥"),
    (r"太原理工|Taiyuan University|Downloaded from|IEEE Trans.*Medical Imaging, Vol", "原料版权水印/本人校名"),
    (r"No\.\s*\d+题|第\s*\d+\s*题（?选|作业\s*\d|考试答案|答案选\s*[ABCD]", "具体题号/答案"),
    (r"(老师|教授)\s*[王李张刘陈杨黄赵吴周]|导师\s*[:：]\s*\S{2,4}$", "具体师生姓名"),
    (r"牛逼|太绝了|笑死|yyds|awsl", "口语/网络梗"),
]
INLINE_LINK = r"(?<!\!)\[[^\]\n]{1,80}\]\(([^)\s]+)\)"


def math_block_issues(lines):
    """按 $$ 出现次序配对，检查每个独立公式块的上下空行。

    按「整行等于 $$」判断会在 `...=16/3.$$` 这类行内闭合处失配，
    因此改成扫描全文 $$ 定界符、按奇偶配对，与 KaTeX auto-render 的行为一致。
    """
    out = []
    occ = []            # (行号 1-based, 该行是否整行只有 $$)
    in_code = False
    for idx, ln in enumerate(lines, 1):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        n = ln.count("$$")
        for _ in range(n):
            occ.append((idx, ln.strip() == "$$"))
    if len(occ) % 2:
        out.append((occ[-1][0], "独立公式块的 $$ 定界符个数为奇数，无法配对"))
        return out
    for k in range(0, len(occ), 2):
        (op_ln, op_alone), (cl_ln, cl_alone) = occ[k], occ[k + 1]
        prev = lines[op_ln - 2].strip() if op_ln >= 2 else ""
        if prev and not prev.startswith("```") and not prev.endswith("$$"):
            out.append((op_ln, "独立公式块上方缺空行 → 会被并进上一段"))
        nxt = lines[cl_ln].strip() if cl_ln < len(lines) else ""
        if nxt and not nxt.startswith("```"):
            out.append((cl_ln, "独立公式块下方缺空行 → 会被并进下一段"))
    return out


def files_of(arg):
    if os.path.isdir(arg):
        return sorted(glob.glob(os.path.join(arg, "*.md")))
    return [arg]

def report(path):
    issues = []
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if not m:
        issues.append((1, "缺少 front matter"))
    else:
        for ln in m.group(1).split("\n"):
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
        body_start = text[:m.end()].count("\n")
    base = os.path.basename(path)
    is_note = "notes" in path and not re.match(r"^\d{3}-", base)
    if is_note:
        for req in ("title", "subject", "category", "summary"):
            if not fm.get(req):
                issues.append((1, f"front matter 缺 {req}"))
        if fm.get("subject") and fm["subject"] not in SUBJECTS:
            issues.append((1, f"subject「{fm['subject']}」不在 SUBJECT_ORDER"))
        if re.search(r"\.md", fm.get("source", "")):
            issues.append((1, "source 含 .md → 会建原始对话回链（作者要求不留）"))
    else:
        for req in ("title", "date", "tags", "category", "summary"):
            if not fm.get(req):
                issues.append((1, f"front matter 缺 {req}"))
        tags = fm.get("tags", "")
        if tags and not (tags.startswith("[") and tags.endswith("]")):
            issues.append((1, f"tags 不是 JSON 数组: {tags[:40]}"))
    if fm.get("category") and fm["category"] not in CATS:
        issues.append((1, f"category「{fm['category']}」不在可选列表"))
    if fm.get("summary") and len(fm["summary"]) < 60:
        issues.append((1, f"summary 过短({len(fm['summary'])}字)，需 100-200 字高信息密度"))

    in_code = False
    math_open = False
    for i, ln in enumerate(lines, 1):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for pat, why in BANNED:
            if re.search(pat, ln):
                issues.append((i, f"{why}: {ln.strip()[:70]}"))
        for lm in re.finditer(INLINE_LINK, ln):
            if not lm.group(1).startswith(("http", "assets/", "../", "./")):
                issues.append((i, f"行内链接会原样显示: {lm.group(0)[:60]}"))
        # 表格单元格里的裸竖线（LaTeX 范数/绝对值）
        if ln.strip().startswith("|") and re.search(r"\\(\||Vert||lVert)", ln):
            pass
        # 标题层级 > ####
        if re.match(r"^#{5,}\s", ln):
            issues.append((i, f"标题层级超过 ####: {ln.strip()[:40]}"))
    if in_code:
        issues.append((len(lines), "代码围栏未闭合"))
    issues.extend(math_block_issues(lines))
    zh = len(re.findall(r"[一-鿿]", text))
    return issues, zh, len(text)

def main():
    total_bad = 0
    for arg in sys.argv[1:]:
        for p in files_of(arg):
            issues, zh, size = report(p)
            flag = "OK " if not issues else "!! "
            print(f"{flag}{p}  正文汉字≈{zh}  {size//1000}KB  问题{len(issues)}")
            for ln, why in issues[:12]:
                print(f"     L{ln}: {why}")
            total_bad += len(issues)
    print(f"合计问题 {total_bad}")

if __name__ == "__main__":
    main()
