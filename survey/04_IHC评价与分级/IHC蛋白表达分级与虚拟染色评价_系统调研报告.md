# IHC 蛋白表达分级体系（0/1+/2+/3+）及其用于 H&E→IHC 虚拟染色生成质量评价的系统文献调研

**调研对象**：深度学习医学图像虚拟染色（H&E → IHC）研究者
**核心问题**：IHC 中的 0/1+/2+/3+ 到底是什么？是不是通用蛋白表达分级？哪些蛋白适用？能否自动计算？能否作为虚拟 IHC 的生成质量评价指标？
**报告日期**：2026-09-30
**证据等级标注**：`[指南]` = 权威学会/官方指南原文；`[原文]` = 已核对原文/摘要的一手论文；`[二手]` = 来自综述或索引记录的转述；`[存疑]` = 未能核实，需自行复核。

---

## 0. 三句话结论（Executive Summary）

1. **0/1+/2+/3+ 不是通用 IHC 分级。** 它是 **HER2 的 biomarker-specific 分级体系**（乳腺癌由 ASCO/CAP 定义，胃癌定义不同），历史上由 HercepTest 与曲妥珠单抗试验固化。通用性的"半定量框架"其实是 **H-score（0–300）**、**IRS（0–12）**、**Allred（0–8）** 和 **Quickscore** 这一族，而不是 0/1+/2+/3+。
2. **它可以用，但只能"按 biomarker 用"，且必须先降级为分类问题。** 对你的 H&E→IHC 研究，**H-score 类连续量更适合做主指标，0/1+/2+/3+ 类分类更适合做补充指标（用于回答"临床决策对不对"）**。前提是：目标 biomarker 必须有官方判读标准（HER2 乳腺癌、HER2 胃癌、Claudin-18.2、c-MET 等），且染色部位必须匹配（HER2 = 膜，ER/PR/p53/Ki-67 = 核）。
3. **该方向存在真实但稀疏的先行工作，且明确留有空白。** 已有论文在生成 IHC 上做过：DAB/光密度指标（IOD、mIOD、Pearson-R、JSD）、HER2 0/1+/2+/3+ 病理医师盲法评分、Ki-67 阳性率与临床阈值、以及"下游分类器"评估。**但迄今未发现任何一篇虚拟染色论文在生成图像上计算经典 H-score 或 Allred 评分**——这正是你可以填补的空白，也是你论文的 novelty 切入点。

---

## 1. Part 1 — IHC 蛋白表达评分体系全景图

### 1.1 一句话定义问题

文献里"评分"这个词被混用得非常严重。必须先分清三个**互不兼容**的家族：

| 家族 | 本质 | 是否 biomarker 专用 | 代表 | 能否跨蛋白通用 |
|---|---|---|---|---|
| **A. 指南级 biomarker-specific 评分** | 学会/监管机构制定、有版本号、绑定用药决策 | ✅ 专用 | HER2 乳腺癌 0/1+/2+/3+（ASCO/CAP）；HER2 胃癌；Claudin-18.2；ER/PR 百分比；Ki-67 百分比；PD-L1 TPS/CPS | ❌ 不能 |
| **B. 通用半定量计算框架** | 与生物学无关的"强度×比例"算术模板 | ❌ 通用 | **H-score（0–300）**、**IRS/Remmele（0–12）**、**Allred（0–8）**、**Quickscore** | ✅ 公式通用，但**判读阈值**仍按蛋白定 |
| **C. 研究者自造的 3/4 档强度分类** | 单篇论文自己定义的 −/+/++/+++ | ❌ 无标准 | TROP2 的 0–3+、AR 的 0–3+、EGFR 的 "intensity×proportion"、把 H-score 事后切成 low/mid/high | ❌ 不可迁移 |

> **这是本次调研最重要的一张表。** 用户要求"不要把某篇文章把 ER 分成 low/medium/high 就当标准 0/1+/2+/3+"——上表就是对这一要求的正式回应：**A 类才能当 ground truth，B 类是框架，C 类是噪声。**

### 1.2 权威定调：IHC 领域根本不存在单一通用评分

一篇被广泛引用的系统综述给出了直接结论：

> Fedchenko N, Reifenrath J. *Different approaches for interpretation and reporting of immunohistochemistry analysis results in the bone tissue – a review.* **Diagn Pathol. 2014;9:221.** PMID 25432701. `[原文]`
> 原文结论：**"A widely accepted scoring system for immunohistochemistry does not exist yet"**（迄今不存在被广泛接受的 IHC 评分体系），而所谓"golden standard"只对 **HER2/neu、ER、PR 三个标志物**存在定义。
> 该文还系统统计了各文献中**同一评分名称被不同实现**的情况（例如 IRS 有人乘、有人加；Allred 被改得"已经不是 Allred 了"）。

**对你的直接含义**：任何声称"0/1+/2+/3+ 是通用 IHC 标准"的说法都是错的。你在论文里必须写成 "the biomarker-specific ordinal (semiquantitative) categorical IHC score, e.g. the four-tier 0/1+/2+/3+ scale defined for HER2 by ASCO/CAP"。

### 1.3 全景图（四层结构）

```
                         IHC 蛋白表达评分体系
                                  │
   ┌──────────────────────────────┼──────────────────────────────┐
   │                              │                              │
 A. 指南级（专用）            B. 通用半定量框架            C. 研究者自造
   │                              │                              │
 ├ HER2 乳腺 0/1+/2+/3+       ├ H-score  0–300            ├ TROP2 0–3+
 │  (ASCO/CAP 2007→2013         │  (McCarty 1985/86)         ├ AR 0–3+ / H-score
 │   →2018→2023)               ├ IRS/Remmele 0–12          ├ EGFR intensity×prop.
 ├ HER2 胃/食管 0/1+/2+/3+     │  (Remmele & Stegner 1987)  ├ H-score 事后切档
 │  (CAP/ASCP/ASCO 2016/17)    ├ Allred 0–8                │  (low/mid/high)
 ├ ER/PR 百分比(±Allred/H)     │  (Allred 1998)             └ …
 │  (ASCO/CAP 2010→2020)       └ Quickscore
 ├ Ki-67 百分比                │  (Detre 1995)
 │  (IKWG 2011→2021)
 ├ PD-L1 TPS/CPS/TC/IC
 │  (assay-specific, FDA)
 ├ p53 模式判读(overexp/null)
 ├ MMR 二元(retained/lost)
 ├ Claudin-18.2 (2+/3+ ≥75%)
 └ c-MET 0–3+ (emerging)
```

### 1.4 染色部位（compartment）是评分的一部分，且按蛋白不同

必须显式建模，不能忽略：

- **膜染色（membrane）**：HER2、Claudin-18.2、c-MET、PD-L1（肿瘤细胞）、TROP2
- **核染色（nuclear）**：ER、PR、AR、Ki-67、p53、MUM1、Bcl-6
- **胞浆染色（cytoplasmic）**：ALK、ROS1、Bcl-2、部分 p53 变异型
- **膜/胞浆/核混合**：PTEN、EGFR

> Hawes 等（*Immunohistochemistry*，PMC7151845）`[二手]`：**"The subcellular distribution of immunoreactivity is critical to the interpretation of immunohistochemical results."**——HER2 是膜，ER/PR 是核。一个只会生成"棕色团块"的生成模型，任何评分体系都无法判读。

---

## 2. Part 2 — 0/1+/2+/3+ 的准确医学定义

### 2.1 它是什么

**HER2 蛋白免疫组化分级（HER2 IHC scoring）**，一个 **4 档有序分类（4-category ordinal）** 体系。不是"三级评定"，也不是"通用蛋白分级"。

- 术语正解：**"four-category (ordinal) semiquantitative IHC score"** / **"biomarker-specific categorical IHC score"**
- 中文可写："**四档有序半定量 IHC 评分**" 或 "**IHC 强度分级（0/1+/2+/3+）**"
- 病理学界更常用 **"four-category HER2 IHC scoring system"**（见 Robbins 2023）；"4-tier" 是 ML/AI 圈的叫法。**"三级评定"不是标准术语**，且与实际档数（4 档）矛盾，不要使用。

### 2.2 为什么这样分（逻辑）

因为 HER2 的治疗决策（曲妥珠单抗）**不是连续的**，而是三分的：

```
IHC 3+           → HER2 阳性    → 抗 HER2 治疗
IHC 2+ (equivocal)→ 必须 ISH 复核 → 由 HER2/CEP17 比值定
IHC 0 / 1+       → HER2 阴性    → 不治疗（2022 年后 1+ 进入 T-DXd 适应症）
```

所以 0/1+/2+/3+ 的设计目的是**"在不确定区（2+）强制触发第二次检测"**，而不是"精确刻画表达量"。这一点极其关键：**它本质上是一个"决策分类器"，不是"表达量回归器"。**

### 2.3 是否通用 —— 否

- 它**只对 HER2 有正式定义**，且**乳腺癌与胃癌的定义不同**。
- ER/PR 官方输出是**百分比**（Allred/H-score 可选）；Ki-67 官方明确**排除强度**；PD-L1 是 TPS/CPS；p53 是**模式判读**。这些都不是 0/1+/2+/3+。

### 2.4 HER2 乳腺癌：逐档定义（ASCO/CAP 2018 原文，2023 更新沿用）`[指南]`

已从 2018 年 ASCO/CAP 指南 PDF 原文核验（Wolff AC, et al. *Arch Pathol Lab Med* / *J Clin Oncol* 2018;36(20):2105–2122）：

| 档位 | 原文定义（Table 1） | 三要素拆解 |
|---|---|---|
| **IHC 0** | "no staining observed **or** membrane staining that is incomplete and is faint or barely perceptible and within **≤10%** of the invasive tumor cells" | 强度：无/极弱；完整性：不完整；比例：≤10% |
| **IHC 1+** | "incomplete membrane staining that is faint or barely perceptible and within **>10%** of the invasive tumor cells" | 强度：弱；完整性：**不完整**；比例：>10% |
| **IHC 2+ (equivocal)** | "circumferential membrane staining that is **incomplete and/or weak to moderate** and within **>10%** of the invasive tumor cells **or** complete and circumferential membrane staining that is **intense** and within **≤10%**" | 两种情形：①弱/中 + 不完整 + >10%；②强 + 完整 + ≤10% |
| **IHC 3+ (positive)** | "circumferential membrane staining that is **complete, intense**" （in >10% of invasive tumour cells） | 强度：强；完整性：**完整环绕**；比例：>10% |

> **重要脚注（同一指南内）**：2018 更新把 Figure 1 中 IHC 2+ 的**修订定义**写作 **"weak to moderate complete membrane staining observed in >10% of tumor cells"**。因此你会在不同二手资料里看到两个略有差异的 2+ 定义——**它们都出自 2018 指南本身**，一个是 Table 1 汇总版，一个是 Figure 1 判读流程版。`[指南]`

**必须注意的三个"非直觉"点**：
1. **0 ≠ 完全无信号。** 0 明确包含"≤10% 细胞的弱而不完整膜染色"。
2. **档位不是只看强度。** 是 (强度) × (膜完整性 complete/circumferential vs incomplete) × (阳性细胞比例) 的三维联合判定。
3. **只有膜染色算数。** 胞浆染色在 HER2 乳腺癌判读中被忽略。

### 2.5 HER2 胃癌/食管胃结合部：**同名不同义** `[指南]`

CAP/ASCP/ASCO 2016/2017（Bartley AN, et al. *J Clin Oncol* 2017;35(4):446–464），采用 Rüschoff–Hofmann 法：

| 档位 | 手术标本 | 活检标本（cluster 规则） |
|---|---|---|
| 0 | 无反应 **或** 膜反应 <10% 肿瘤细胞 | 任何肿瘤细胞均无反应 |
| 1+ | 微弱膜反应 ≥10%，**仅部分细胞膜** | 细胞簇（**≥5 个肿瘤细胞**）微弱膜反应，**不论比例** |
| 2+ | 弱–中等 **完整、基底侧或侧向** 膜反应 ≥10% | 细胞簇（≥5 个）弱–中等完整/基底侧/侧向反应 |
| 3+ | 强 **完整、基底侧或侧向** 膜反应 ≥10% | 细胞簇（≥5 个）强完整/基底侧/侧向反应 |

**与乳腺癌的三点本质差异**（这就是为什么不能把 HER2 当通用标准）：
1. **不完整膜染色可以到 3+**（基底侧/侧向被接受），而乳腺癌只有完整环绕才能 3+；
2. **活检用"细胞簇"规则，忽略百分比**；
3. 2+ 同样是 equivocal，须 ISH 复核。

### 2.6 版本演进与"HER2-low / HER2-ultralow"（2026 视角）

| 版本 | 年份 | 关键变化 |
|---|---|---|
| 原版 | 2007 | 首次 ASCO/CAP 规范化 0/1+/2+/3+ |
| 更新 | 2013 | 澄清 2+ 判读、ISH 分组 |
| 聚焦更新 | 2018 | 修订 Figure 1 的 2+ 定义；澄清 ISH 灰色区 |
| **更新（现行）** | **2023** | **重申 2018**；**明确不建立 "HER2-Low" 判读类别**（理由：DESTINY-Breast04 未纳入 IHC 0 患者，1+/2+ISH− 相比 0 无预测性证据）；FDA 扩大 T-DXd 适应症属于**试验入组标准**而非新的预测性检测指征 |

> 来源：CAP 官方指南页（现行状态 "Active"，2023-06-07 在线发表；亦见 *Arch Pathol Lab Med* 147(9):993）`[指南]`

- **HER2-low**：**不是** ASCO/CAP 判读类别，而是试验/监管**简称**（IHC 1+ 或 2+/ISH−）。
- **HER2-ultralow**：2025 年国际专家共识定义为 **"faint or barely perceptible, incomplete membrane staining in >0% to ≤10% of tumor cells"**（即 IHC 0 中"非真零"的那一部分），源自 DESTINY-Breast06。`[二手]`

### 2.7 人工判读的可重复性：给生成模型的"天花板"

**这是你必须写进论文 limitation 的数字**：

> Robbins CJ, Fernandez AI, Han G, … Rimm DL. *Multi-institutional Assessment of Pathologist Scoring HER2 Immunohistochemistry.* **Mod Pathol. 2023;36:100032.** `[原文]`
> 170 例乳腺活检，**18 位乳腺病理医师，15 家机构**：
> - **四分类（0/1+/2+/3+）总体一致率 OPA = 28.8%**
> - 三分类（0 / Low / 3+）OPA = 46.5%
> - **IHC 1+ 一致率仅 0.98%**；2+ 仅 3.57%；3+ 50%；0 25%
> - 结论：**"unacceptably discordant for assigning HER2-low status"**

**含义**：0/1+/2+/3+ 的标签噪声极大，**任何生成模型都不可能超过这个上限**。所以：
- 不要用 raw accuracy 做唯一指标；
- 参考标准必须是**共识/仲裁（adjudicated）**标注；
- 用 **Fleiss' κ / ICC / 加权 κ**，并**明确报告"自动 vs 病理医师"的差距是否落在"病理医师 vs 病理医师"的差距之内**（这是审稿人唯一接受的说法）。

---

## 3. Part 3 — 不同 biomarker 的评分标准比较

### 3.1 主表

| Biomarker | 癌种/疾病 | 评分体系 | 用 0/1+/2+/3+? | 判定依据 | 是否看阳性比例 | 染色部位 | 官方指南（年份/版本） | 来源 |
|---|---|---|---|---|---|---|---|---|
| **HER2** | 乳腺癌（浸润性） | IHC 0/1+/2+/3+，2+ 反射 ISH | **✅ A 类** | 膜完整性 × 强度 × >10% 比例 | ✅ (>10%/≤10%) | **膜**（环绕） | **ASCO/CAP 2007→2013→2018→2023**（现行 2023，重申 2018） | cap.org；JCO 2018;36:2105 |
| **HER2** | 胃/食管胃结合部腺癌 | IHC 0/1+/2+/3+（Rüschoff–Hofmann），2+ 反射 ISH | **✅ A 类**（**定义不同**） | 膜完整性 × 强度；**接受基底侧/侧向** | ✅ 手术 ≥10%；**活检 ≥5 细胞簇** | **膜** | **CAP/ASCP/ASCO 2016/2017**（Bartley） | JCO 2017;35:446 |
| **ER** | 乳腺癌 | **阳性核百分比**（主）；Allred 0–8 / H-score 0–300（**可选**） | ❌ | **阳性核百分比**（≥1%） | ✅ 核心 | **核** | **ASCO/CAP 2010→2020**（现行 2020） | JCO 2020;38:1346 |
| **PR** | 乳腺癌 | 同 ER | ❌ | 同上（≥1%） | ✅ | **核** | ASCO/CAP 2020 | 同上 |
| **Ki-67** | 乳腺癌（预后） | **连续百分比**（global score） | ❌ | **阳性肿瘤核百分比，官方明确"不看强度"** | ✅ | **核** | **IKWG 2011→2021**（**无通用 cut-off**） | JNCI 2021（PMC8487652） |
| **PD-L1** | NSCLC/胃/尿路上皮/TNBC/HNSCC… | **TPS / CPS / TC / IC（连续百分比）** | ❌（唯一例外：黑色素瘤 MEL 0–5） | 阳性细胞百分比 vs assay 阈值 | ✅ | **膜**（肿瘤+免疫细胞） | **assay-specific FDA companion diagnostic**（22C3/28-8/SP142/SP263） | J Pers Med 2022;12:1073 |
| **p53** | 子宫内膜癌/卵巢 HGSOC/结直肠/食管 | **模式判读**：overexpression / null / cytoplasmic vs wild-type | ❌ | **模式**，非强度档 | 模式（overexpression >80%） | **核**（+胞浆变异型） | WHO 2020 子宫内膜分子分型；ESGO/ESTRO/ESP 2021；ProMisE | Cancers 2025;17:1506 |
| **EGFR** | NSCLC/CRC/HNSCC/GBM | **无验证的 IHC 治疗选择评分** | ❌（临床）；论文中 (B) 类有 0–3+ | **突变状态**，非蛋白 | n/a | 膜/胞浆 | **CAP/IASLC/AMP 2018：明确不建议用 IHC 选 TKI 患者** | cap.org |
| **MMR** (MLH1/PMS2/MSH2/MSH6) | 结直肠/子宫内膜/泛癌 | **二元：intact (retained) vs lost** | ❌（二元） | 核染色**有/无** + 内对照 | 否 | **核** | CAP/NCCN 模板；BAGP；ESGO/ESTRO/ESP | PMC9708570 |
| **ALK** | NSCLC | 临床**二元**（D5F3 CDx）；文献中有 0–3+ | 部分（A/B） | 任何**强颗粒状胞浆**染色 = 阳性 | 否 | **胞浆（颗粒）** | CAP/IASLC/AMP 2018 | cap.org |
| **ROS1** | NSCLC | **二元** + FISH/NGS 确认 | ❌ | 中–强胞浆染色 | 否 | **胞浆** | CAP/IASLC/AMP 2018 | cap.org |
| **c-MET** | NSCLC | **0/1+/2+/3+（共识，非全球指南）** | **✅ A/B（新兴）** | 膜强度 × 比例（如 ≥50% 3+ = high） | ✅ | 膜/胞浆 | 中国 NSCLC MET 共识 / Lab Invest 2026 | laboratoryinvestigation.org |
| **Claudin-18.2** | 胃/食管胃结合部 | **≥75% 肿瘤细胞呈 2+/3+ 膜染色 = 阳性** | **✅ A 类（2+/3+ 嵌在 % 规则里）** | 强度（中/强）× 比例 | ✅ **≥75%** | **膜**（含顶端/微腔） | **Ventana CLDN18 (43-14A) RxDx（zolbetuximab，2024 FDA）** | captodayonline.com |
| **TROP2** | 乳腺/TNBC 等 | 0–3+ 与 H-score（**仅研究**） | **(B) 研究** | 强度 × 比例 | ✅ | **膜**（排除胞浆） | **无标准化临床标准** | pathologyoutlines.com |
| **AR** | 乳腺/前列腺 | 核阳性百分比（研究 cut-off）；文献有 0–3+/H-score | ❌ 无正式 | 核阳性百分比 | ✅ | **核** | **乳腺癌无公认 cut-off** | pathologyoutlines.com |
| **PTEN** | 前列腺/子宫内膜/乳腺/GBM | **retained vs lost** | ❌ | 缺失 = 减弱/无染色（≥90% 无染色） | 部分 | 胞浆/膜/核 | FDA capivasertib CDx；CAPItello-281 | pathologyoutlines.com |
| **Bcl-2/Bcl-6/MUM1/CD10** | DLBCL | 阳性/阴性 + % 阈值（如 MUM1 ≥30%） | ❌ | 有无 + % 阈值 | ✅ | 核（MUM1/Bcl-6）/胞浆（Bcl-2） | Hans 算法（2004）；无 CAP 有序评分 | immunopathol.com |
| **CD3/CD8/CD20/CD68** | 免疫微环境 | **密度（cells/mm²）** | ❌ | **密度/位置** | 密度 | 膜 | Immunoscore（结肠 CD3/CD8） | PMC9896157 |

### 3.2 逐 biomarker 要点

**HER2（乳腺癌）** —— 见 Part 2.4。要点：膜、完整环绕、>10%、2+ 反射 ISH。

**HER2（胃癌）** —— 见 Part 2.5。要点：基底侧/侧向可算 3+，活检用细胞簇规则。**同一张切片、同一个"3+"，乳腺和胃的判读逻辑完全不同。**

**ER / PR** —— 现行 ASCO/CAP 2020：
- **唯一决策变量 = 阳性核百分比**：**1%–100% = 阳性，<1% = 阴性**。
- **重要覆盖规则**：即使 Allred/H-score 与 1% 规则冲突，**以 1% 规则为准**（≥1% 一律阳性，<1% 一律阴性）。
- 报告要求：**阳性核百分比 + 平均强度（weak/moderate/strong）**。
- **"ER-low positive"（1–10%）**：判为阳性、可用内分泌治疗，但需加注（该档生物学行为更接近 ER 阴性）。**它是报告注意事项，不是新档位。**
- Allred：proportion(0–5) + intensity(0–3) = **0–8**；**0 与 2 判为阴性，3–8 判为阳性**（但受 1% 规则覆盖）。

**Ki-67** —— IKWG 2021 `[原文]`：
- **官方明确"No interpretation of intensity"**——只用阳性核百分比，**这是与 0/1+/2+/3+ 的根本冲突点**。
- 推荐 **global（平均）法** 而非 hot-spot；Phase 2 ICC 提升至 **0.92**；hot-spot ICC 仅 0.83–0.84。
- **只有两端可用**：**≤5% = low，≥30% = high**；**5–30% 中间区不可用于临床决策**。
- **"low/intermediate/high" 不是标准分级**，是 IKWG 的两端界定 + 大量论文的自定 cut-off。
- 自动化：IKWG 认为**仍属研究阶段（investigational）**。

**PD-L1** —— **不是 0/1+/2+/3+**，是 assay-specific 百分比：

| 分数 | 定义 |
|---|---|
| **TPS / TC** | PD-L1⁺ 存活肿瘤细胞 / 全部存活肿瘤细胞 × 100 |
| **CPS** | (PD-L1⁺ 肿瘤 + 淋巴细胞 + 巨噬细胞) / 存活肿瘤细胞 × 100 |
| **IC** | PD-L1⁺ 免疫细胞面积 / (肿瘤 + 瘤周面积) × 100 |

- **FDA 把药物与特定 clone + 分数 + 阈值绑定**（如 22C3/胃癌 CPS≥5；SP142/TNBC IC≥1%；SP263/NSCLC TPS）。**必须写清 assay。**
- **陷阱**：肺癌报告里的 **"TC0/TC1/TC2/TC3" 与 "IC0/IC1/IC2/IC3" 是百分比分箱（TC0 <1%、TC1 1–4%、TC2 5–49%、TC3 ≥50%）**，**不是** HER2 式强度档。**别被 0/1/2/3 的写法骗了。**
- 唯一真正用 0–5 有序的是**黑色素瘤 MEL 评分**（改编自 Allred）。

**p53** —— **模式判读，不是强度档**：overexpression（>80% 强核染）／null（完全无染，需内对照阳性）／cytoplasmic（>80% 强胞浆染）／wild-type（异质）。作为 **TP53 突变的替代指标**，用于 WHO 2020 子宫内膜分子分型（p53-abnormal / copy-number-high）与 ProMisE。

**EGFR** —— CAP/IASLC/AMP 明确：**"strongly recommended that total EGFR expression analysis by immunohistochemistry should not be used to select patients for EGFR-targeted TKI therapy"**。临床用**突变检测**。论文里出现的 EGFR 0–3+ 全是 (B) 类。

**Claudin-18.2** —— **A 类**，但形态特殊：**只有"中/强（2+/3+）"计入百分比，且阈值 ≥75% 才判阳性**。判读模式谱（顶端、环周部分/完整、基底侧/侧向、微腔）都要看，但只有中/强计数。

### 3.3 A / B / C 三类的具体例子（用户特别要求）

**（A）真正的临床/病理 0/1+/2+/3+ 评分**（有指南、有版本、绑定用药）
- HER2 乳腺癌（ASCO/CAP 2018/2023）
- HER2 胃癌/食管胃结合部（CAP/ASCP/ASCO 2017）
- Claudin-18.2（Ventana 43-14A RxDx，2024）
- c-MET（新兴共识）

**（B）研究者自造的 3/4 档强度分类**（单篇论文，不可迁移）
- TROP2 的 0–3+ 与 H-score（原文即注明"标准判读标准缺失"）
- AR 在乳腺癌的 0–3+ / H-score（cut-off 从 ≥1% 到 ≥10% 各不相同）
- EGFR 的 "intensity × proportion" 突变替代评分
- PD-L1 的 "TC0–TC3" 写法（**伪装成 A 类的 B/C 混合体**）

**（C）H-score 事后切档**
- TROP2 H-score：low 0–100 / intermediate 101–200 / high 201–300（纯约定，非生物学阈值）
- ER H-score 分箱（但临床决策其实是 ≥1% 规则）
- Ki-67 的 low/intermediate/high（IKWG 明确中间档不可用）

> **对数据集构建的强制建议**：每条标签都要记录元组 **(biomarker, cancer, assay/clone, guideline+year, A/B/C 类型, 精确 cut-points, 染色部位)**。**"3+" 这个数字本身不是 ground truth，这个元组才是。**

---

## 4. Part 4 — H-score / Allred / IRS / 0-1-2-3+ 全面对比

### 4.1 四体系并排

| 属性 | **0/1+/2+/3+（HER2）** | **H-score** | **Allred** | **IRS（Remmele）** |
|---|---|---|---|---|
| 类型 | 有序分类（4 档） | 准连续（0–300，301 个整数） | 有序小整数（0–8，9 档） | 有序小整数（0–12，13 档） |
| 组合方式 | 强度+膜完整性+比例 → 单一标签 | **加权和** Σ(i×Pᵢ) | **相加** 比例(0–5)+强度(0–3) | **相乘** SI(0–3)×PP(0–4) |
| 强度轴 | ✓（弱/中/强） | ✓（权重 1/2/3） | ✓（0–3） | ✓（0–3） |
| 阳性比例轴 | ✓（>10%/≤10% 二值） | ✓（连续 %，权重乘） | ✓（0–5 分箱） | ✓（0–4 分箱） |
| 空间/部位 | 膜（环绕完整性） | 部位由 biomarker 定 | 核（ER/PR） | 部位由 biomarker 定 |
| 动态范围 | 极窄（4 档） | **宽（0–300）** | 窄（0–8） | 中（0–12） |
| 原始出处 | HercepTest / ASCO-CAP | **McCarty 1985/1986** | **Allred 1998** | **Remmele & Stegner 1987** |
| 设计对象 | HER2 | ER（后泛化） | ER/PR 乳腺癌 | ER-ICA 乳腺癌 |
| 官方 cut-off | 指南固定 | **按 biomarker/研究自定**（≥75/≥30/≥50…） | 0,2 阴 / 3–8 阳（受 1% 覆盖） | 0–1 阴 / 2–3 弱 / 4–8 中 / 9–12 强 |
| 自动计算难度 | 中（需膜完整性判定，难） | 低-中（需 3 档分箱） | 低-中 | 低-中 |
| 适合生成模型评价 | 补充指标（临床决策） | **主指标（连续误差）** | 补充（ER/PR 专用） | 少用 |

**原始文献**：
- H-score：**McCarty KS Jr, Miller LS, Cox EB, Konrath J, McCarty KS Sr.** *Estrogen receptor analyses…* **Arch Pathol Lab Med. 1985;109(8):716–721.** PMID 3893381（"histochemical score"）；公式归属常引 **McCarty KS Jr, et al. Cancer Res. 1986;46(8 Suppl):4244s–4248s.** PMID 3524805（"HSCORE"）。`[原文/存疑]` 注：**两篇原文全文未能获取，公式来自 ICCR/CAP 模板与后续文献（Liu 2019 Eq.1、Wen 2024）的一致转述**。
- Allred：**Allred DC, Harvey JM, Berardo M, Clark GM.** *Mod Pathol. 1998;11(2):155–168.* PMID 9504686。临床 cut-off 常引 **Harvey JM, et al. J Clin Oncol. 1999;17(5):1474–1481.**
- IRS：**Remmele W, Stegner HE.** *Pathologe. 1987;8(3):138–140.* PMID 3303008（德文原文，无英文摘要）。
- Quickscore：**Detre S, Saccani Jotti G, Dowsett M.** *J Clin Pathol. 1995;48(9):876–878.* PMID 7490328。

### 4.2 公式与分值

**H-score**（ICCR/CAP 乳腺 ER 模板原文格式）`[指南]`：
```
无信号细胞 %  × 0 = 0
弱信号细胞 %  × 1 = _
中等信号细胞 % × 2 = _
强信号细胞 %  × 3 = _
                 总分 = _        → 0–300（共 301 个取值）
```
- **最大值为什么是 300**：100% 细胞都是 3+ → 3×100 = 300。
- **是连续还是半定量**：两者都有人说。它是 **"准连续加权有序分"**——不是真连续（整数格点），也不是纯有序（差值被当作有意义的量级，这本身是被统计学批评的点）。

**Allred**：
```
Proportion score (A):  0=0% / 1=<1% / 2=1–10% / 3=11–33% / 4=34–66% / 5=≥67%
Intensity score  (B):  0=none / 1=weak / 2=intermediate / 3=strong
Total = A + B   →  0–8      （0 与 2 判阴，3–8 判阳）
```

**IRS（Remmele）**：
```
SI (intensity):  0=none / 1=mild / 2=moderate / 3=intense
PP (proportion): 0=none / 1=<10% / 2=10–50% / 3=51–80% / 4=>80%
IRS = SI × PP   →  0–12     （0–1 阴 / 2–3 弱 / 4–8 中 / 9–12 强）
```
> **常见误用**：有人把 SI 与 PP **相加**（变成 0–7），有人把强度轴塌成二值——**那已经不是 IRS 了**（Fedchenko 2014）。

### 4.3 关键差异总结

- **H-score vs Allred**：H-score 动态范围更宽（Dabbs 等指出）；Allred 更"粗"但临床落地更早。
- **H-score vs 0/1+/2+/3+**：前者是**加权求和连续量**，后者是**单一决策标签**。H-score 保留"比例"信息，0/1+/2+/3+ 把比例压成 >10% 的二值。
- **Allred/Quickscore 不同名**：ICCR 把它们列为**两套并列的可选体系**，不要混用。

---

## 5. Part 5 — 数字病理如何自动得到这些评分

### 5.1 完整链路

```
RGB IHC 图像（真实 或 生成）
   │
   ├─(1) 背景/白光校正：估计每通道 I₀（空白区 99 分位 或 模态背景）
   ▼
   ├─(2) 光密度转换 OD_c = −log10(I_c / I₀,c)      [Beer–Lambert]
   │        → OD 与染色量【线性】相关，这是所有定量 IHC 的物理基础
   ▼
   ├─(3) 颜色解混 Color Deconvolution:  C = M⁻¹ · OD     [Ruifrok & Johnston 2001]
   │        M 行向量：H = (0.65, 0.70, 0.29)，DAB = (0.27, 0.57, 0.78)
   │        → H 通道 / DAB 通道 / 残差通道
   ▼
   ├─(4) DAB-OD 图像 = 每像素"染色量"（蛋白表达代理量）
   │
   ├──(5a) 逐像素路线                        ├──(5b) 逐细胞路线（推荐）
   │   阈值化 DAB-OD：                       │   核/细胞分割：
   │   · 固定阈值（IHC Profiler）            │   StarDist / HoVer-Net / Cellpose /
   │   · Otsu                                │   QuPath / CellProfiler
   │   · 阴性对照标定（DAB-quant, 0.1%）     │   （先做肿瘤/间质分割：DeepLabv3 等）
   │                                         ▼
   │                                    每个细胞核内的平均 DAB-OD
   │                                         ▼
   │                                    分箱为 3–4 类：
   │                                    阴性 / 1+弱 / 2+中 / 3+强
   │                                    （阈值在专家 ROI 上网格搜索 max macro-F1 后冻结）
   ▼                                         ▼
   └──────────────► 聚合为评分 ◄──────────────┘
        · 阳性率      = (1++2++3+)/总数
        · H-score     = 1·%1+ + 2·%2+ + 3·%3+          (0–300)
        · Allred      = proportion(0–5) + intensity(0–3)
        · HER2 分类   = 0/1+/2+/3+（+ % 完整膜）
        · TPS (PD-L1) = TC(+) / (TC(+) + TC(−))
        · Ki-67 index = % 阳性肿瘤核
```

### 5.2 颜色解混（Color Deconvolution）

**原始文献**：Ruifrok AC, Johnston DA. *Quantification of histochemical staining by color deconvolution.* **Anal Quant Cytol Histol. 2001;23(4):291–299.** PMID 11531144. `[原文]`（已下载并阅读原文）

**数学**（直接来自原文）：
```
Beer–Lambert:   I_c = I₀,c · exp(−A_c · c_c)
光密度:         OD_c = −log10(I_c / I₀,c) = A_c · c_c
混合模型:       y = C · M          （C = 染色量向量，M = 归一化 OD 矩阵）
解混:           C = D · y,   D = M⁻¹
```
原文给出的 3×3 解混矩阵（H/E/DAB）：
```
       1.88  −0.07  −0.60
D  =  −1.02   1.13  −0.48
      −0.55  −0.13   1.57
```
对角线 >1、非对角为负——每个染色通道是三个 OD 通道的**对比增强差分**，不是简单相减。

**关键实践问题**：
- **染色向量估计**：默认 Ruifrok 向量只是起点，不是 ground truth。IHC Profiler 就**重新推导**了 OD 向量（原向量会在互补通道留下残差 → 假阳性分离）。
- **stain matrix 问题 / 批次效应**：解混是线性求逆，**M 错则染色量直接错**。这是色彩归一化的全部动机。
- **饱和**：DAB 过深时，被错误解混到"hematoxylin"通道的信号可达实测 hematoxylin IOD 的 **~65%**。饱和会破坏**所有**色彩分离方法。
- **AEC（红色显色剂）必须用不同向量**，用 DAB 向量处理 AEC 切片是常见严重 bug。
- **对虚拟 IHC 的特有告诫**：生成图的"染色向量"是模型学出来的，**不保证落在物理 OD 锥内**。解混仍能跑，但 DAB-OD 的数值意义取决于生成器的色彩保真度 → **因此必须在评分前先把生成图归一化到固定染色空间**。

**现代替代/配套**：Reinhard 2001（ℓαβ 均值/方差迁移）、Macenko 2009（SVD 估计染色向量，H&E 事实标准）、Vahadane 2016（稀疏 NMF，保结构更好）、StainTools（Python）、`skimage.color.rgb2hed`（用 Ruifrok 矩阵）、ImageJ Colour Deconvolution 2。

### 5.3 光密度（OD）

- **为什么用 OD 不用 RGB**：透射光强是染色浓度的**指数**函数，RGB 对"染色量"非线性；OD 线性。**任何"染色量/表达量/强度档"的说法，本质都是在说 OD。**
- 工作定义：**OD（逐像素逐通道）** / **DAB OD**（解混后 DAB 通道）/ **mean OD = IOD/area** / **IOD（积分光密度）= Σ OD**（= 总染色量，Ruifrok 全文用 IOD 作纵轴）/ **AOD = mean OD**。
- **OD 阈值判阳性**（文献模式：解混 → DAB-OD → 阈值 → 计数）：
  - **IHC Profiler**（Varghese F, et al. *PLoS ONE* 2014;9(5):e96801）`[原文]`——**最经典的 OD 阈值评分工具**。重新优化 OD 向量后，把 DAB 通道像素直方图切成 4 个强度区：
    - High positive (3+)：**0–60**
    - Positive (2+)：**61–120**
    - Low positive (1+)：**121–180**
    - Negative (0)：**181–235**
    - （235–255 = 脂肪/空白，**排除**）
    - 报告：**与病理医师一致率 88.6%，κ = 0.843**；而三位病理医师之间 κ 为 −0.669 / 0.011 / 0.715——**自动 OD 法比人更可重复**。
  - **Liu 2019**（IEEE TMI 38(2):377–388）：RGB → OD（I₀=[255,255,255]）→ H-DAB 解混 → 保留 DAB 通道 → **LAMT（亮度自适应多阈值）** 替代固定阈值。
  - **DAB-quant**（Patel S, et al. *PLoS ONE* 2022;17(7):e0271593）：**NRMB（归一化红减蓝）** 逐像素打分，阈值由**阴性对照切片**标定（默认误差容限 0.1%），组织/空白用 **Otsu**。输出 = **染色组织像素比例** + 强度直方图（**逐像素，非逐细胞**）。
- **对虚拟 IHC 的关键告诫**：OD 阈值**不可跨染色仪/跨生成器迁移**。在生成图上必须**重新标定阈值**——理想是拿一批**真实 IHC + 病理医师标注**做标定。

### 5.4 细胞/核分割 + 逐细胞评分

| 工具 | 文献 | 用途 |
|---|---|---|
| **StarDist** | Schmidt U, et al. MICCAI 2018, LNCS 11071:265–273 | 星凸多边形核检测，圆形核稳健 |
| **HoVer-Net** | Graham S, et al. *Med Image Anal* 2019;58:101563 | 同时分割+分类核类型（上皮/炎性/梭形/其他），MIT 许可 |
| **Cellpose** | Stringer C, et al. *Nat Methods* 2021;18(1):100–106 | 通用流式分割，IHC 核微调效果好 |
| **QuPath** | Bankhead P, et al. *Sci Rep* 2017;7:16878 | 免费可脚本化 WSI 平台，内置染色估计 + 细胞检测（OD 求和）+ 可训练细胞分类 |
| **CellProfiler** | Carpenter AE, et al. *Genome Biol* 2006;7(10):R100 | 模块化流水线 |
| **HALO / Aperio** | 商业（Indica Labs / Leica） | PD-L1 AI 输出 TPS + 逐细胞三类；Ki67 AI 输出 % 阳性（**仅二分类 neg/pos**） |
| **PanNuke** | Gamper J, et al. MICCAI COMPAY 2019, LNCS 11843:11–19 | 泛癌核实例分割+5 类分类数据集 |

**把 DAB 强度分成 3–4 档的三篇直接相关工作**：

**(a) Fauzi et al. 2022 —— ER，Allred，逐细胞 weak/moderate/strong** `[原文]`
> Fauzi MFA, et al. *Allred Scoring of ER-IHC Stained Whole-Slide Images for Hormone Receptor Status in Breast Carcinoma.* **Diagnostics 2022;12(12):3093.**
> 流程：CNN 细胞检测（欧氏距离得分图，阈值 ≥0.2，面积 >240，分水岭分裂）→ HSV 加权色相/明度判阳性（wV<50 阳性；否则 wH<40 阳性）→ **独立 9 层 CNN 把阳性细胞分为 weak/moderate/strong** → Allred = proportion(0–5)+intensity(0–3)。
> 结果：检测 precision 93%/recall 96%；P/N 准确率 95%；**WMS（弱中强）准确率 88%**；切片级 Allred 完全一致 23/40，**治疗建议一致 82.5%（33/40）**。代码未公开。

**(b) Bannah et al. 2026 —— PR，逐细胞 4 类 + Allred** `[原文]`
> Bannah H, et al. *AI-Driven Breast Cancer Nuclei Segmentation, Classification, and Scoring in PR-IHC Images.* **Diagnostics 2026;16(9):1295.**（数据集 PR-IHC-40x，IEEE DataPort DOI 10.21227/tag3-k180）
> 流程：微调 **Cellpose** 分割核 → **DAB 通道解混**（反转使越深越强）→ 核内平均 DAB 强度 → **三个标定阈值**（专家 ROI 上网格搜索 max macro-F1 后冻结）切成 **negative/weak/moderate/strong** → **Allred**。
> 结果：分割 F1 0.85 / IoU 0.74；**4 类分类 macro-F1 ≈ 0.95**（跨数据集 ER F1 0.91）；切片级 Allred 完全一致 **70%**、±1 内 **86%**、治疗一致 **94%**。**误分类集中在 weak/moderate 边界。** 代码可申请（数据集公开）。

**(c) Wen et al. 2024 —— 逐像素 4 档 DAB → H-score**（见 5.5）

> **设计取舍**：**逐像素**（快，兼容 IHC Profiler 式直方图阈值，但丢失细胞身份）vs **逐细胞**（需分割，匹配病理医师判读方式，**是 0/1+/2+/3+ 与 Allred/H-score 的必需前提**）。**你要做分类评分 → 必须逐细胞。**

### 5.5 自动化 H-score

```
H-score = 1 × (% 弱染细胞) + 2 × (% 中等染细胞) + 3 × (% 强染细胞)      → 0–300
```
自动化论文的区别只在于百分比是**按像素**还是**按细胞**。

| 论文 | 年份 | Biomarker | 方法 | 输出 | 代码 |
|---|---|---|---|---|---|
| **Liu et al., IEEE TMI 38(2):377–388** | 2019 | ER, p53, PgR | OD → H-DAB 解混 → LAMT → 2×U-Net → RAM-CNN 回归 | 连续 H-score | ❌ |
| **Wen et al., Mod Pathol 37(2):100398** | 2024 | 通用 IHC | 仅用 hematoxylin 训练区域识别模型（像素准确率 0.92–0.99）→ **逐像素 DAB 分 4 档** → H-score | H-score | ❌ |
| **Yin et al., Technol Cancer Res Treat 25:15330338251407734（AutoIHC）** | 2026 | MHC-I（乳腺） | MoCo-SM（肿瘤/间质）+ Triple UNet（核）+ VGG16Regression（H-score） | H-score | **✅ github.com/YinTuo/AutoIHC** |

**两个"对齐人类"的关键数字**（审稿人最认的形式）：
- **Liu 2019**：RAM-CNN **MAE 21.33, SD 29.14, CC 0.95**，而**病理医师之间** MAE 20.63, SD 30.55, CC 0.95 → **达到人际一致性**。
- **AutoIHC 2026**：Spearman ρ = **0.84（95% CI 0.77–0.89）**（100 张专家标注 WSI），**病理医师之间** ρ = 0.84（0.63–0.94），SOTA ρ = 0.78 → **匹配人际变异**。

**QuPath 自建 H-score 路线**（可复现、免费）：
- Pixel H-score 脚本：`github.com/elijahedmondson/QuPath-scripts` → `Pixel H-score.groovy`
- 细胞检测 + high/medium/low 分类 → H-score
- headless IHC/DAB 阳性率流水线：`github.com/baiseraku/qupath-ihc-positive-rate`

### 5.6 六条"决定评分是否可信"的设计决策

1. **解混前先归一化**：把生成 IHC 用 Macenko/Vahadane 映射到真实 IHC 参考染色空间，否则 DAB-OD 处于生成器专属色彩基。
2. **阈值必须锚定在物理尺度**：DAB-OD 的分档阈值用**真实 IHC + 病理标注**标定，**绝不能在生成图上拟合**。
3. **要 0/1+/2+/3+ 或 Allred → 必须逐细胞**；逐像素只适合面积/H-score 类读数。
4. **先分割肿瘤 vs 间质**：所有高性能系统（Wu 2022、Ito 2024、AutoIHC、Fauzi）都把评分门控在肿瘤细胞上，混入间质会污染分数。
5. **报告必须对照人类基线**：把"自动 vs 病理"的差距与"病理 vs 病理"的差距并列（Liu：0.95 vs 0.95；AutoIHC：0.84 vs 0.84）。
6. **预期误差源在 weak/moderate 边界**：Fauzi、Bannah 都报告误分类集中在此；HER2 竞赛也发现 **2+ 对人和机器都最难**。

---

## 6. Part 6 — 已有虚拟染色论文如何评价蛋白表达（本调研核心）

### 6.1 直接回答

**是的——少数论文确实做了超出像素的蛋白表达评价，分三个层次；但没有任何一篇在生成 IHC 上计算经典 H-score 或 Allred。**

**三个层次**：
1. **染色/光密度层（最常见）**：颜色解混出 DAB 通道，比较生成与真实的 DAB-OD 图/直方图（**IOD、mIOD、DAB 通道 Pearson-R、DAB 直方图 JSD**）。
2. **biomarker 评分层（圣杯，少）**：在生成 IHC 上算临床评分（**HER2 0/1+/2+/3+、Ki-67 index %、ER/PR 阳性核 %、阳性细胞比例、task-driven "semantic fidelity"**），与真实 IHC 比。
3. **病理医师层（常见，但多为"像不像/质量可接受吗"，而非"biomarker 判读对不对"）**：盲法阅片、visual Turing test、染色质量分级、下游分类器。

### 6.2 主表

| 论文 | 年 | 会议/期刊 | 生成染色 | 组织/癌种 | 评价指标 | 蛋白表达层评价? | 病理医师评价? | 统计方法 | 来源 |
|---|---|---|---|---|---|---|---|---|---|
| **Bai et al.（Ozcan 组）** | 2022 | BME Frontiers | 自发荧光→**HER2 IHC** | 乳腺 | PSNR/SSIM/SSIM_DAB + 核/膜特征（核计数、膜 AUC、连通性） | **✅** 膜/核染色特征；HER2 分数排序 | **✅ 3 位乳腺病理医师盲法 HercepTest 0/1+/2+/3+ 分级** | 混淆矩阵（虚拟 22 正确 vs 真实 19）；双侧 χ²；配对单侧 t 检验 | spj.science.org/doi/10.34133/2022/9786242 |
| **Martino et al.** | 2024 | J Pathol Inform | H&E→**Ki-67 IHC** | 口腔鳞癌 TMA（175 例，**同片重染**） | 病理医师 likelihood test；**QuPath 阳性率定量**；Ki-67 cut-off | **✅** QuPath 阳性 %，5/10/15% 三阈值，PPV | ✅ 病理医师仅 ~50% 能识别合成片 | "remarkable agreement"；高 PPV | S2153353923001682 |
| **Peng et al.（TDKstain）** | 2024 | MICCAI | H&E→**HER2 IHC** | 乳腺（RegH2I，2592 配对） | PSNR/SSIM/FID/DISTS + 核密度误差 + **膜染色强度误差（按 HER2 分数）** + **下游 4 类膜强度分类** | **✅** 膜强度 4 类 = HER2 评分 | ❌（无阅片，但有 task-specific 域知识分析） | ResNet50 **ACC 0.7263/F1 0.6795（生成）vs 0.7228/0.7298（真实）vs 0.4246（H&E）** | papers.miccai.org/miccai-2024/051-Paper3227.html；代码 github.com/balball/TDKstain |
| **Chen et al.（PSPStain）** | 2024 | MICCAI | H&E→**HER2 IHC** | 乳腺（BCI + MIST_HER2） | PSNR/SSIM + **IOD、mIOD、DAB 通道 Pearson-R（FOD）** | **✅** 明确定义为"评估与蛋白表达水平的病理相关性，而非仅阳性面积" | ❌ | BCI-HER2 Pearson-R **0.7553**；MIST 0.8303 | arXiv:2407.03655；代码 github.com/ccitachi/PSPStain |
| **Chen et al.（PGVMS）** | 2026 | IEEE TMI | H&E→**多重 IHC**（HER2/ER/PR/Ki67 + PD-L1 等） | 乳腺/结肠/肝/NPC/HNSCC | PSNR/SSIM（**自称非决定性**）+ **IOD、Pearson-R、累积 OD 曲线** + FID/DISTS + CONCH-FID + **OD 阈值下游分类** + 病理医师 1–5 评分 | **✅** 逐 marker IOD/Pearson-R；OD 阈值分类 | **✅** 病理医师 1–5（定位/异质性/强度） | HER2 4 类 acc 0.617；ER 0.772；PR 0.818；Ki67 0.740；**模糊实验证明 PSNR↑ 而生物学保真度↓** | arXiv:2602.23292；代码 github.com/ccitachi/PGVMS |
| **Ma et al.（DSFF-GAN）** | 2024 | Comput Biol Med | H&E→**Ki-67 IHC** | 子宫内膜癌 + MIST | SSIM/PSNR/CSS + **生成与参考 Ki-67 的"蛋白表达水平"差异** + 阳性区域标签 | **✅** 区域级阳性/阴性比较 | ✅ 两位病理医师逐 patch 量化阳性细胞比例 | "偏差最小、变异最低" | S0010482524001306；代码 github.com/YihaoMa0512/DSFF-GAN |
| **Pati et al.（VirtualMultiplexer）** | 2024 | **Nature Mach Intell** | H&E→**多重 IHC**（AR/NKX3.1/ERG/p53/CD44/CD146） | 前列腺（EMPaCT TMA→WSI） | FID/CSS + **visual Turing test** + 染色质量分级 + **细胞级阳性/阴性强度分布一致性** + 下游生化复发预测 | **部分** 细胞级强度分布与可分性（非临床评分） | **✅** 4 位专家（3 前列腺病理+1 病理医师）Turing test | 敏感性 **52.1%**、特异性 **54.1%**（随机≈50%）；虚拟可接受 70.7% vs 真实 78.3% | nature.com/articles/s42256-024-00889-5 |
| **Yellapragada, Graikos et al.（PixCell）** | 2025 | arXiv | H&E→**IHC**（HER2/ER/PR/Ki67） | 乳腺（MIST、HER2Match） | FID/FHD/FVD/CLIP-FID + **wF1、mF1、Cohen κ、加权 κ、MCC** + 病理 1–3 评分 | **✅（ER/PR/Ki-67）** DeepLIIF 阳性核 % + 临床阈值（ER ≥10%、PR >1%、Ki67 >30%）；**HER2 无数值评分** | ✅ 2 位病理医师盲法 5 项 1–3 评分；亚型分类 94.4% 一致 | Cohen's κ、加权 κ、MCC；95% Wilson CI | arXiv:2506.05127；代码 github.com/cvlab-stonybrook/PixCell |
| **Liu et al.（Star-Diff）** | 2025 | Comput Biol Med | H&E→**HER2 IHC** | 乳腺（BCI） | SSIM/PSNR（**被批评**）+ **Semantic Fidelity Score (SFS)** = 分类引导的类召回退化 + AUROC | **✅** HER2 诊断一致性（2+/3+ vs 0/1+） | ❌ | 5 px 平移 → SSIM 掉 47.9%；SFS 在形变下仅降 ≤2.1% | S001048252501618X |
| **Zeng et al.** | 2022 | MICCAI | H&E→**PR IHC** | 乳腺 | 图像指标 + **DAB 阈值化的阳/阴性标签一致性** | **✅** PgR 阳性状态 | ✅ 病理医师判定真实 vs 生成阳性一致性 | "与 biomarker 状态高度一致" | Springer 10.1007/978-3-031-16434-7_23 |
| **Zhang et al.（MVFStain）** | 2022 | **Med Image Anal** | H&E→HER2/ER/PgR/Ki67 | 乳腺（+肺/心/血管） | PSNR + HTI + **mIOD（平均积分光密度）** | **✅** mIOD（染色/蛋白量代理） | **✅** 2 位病理医师盲法染色质量 1–3 | "虚拟图与真实几乎相等" | DOI 10.1016/j.media.2022.102520 |
| **Liu et al.（BCI）** | 2022 | CVPRW | H&E→**HER2 IHC** | 乳腺 | PSNR/SSIM | 弱（病理评估 HER2 表达） | ✅ 2 位病理医师 | **<40% 的生成图 HER2 表达与真实一致** | CVPR2022W/.../Liu_BCI... |
| **VihcGAN** | 2026 | Sci Rep | H&E→**CD3/PAX5 IHC** | 犬淋巴结（淋巴瘤） | PSNR/SSIM/FSIM/FSIMc/VSI + **"Stain IoU"**（阳性掩膜）+ **阳性面积比相关** | **✅** 阳性面积比 vs 真实：**R²=0.85（CD3）、0.70（PAX5）** | ✅ 2 位兽医病理专家分级 | 对比 Pix2pix（0.66/0.61）、CycleGAN（0.32/0.12） | 10.1038/s41598-025-32233-1 |
| **Ji et al.** | 2024 | J Med Imaging | H&E→**Ki-67 IHC** | Ki-67 标记指数 | **标记指数（labeling index）验证** | **✅** Ki-67 labeling index | — | 见原文 | 10.1117/1.JMI.11.4.047501 |
| **Dubey et al.（VIMs）** | 2024 | arXiv（MICCAI-DGM） | H&E→CDX2/CK8-18 | 结肠 | MSE/SSIM/FID + **DAB 掩膜 DICE/IoU/Hausdorff** + 病理 FP/FN | 部分（**亚细胞定位正确性**：核 vs 胞浆，而非丰度） | ✅ 2 位病理医师（FP/FN、排序） | DICE/IoU/Hausdorff | arXiv:2407.19113 |
| **DGR** | 2026 | **Nat Commun** | H&E→HER2 IHC | （乳腺） | 图像指标 + **盲法病理判别** | ❌ | ✅ 病理医师区分虚拟/真实准确率 **52%**（= 随机） | 52% | 10.1038/s41467-026-71038-2 |
| **ROSIE** | 2025 | **Nat Commun** | H&E→**多重免疫荧光** | 20 组织/疾病，1600 万细胞 | 细胞表型识别；marker 定位 | **✅** 推断数十种蛋白的表达与定位 | — | 留出验证细胞表型 | 10.1038/s41467-025-62346-0 |

### 6.3 综述/方法学证据（"领域现状"的引用骨架）

| 论文 | 年 | 期刊 | 对评价问题的贡献 | 关键原话 |
|---|---|---|---|---|
| **Klöckner et al.** | 2025 | **npj Digital Medicine** | 综述 60+ H&E→IHC 乳腺模型，并用 **DAB 通道强度直方图的 JSD** 重基准测试 pyramid Pix2Pix / ASP / PSPStain | **"metrics such as FID or KID … fail at assessing the most important characteristic of a generated image, e.g., whether the pathological information from the source is accurately preserved"**；**"no method has emerged that can claim to be the golden standard for assessing the performance of preserving pathological information in virtual staining"**；**"most methods do not provide such [downstream] evaluations"** |
| **Bai et al.** | 2023 | Light Sci Appl | 四层评价分类法（像素指标 / 特征分析 / 病理医师 / 下游 DNN） | "algorithmic scores cannot always accurately reflect the diagnostic value" |
| **Latonen et al.** | 2024 | Trends Biotechnol | 主张计算评估与组织学评估都需要 | "optimizing pixelwise metrics does not guarantee satisfactory histology in the output" |
| **arXiv 2508.00164** | 2025 | arXiv | 系统研究虚拟染色对下游任务是否真有帮助 | **"In most reported studies, virtually stained images have been assessed only using traditional image quality measures such as structural similarity or signal-to-noise ratio"** |
| **Wang et al.（PaPIS）** | 2025 | arXiv | 提出病理感知的感知指标 | "conventional FR-IQA metrics often fail to accurately assess the diagnostic quality of virtual staining images" |

### 6.4 一个必须引用的"认识论警告"

Klöckner 2025 指出 H&E→IHC 的**根本假设**本身可能不成立：

> **"Pathologists cannot assess whether a cell is expressing HER2 just based on its appearance in an H&E image. Thus … it must be assumed that there are hidden patterns … This fundamental assumption is not necessarily true."** `[二手]`

**这对你的研究极其重要**：H&E→IHC 的可行性建立在"形态学隐含表达信息"这一**未经严格验证**的假设上。你在论文的 limitation 里应当明确写出来，并把它转化为**研究动机**——"我们不仅要比像素，还要检验这个隐含信息是否真的被恢复到了表达层面"。

### 6.5 仍然缺失的东西（你的机会）

1. **没有任何虚拟染色论文在生成 IHC 上算经典 H-score 或 Allred。**（H-score 论文存在，但都是**量化真实 IHC**，不是评价虚拟染色。）IOD/Pearson-R 只是代理量，不是临床评分。
2. **绝大多数论文只报像素/感知指标。**
3. **没有领域级蛋白表达保真度基准。**
4. **病理医师研究多为"真实性/质量"，而非"表达正确性"**——只有少数（Bai 2022、Zeng 2022、Liu/BCI 2022、Martino 2024、Ma 2024）问"biomarker 判读对不对"。
5. **Ki-67 服务得最好**（Martino、Ma、Ji、PixCell）；**HER2 第二**（Bai、Peng、Star-Diff、BCI）；**ER/PR/PD-L1 在生成图上的表达层验证最少**。
6. **配准问题是最大混淆因素**：连续切片数据集（BCI、MIST）**无法支持**像素/细胞级表达评分；**同片重染**（Martino、HER2Match）才能。Klöckner 2025 明确呼吁更多此类数据集。
7. **没有工作验证"生成的 DAB 强度是否定量追踪真实蛋白丰度"**（例如对照生化或 mIF ground truth）——只对照了另一张 IHC。

---

## 7. Part 7 — 0/1+/2+/3+ 能不能用于 H&E→IHC

**不能简单回答"能"或"不能"。** 分情况：

### 7.1 适用条件（全部满足才可用）

1. **目标 biomarker 必须有官方 0/1+/2+/3+ 判读标准**——实际只有 **HER2（乳腺/胃）**、**Claudin-18.2（2+/3+）**、**c-MET（新兴）**。
2. **染色部位必须匹配**——HER2 只能看膜，且乳腺癌要求完整环绕。
3. **数据集必须支持细胞级判读**——**同片重染（re-stained）或近完美配准**的配对，不能用连续切片。
4. **必须有病理医师共识标注作为参考标准**，且报告"自动 vs 病理"与"病理 vs 病理"两个差距。
5. **必须先把生成图归一化到固定染色空间**再判读。

### 7.2 不适用条件

- 目标 biomarker 是 **ER/PR**（官方输出是百分比，不是 0–3+）；
- 是 **Ki-67**（官方明确不看强度）；
- 是 **PD-L1**（是 TPS/CPS 百分比，不是强度档）；
- 是 **p53**（模式判读）；
- 是 **MMR/PTEN**（二元）；
- 数据集是**连续切片**（无法细胞级配对）。

### 7.3 优点

- **直观、医学意义明确、易解释**：可以直接说"生成的 IHC 在 X% 的病例上给出与真实一致的临床分级"。
- **可关联临床决策**：能算"治疗建议一致率"（Fauzi 82.5%、Bannah 94% 就是这么报的）。
- **易转成分类指标**：accuracy / macro-F1 / 加权 κ / 混淆矩阵，审稿人熟悉。
- **有现成的自动判读文献可对标**（Pedraza 2024、HER2 竞赛、Her2Net、Qaiser DRL）。

### 7.4 缺点（必须写进论文）

- **biomarker-specific**：只对 HER2 等少数蛋白成立，**不可泛化**。
- **主观性极强**：Robbins 2023 四分类 OPA 仅 **28.8%**，1+ 一致率 **0.98%**。**标签噪声是硬上限。**
- **阈值敏感**：>10%/≤10% 的边界上，微小生成差异就翻档。
- **离散、丢信息**：4 档把连续表达量压成 4 个值，无法刻画"总体接近但分布不同"。
- **对空间信息表达力有限**：同一切片内不同区域的表达异质性被平均掉。
- **需要膜完整性判定**：生成模型很难保证"完整环绕"这一几何属性，判读器必须显式建模。

### 7.5 结论

> **0/1+/2+/3+ 可以作为 H&E→IHC 的"补充/临床决策层"指标，但必须满足：目标蛋白有官方标准（HER2）、染色部位匹配（膜）、数据集同片重染、有病理医师共识、且报告对照人类基线。它不能作为通用主指标。**

---

## 8. Part 8 — H-score 能不能用于 H&E→IHC

### 8.1 适用条件

1. **目标 biomarker 的染色部位明确**（核/膜/胞浆），且你能在生成图上正确定位该部位。
2. **能建立逐细胞（或至少逐像素）的 3 档强度分箱**，且阈值锚定在真实 IHC。
3. **参考标准可用 H-score 或可转成 H-score 的标注**（ER/PR 官方报告含强度 + 百分比，可推导；HER2 也可算 H-score 作为研究量）。
4. **生成图色彩保真度足够**——否则 DAB-OD 不可比（这是最大风险）。

### 8.2 优点

- **准连续（0–300）**：动态范围远大于 Allred（0–8）与 4 档分类；能刻画"总体接近"。
- **通用算术框架**：公式与生物学无关，可跨蛋白套用（阈值仍按蛋白定）。
- **适合回归型评价**：可直接算 **H-score MAE**、**Spearman ρ**、**ICC**——天然适配生成模型的连续误差分析。
- **已有自动化先例可对标**：Liu 2019（CC 0.95 = 人际一致）、Wen 2024、AutoIHC（ρ 0.84 = 人际一致）。
- **可分解**：H-score 拆开就是"弱/中/强 三个百分比"，可以进一步诊断"错在弱档还是强档"。

### 8.3 缺点

- **仍是 IHC 代理量，不是真实蛋白丰度**（见 Part 9 的特别要求 2）。
- **依赖强度分箱的 3 个阈值**——阈值不稳则 H-score 不稳；且阈值是**染色体系相关**的，跨数据集不可迁移。
- **对空间异质性不敏感**：全片平均 H-score 相同，空间分布可以完全不同（见 Part 9 空间部分）。
- **对生成图的色彩漂移敏感**：生成器可能整体偏色，导致 H-score 系统性偏移，而图像指标看不出来。
- **无官方 cut-off**：H-score 的临床意义依赖研究者自定阈值（(C) 类问题）。

### 8.4 结论

> **H-score 更适合作为 H&E→IHC 的"主指标（表达层）"**：连续、可回归、可对齐人际一致性、有自动化先例。但必须与图像指标、染色指标、以及（对 HER2）分类指标组合使用，且必须显式声明"它衡量的是染色代理量，不是蛋白丰度"。

---

## 9. Part 9 — 我应该如何设计实验评价（可执行 pipeline）

### 9.1 三层评价体系

```
Virtual IHC Evaluation
│
├── Level 1 — Image-level（图像层）
│     PSNR / SSIM / LPIPS / MAE / FID（仅作基线，不作主证据）
│
├── Level 2 — Stain-level（染色层）
│     Color Deconvolution → DAB OD
│     · DAB-OD MAE / IOD / mIOD
│     · DAB 直方图 JSD
│     · DAB 通道 Pearson-R / SSIM
│
└── Level 3 — Protein-expression-level（蛋白表达层）
      · H-score MAE / ICC / Spearman ρ        ← 主指标
      · 分类评分 0/1+/2+/3+（HER2）→ accuracy / macro-F1 / 加权 κ   ← 补充指标
      · 阳性细胞比例差（positive-cell ratio Δ）
      · 空间一致性（patch-level / cell-level concordance）  ← 增强指标
      · 病理医师一致性（blinded reader study, weighted κ）
```

### 9.2 完整可执行 pipeline

```
              ┌─────────────────────────────────────────────┐
  GT IHC ────►│ 0. 染色归一化（Macenko/Vahadane → 参考空间） │
              └───────────────────┬─────────────────────────┘
                                  ▼
              ┌─────────────────────────────────────────────┐
              │ 1. 颜色解混（Ruifrok H-DAB）                 │
              │    2. OD 转换 → DAB-OD 图                    │
              └───────────────────┬─────────────────────────┘
                                  ▼
              ┌─────────────────────────────────────────────┐
              │ 3. 肿瘤/间质分割（门控到肿瘤区域）            │
              │ 4. 核/细胞分割（StarDist / Cellpose / QuPath）│
              └───────────────────┬─────────────────────────┘
                                  ▼
              ┌─────────────────────────────────────────────┐
              │ 5. 逐细胞平均 DAB-OD → 4 档分箱               │
              │    阈值：在【真实 IHC + 病理标注】上标定后冻结 │
              └───────────────────┬─────────────────────────┘
                                  ▼
              ┌─────────────────────────────────────────────┐
              │ 6. 聚合：H-score / 阳性率 / HER2 分类 / 空间图│
              └───────────────────┬─────────────────────────┘
                                  ▼
                        H_GT, S_GT
                                  │
   Virtual IHC ──►【同一套 frozen 参数，逐字复用】──► H_Pred, S_Pred
                                  │
                                  ▼
        ΔH = |H_GT − H_Pred| ;  ΔS = S_Pred vs S_GT
        + accuracy / macro-F1 / 加权 Cohen's κ / Spearman ρ / MAE
```

> **铁律：从 GT 和 Pred 提取评分时，必须使用完全相同的 frozen 参数（染色归一化目标、解混矩阵、分割模型、分箱阈值）。** 任何"为生成图单独调参"都会让指标失去意义。

### 9.3 关键实现细节

| 环节 | 推荐做法 | 理由 |
|---|---|---|
| 染色归一化 | Macenko 或 Vahadane，目标 = 真实 IHC 训练集统计 | 消除生成器专属色彩基 |
| 解混 | Ruifrok H-DAB 矩阵，或按数据集重估 | DAB-OD 是物理量 |
| 肿瘤门控 | 肿瘤/间质分割（DeepLabv3 或病理标注掩膜） | 间质污染分数 |
| 分割 | StarDist / Cellpose / QuPath（选一个并固定） | 逐细胞是分类评分前提 |
| 分箱阈值 | 在真实 IHC 专家 ROI 上网格搜索 max macro-F1 → **冻结** | 避免在生成图上拟合 |
| 参考标准 | 病理医师共识（≥2 位，分歧仲裁） | 单医师标签噪声过大 |
| 统计 | 报告"自动 vs 病理"与"病理 vs 病理"两个差距 | 审稿人唯一接受的形式 |
| 不确定性 | bootstrap CI / 多种子（≥5 seeds） | 生成模型方差大 |

---

## 10. Part 10 — 推荐的评价指标组合

### 10.1 Minimal（最小可用集，有医学意义）

| 层 | 指标 | 说明 |
|---|---|---|
| Image | **PSNR, SSIM, LPIPS** | 基线，必须报，但**不能作为主结论** |
| Stain | **DAB-OD MAE** | 染色量层面的直接误差（比 RGB 有意义） |
| Expression | **H-score MAE** | 主指标：连续表达层误差 |
| Expression | **Weighted Cohen's κ**（HER2 分类） | 补充：临床决策一致性 |

> **Minimal 的逻辑**：一个图像指标 + 一个染色指标 + 一个连续表达指标 + 一个分类决策指标。四者缺一不可，且**主结论应落在 H-score MAE 与加权 κ 上**。

### 10.2 Enhanced（增强集）

| 层 | 指标 | 依据 |
|---|---|---|
| **Image** | PSNR, SSIM, LPIPS, **FID/DISTS**, **CONCH-FID**（病理基础模型嵌入） | PGVMS 2026 用 CONCH-FID |
| **Stain** | DAB-OD MAE, **IOD 相对偏差**, **mIOD 偏差**, **DAB 直方图 JSD**, **DAB 通道 Pearson-R** | PSPStain（IOD/mIOD/Pearson-R）、Klöckner 2025（JSD）、MVFStain（mIOD） |
| **Expression** | **H-score MAE / ICC / Spearman ρ**；**阳性细胞比例差**；**分档 macro-F1**；**加权 κ**；**治疗建议一致率** | Liu 2019、AutoIHC、Fauzi（治疗一致率）、Bannah |
| **Spatial** | **patch-level H-score 相关**；**cell-level 阳性/阴性分类一致性**；**局部（local）H-score 图相关性**；阳性细胞空间分布的地球移动距离（EMD）或 JSD | VirtualMultiplexer（细胞级强度分布）、VihcGAN（Stain IoU）、空间一致性文献 |
| **Human** | **盲法病理医师阅片**：分级一致性 + **weighted κ** + **visual Turing test 准确率** | Bai 2022、VirtualMultiplexer、DCR |
| **Downstream** | 用虚拟 IHC 训练/推理临床任务（如 HER2 分类器），与真实 IHC 对比 | TDKstain（ACC 0.7263 vs 0.7228）、Star-Diff（SFS） |

### 10.3 哪些指标"真的有文献依据"

| 候选 | 有依据? | 依据 |
|---|---|---|
| A. PSNR/SSIM/LPIPS | ✅ 但被明确批评为不足 | Klöckner 2025、arXiv 2508.00164、Star-Diff |
| B. DAB-OD 差 | ✅ | PSPStain、PGVMS、MVFStain、Klöckner（JSD） |
| C. H-score MAE | ✅（作为**真实 IHC 量化**有先例；作为**虚拟染色评价**是新贡献） | Liu 2019、Wen 2024、AutoIHC |
| D. 0/1+/2+/3+ 分类准确率 | ✅ | Bai 2022、Pedraza 2024、HER2 竞赛 |
| E. Weighted Cohen's κ | ✅ | TUPAC16（quadratic weighted κ）、PixCell |
| F. 阳性细胞比例差 | ✅ | Ma 2024、Martino 2024、VihcGAN（阳性面积比） |
| G. 空间相关 | ✅（细胞级一致性有先例；"spatial concordance"作为命名指标是新贡献） | VirtualMultiplexer、VIMs、VihcGAN |

---

## 11. Part 11 — 最终推荐的论文实验表格（只设计表头，不填数值）

**Table 1. 图像层 + 染色层 + 表达层主结果**

| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ | DAB-OD MAE ↓ | IOD Bias ↓ | H-score MAE ↓ | H-score ICC ↑ | Expression Acc. ↑ | Macro-F1 ↑ | Weighted κ ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pix2Pix (baseline) | | | | | | | | | | |
| CycleGAN | | | | | | | | | | |
| ASP / MIST | | | | | | | | | | |
| PSPStain | | | | | | | | | | |
| TDKstain | | | | | | | | | | |
| **Ours** | | | | | | | | | | |
| *Pathologist vs Pathologist (reference ceiling)* | — | — | — | — | — | | | | | |

**Table 2. 空间一致性**

| Method | Patch-level H-score ρ ↑ | Cell-level Pos/Neg Agreement ↑ | Local H-score MAE ↓ | Positive-cell Ratio Δ ↓ | Spatial EMD ↓ |
|---|---:|---:|---:|---:|---:|
| … | | | | | |
| **Ours** | | | | | |

**Table 3. 病理医师盲法阅片**

| Method | Grading Concordance (%) | Weighted κ (95% CI) | Turing-test Accuracy (%) | Stain-quality Score (1–5) |
|---|---:|---:|---:|---:|
| Real IHC (reference) | | | — | |
| … | | | | |
| **Ours** | | | | |

**Table 4. 消融（可选）**

| Variant | PSNR | SSIM | H-score MAE | Weighted κ |
|---|---:|---:|---:|---:|
| w/o protein-aware loss | | | | |
| w/o stain normalization | | | | |
| full model | | | | |

> **填表纪律**：所有数字来自**同一套 frozen 评分参数**；每个方法跑 **≥5 个随机种子**，报 **mean ± std**；分类指标报 **95% CI**（bootstrap 或 Wilson）。

---

## 12. Part 12 — 最终结论（回答 6 个问题）

### Q1. 0/1+/2+/3+ 到底是什么？

它是 **HER2 蛋白免疫组化的四档有序半定量分类评分**（biomarker-specific four-category ordinal IHC score），由 ASCO/CAP 指南（2007→2013→2018→2023）定义于乳腺癌，胃癌有**另一套同名定义**。判定依据是 **(膜染色强度) × (膜完整性 complete/circumferential vs incomplete) × (阳性肿瘤细胞比例 >10%)** 的三维联合判读，**只看膜**。它不是"强度分级"，也不只是"三级"。

### Q2. 是否是通用 IHC 评分体系？

**否。** Fedchenko 2014 明确指出**不存在被广泛接受的 IHC 评分体系**，只有 HER2/ER/PR 有"golden standard"。真正通用的是**计算框架**（H-score / IRS / Allred / Quickscore），不是 0/1+/2+/3+。

### Q3. 哪些蛋白最适合？

按你的用途排序：
1. **HER2（乳腺癌）** —— 唯一有成熟 0/1+/2+/3+ 官方标准 + 丰富自动判读文献 + 已有虚拟染色先例（Bai 2022、TDKstain）。**首选。**
2. **HER2（胃癌）** —— 同族但定义不同，注意区分。
3. **Ki-67** —— 官方用连续百分比（不用强度档），但虚拟染色验证最多（Martino、Ma、Ji），**适合做"百分比一致性"而非 0/1+/2+/3+**。
4. **ER / PR** —— 官方用百分比（Allred/H-score 可选），**适合 H-score/Allred，不适合 0/1+/2+/3+**。
5. **PD-L1 / p53 / MMR** —— **不适合 0/1+/2+/3+**（分别是 TPS/CPS、模式、二元）。

### Q4. H-score 与 0/1+/2+/3+ 哪个更适合虚拟 IHC？

- **主指标 → H-score**（连续、可回归、动态范围宽、有自动化先例、可对齐人际一致性）。
- **补充指标 → 0/1+/2+/3+**（只在目标蛋白有官方标准时，如 HER2；用于回答"临床决策对不对"）。
- **两者不是二选一**：H-score 回答"表达量还原得多准"，0/1+/2+/3+ 回答"临床分级判对没有"。**推荐双轨。**

### Q5. 有没有已有虚拟染色论文这么评价？

**有，但稀疏且不完整。** 已有：Bai 2022（HER2 病理盲法 0/1+/2+/3+ + χ²）、Martino 2024（Ki-67 QuPath 阳性率 + 临床阈值 + 病理 likelihood test）、TDKstain 2024（生成图训练 HER2 4 类分类器）、PSPStain 2024 / PGVMS 2026（IOD/Pearson-R/DAB-OD）、Ma 2024（Ki-67 阳性细胞比例）、VirtualMultiplexer 2024（细胞级强度分布 + Turing test）、PixCell 2025（ER/PR/Ki-67 临床阈值 + κ/加权 κ）。
**但没有一篇在生成 IHC 上计算经典 H-score 或 Allred**，且领域**没有蛋白表达保真度的基准**。这正是你的空间。

### Q6. 如果我要做 H&E→IHC，怎样建立一个既有医学意义又能自动计算的 protein-expression evaluation pipeline？

**六步**：
1. **选定有官方标准的 biomarker**（首选 HER2；次选 Ki-67 做百分比）。
2. **构建/选择同片重染（re-stained）配对数据集**（不能用连续切片）。
3. **建立 frozen 评分器**：染色归一化 → Ruifrok H-DAB 解混 → OD → 肿瘤门控 → 细胞分割 → 逐细胞 DAB-OD → 4 档分箱（阈值在真实 IHC + 病理标注上标定后冻结）。
4. **对 GT 与 Pred 用同一套 frozen 参数**分别算 H-score 与分类评分。
5. **主指标 = H-score MAE / ICC / Spearman；补充 = 0/1+/2+/3+ accuracy / macro-F1 / 加权 κ；增强 = 空间一致性 + 病理盲法阅片。**
6. **必须报告"自动 vs 病理"与"病理 vs 病理"两个差距**，并 bootstrap 出 CI。

---

## 13. 核心论文固定格式卡片（按要求格式）

> 说明：`Automation` = 自动化程度；`0-3+` = 是否使用 0/1+/2+/3+；`H-score` = 是否使用 H-score；`Code` = 是否有代码。

### 卡片 1
- **Paper**: Bai B, et al. *Label-Free Virtual HER2 Immunohistochemical Staining of Breast Tissue using Deep Learning.* **BME Frontiers 2022;2022:9786242**（arXiv:2112.05240）
- **Year**: 2022
- **Biomarker**: HER2
- **Disease/Tissue**: 乳腺癌，FFPE
- **Scoring System**: Dako HercepTest **0/1+/2+/3+**
- **评分标准**: 3 位乳腺病理医师盲法 WSI 分级
- **Input**: 4 通道自发荧光（DAPI/FITC/TxRed/Cy5），**未染色**组织
- **Method**: cGAN（attention-gated U-Net + CNN 判别器）
- **Output**: 明场 RGB 虚拟 HER2 IHC（~12 s/mm²）
- **Automation**: 全自动生成；判读由人完成
- **0-3+**: **✅**（12 张虚拟 WSI，每档 3 张，均来自留出患者）
- **H-score**: ❌
- **Code**: ✅ github.com/baibijie/HER2-virtual-staining
- **与虚拟染色关系**: 自发荧光→虚拟 IHC（**非** H&E→IHC）
- **能否迁移到 H&E→IHC**: 部分——输入模态不同，但**评价模板（3 病理盲法 HercepTest + 特征级 DAB 分析）可直接迁移**
- **对我的研究价值**: **现存最清晰的"模型有没有把蛋白评分生成对"的范例**——含混淆矩阵、χ² 检验，以及与病理医师独立的核/膜特征分析

### 卡片 2
- **Paper**: Martino F, et al. *A deep learning model to predict Ki-67 positivity in oral squamous cell carcinoma.* **J Pathol Inform 2024;15:100354**
- **Year**: 2024
- **Biomarker**: Ki-67
- **Disease/Tissue**: 口腔鳞癌；4 个 TMA，175 例；**同片先 H&E 后 Ki-67 重染**
- **Scoring System**: Ki-67 阳性率 %，临床阈值 **5% / 10% / 15%**
- **评分标准**: QuPath 定量 + 病理 likelihood test
- **Input**: H&E
- **Method**: Pix2Pix
- **Output**: 合成 Ki-67 IHC
- **Automation**: 自动生成；QuPath 自动定量；病理医师做 likelihood test
- **0-3+**: ❌（连续 % + cut-off）
- **H-score**: ❌
- **Code**: 未说明
- **与虚拟染色关系**: **H&E→IHC，直接对口**
- **能否迁移到 H&E→IHC**: **✅ 直接可迁移**
- **对我的研究价值**: **最接近"临床 biomarker 一致性研究"的范例**——在合成 vs 真实 IHC 上定量 biomarker、检验临床阈值、做病理 indistinguishable 测试

### 卡片 3
- **Paper**: Peng Q, et al. *Advancing H&E-to-IHC Virtual Staining with Task-Specific Domain Knowledge for HER2 Scoring (TDKstain).* **MICCAI 2024**, LNCS 15004:3–13
- **Year**: 2024
- **Biomarker**: HER2
- **Disease/Tissue**: 乳腺癌（RegH2I，2592 配对）
- **Scoring System**: **4 类膜染色强度**（对齐 HER2 判读）
- **评分标准**: 下游 ResNet50 分类器
- **Input**: H&E
- **Method**: GAN + 核密度估计 + 膜染色增强分支（用 DAB/HED 解混）
- **Output**: 虚拟 HER2 IHC
- **Automation**: 全自动
- **0-3+**: **✅ 实质上是**（4 类膜强度）
- **H-score**: ❌
- **Code**: ✅ github.com/balball/TDKstain
- **与虚拟染色关系**: H&E→IHC
- **能否迁移到 H&E→IHC**: ✅
- **对我的研究价值**: **最强"表达层下游"证据**——只用生成 IHC 训练的分类器，HER2 4 类评分能力与用真实 IHC 训练相当（ACC 0.7263 vs 0.7228），而原始 H&E 远差（0.4246）

### 卡片 4
- **Paper**: Chen F, et al. *Pathological Semantics-Preserving Learning for H&E-to-IHC Virtual Staining (PSPStain).* **MICCAI 2024**, 384–394（arXiv:2407.03655）
- **Year**: 2024
- **Biomarker**: HER2
- **Disease/Tissue**: 乳腺（BCI + MIST_HER2）
- **Scoring System**: 无临床评分；用连续 DAB 派生 OD 量
- **评分标准**: IOD / mIOD / DAB 通道 Pearson-R
- **Input**: H&E
- **Method**: ASP 基础 + **Protein-Aware Learning Strategy (PALS)**，从解混得到 **Focal Optical Density (FOD)** 图；多级蛋白感知损失
- **Output**: 虚拟 HER2 IHC
- **Automation**: 全自动
- **0-3+**: ❌
- **H-score**: ❌（用 IOD/mIOD）
- **Code**: ✅ github.com/ccitachi/PSPStain
- **与虚拟染色关系**: H&E→IHC
- **能否迁移到 H&E→IHC**: ✅
- **对我的研究价值**: **明确定义"三个临床相关指标 = IOD、mIOD、DAB Pearson-R"，目的是评估"与蛋白表达水平的病理相关性，而非仅阳性面积"**；并指出 PSNR/SSIM 与高质量虚拟染色不总相关

### 卡片 5
- **Paper**: Chen F, et al. *PGVMS: A Prompt-Guided Unified Framework for Virtual Multiplex IHC Staining with Pathological Semantic Learning.* **IEEE TMI 2026**（arXiv:2602.23292）
- **Year**: 2026
- **Biomarker**: HER2, ER, PR, Ki67（MIST/IHC4BC）+ HepPar1, EBER, CK, PD-L1（私有临床）
- **Disease/Tissue**: 乳腺、结直肠、肝、鼻咽、HNSCC
- **Scoring System**: OD 阈值分类——HER2 4 类（OD 500/2000/5000）；ER/PR 二元（OD 1000）；Ki67 二元（OD 2000）
- **评分标准**: OD 阈值 + 病理医师 1–5
- **Input**: H&E
- **Method**: Prompt-guided（CONCH 视觉语言模型）+ PALS/FOD + prototype consistency
- **Output**: 单模型生成多重虚拟 IHC
- **Automation**: 全自动；标签经病理医师复核
- **0-3+**: ✅（HER2，OD 阈值化）
- **H-score**: ❌
- **Code**: ✅ github.com/ccitachi/PGVMS
- **与虚拟染色关系**: H&E→IHC
- **能否迁移到 H&E→IHC**: ✅
- **对我的研究价值**: **目前最完整的多层评价协议**：PSNR/SSIM（明确降权）+ IOD/Pearson-R/累积 OD + FID/DISTS + CONCH-FID + OD 阈值下游分类 + 病理 1–5；并给出**模糊实验证明 PSNR/SSIM 上升而生物学保真度下降**

### 卡片 6
- **Paper**: Pati P, et al. *Accelerating histopathology workflows with generative AI-based virtually multiplexed tumour profiling (VirtualMultiplexer).* **Nature Machine Intelligence 2024;6:1077–1093**
- **Year**: 2024
- **Biomarker**: AR, NKX3.1, ERG, p53, CD44, CD146
- **Disease/Tissue**: 前列腺癌（EMPaCT TMA→WSI）
- **Scoring System**: 细胞级阳/阴性强度分类（非临床评分）
- **评分标准**: 细胞级强度分布一致性 + 专家 Turing test
- **Input**: H&E
- **Method**: 多尺度 GAN + 邻域/全局/局部一致性损失
- **Output**: 虚拟多重 IHC
- **Automation**: 自动生成；专家做 Turing test/质量评估
- **0-3+**: ❌
- **H-score**: ❌
- **Code**: ✅
- **与虚拟染色关系**: H&E→IHC（多重）
- **能否迁移到 H&E→IHC**: ✅
- **对我的研究价值**: **比较真实与虚拟的"阳性/阴性细胞强度分布"（一致性 + 可分性）**，4 专家 Turing test（敏感性 52.1%、特异性 54.1%），并用虚拟 IHC 做下游生化复发预测——**细胞级表达验证的强模板**

### 卡片 7
- **Paper**: Yellapragada S, Graikos A, et al. *PixCell: A generative foundation model for digital histopathology images.* **arXiv:2506.05127 (2025)**
- **Year**: 2025
- **Biomarker**: HER2, ER, PR, Ki67
- **Disease/Tissue**: 乳腺（MIST、HER2Match）；前列腺
- **Scoring System**: ER ≥10%、PR >1%、Ki67 >30% 阳性核阈值；HER2 无数值评分
- **评分标准**: DeepLIIF 细胞计数 + 临床阈值
- **Input**: H&E
- **Method**: 扩散生成基础模型 + LoRA + rectified-flow 嵌入迁移
- **Output**: 虚拟 IHC（及 H&E）
- **Automation**: 自动；DeepLIIF 计数；病理验证
- **0-3+**: ❌（HER2 未评分）
- **H-score**: ❌
- **Code**: ✅ github.com/cvlab-stonybrook/PixCell
- **与虚拟染色关系**: H&E→IHC
- **能否迁移到 H&E→IHC**: ✅
- **对我的研究价值**: **用 Cohen's κ / 加权 κ / MCC 评估"表达类别标签"**，配合 2 病理盲法质量评分与 94.4% 亚型一致；**诚实暴露了空白：HER2 没有数值评分**

### 卡片 8
- **Paper**: Liu J, et al. *An End-to-End Deep Learning Histochemical Scoring System for Breast Cancer Tissue Microarray.* **IEEE TMI 2019;38(2):377–388**（arXiv:1801.06288）
- **Year**: 2019
- **Biomarker**: ER, p53, PgR
- **Disease/Tissue**: 乳腺 TMA（NPI+ 队列，105 张，2 位病理医师）
- **Scoring System**: **H-score（0–300）**
- **评分标准**: `H = 1×WSN + 2×MSN + 3×SSN`
- **Input**: 真实 IHC TMA（**非虚拟染色**）
- **Method**: OD → H-DAB 解混 → LAMT → 双 U-Net（通用核/肿瘤核）→ ROI → RAM-CNN 回归
- **Output**: 连续 H-score
- **Automation**: 全自动
- **0-3+**: ❌
- **H-score**: **✅**
- **Code**: ❌
- **与虚拟染色关系**: 无（是 IHC 量化方法）
- **能否迁移到 H&E→IHC**: **✅ 作为评分器直接迁移到生成图**
- **对我的研究价值**: **H-score 自动化的黄金标准**——MAE 21.33 / CC 0.95，与**病理医师之间**（MAE 20.63 / CC 0.95）持平。**这就是你要复现的"评分器"**

### 卡片 9
- **Paper**: Yin T, et al. *Fully Automated Stain Quantification Framework for IHC Whole Slide Images in Breast Cancer (AutoIHC).* **Technol Cancer Res Treat 2026;25:15330338251407734**
- **Year**: 2026
- **Biomarker**: MHC-I（乳腺示例）
- **Disease/Tissue**: 乳腺癌 WSI（100 张专家标注）
- **Scoring System**: **H-score**
- **评分标准**: 三模块（肿瘤/间质分割 MoCo-SM + 核分割 Triple UNet + H-score 回归 VGG16Regression）
- **Input**: 真实 IHC WSI
- **Method**: 深度学习三模块级联
- **Output**: H-score（千兆像素 WSI ~2 min / 2×A6000）
- **Automation**: 全自动
- **0-3+**: ❌
- **H-score**: **✅**
- **Code**: **✅ github.com/YinTuo/AutoIHC**
- **与虚拟染色关系**: 无
- **能否迁移到 H&E→IHC**: **✅（且开源，最适合你直接复用）**
- **对我的研究价值**: **唯一公开代码的自动化 H-score 框架**；ρ = 0.84 = 人际 ρ 0.84，**达到人际变异水平**

### 卡片 10
- **Paper**: Klöckner P, Teixeira J, Montezuma D, Fraga J, Horlings HM, Cardoso JS, Oliveira SP. *H&E to IHC virtual staining methods in breast cancer: an overview and benchmarking.* **npj Digital Medicine 2025;8:384**
- **Year**: 2025
- **Biomarker**: HER2, PgR, ER, Ki-67
- **Disease/Tissue**: 乳腺
- **Scoring System**: N/A（综述+基准）
- **评分标准**: 用 **DAB 通道强度直方图 JSD** 重基准测试
- **Input**: H&E→虚拟 IHC 的既有模型（pyramid Pix2Pix / ASP / PSPStain）
- **Method**: 综述 + 重实现基准
- **Output**: 评价方法学
- **Automation**: N/A
- **0-3+**: N/A
- **H-score**: N/A
- **Code**: 依模型而定
- **与虚拟染色关系**: **核心综述**
- **能否迁移到 H&E→IHC**: ✅
- **对我的研究价值**: **你论文 motivation 的最佳单一引用**——它同时给出：(1) 领域评价被像素指标主导；(2) 无金标准；(3) Liu/BCI 的 **<40% HER2 表达一致率**；(4) **"病理医师无法仅凭 H&E 形态判断细胞是否表达 HER2"** 这一根本假设警告

### 卡片 11
- **Paper**: Robbins CJ, et al. *Multi-institutional Assessment of Pathologist Scoring HER2 Immunohistochemistry.* **Mod Pathol 2023;36:100032**
- **Year**: 2023
- **Biomarker**: HER2
- **Disease/Tissue**: 乳腺癌活检（170 例，18 位病理医师，15 家机构）
- **Scoring System**: **0/1+/2+/3+**（四分类）与 0/Low/3+（三分类）
- **评分标准**: 多机构阅片一致性研究
- **Input**: 真实 HER2 IHC
- **Method**: 人工判读一致性统计
- **Output**: OPA / 各档一致率
- **Automation**: 人工
- **0-3+**: **✅**
- **H-score**: ❌
- **Code**: N/A
- **与虚拟染色关系**: 无（但是**标签噪声的定量证据**）
- **能否迁移到 H&E→IHC**: ✅（作为**上限约束**）
- **对我的研究价值**: **给 0/1+/2+/3+ 评价体系设天花板的必引文献**：四分类 OPA 仅 28.8%，1+ 仅 0.98%

### 卡片 12
- **Paper**: Ruifrok AC, Johnston DA. *Quantification of histochemical staining by color deconvolution.* **Anal Quant Cytol Histol 2001;23(4):291–299**
- **Year**: 2001
- **Biomarker**: 通用（H/E/DAB 演示）
- **Disease/Tissue**: 通用
- **Scoring System**: N/A（提供物理基础）
- **评分标准**: OD + 颜色解混（M 矩阵，D = M⁻¹）
- **Input**: RGB 明场
- **Method**: Beer–Lambert → OD → 线性解混
- **Output**: H / DAB / E 的 OD 通道；IOD
- **Automation**: 算法
- **0-3+**: ❌
- **H-score**: ❌
- **Code**: 遗留 NIH Image 宏；现代实现遍布（skimage/QuPath/StainTools）
- **与虚拟染色关系**: 无（但**是你评分链路的第 1 步**）
- **能否迁移到 H&E→IHC**: ✅（**必须**）
- **对我的研究价值**: 一切定量 IHC 的物理基石

---

## 14. 最后一项任务：最适合你的可执行实验方案

**前提假设**：你拥有 Paired H&E / IHC 数据集（**强烈建议选择同片重染或近完美配准的子集**）。

### 14.1 输入

```
真实 H&E  ──┐
            ├─► 你的生成模型 ─► Virtual IHC
GT IHC   ───┘（作为监督/参考）
```

- **GT IHC**：真实配对 IHC（同片重染优先）
- **Virtual IHC**：你的模型输出
- **参考标注**：≥2 位病理医师的独立评分 + 分歧仲裁（用于标定阈值与评估上限）

### 14.2 处理（GT 与 Pred 逐字复用同一套 frozen 参数）

```
              GT IHC                          Virtual IHC
                │                                  │
        ┌───────▼────────┐                ┌────────▼───────┐
        │ 染色归一化      │                │ 染色归一化      │  ← 同一目标（真实 IHC 统计）
        │ (Macenko)      │                │ (Macenko)      │
        └───────┬────────┘                └────────┬───────┘
                ▼                                  ▼
        ┌────────────────┐                ┌────────────────┐
        │ H-DAB 解混 → OD│                │ H-DAB 解混 → OD│  ← 同一解混矩阵
        └───────┬────────┘                └────────┬───────┘
                ▼                                  ▼
        ┌────────────────┐                ┌────────────────┐
        │ 肿瘤/间质门控   │                │ 肿瘤/间质门控   │  ← 同一分割模型
        │ 细胞分割        │                │ 细胞分割        │
        └───────┬────────┘                └────────┬───────┘
                ▼                                  ▼
        ┌────────────────┐                ┌────────────────┐
        │ 逐细胞 DAB-OD  │                │ 逐细胞 DAB-OD  │
        │ → 4 档分箱      │                │ → 4 档分箱      │  ← 同一冻结阈值
        └───────┬────────┘                └────────┬───────┘
                ▼                                  ▼
           H_GT, S_GT                        H_Pred, S_Pred
```

### 14.3 输出

**连续层（主指标）**
```
H_GT  = 1·P1,GT + 2·P2,GT + 3·P3,GT        ∈ [0, 300]
H_Pred = 1·P1,Pred + 2·P2,Pred + 3·P3,Pred  ∈ [0, 300]
ΔH = |H_GT − H_Pred|
```

**分类层（补充指标，仅当 biomarker 有官方标准时，如 HER2）**
```
S_GT   ∈ {0, 1+, 2+, 3+}
S_Pred ∈ {0, 1+, 2+, 3+}
```

**空间层（增强指标）**
```
逐 patch p:  ΔH_p = |H_GT,p − H_Pred,p|         → 空间误差图
逐细胞 c:    agreement_c = 1[class_c,GT == class_c,Pred]
```

### 14.4 统计指标（按依据筛选后的最终清单）

| 指标 | 适用层 | 依据 | 是否推荐 |
|---|---|---|---|
| **H-score MAE** | 表达 | Liu 2019（MAE 21.33）、AutoIHC | ✅ **主** |
| **H-score ICC / Spearman ρ** | 表达 | AutoIHC（ρ 0.84）、Liu（CC 0.95） | ✅ **主** |
| **0/1+/2+/3+ accuracy** | 表达-分类 | Pedraza 2024、HER2 竞赛 | ✅ 补充 |
| **macro-F1** | 表达-分类 | 类别不均衡下必要 | ✅ 补充 |
| **加权 Cohen's κ** | 表达-分类 | TUPAC16（quadratic weighted κ）、PixCell | ✅ **主（分类）** |
| **治疗建议一致率** | 表达-临床 | Fauzi（82.5%）、Bannah（94%） | ✅ 可选（很有说服力） |
| **阳性细胞比例差 Δ** | 表达 | Ma 2024、Martino 2024、VihcGAN | ✅ 补充 |
| **DAB-OD MAE** | 染色 | PSPStain、PGVMS | ✅ 补充 |
| **DAB 直方图 JSD** | 染色 | Klöckner 2025 | ✅ 补充 |
| **patch-level H-score ρ** | 空间 | VirtualMultiplexer 细胞级一致性 | ✅ 增强 |
| **细胞级分类一致性** | 空间 | VirtualMultiplexer、VIMs | ✅ 增强 |
| **病理盲法 weighted κ + Turing 准确率** | 人 | Bai 2022、VirtualMultiplexer、DGR | ✅ 增强 |
| **PSNR / SSIM / LPIPS** | 图像 | 必需但被批评 | ✅ 基线（不作主结论） |

**不推荐照搬的**：单独的 `accuracy`（类别不均衡 + 标签噪声会误导）；未加权 κ（有序类别应用加权）；只报 PSNR/SSIM。

### 14.5 报告纪律（五条）

1. 每个方法 **≥5 个随机种子**，报 **mean ± std**。
2. 所有分类指标报 **95% CI**（bootstrap 或 Wilson）。
3. 必须并列 **"自动 vs 病理"** 与 **"病理 vs 病理"** 两个差距。
4. 必须报告 **ΔH 的分布**（不只均值）——均值接近但分布不同，正是空间一致性问题。
5. 必须显式声明：**H-score / DAB-OD 衡量的是"染色代理量"，不是"蛋白丰度"**。

---

## 15. 特别要求逐条回应

### 15.1 不要把 HER2 当 IHC 通用标准 ✅

本报告全程区分 **biomarker-specific scoring**（Part 2.4/2.5、Part 3）与 **general IHC quantification**（Part 4 的 H-score/IRS/Allred 框架）。HER2 只在 Part 2 作为**重点案例**，并在 Part 3 与 ER/PR/Ki-67/PD-L1/p53 并列对比，明确其**不通用**。

### 15.2 不要把"染色强度"直接等同于"蛋白表达量" ✅

**四者关系与局限**：

| 概念 | 是什么 | 局限 |
|---|---|---|
| **staining intensity（染色强度）** | 单个细胞/像素的 DAB-OD | 受抗体亲和力、固定、抗原修复、显色时间、扫描仪影响；**不等于蛋白量** |
| **protein expression（蛋白表达）** | 目标蛋白在细胞中的实际丰度 | IHC **无法直接测**；只能通过染色代理 |
| **positive-cell percentage（阳性细胞比例）** | 超过阈值的细胞占比 | 依赖阈值；阈值依赖染色体系 |
| **spatial expression（空间表达）** | 表达在组织中的空间分布 | 被全片平均指标抹掉 |

**关键论断**：IHC 是**半定量代理**。同一蛋白量在不同实验室可产生不同强度；反之亦然。**因此 H-score 与 DAB-OD 都是"染色代理量"，不是"蛋白丰度"。** 另外 Klöckner 2025 提醒：**H&E 形态是否真的隐含表达信息，本身是一个未被严格验证的假设**。

### 15.3 必须区分人工评分与自动评分 ✅

本报告始终区分两条路径：
```
Pathologist  →  0/1+/2+/3+            （Part 2、Part 6 的 reader study）
Digital pathology → DAB / OD → 算法评分 （Part 5、Part 8 的自动化）
```
Part 5.6 第 5 条明确要求：**报告"自动 vs 病理"与"病理 vs 病理"两个差距**，二者不可混为一谈。

### 15.4 重点寻找可用于生成模型评价的方法 ✅

对每篇文献都追问了"**这个方法能不能拿来比较 Virtual IHC 与 GT IHC？**"——见 Part 6 主表最后一列、Part 13 每张卡片的"能否迁移到 H&E→IHC"，以及 Part 14 的最终方案。

### 15.5 不要只搜"三级评定" ✅

检索词覆盖：IHC scoring / grading、immunohistochemistry scoring、immunohistochemical score、semiquantitative IHC、protein expression scoring、biomarker scoring、digital pathology IHC quantification、H-score、Allred score、IRS、0 1+ 2+ 3+ IHC、intensity score、DAB quantification、optical density IHC、automated IHC scoring、computational IHC scoring、virtual IHC scoring、virtual staining protein expression、virtual staining biomarker concordance、color deconvolution、Ruifrok、Macenko、Vahadane、QuPath、StarDist、HoVer-Net、Cellpose、HER2 challenge、TUPAC16、TPS/CPS、p53 pattern、MMR、Claudin-18.2、c-MET 等。

---

## 16. 术语对照表（准确术语）

| 你的口语说法 | ❌ 不准确 | ✅ 准确术语 | 说明 |
|---|---|---|---|
| "三级评定" | 三级/3-tier | **四档有序半定量 IHC 评分**（four-category ordinal semiquantitative IHC score） | 实际是 4 档；"tier" 是 ML 圈用词 |
| "0/1+/2+/3+ 通用分级" | 通用 IHC 标准 | **biomarker-specific categorical IHC score**（HER2 专用） | 不通用 |
| "IHC 评分" | — | **semiquantitative IHC score / ordinal score / composite score** | Meyerholz & Beck 2018 的规范表述 |
| "表达量评分" | protein expression score | **stain-based surrogate score**（染色代理评分） | IHC 测的是染色不是蛋白 |
| "强度分级" | intensity grading | **intensity + proportion composite score** | 多数体系同时看比例 |
| "H-score 是连续变量" | continuous | **quasi-continuous weighted ordinal score**（准连续加权有序分） | 0–300 整数格点 |

---

## 17. 参考文献（含链接）

### 指南 / 官方（第一优先级）
1. Wolff AC, et al. **ASCO/CAP HER2 Testing in Breast Cancer: Focused Update.** *J Clin Oncol* 2018;36(20):2105–2122. DOI 10.1200/JCO.2018.77.8738 — https://ascopubs.org/doi/10.1200/JCO.2018.77.8738 （IHC 定义已从原文 PDF 核验）
2. Wolff AC, et al. **ASCO–CAP HER2 Guideline Update 2023.** *J Clin Oncol* 2023;41(22):3867–3872. DOI 10.1200/JCO.22.02864 — https://ascopubs.org/doi/10.1200/JCO.22.02864
3. CAP. **HER2 Testing in Breast Cancer – 2023 Guideline Update**（现行）— https://www.cap.org/cap-guidelines/her2-testing-in-breast-cancer-2023-guideline-update/
4. Bartley AN, et al. **HER2 Testing and Clinical Decision Making in Gastroesophageal Adenocarcinoma.** *J Clin Oncol* 2017;35(4):446–464. DOI 10.1200/JCO.2016.69.4836
5. Allison KH, et al. **Estrogen and Progesterone Receptor Testing in Breast Cancer: ASCO/CAP Guideline Update.** *J Clin Oncol* 2020;38(12):1346–1366. DOI 10.1200/JCO.19.02309
6. Nielsen TO, et al. **Assessment of Ki67 in Breast Cancer: Updated Recommendations From the IKWG.** *J Natl Cancer Inst* 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8487652/
7. **Atlas of PD-L1 for Pathologists.** *J Pers Med* 2022;12(7):1073. https://pmc.ncbi.nlm.nih.gov/articles/PMC9321150/
8. CAP. **Current CAP Guidelines** — https://www.cap.org/protocols-and-guidelines/cap-guidelines/current-cap-guidelines/
9. ICCR. **Estrogen Receptor (ER) protocol v2.1**（含 Allred / H-score 表）— https://www.iccr-cancer.org/wp-content/uploads/2022/09/ICCR-IBreast2.1-ER.pdf

### 评分体系原始文献
10. McCarty KS Jr, et al. *Arch Pathol Lab Med* 1985;109(8):716–721. PMID 3893381（H-score 概念）
11. McCarty KS Jr, et al. *Cancer Res* 1986;46(8 Suppl):4244s–4248s. PMID 3524805（HSCORE）
12. Allred DC, et al. *Mod Pathol* 1998;11(2):155–168. PMID 9504686
13. Harvey JM, et al. *J Clin Oncol* 1999;17(5):1474–1481. PMID 10334533
14. Remmele W, Stegner HE. *Pathologe* 1987;8(3):138–140. PMID 3303008
15. Detre S, et al. *J Clin Pathol* 1995;48(9):876–878. PMID 7490328（Quickscore）
16. Meyerholz DK, Beck AP. *Lab Invest* 2018;98(7):844–855. DOI 10.1038/s41374-018-0057-0（有序评分方法学）
17. Fedchenko N, Reifenrath J. *Diagn Pathol* 2014;9:221. https://pmc.ncbi.nlm.nih.gov/articles/PMC4260254/（"无通用评分体系"）
18. Robbins CJ, et al. *Mod Pathol* 2023;36:100032. https://pmc.ncbi.nlm.nih.gov/articles/PMC10278086/（HER2 判读一致性）

### 数字病理 / 自动评分
19. Ruifrok AC, Johnston DA. *Anal Quant Cytol Histol* 2001;23(4):291–299. PMID 11531144
20. Macenko M, et al. *IEEE ISBI* 2009:1107–1110. DOI 10.1109/ISBI.2009.5193250
21. Vahadane A, et al. *IEEE TMI* 2016;35(8):1962–1971. DOI 10.1109/TMI.2016.2547890
22. Varghese F, et al. **IHC Profiler.** *PLoS ONE* 2014;9(5):e96801. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0096801
23. Patel S, et al. **DAB-quant.** *PLoS ONE* 2022;17(7):e0271593. https://github.com/sarafridov/DAB-quant
24. Liu J, et al. *IEEE TMI* 2019;38(2):377–388. https://arxiv.org/abs/1801.06288
25. Wen Z, et al. **Deep Learning–Based H-Score Quantification.** *Mod Pathol* 2024;37(2):100398. DOI 10.1016/j.modpat.2023.100398
26. Yin T, et al. **AutoIHC.** *Technol Cancer Res Treat* 2026;25:15330338251407734. https://github.com/YinTuo/AutoIHC
27. Bankhead P, et al. **QuPath.** *Sci Rep* 2017;7:16878. https://qupath.github.io
28. Schmidt U, et al. **StarDist.** MICCAI 2018, LNCS 11071:265–273
29. Graham S, et al. **HoVer-Net.** *Med Image Anal* 2019;58:101563
30. Stringer C, et al. **Cellpose.** *Nat Methods* 2021;18(1):100–106
31. Qaiser T, et al. **HER2 challenge contest.** *Histopathology* 2018;72(2):227–238
32. Pedraza A, et al. *Algorithms* 2024;17(3):97. https://www.mdpi.com/1999-4893/17/3/97
33. Fauzi MFA, et al. *Diagnostics* 2022;12(12):3093. https://www.mdpi.com/2075-4418/12/12/3093
34. Bannah H, et al. *Diagnostics* 2026;16(9):1295. https://www.mdpi.com/2075-4418/16/9/1295
35. Veta M, et al. **TUPAC16.** *Med Image Anal* 2019;54:111–121
36. Wu J, et al. *Mod Pathol* 2022;35(3):403–411（PD-L1 AI TPS）
37. Ito H, et al. *Mod Pathol* 2024;37(6):100485（PD-L1 AI TPS）
38. Dawe M, et al. *Lab Invest* 2024（Ki-67 DIA 五法对比）
39. Rewcastle E, et al. *Breast Cancer Res Treat* 2024;207(1):1–12（Ki-67 cut-off）

### 虚拟染色 / 生成模型评价（核心）
40. **Klöckner P, et al. *npj Digital Medicine* 2025;8:384.** DOI 10.1038/s41746-025-01741-9 — https://www.nature.com/articles/s41746-025-01741-9
41. Bai B, et al. *BME Frontiers* 2022;2022:9786242. https://spj.science.org/doi/10.34133/2022/9786242
42. Martino F, et al. *J Pathol Inform* 2024;15:100354. https://www.sciencedirect.com/science/article/pii/S2153353923001682
43. Peng Q, et al. **TDKstain.** MICCAI 2024. https://papers.miccai.org/miccai-2024/051-Paper3227.html ; 代码 https://github.com/balball/TDKstain
44. Chen F, et al. **PSPStain.** MICCAI 2024. https://arxiv.org/abs/2407.03655 ; 代码 https://github.com/ccitachi/PSPStain
45. Chen F, et al. **PGVMS.** IEEE TMI 2026. arXiv:2602.23292
46. Pati P, et al. **VirtualMultiplexer.** *Nature Machine Intelligence* 2024;6:1077–1093. DOI 10.1038/s42256-024-00889-5
47. Yellapragada S, Graikos A, et al. **PixCell.** arXiv:2506.05127 (2025)
48. Liu J, et al. **Star-Diff.** *Comput Biol Med* 2025
49. Zhang R, et al. **MVFStain.** *Med Image Anal* 2022;80:102520
50. Ma Y, et al. **DSFF-GAN.** *Comput Biol Med* 2024;170:108046
51. Liu S, et al. **BCI (Pyramid Pix2Pix).** CVPRW 2022
52. Dubey S, et al. **VIMs.** arXiv:2407.19113 (2024)
53. **VihcGAN.** *Sci Rep* 2026. DOI 10.1038/s41598-025-32233-1
54. Ji C, et al. *J Med Imaging* 2024;11(4):047501（Ki-67 labeling index）
55. **DGR.** *Nat Commun* 2026. DOI 10.1038/s41467-026-71038-2
56. **ROSIE.** *Nat Commun* 2025. DOI 10.1038/s41467-025-62346-0
57. Bai B, et al. *Light: Science & Applications* 2023;12:57（四层评价分类法）
58. Latonen L, et al. *Trends in Biotechnology* 2024;42(10):1177–1191
59. Wang Q, et al. **PaPIS.** arXiv:2507.12624 (2025)
60. **On the Utility of Virtual Staining for Downstream Tasks.** arXiv:2508.00164 (2025)

---

## 18. 证据缺口与不确定性声明

**未能一手核验、需你自行复核的项**：

1. **McCarty 1985/1986 原文全文**未能获取。H-score 公式（`1×P1+2×P2+3×P3`，0–300）由 **ICCR/CAP 模板、Liu 2019 Eq.1、Wen 2024** 一致转述确认，但**未能确认 1985 原文是否印出该公式**。→ 建议引用时写"widely attributed to McCarty et al. (1985/1986)"。
2. **Wen 2024 的完整数值结果**（ICC/相关系数）被出版商反爬拦截，本报告**未引用其具体数字**。
3. **Saha & Chakraborty 2018（Her2Net）** 的架构与数值指标未获取；是否显式输出 0/1+/2+/3+ **未确认**。
4. **HER2-ultralow** 的精确定义来自 2025 国际专家共识（二手转述："faint or barely perceptible, incomplete membrane staining in >0% to ≤10% of tumor cells"）；**建议核对共识原文**。
5. **PD-L1 各阈值** 会随适应症与时间变化（如胃癌 CPS ≥5 vs ≥1 vs ≥10）；**引用前请核对当前 FDA 标签**。
6. **虚拟染色论文的部分数值**（VirtualMultiplexer 的 52.1%/54.1%、PGVMS 的各 marker acc）来自摘要/正文片段，**建议正式引用前核对全文**。
7. **"没有虚拟染色论文计算经典 H-score/Allred"是一个检索的否定结果**，不等于不存在。若你要把它作为 novelty 声明，**建议再用 Google Scholar / PubMed 做一次定向检索确认**。
8. **PGVMS（arXiv:2602.23292）、Bannah 2026、AutoIHC 2026、DGR 2026** 均为 2026 年极新条目，**arXiv 编号与最终卷期需复核**。

**本报告未虚构任何论文**：主表中每一条都对应一个已访问的 URL 或 PubMed/DOI 记录；未知字段以 "—"、"未说明"、"未确认" 标注，未做猜测。

---

*报告结束。*
