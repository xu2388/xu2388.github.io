---
title: UMDST：无监督多染色图像转换的统一框架 —— 论文精读
date: 2026-10-25
tags: ["论文精读","虚拟染色","染色转换","无监督","肾脏病理"]
category: 研究
summary: 针对肾脏病理「每种染色对各建一个模型」的成本困境，UMDST（AAAI 2022）用单一非配对 GAN 同时支持 H&E、MAS、PAS、PASM 四种染色之间的任意转换：风格引导归一化（SGN）以目标域风格仿射因子平衡内容与风格，多风格编码（MSE）把染色标签映射为可学习风格码，改进独热标签（δ=0.05）进一步解锁混合染色与对比度调节；ANHIR 数据集上 CSS 达 0.682 / 0.674 / 0.600（MAS / PAS / PASM），五位病理医生评分 ER=4.4（与 UGATIT 持平）。
source: 豆包对话 · UMDST 模型及解决的问题 / UMDST 模型在肾脏病理图像染色中的创新与优势
---

> **论文**：*Unpaired Multi-Domain Stain Transfer for Kidney Histopathological Images*
> **作者**：Yiyang Lin\*, Bowei Zeng\*, Yifeng Wang\*, Yang Chen, Zijie Fang, Jian Zhang, Xiangyang Ji, Haoqian Wang, Yongbing Zhang†（清华大学深圳国际研究生院、哈尔滨工业大学（深圳）、北京大学电子与计算机工程学院、清华大学自动化系；\* 同等贡献，† 通讯作者）
> **发表**：**AAAI 2022**（Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 36 No. 2, pp. 1630–1637）；DOI：10.1609/aaai.v36i2.20054
> **arXiv**：未检索到本论文的 arXiv 预印本版本，本文不标注任何编号
> **代码**：https://github.com/linyiyang98/UMDST （官方仓库，README 明确标注 AAAI 2022，已核实可访问）
> **方法名**：**UMDST**（**U**npaired **M**ulti-**D**omain **St**ain **T**ransfer，源自论文标题与官方仓库名；论文正文中自称为 "our method"）

---

## 〇、材料来源与核对原则

本文的原料是两条豆包对话记录：一条围绕「这个工作解决了什么问题」展开，另一条聚焦「模型在肾脏病理染色中的创新与优势」，其中还夹杂了笔者当时把该方法迁移到自有扩散模型的大量设想性讨论。这类原料真假混杂：论文事实、模型复述、AI 建议值、乃至完全无出处的虚构对象混在一起。

处理方式只有一条规则：**以论文原文为准**。笔者通过 AAAI 官方渠道取得该论文 PDF 全文并逐条核对，正文只保留两类内容——论文可核实的事实（公式、数值、实验设置）与明确标注为「笔者判断」的推断。原料中出现但无法核实或已被判定为编造的内容（例如迁移方案的损失权重数值、一个所谓「病理专用风格提取器」的模型名——豆包在后续回答中自己也承认检索不到其正式论文），一律不写入正文，也不进参考文献。完整的核对结论集中放在文末附表。

---

## 一、问题：逐对建模的代价与统一转换的必要性

肾脏病理是典型的「多染色协同诊断」场景。论文引言给出了明确的领域事实：H&E 显示组织形态学特征，用于初筛；但 H&E 无法呈现诊断所需的全部信息，病理医生随后还需要特殊染色（special stain）——MAS 主要用于区分肾组织内的胶原纤维与肌纤维（分别呈蓝色与红色）；PAS 用于观察肾小球基底膜、肾小管基底膜与系膜区（合称 GTM）；PASM 与 PAS 显示相同成分，但细节更清晰。

麻烦在于：由于多种染料之间的**颜色相互干扰**，同一片组织很难同时完成多种染色；若病理医生需要多种染色结果，就得**多次取样、分别染色**，直接推高诊断成本并延长患者等待时间。

虚拟染色是自然的答案，但已有路线各撞上一堵墙（论文引言的梳理）：

| 路线 | 代表工作 | 卡在哪里 |
|---|---|---|
| 像素级配对 | Rivenson 等 2019（自然·生物医学工程） | 需要像素级配对数据，临床几乎拿不到 |
| 非配对、逐对建模 | Lo 等 2021（CycleGAN 类，肾脏染色转换） | 每两种染色各需一个模型，k 种染色需 k(k−1) 个（4 种即 12 个），算力浪费严重 |
| 非配对、单域对 | UGATIT（ICLR 2020） | 只支持两个域之间的迁移 |
| 单网络多域 | StarGAN（CVPR 2018） | 有时生成质量不佳，且任务扩展性差，无法支持混合染色、对比度调节等扩展应用 |

UMDST 的目标因此被定义为：**用非配对数据训练单一网络，从任意一种染色生成任意其他染色**，并保留输入图像的组织结构。论文引言还有一处值得警惕的表述——「多域染色转换的时间成本可降低数十倍甚至数百倍」，这是**引言中的动机性断言**，正文并未给出任何计时实验来支撑它，本文只按原文性质转述，不当作实验结论。

---

## 二、方法：SGN、MSE 与改进独热标签

### 2.1 总体结构

生成器由三个部分构成：De-stain（去染色）、Re-stain（重染色）与 Multiple Style Encoding（MSE，多风格编码）。De-stain 由下采样与残差块组成，目标是去除输入图像的风格、保留内容，其残差块使用实例归一化（IN）；Re-stain 由上采样与残差块组成，负责按「输入内容 + 目标染色风格」生成图像，其残差块使用风格引导归一化（SGN）。判别器包含下采样、辅助分类器（Auxiliary Classifiers）、分类模块与判别模块：分类模块判断输入的染色类型，判别模块判断图像真假，辅助分类器帮助对应模块更关注图像中的关键位置。整体还采用全局判别器与局部判别器的组合。

训练流程（论文算法 1）分两阶段：给定原图 $x$ 与其标签 $L_o$、目标标签 $L_t$，第一阶段把 $x$ 经 De-stain 得结构特征，把 $L_t$ 经 MSE 得仿射因子，再经 Re-stain 得目标图，更新判别器；第二阶段以同样方式生成重构图 $G(G(x,L_t),L_o)$ 与身份图 $G(x,L_o)$，更新生成器。生成器侧共五类损失项：对抗损失、分类损失、辅助损失、循环损失 $l_{cyc}$ 与身份损失 $l_{idt}$，对抗项采用最小二乘 GAN 目标；循环与身份约束继承自 CycleGAN 一脉。需要说明：原料曾给这套总损失编配过一组具体权重数值，那些是豆包为「迁移到扩散模型」给出的**建议值**，并非论文实测配置，本文一律不载；论文自身的权重设定请以原文及其补充材料为准。

### 2.2 风格引导归一化（SGN）：本文最核心的机制

Re-stain 阶段的矛盾在于：既要用输入图像的**内容**（组织结构），又要注入目标域的**风格**（染色）。SGN 的公式（论文式 (1)，已对照原文核实）为：

$$SGN(\varphi)=f_{\gamma}(\varphi)\cdot\bigl(\rho\cdot\hat{a}_{I}+(1-\rho)\cdot\hat{a}_{L}\bigr)+f_{\beta}(\varphi)$$

逐项解释：

- $\hat{a}_{I}$、$\hat{a}_{L}$：分别是输入特征图的通道归一化（channel-wise）与层归一化（layer-wise）。二者按权重混合，共同承载「输入图像的内容」；
- $\rho$：决定 $\hat{a}_{I}$ 与 $\hat{a}_{L}$ 的配比。论文正文只说明这一点，未给出任何具体取值；原料宣称「编码器侧 $\rho=0.8$、解码器侧 $\rho=0.2$」，笔者在正文中查无此值，不采信；
- $f_{\gamma}(\varphi)$、$f_{\beta}(\varphi)$：作用在混合内容特征上的仿射变换因子（缩放与偏移），由风格引导因子 $\varphi$ 生成，专门编码**目标染色域的风格**。

**为什么这样设计**：论文指出，LIN（层-实例归一化机制，见 UGATIT 一文）中 $f_{\gamma}$、$f_{\beta}$ 是固定值，因此只能服务单一目标域、无法适配多染色域；SGN 把这两个因子改为由 $\varphi$ 动态生成，改变目标标签即改变风格注入方式，这正是「一个网络服务多域」在归一化层上的落点。从归一化谱系看，这条线是：IN 去风格 → AdaIN / CIN / BIN 引入目标风格统计 → AdaLIN 学习 IN 与 LN 的混合比例但仍不支持多风格 → FIN 用人工标签控制方向但关系是静态的 → SGN 让标签与风格的关系由网络动态学习。

对内容/风格的这种处理完全发生在**特征统计量层面**（均值-方差的归一化与仿射），不涉及任何蛋白表达意义上的语义约束——这是它与后来语义路线工作（第四节详述）的根本分界，笔者判断这一点决定了 UMDST 适合「显色规则由组织结构决定」的 histochemical 特殊染色，而不能直接搬到阳性信号语义敏感的 IHC 任务上。

### 2.3 多风格编码（MSE）：把标签变成可学习的风格码

SGN 需要的 $\varphi$ 由 MSE 生成（论文式 (2)、(3)，已核实）：

$$\varphi=\mathrm{sigmoid}(LW)^{\theta}$$

$$f_{\gamma}(\varphi)=\varphi\cdot\gamma_{1}+\gamma_{2},\qquad f_{\beta}(\varphi)=\varphi\cdot\beta_{1}+\beta_{2}$$

其中 $W$ 是 $n\times n$ 可学习风格编码矩阵、$\theta$ 是 $n\times 1$ 可学习风格编码向量，$n$ 为染色域数量（论文取 $n=4$），$L$ 为目标染色标签向量，$\gamma_{1},\gamma_{2},\beta_{1},\beta_{2}$ 均为可学习参数。

直觉上：若 $L$ 用传统独热标签，$LW$ 只是按行「取出」$W$ 中对应那一行——每种染色的风格码退化为静态模板，染色域之间的关联没有被建模；且训练标签与测试标签一旦存在差异，网络就无从适应。让 $\varphi$ 参与 sigmoid 与 $\theta$ 的运算、再经线性映射得到仿射因子，风格码之间才可能存在可学习的相互作用。原料中复述的 MSE 公式写作 $\varphi=\sigma(W\cdot l+\theta)$，与论文式 (2) 的运算结构不符，本文按论文原文改写。

### 2.4 改进独热标签：一个 δ 撬开两类扩展任务

标签的定义（论文式 (4)，已核实）：

$$L=[\delta,\delta,1,\delta,\dots,\delta]\in\mathbb{R}^{n}$$

$\delta$ 为小值，**实验取 0.05**，且论文强调可按实际需求任意设定。四种染色的标签记号（论文示例，顺序可自定义）：$[1,\delta,\delta,\delta]$ 对应 PASM，$[\delta,1,\delta,\delta]$ 对应 H&E，$[\delta,\delta,1,\delta]$ 对应 PAS，$[\delta,\delta,\delta,1]$ 对应 MAS。

这里要纠正原料的一处算错：豆包把软标签写成 $(1-\delta)\cdot\mathrm{OneHot}(k)+\delta\cdot\mathbf{1}$ 并举例 PASM 为 $[0.05,0.05,0.05,0.95]$——按其自身公式，目标位置应为 $0.95+0.05=1$，与论文定义的 $[\delta,\delta,\delta,1]$ 恰好等价；例子里的 0.95 是算术错误。本文以论文形式 $[\delta,\dots,1,\dots,\delta]$ 为准。

非目标位置保留非零的 δ，带来两类传统独热标签做不到的扩展应用（论文正文均有示例）：

| 扩展任务 | 标签形式 | 效果 |
|---|---|---|
| 混合染色 | $[1-\xi,0,0,\xi]$，ξ 控制两种染色占比 | 同一张图上叠加显示 PASM 与 MAS 的染色结果 |
| 染色对比度调节 | $[0,0,0,1+\tau]$ | τ 在一定范围内越大，MAS 各色之间的对比度越强 |

**为什么值得单列**：这两项应用不是「多训了几个模型」，而是标签接口本身从离散索引变成了连续可调的输入——同一网络在不重训的情况下响应用户编辑的标签。原料把这一点的意义说成「打破域硬分割」，方向是对的，但其声称的「防止过拟合、学到染色渐变特征」等训练动力学解释，论文并未验证，应视为推测。

### 2.5 关键超参数一览（仅列已核实项）

| 参数 | 取值 | 核实状态 |
|---|---|---|
| δ（改进独热标签小值） | 0.05 | 论文正文核实 |
| n（染色域数） | 4 | 论文正文核实 |
| 输入 patch 尺寸 / 重叠 | $256\times256$ / 192 | 论文正文核实 |
| 训练迭代数 | 300000 | 论文正文核实 |
| 优化器 | Adam，$\beta_1=0.5$、$\beta_2=0.999$ | 论文正文核实 |
| 学习率 | 初始 0.0001，150000 次迭代后线性衰减 | 论文正文核实 |
| batch size | 1 | 论文正文核实 |
| 硬件 | RTX 3090 单卡（i5-10400 / 16 GB RAM） | 论文正文核实 |
| ρ 的分层取值 | —— | 正文未给出，原料声称值未核实，不采用 |
| 各项损失权重数值 | —— | 正文见原文及补充材料，原料声称值系 AI 建议，不采用 |

---

## 三、实验与判据：数字要逐条对上出处

### 3.1 数据集与指标

实验基于 **ANHIR 数据集**（Borovec 等 2020，IEEE TMI）：人类肾脏高分辨率切片共 5 组，每组 4 张连续组织切片、分别经 H&E / MAS / PAS / PASM 染色，组织结构大体相似但**未做像素级配准**；40× 放大，分辨率 0.2528 µm/pixel，缩放到原尺寸的 25%。训练用 kidney 1–4 组（kidney 1 的 H&E 切片因颜色与其他组差异过大而被剔除），测试用 kidney 5 组；切块后训练集 39764 张（H&E 7500 / MAS 12008 / PAS 9616 / PASM 10640），测试集 8387 张。这是一个 WSI 个位数规模的数据集，论文摘要自己也称之为 "a tiny dataset"。

两项核心指标（论文正文定义）：

- **CSS**（Contrast-Structure Similarity，对比度-结构相似性）：衡量生成图像从原图保留了多少结构信息，反映网络提取内容的能力，越高越好；
- **ER**（Expert Rating，专家评分）：5 位病理医生打分取均值，1 最低、5 最高。

### 3.2 定量结果（表 1、表 2 均按论文原表转录，已核实）

**表 1：不同方法的 CSS（越高越好）**

| 方法 | MAS | PAS | PASM |
|---|---|---|---|
| MUNIT | 0.145±0.073 | 0.115±0.019 | 0.110±0.055 |
| FUNIT | 0.332±0.052 | 0.318±0.034 | 0.246±0.018 |
| StarGAN | 0.520±0.046 | 0.543±0.051 | 0.491±0.057 |
| UGATIT | 0.584±0.043 | 0.510±0.038 | 0.399±0.064 |
| **UMDST（Ours）** | **0.682±0.039** | **0.674±0.040** | **0.600±0.025** |

**表 2：各模型的 ER（5 位病理医生均值）**

| 指标 | MUNIT | FUNIT | StarGAN | UGATIT | UMDST |
|---|---|---|---|---|---|
| ER | 1.2 | 2.8 | 3.2 | 4.4 | 4.4 |

对照原料，必须指出两处**列对应与解读错误**：

1. 原料称「CSS 如 MAS 为 0.674±0.040」——0.674±0.040 在论文表 1 中属于 **PAS** 列，MAS 列的数值是 0.682±0.039。数值本身真实存在，列名张冠李戴。
2. 原料称 ER 4.4 为「最高分、与真实染色一致性极高」——表 2 显示 UGATIT 同为 4.4，两者**并列**。UMDST 在主观评分上并未拉开与最强双域基线的差距，其优势在于：UGATIT 达到同样水平需要为 4 种染色分别维护多达 12 个模型，而 UMDST 只有一个。这是笔者对该结果的解读，论文未做这一对比论证的显式展开。

### 3.3 泛化与扩展实验

论文的泛化分析分三个维度（cross-tissue / cross-staining / cross-task），均为论文正文可核实内容：

- **跨组织 + 跨染色**：取小鼠肾脏的 CD31 染色切片（该染色类型不在训练集中）作为输入，生成 PAS、PASM、H&E；论文报告网络仍能学到 CD31 图像的主要特征，生成的 PASM 图中 GTM 仍能被准确染黑，并与 UGATIT 的结果对照（论文图 7）。
- **跨任务（混合染色）**：论文图 8 给出不同 δ 下的 MAS+PASM 混合结果，并报告一个非单调规律——δ=0（即传统独热标签）时既显不出 PASM 的黑色区域也显不出 MAS 的红蓝区域；δ 取适当值（如 0.05）三者可同图呈现；δ 过大性能反而下降。改进独热标签是一把双刃剑，这是论文自己的表述。
- **跨任务（对比度调节）**：论文图 9 给出 MAS 染色在不同 δ 相关设定下的对比度调节结果。

除 CSS 与 ER 外，论文未提供病理定量的第三指标（如光密度类测量）。对一项以「结构保留」为核心卖点的工作而言，CSS 是唯一客观的结构判据，笔者判断其证据链偏薄——这在第四节与语义路线的对比中会看得更清楚。

---

## 四、与虚拟染色主线工作的关系：位置与分界

笔者的主线是 H&E→IHC 虚拟染色；UMDST 处理的则是肾脏内部**组织化学特殊染色之间**的多域转换，不涉及免疫组化。值得注意的是，论文结论自陈的下一步恰是：希望把方法扩展到免疫组化（IHC）染色技术——这与主线直接接壤，但论文本身没有给出任何 IHC 实验。

下表只列维度定位，各方法的具体内容以既有精读文为准，此处不复述。表格后附对应精读的裸链接。

| 方法 | 任务范围 | 是否配对 | 生成范式 | 语义/结构约束层次 | 支持染色种类 |
|---|---|---|---|---|---|
| UMDST（本文） | 肾脏多染色互转 | 非配对 | GAN（LS 对抗+循环+身份） | 风格统计层（SGN/MSE），结构以 CSS 事后度量 | 4 种特殊染色 + 未见染色域泛化 |
| PSPStain | H&E→IHC | 相邻切片配对（错位） | GAN（CUT 基线） | 蛋白表达语义层 | 单一 IHC 靶标（HER2/DAB） |
| DGR | H&E→IHC | 抗错位场景（细节见精读） | 扩散 | 生成与配准解耦 | 单一 IHC 靶标 |
| Star-Diff | H&E→IHC（复染） | 见精读 | 扩散（复原式） | 染色复原约束 + SFS 指标 | 复染/IHC 目标 |
| PST-Diff | H&E→HER2-IHC | 见精读 | 扩散（Schrödinger Bridge） | 病理与结构双约束 | 单一 IHC 靶标 |
| ODA-GAN | H&E→IHC | 非配对 | GAN | 特征正交解耦（染色/形态） | 单一 IHC 靶标 |
| MIU-Diff | H&E→IHC | 非配对 | 扩散（score-based） | 互信息引导的结构-风格分离 | 单一 IHC 靶标 |

精读文裸链接（站内）：

- https://xu2388.github.io/articles/013-PSPStain语义保持精读.html
- https://xu2388.github.io/articles/011-DGR抗错位虚拟染色精读.html
- https://xu2388.github.io/articles/012-StarDiff复原扩散精读.html
- https://xu2388.github.io/articles/014-PST-Diff结构约束精读.html

**分界点（笔者判断）**：UMDST 的全部约束都作用在「颜色分布与特征统计」这一层——SGN 调的是归一化后的仿射因子，MSE 学的是标签到风格码的映射，判别器检查的是「像不像该染色的图」；它从未要求「胶原纤维该在哪个位置呈蓝色」这类成分级对应关系成立。以「显色位置由组织结构决定」的特殊染色任务而言，这种风格级建模在分布层面通常够用；而 IHC 的阳性信号强度本身携带分子语义，纯风格约束不足以保证临床可用，这也是 2024 年以后语义路线兴起的原因。两者相隔两年，恰好构成「风格保持」与「语义保持」两代目标的一次清晰对望。

对笔者自己的浓度空间路线（见 008、015 两篇），UMDST 真正可迁移的只有一件东西：**改进独热标签把「目标域」从离散索引变成连续可调输入**的接口设计——它提示多标志物 IHC 生成（一次任务面向 HER2、ER、PR 等多个靶标）可以用单一条件向量空间而不必逐靶标建模。原料中围绕「把 SGN 嵌入扩散 UNet 残差块」的整套方案是豆包为笔者的模型**代拟的设计**，其中的权重数值、分层 ρ 取值、预训练风格提取器选型均无论文依据，且其中一个推荐组件的模型名被证实查无出处，整套方案不能作为「迁移自 UMDST」的工作引用，只能视为未经实验的设想存档。

---

## 五、局限与下一步

以下局限部分为论文事实、部分为笔者的批评性推断，分别注明。

1. **数据规模与任务范围**（论文事实）：全部训练与测试来自 5 组人类肾脏 WSI，摘要自称 "tiny dataset"；结论中的 IHC 扩展是展望，无实验。
2. **主观评分没有拉开差距**（论文事实+笔者解读）：ER 上 UMDST 与 UGATIT 并列 4.4，其对最强基线的优势主要来自多域统一（单模型对 12 模型）而非单任务生成上限。
3. **结构评价依赖单一指标**（笔者判断）：CSS 度量「保留了多少原图结构」，但没有任何指标度量「染色是否落在正确的组织成分上」；混合染色实验以定性图示呈现，缺少定量判据。
4. **GAN 训练设定偏小**（论文事实）：batch size 为 1、单卡 RTX 3090，复现门槛低，但也意味着训练稳定性与规模化行为未被检验。
5. **「省时数十倍」无实验**（论文事实）：该表述只出现在引言动机段，正文无计时对比。
6. **对主线的启示边界**（笔者判断）：SGN/MSE 是生成范式无关的即插层，理论上可嵌入扩散 UNet 的归一化位置；但原料中的迁移草案未经任何实验，且其「注入目标模态特征」的关键问题（标签只传意图、不传风格内容）在草案层面并未真正解决，若要落地需要独立设计与验证，不应引用原料方案。

下一步按笔者的计划：先在自建数据上验证「连续域条件 + 语义保持损失」的组合能否同时接管 UMDST 的风格可控性与 PSPStain 路线的蛋白语义约束，再考虑多 IHC 标志物的统一条件空间。

---

## 附：原料论断核对状态一览

| 原料论断 | 核对结果 | 处理 |
|---|---|---|
| SGN 公式 | 与论文式 (1) 一致 | 采用 |
| MSE 公式 | 原料写作 $\sigma(W\cdot l+\theta)$，与论文式 (2)(3) 不符 | 按论文改写后采用 |
| δ=0.05 | 论文式 (4) 正文明载 | 采用 |
| 软标签示例 0.95 | 目标位置应为 1，原料算错 | 按论文更正 |
| CSS 0.674±0.040「属于 MAS」 | 数值真实，但对应 PAS 列；MAS 为 0.682±0.039 | 更正列对应后采用 |
| ER 4.4「最高」 | 真实，但与 UGATIT 并列 4.4 | 采用并更正表述 |
| ρ 编码器 0.8 / 解码器 0.2 | 正文查无此值 | 不采用 |
| 总损失各项 λ 权重数值 | 系豆包迁移建议值，非论文配置 | 不采用，不入正文 |
| 「病理专用风格提取器」组件名 | 豆包后续回答自认检索不到正式论文 | 不采用，不入正文与参考文献 |
| 单次/逐对建模成本对比、k(k−1) | 论文引言明载 | 采用 |
| 「省时数十至数百倍」 | 引言动机断言，无实验 | 定性转述并标注 |
| 论文题目/作者/venue/代码 | AAAI 官方页与 GitHub 核实一致 | 采用 |
| arXiv 编号 | 未检索到 | 不标注任何编号 |

---

## 参考文献

1. Lin Y., Zeng B., Wang Y., Chen Y., Fang Z., Zhang J., Ji X., Wang H., Zhang Y. *Unpaired Multi-Domain Stain Transfer for Kidney Histopathological Images*. Proceedings of the AAAI Conference on Artificial Intelligence, 36(2): 1630–1637, 2022. DOI: 10.1609/aaai.v36i2.20054. 代码：https://github.com/linyiyang98/UMDST
2. Borovec J., Kybic J., Arganda-Carreras I., et al. *ANHIR: Automatic Non-Rigid Histological Image Registration Challenge*. IEEE Transactions on Medical Imaging, 39(10): 3042–3052, 2020.
3. Rivenson Y., Wang H., Wei Z., et al. *Virtual Histological Staining of Unlabelled Tissue-Autofluorescence Images via Deep Learning*. Nature Biomedical Engineering, 3(6): 466–477, 2019.
4. Lo Y.-C., Chung I.-F., Guo S.-N., Wen M.-C., Juang C.-F. *Cycle-Consistent GAN-Based Stain Translation of Renal Pathology Images with Glomerulus Detection Application*. Applied Soft Computing, 98: 106822, 2021.
5. Kim J., Kim M., Kang H., Lee K. H. *U-GAT-IT: Unsupervised Generative Attentional Networks with Adaptive Layer-Instance Normalization for Image-to-Image Translation*. ICLR 2020.
6. Choi Y., Choi M., Kim M., Ha J.-W., Kim S., Choo J. *StarGAN: Unified Generative Adversarial Networks for Multi-Domain Image-to-Image Translation*. CVPR 2018.
7. Huang X., Liu M.-Y., Belongie S., Kautz J. *Multimodal Unsupervised Image-to-Image Translation*. ECCV 2018.
8. Liu M.-Y., Huang X., Mallya A., et al. *Few-Shot Unsupervised Image-to-Image Translation*. ICCV 2019.
9. Mao X., Li Q., Xie H., Lau R. Y., Wang Z., Smolley S. P. *Least Squares Generative Adversarial Networks*. ICCV 2017.
10. Zhu J.-Y., Park T., Isola P., Efros A. A. *Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks*. ICCV 2017.
11. de Haan K., Zhang Y., Zuckerman J. E., et al. *Deep Learning-Based Transformation of H&E Stained Tissues into Special Stains*. Nature Communications, 12(1), 2021.
12. Zhang Y., de Haan K., Rivenson Y., Li J., Delis A., Ozcan A. *Digital Synthesis of Histological Stains Using Micro-Structured and Multiplexed Virtual Staining of Label-Free Tissue*. Light: Science & Applications, 9(1), 2020.
13. Vasiljević J., Feuerhake F., Wemmert C., Lampert T. *Towards Histopathological Stain Invariance by Unsupervised Domain Augmentation Using Generative Adversarial Networks*. Neurocomputing, 460: 277–291, 2021.
14. 站内既有精读（第四节对比对象）：013-PSPStain语义保持精读、011-DGR抗错位虚拟染色精读、012-StarDiff复原扩散精读、014-PST-Diff结构约束精读、ODA-GAN 与 MIU-Diff 方法梳理（notes），链接见第四节。
