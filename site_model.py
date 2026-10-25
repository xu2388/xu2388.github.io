# -*- coding: utf-8 -*-
"""全站内容模型：学科注册表 + 文章/笔记采集。

build_site.py（页面生成）与 build_notes.py（笔记页生成）共用这里的学科定义，
保证「学习 → 学科 → 笔记」三级路径只有一份真相。
"""

# ---------------------------------------------------------------- 学科注册表
# (学科名, URL slug, 所属分组, 一句话说明)
# 学科名必须与 notes/*.md 的 frontmatter `subject` 完全一致。
SUBJECTS = [
    ("计算机网络", "network", "计算机基础", "五层模型、TCP/IP 与协议分层"),
    ("计算机组成原理", "computer-organization", "计算机基础", "存储层次、指令执行与流水线"),
    ("操作系统/Linux", "os-linux", "计算机基础", "进程线程、内存管理与命令行"),
    ("数据结构与算法", "data-structures", "计算机基础", "线性表、树、图与复杂度"),
    ("离散数学", "discrete-math", "计算机基础", "命题逻辑、集合与图论"),
    ("数据库/MySQL", "database", "编程与开发", "SQL、索引、事务与范式"),
    ("JavaWeb", "javaweb", "编程与开发", "Servlet、JDBC、DAO 分层与 MVC"),
    ("Web开发/前端", "web-frontend", "编程与开发", "Django 路由、模板与 ORM"),
    ("机器学习", "machine-learning", "AI 与数据", "特征工程、模型评估与调参"),
    ("深度学习/神经网络", "deep-learning", "AI 与数据", "CNN、RNN、注意力与训练细节"),
    ("数字图像处理", "image-processing", "AI 与数据", "滤波、频域与形态学"),
    ("大数据技术", "big-data", "AI 与数据", "HDFS、MapReduce 与 Spark"),
    ("高等数学/最优化", "math-optimization", "数学", "极限、多元微分与梯度法"),
    ("线性代数", "linear-algebra", "数学", "矩阵、特征值与空间分解"),
    ("概率论/数理统计", "probability", "数学", "分布、估计与假设检验"),
    ("信号与系统", "signals-systems", "电子与物理", "卷积、傅里叶与系统响应"),
    ("大学物理", "physics", "电子与物理", "力学、电磁与热学"),
    ("区块链/分布式", "blockchain", "系统与分布式", "共识、账本与一致性"),
    ("英语/雅思", "english", "通识", "词汇、写作与应试"),
    ("思政/毛概/近代史", "politics", "通识", "课程要点与时政"),
]

# 分组顺序（学习板块的学科网格按此排列）
GROUP_ORDER = ["计算机基础", "编程与开发", "AI 与数据", "数学", "电子与物理", "系统与分布式", "通识"]

# 科研板块的笔记学科（不属于「课程」，单独归类）
RESEARCH_SUBJECT = "虚拟染色/科研"
RESEARCH_SUBJECT_SLUG = "research-notes"
RESEARCH_SUBJECT_DESC = "虚拟染色主线的研究记录、方法与踩坑"

SUBJECT_INDEX = {name: (slug, group, desc) for name, slug, group, desc in SUBJECTS}


def subject_slug(name):
    """学科名 → URL slug。未登记的学科退化成中文名（GitHub Pages 可正常访问）。"""
    if name == RESEARCH_SUBJECT:
        return RESEARCH_SUBJECT_SLUG
    if name in SUBJECT_INDEX:
        return SUBJECT_INDEX[name][0]
    return name


def subject_group(name):
    if name == RESEARCH_SUBJECT:
        return "科研"
    return SUBJECT_INDEX.get(name, (None, "其他", ""))[1]


def subject_desc(name):
    if name == RESEARCH_SUBJECT:
        return RESEARCH_SUBJECT_DESC
    return SUBJECT_INDEX.get(name, (None, None, ""))[2]


def subject_sort_key(name):
    """按注册表顺序排序，未登记的排最后。"""
    order = [s[0] for s in SUBJECTS] + [RESEARCH_SUBJECT]
    return (order.index(name) if name in order else 999, name)
