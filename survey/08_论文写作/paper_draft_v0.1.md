# Concentration-Domain H&E-to-IHC Virtual Staining with a Dual-Branch Fusion Frontend

> 论文草稿 v0.1 · 2026-10-18
> 用法：方括号【】是待填/待核实的占位，其余可以直接用。
> 所有数字都标了来源，没来源的一律不要写死。

---

## Abstract（v0.2 · 约 250 词）

> 摘要的标准六段式（写别的论文也照这个）：① 临床场景 ② 现有做法的缺口 ③ "我们提出" ④ 机制细节 ⑤ 结果数字 ⑥ 意义/边界。
> 数字规则：**只写 1–3 个，只写你赢的那个**。MICCAI/TMI/MedIA 基本都写数字；CVPR 系有时只写 "by a large margin"。

Hematoxylin and eosin (H&E) staining is routine in pathology, whereas immunohistochemistry (IHC) requires additional sections, separate staining and slide registration, consuming tissue that may be needed for downstream molecular assays. Virtual staining predicts the IHC appearance directly from H&E, but current methods built on contrastive unpaired translation improve the task almost exclusively by adding loss terms while leaving the generator untouched. Two consequences follow: artifacts produced by the generator's own resampling path remain unexamined, and RGB outputs entangle the contributions of the two stains, so an incorrect stain balance cannot be separated from an incorrect texture.

We reformulate H&E-to-IHC translation in the stain concentration domain. The input is decomposed into hematoxylin (H) and eosin (E) concentrations, and the network predicts H and DAB concentrations that are rendered back to RGB by an explicit Beer–Lambert model, making the stain ratio directly measurable. Within this representation we introduce (i) a dual-branch fusion frontend that processes the two stain channels separately before fusion and suppresses the low-frequency banding characteristic of CUT-based generators, (ii) a multi-scale large-kernel bottleneck that enlarges the receptive field without directional convolutions, and (iii) a regularizer on the joint DAB/H ratio distribution, which per-channel statistics cannot capture.

On the BCI benchmark, the proposed framework reduces the column-stripe score from 0.224 to 0.097, a 57% reduction, while preserving the structural correspondence with the H&E input (edge correlation 0.70 → 0.91)【待核实：0.70 是官方 3ch 权重还是我们自己的基线？若为前者，此处须改成同基线对比】. We further show that InstanceNorm renders such generators invariant to per-slide stain intensity, which bounds what loss-level remedies can achieve.

**Keywords**: virtual staining; H&E-to-IHC; stain deconvolution; concentration domain; banding artifact; distribution regularization

---

## Title（暂缓，等 Method 定稿后再定）

候选：
1. Concentration-Domain H&E-to-IHC Virtual Staining with a Dual-Branch Fusion Frontend
2. Suppressing Banding Artifacts in CUT-based Virtual Staining via Stain-Decoupled Representation
3. Beyond RGB: Decoupled Stain Concentration for H&E-to-IHC Translation

起名原则：题目里要出现 **H&E-to-IHC**（检索词）+ **一个你的差异化词**（concentration / decoupled / banding）。别只写 "A Novel Framework for..."。

---

## 1. Introduction

**P1 — 临床动机（3–4 句）**
IHC is the standard for assessing biomarkers such as HER2, where diagnosis depends jointly on membrane staining intensity and the proportion of positive cells. Acquiring IHC requires serial sectioning, separate staining and slide registration, which consumes tissue and introduces inter-section misalignment. Virtual staining offers an alternative by predicting the IHC appearance directly from an H&E slide.

**P2 — 谱系与缺口（本文立论的核心，必须写实）**
Existing H&E-to-IHC methods form a compact lineage rooted in CUT. ASP replaces the patch-level contrastive objective with adaptive supervised PatchNCE; PSPStain adds protein-aware statistics on the DAB channel; CCPL extends the same statistics from DAB to a joint hematoxylin–DAB supervision. Across these generations the generator and discriminator remain unchanged — a ResNet-6Blocks generator with InstanceNorm and a fixed, weakly anti-aliased resampling path — and all reported gains originate in the loss layer. As a result, artifacts produced by the generator itself, rather than by the training objective, have not been examined.

**P3 — 我们的做法（一段讲清四件事）**
We take a different starting point. Instead of adding another loss term to an RGB pipeline, we reformulate the problem in the stain concentration domain: the input becomes two deconvolved stain channels (H, E) and the output two concentration maps (H, DAB) that are rendered to RGB by an explicit Beer–Lambert model. This representation makes the stain balance directly measurable, and it exposes two failure modes that RGB outputs conceal. We then address the first — banding artifacts arising from the generator's resampling path — with a dual-branch fusion frontend, and constrain the second — the relative abundance of the two stains — with a ratio-distribution regularizer.

**P4 — 贡献（4 条，措辞保守）**
- We reformulate H&E-to-IHC translation in a stain concentration domain with an explicit physical rendering step, making per-channel stain statistics directly observable.
- We introduce a dual-branch fusion frontend that suppresses the 7–20 px banding characteristic of CUT-based generators, reducing the column-stripe score by more than half.
- We propose a stain-ratio distribution regularizer that constrains the joint DAB/H distribution, which existing per-channel statistics do not capture.
- We report and analyse a structural limitation of InstanceNorm-based generators: they are provably invariant to per-slide stain intensity, which bounds what any loss-level remedy can achieve.

> ⚠️ 写作纪律：**不要把「2 通道输入」单独说成创新**。审稿人第一问就是「为什么不用 RGB」。正确答法是：它让失效**可测量**，而不是它更「物理」。

---

## 2. Related Work

**2.1 Virtual staining.** pix2pix / Pyramid pix2pix（配对）；CUT / ASP（非配对 + 对比）；PSPStain（蛋白感知统计）；CCPL（跨通道统计）。一句话收口：这些工作共享同一生成器，差异集中在损失。

**2.2 Artifacts in generative translation.** 反卷积棋盘格（Odena 2016）；StyleGAN2/3 的 upsampling 与 alias-free 设计；BlurPool。指出：CUT 默认已带弱抗混叠，因此本文关注的不是棋盘格，而是抗混叠不足残留的**低频带状伪影**（7–20 px）。

**2.3 Distribution matching.** Gram / CORAL / FFD / focal frequency loss。指出：这些方法约束边缘分布或全局频谱，**不约束两个染色通道的联合比例**。

---

## 3. Method

### 3.1 Concentration-domain representation

用固定染色矩阵 M 做颜色反卷积：

```
OD = -log((I + eps) / I0)
[C_H, C_E]   = pinv(M_HE)  @ OD        # 输入侧
[C_H, C_DAB] = pinv(M_IHC) @ OD        # 输出侧（仅训练时用于监督）
```

渲染回 RGB：

```
I = I0 · exp( - M_IHC · [C_H, C_DAB] )
```

说明三点：① M 用固定矩阵而非逐图估计（逐图 Macenko 在本数据上退化，两列夹角 <1°，需在附录写明）；② 渲染是可微的，端到端训练；③ 相比 RGB 输出，浓度输出让 D/H 比可直接读出。

### 3.2 Dual-branch fusion frontend

原 stem：`Conv7×7(2→64) + IN + ReLU`，两个染色通道在第一层就被线性混合。
替换为：H、E 各走一个 `Conv3×3(1→64) + IN + ReLU`，再用 CGAFusion 融合（空间注意力 + 通道注意力 + 像素注意力，`result = x+y + p·x + (1-p)·y`，接 1×1 投影）。

保留 `--frontend_mode {none, cga}` 开关，默认关，便于回退。

### 3.3 Multi-scale large-kernel bottleneck

接在 6 个 ResBlock 之后、上采样之前（`B×256×128×128`，形状不变）：

```
x → 1×1 conv + IN + SiLU
  → DW3 → (+DW5) → (+DW7) → (+DW9) → (+DW11)     # 串联残差，感受野累加
  → 1×1 conv + IN + SiLU
  → SE（各向同性，降维 16）
  → x + γ · (y ⊙ SE(y))                            # γ 零初始化
```

设计要点写三条：① 只取 PKINet 的多核 inception 结构，**不用其方向性上下文注意力**（`(1,k)`/`(k,1)` 卷积可能重新引入竖纹）；② SE 为各向同性；③ γ 零初始化，从已有权重续训时起点恒等。

### 3.4 Stain-ratio distribution regularization

在组织区 M 上定义逐像素比值 `r = C_DAB / (C_H + eps)`，用一维 Wasserstein 距离逐图对齐生成与真实的比值分布：

```
L_ratio = (1/B) Σ_b W1( P(r_fake^b | M) , P(r_real^b | M) )
```

配套两项（防止退化解）：
- `L_ch`：H 与 DAB 各自的均值 + 分布（逐通道边缘统计）；
- `L_pos`：阳性面积占比之差，`|p_fake^+ − p_real^+|`。

W1 用可微软直方图（线性插值分箱 + CDF L1）实现，避免硬分箱断梯度。组织掩码由 OD + Otsu + 形态学在数据侧预算，不进入损失循环。

### 3.5 Objective

```
L = L_GAN + λ_NCE·L_NCE + λ_gp·L_GP + λ_ssim·L_SSIM
  + λ_ch·L_ch + λ_ratio·L_ratio + λ_pos·L_pos
```

---

## 4. Experiments

### 4.1 Setup
- 数据：BCI（H&E→IHC，HER2）。训练【待补】对，测试 977 张，其中组织面积 ≥5% 的有效样本 796 张。
- 实现：ResNet-6Blocks，ngf=64，PatchGAN 判别器（5 层，ndf=32），spectral norm，crop 512，batch 1，Adam 1e-4，线性衰减，50 epoch。
- 指标：CSS（列条纹）、DSR（方向性能量比）、edgeCorr（与 H&E 的边缘相关）、D/H 中位数与 IQR、DAB 均值、阳性面积占比、PSNR/SSIM（**必须注明未配准，仅作参考**）。

### 4.2 Artifact suppression（主表）

| Method | CSS ↓ | DSR_v/DSR_h ↓ |
|---|---|---|
| CUT baseline (2ch) | 0.224 | 【待补】 |
| + CGA frontend | **0.097** | 【待补】 |
| + large-kernel bottleneck | 【待补】 | 【待补】 |

### 4.3 Structure fidelity
edgeCorr(gen, H&E)：baseline 0.70 → CGA 0.91【待补：确认是否同配置】。

### 4.4 Stain statistics

| | Real IHC | Ours |
|---|---|---|
| D/H median | 0.804 | 1.001 |
| D/H IQR width | 0.767 | 0.037 |
| DAB median | 0.152 | 0.179 |
| Positive-area ratio | 0.084 | 0.205 |

### 4.5 Ablation
逐项加：baseline → +CGA → +bottleneck → +ratio loss。同 seed、同 epoch、同起点。

### 4.6 Limitations（这一节必须有，且要写得坦率）
- 相邻切片未配准，PSNR/SSIM 不能作为质量判据；
- 生成器含 InstanceNorm，对输入全局缩放严格不变，切片级染色强度不可观测，D/H 分布坍缩（IQR 窄 20 倍）；
- 因此本文的比值约束只能校正全局水平，不能恢复逐切片自适应。

---

## 5. Conclusion

（3 句）浓度域表征让染色平衡可测量；双分支融合前端显著抑制带状伪影；比值分布约束校正了全局染色偏移。本文同时指出 InstanceNorm 造成的尺度不可观测性是该类架构的共同边界。

---

## 附：写作纪律（自己核对用）

1. **不写「首次」**，除非能给出检索日期与关键词。
2. **不拿 PSNR/SSIM 主张更好**——数据未配准。
3. **基线与本方法必须同配置同起点**，否则收益归属不清（CCPL 就栽在这：82% 的「提升」来自换基线）。
4. **报了 CSS 就必须报它怎么算的**（列均值残差、频带、是否归一化）。
5. **不把「第三名」写成「最低」**。
6. 大创汇报那一晚不要碰论文；论文按每晚一个 section 推进。
