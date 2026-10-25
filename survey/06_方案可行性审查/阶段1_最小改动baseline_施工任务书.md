# 阶段 1 · 最小改动 baseline 施工任务书

> 2026-10-05 · 上游：`StainFuser改造为H&E2IHC_可行性与实验路线.html` §8.2 · `E0_染色空间闭环验证_实验任务书.md`
> **给执行 agent 用。按顺序做，不要跳步，不要顺手改架构。**

---

## 0. 先回答一个问题：门禁开到哪一步？

**E0 全过 ⇒ 只允许开始「阶段 1」。不允许直接进阶段 2。**

```
阶段 0 门禁（E0.1–E0.4）
        │ 全过
        ▼
★ 阶段 1 · 最小改动 baseline  ← 你现在可以开始的就是这一步
        │ 通过判据
        ▼
阶段 2a · 只换渲染器
        ▼
阶段 2b · 再换生成空间        ← 这才是「染色空间改造」本体
```

### 为什么阶段 1 不是"改造前的准备"，而是改造的第一步

**阶段 1 要改的东西本身就是改造**（换掉两个条件槽位）。它存在的唯一目的是把两个问题**分开**：

| 问题 | 由谁回答 |
| --- | --- |
| StainFuser 能不能做 H&E→IHC？ | **阶段 1** |
| 染色空间改造有没有用？ | 阶段 2 |

**如果跳过阶段 1 直接换输出空间**：一旦出问题，你无法区分是「StainFuser 不适合这个任务」还是「染色空间渲染有问题」。这和你在 HistDiST 上得出的纪律是同一条——**先修 scheme B 拿稳定 baseline，再谈架构**。

---

## 1. 动手前的检查表（逐条打勾，缺一条就停）

| # | 检查项 | 怎么查 | 不通过怎么办 |
| --- | --- | --- | --- |
| 1 | **E0.4 已通过**（StainFuser 能跑通并出图） | `run_patch.py` 出图 | 先修 E0.4 的四个坑 |
| 2 | **`STAIN_MAT_FULL` 形状 = (3,3)、列序已确认** | 看 `out/e02_results.json` 的 `matrix_source` 字段 | 若是 `ruifrok_hed` ⇒ 你的矩阵**没加载成功**。阶段 1 的 H-score 判据会不可比，**必须先接上自己的 M** |
| 3 | **E0.3 的 ICC 已知** | `out/e03_results.json` | 若 ICC < 0.8 ⇒ §5 的 H-score 判据要降级为"仅作趋势参考"，改用别的指标 |
| 4 | **E0.1 的结果已知**（V1 / V3） | `out/e01_results.json` | 阶段 1 不受影响（它不改输出空间），但**阶段 2 的门禁取决于这个数** |
| 5 | 权重已下载（≈14.3 GB） | `checkpoint.pth` 等 | 见 E0.4 |
| 6 | 依赖版本锁死 | `diffusers==0.26.3` + `transformers==4.38.2` + `huggingface_hub==0.21.3` | 版本不对会报 `cached_download` ImportError |

> ⚠️ **第 2 条最容易漏。** 没有确认过列序的话，"E 通道""DAB 通道"这些名字可能全是错的——**但注意：E0.2 的结论不受影响**，因为 `C_E ≡ C_res` 这个代数恒等式对**任何**满秩 3×3 矩阵都成立。受影响的只有**命名**和 **H-score 的绝对值**。

---

## 2. ★ 先做一个零训练的检查（第 0 步，别跳过）

**目的：量化「目标图 latent 泄漏」到底值多少。** 这直接决定阶段 1 的必要性，而且**不用训练**。

用**预训练 checkpoint** 跑三次推理，只改 `--target_path`：

| 试验 | `target_path` 给什么 | 预期 |
| --- | --- | --- |
| T1 | **真实配对的 IHC 图** | 质量最好（它在偷看答案） |
| T2 | **另一张无关的 IHC 图** | 明显变差 |
| T3 | **纯灰/纯白图** | 最差 |

**判据与解读：**

- **T1 ≫ T2 ≈ T3** ⇒ 泄漏**主导**了输出 ⇒ 阶段 1 换掉 `encoder_hidden_states` 是**必须的**，且这一步会带来最大的可见变化。
- **T1 ≈ T2 ≈ T3** ⇒ 泄漏影响很小 ⇒ 阶段 1 的收益可能主要来自 `controlnet_cond` 那一侧。**记录下来**，这会影响你阶段 2 的取舍。
- 无论哪种结果，**把这个 T1/T2/T3 的差值写进论文**——它是"原方法在 H&E→IHC 上不可用"的**直接量化证据**，本身就是一条贡献。

> 这一步零训练、半小时内可完成。**不做它，你在阶段 1 看到的任何提升都无法归因。**

---

## 3. 阶段 1 的边界

### 做（就这三件事）

1. 把 `encoder_hidden_states` 从**目标图 latent** 换成**可学习染色 token**
2. 把 `controlnet_cond` 从**原始 RGB** 换成**染色分解后的结构分量**
3. 加日志（§4）

### 明确不做

- ❌ 不动输出空间（仍是 SD2.1 VAE 的 **4 通道 latent**，仍走 VAE 解码）
- ❌ 不动 `conv_in`（4 通道）、`down_blocks`、`mid_block`
- ❌ 不加 channel attention
- ❌ 不换解码器、不引入 Beer–Lambert 渲染器
- ❌ 不改损失函数（仍是纯 ε-MSE）

**理由**：阶段 1 的全部价值在于"**只动条件，不动表示**"。动了别的，判据就失效了。

---

## 4. 精确改动清单

### 4.1 `encoder_hidden_states`（P0，~20 行）

**位置**：`recipe.py` **L268**（训练）/ **L342**（推理）—— 传给 conditioner 与 noise_predictor 的那个实参。

**投影层的创建/使用位置（实测，回源核实过）**：

| 组件 | 创建 | 使用 |
|---|---|---|
| UNet 的 `encoder_projector` | `arch.py` **L151–155** | `arch.py` **L188–189** |
| ControlNet 的 `encoder_projector` | `arch.py` **L76–80** | `arch.py` **L115–116** |

**现状**（实测）：
```python
# tgt_latents: (B, 4096, 4)     ← 目标图 VAE latent 拍平（4 通道 × 64×64）
# encoder_hid_dim = 4           ← arch.py L152: 4 != 1024 ⇒ 建 Linear(4, 1024)
# encoder_projector = nn.Linear(4, 1024)   ← 随机初始化 + 可训练（L150 之后才创建）
```

★ **注意 `encoder_hid_dim=4` 硬编码在两个地方**（漏一处会静默不生效）：
- `train.py` **L60**：`OveriddenUnet2D(unet, encoder_hid_dim=4)`
- `src/misc/model_utils.py` **L40**：同一行（**推理走这条**）

**★ 改法有两个，先试 A：**

**A（推荐，零改动）**：**token 的 dim 就取 4**，与现状完全一致。
`encoder_hid_dim=4` 不动 ⇒ **`train.py` / `model_utils.py` 一个都不用改**。

```python
# p_tok: (B, 256, 4)            ← 可学习染色 token（零初始化）
# encoder_projector 仍是 nn.Linear(4, 1024)，不动
```

**B（要更多容量，代价是改 2 个文件）**：把 `encoder_hid_dim` 从 4 改成 768。
**必须同时改 `train.py` L60 和 `model_utils.py` L40**，否则训练和推理的投影层维度不一致。
```python
# p_tok: (B, 256, 768)
# encoder_hid_dim = 768  ⇒ encoder_projector = nn.Linear(768, 1024)
```

**为什么默认推荐 A**：原设计的 `encoder_hidden_states` **本来就是每个位置 4 维**
（`(B, 4096, 4)`）。所以 `dim=4` **不是降级，是与 baseline 同容量**；
而且它把"改动小"这条优先级落到了实处（零文件改动）。
**B 的好处是 token 有更大容量**，但它引入了一个额外的失败模式（投影层随机初始化，
训练/推理两处维度不同步），**不建议在第一版就上**。

**最简版实现**：
```python
class StainToken(nn.Module):
    """可学习的 target-domain 染色 token。零初始化 ⇒ step 0 与无条件数值一致。

    ★ dim 默认 4：与 encoder_hid_dim=4 对齐 ⇒ 无需改 train.py / model_utils.py。
      若要 dim=768，记得同步改那两处的 encoder_hid_dim。
    """
    def __init__(self, n_tokens=256, dim=4):
        super().__init__()
        self.tok = nn.Parameter(torch.zeros(1, n_tokens, dim))
    def forward(self, batch_size):
        return self.tok.expand(batch_size, -1, -1)
```

**★ 三个必须做的细节：**

1. **必须显式零初始化。** `nn.Linear` 默认是**随机**初始化；你 HistDiST 里的 `ProteinAdapter` 是零初始化（`nn.init.zeros_`），这保证 **step 0 与 baseline 数值一致**，让"有没有效果"有一个干净的零点。**换维度后要显式零初始化，否则失去这个性质。**
2. **记录 `|p_tok|` 的 RMS 与梯度范数。** 零初始化 + 无监控 = 典型失败模式（token 塌缩到 0，模型退化成无条件生成，输出"H&E 变暗"）。见 §5。
3. **`encoder_projector` 本身也是随机初始化且可训练**（`arch.py` L150 之后才创建，
   `train.py` L78 把它放进 `param_dict["noise_predictor_encoder_projector"]`）。
   ⇒ **它也是一个"从随机开始学"的注入点**，同样要监控它的权重范数。

### 4.2 `controlnet_cond`（P0，~30 行）

**位置**：`recipe.py` **L269**（训练）/ **L343**（推理）；消费层在 `arch.py` **L345–347**。

**现状**：`controlnet_cond = src_latents` = **原始 RGB 像素**（3 通道，`[0,1]`，512²）。变量名 `src_latents` 是误导，它**不是** latent。

**改成**：染色分解后的**结构分量**。三个候选，按推荐度：

| 方案 | 内容 | 说明 |
| --- | --- | --- |
| **A（推荐先试）** | `[C_H, C_E, C_res]` 三通道 | 复用 E0.2 的分解。**保留 3 通道 ⇒ 网络结构零改动**（`Conv2d(3,16,3,1)` 不变） |
| B | `[C_H, C_H, C_H]`（H 通道复制 3 份） | 最小改动，但**丢掉伊红承载的膜/胞质形态**——HER2 是膜染色，这一条要谨慎 |
| C | HED 三通道 | 现成可用，但 HED 是为 H&E 设计的，IHC 上语义不干净 |

**★ 硬约束（实测，别踩）：**

1. `controlnet_cond_embedding` 的第一层是 **`Conv2d(3,16,3,1)`**，硬编码 3 通道。**喂 1 通道会 RuntimeError。**
2. `conditioning_embedding_in_channels` 是**死参数**——**已回源核实**：`arch.py` L30–62 把这个形参**接收**了，
   但 `super().__init__(...)` 的实参表里**没有它** ⇒ `ControlNetModel` 用默认 `in_channels=3`。
   ⇒ `train.py` L64 和 `model_utils.py` L44 里写的 `conditioning_embedding_in_channels=4` **是假的**，
   **它让你以为 cond 是 4 通道，实际是 3 通道**。**改了不生效。**
   要真改，必须**显式加进 `super().__init__(...)` 的实参表**。
3. **改通道数会破坏 checkpoint 加载**：`load_state_dict(strict=False)` 只忽略「缺键/多键」，**不忽略尺寸不匹配**（会抛 `size mismatch`）。
   ⇒ **保持 3 通道、只换内容。**
4. **好消息**：`controlnet_cond_embedding` **不是**从预训练 UNet 复制来的（`arch.py` L64–74 只复制 `conv_in / time_proj / time_embedding / class_embedding / down_blocks / mid_block`）。它是新建层、末层是 `zero_module`。**换内容不丢预训练先验，是低风险操作。**

**实现提示**：在 `dataset.py` 里加一个变换即可（把 RGB 转成染色分解三通道），**不需要改网络**。

### 4.3 三处配套改动

| # | 改什么 | 位置 | 为什么 |
| --- | --- | --- | --- |
| 1 | `latent_dist.sample()` → `.mode()` | `recipe.py` **L188, L562** | 训练与采样一致。**你 HistDiST 已经这么做了，理由相同** |
| 2 | 加 latent 钳位 **+ 记录被钳像素比例** | `recipe.py` **L251** | ⚠️ **必须记录比例**，否则会把「可检测的失败」变成「不可检测的失败」（你上次的教训） |
| 3 | 加条件 dropout（condition 置零的概率） | `recipe.py` **L265–280** | ~10 行，为后续 CFG 铺路。**但会改变收敛行为 ⇒ 作为独立 arm，不要和 4.1/4.2 混在一起** |
| 4 | **推理端也记录 clamp 比例** | `src/misc/utils.py` **L809** | `inverse_transform(..., is_tsf=True)` 用 `clamp(-1,1)` 映射到 `[0,255]`。**这是黑团被"洗白"的那一步**——不记录比例就看不见它。**E0.4 已回源确认这条路径存在**（见 E0 任务书 §5） |

**可训练集合（确认一下，别改错）**：ControlNet 全部 + UNet `encoder_projector` + UNet `up_blocks/conv_norm_out/conv_act/conv_out`。
**冻结**：VAE 全部；UNet 的 `conv_in` / `down_blocks` / `mid_block`。
（依据：`train.py` L55, L76–82；`recipe.py` L55–74）

---

## 5. ★ 日志：第一天就要加，不是"以后补"

**这是 HistDiST 那次最贵的教训：日志缺字段 = 信号消失。** 崩溃前夜唯一的预警因为被合并进另一个字段而消失了。阶段 1 的最小日志集：

| 字段 | 为什么必须有 |
| --- | --- |
| `p_tok_rms` | **零初始化 token 塌缩的唯一预警。** 塌缩 ⇒ 模型退化成无条件生成 ⇒ 输出"H&E 变暗" |
| `p_tok_grad_norm` | 确认梯度**真的传到了** token。零初始化层最怕"看起来在训、其实没梯度" |
| `cond_rms` | 确认染色分解通道被正确喂入（值域不对会静默退化） |
| `latent_clamp_frac` | 被钳位的潜码像素比例。**"把可检测的失败变成不可检测的失败"已经出现过三次** |
| `x0_pred_min` / `x0_pred_max` | 采样时预测的极值。**黑团的早期信号**（见 `05_伪影与失败模式`） |

**纪律**：凡「两个原因 → 同一个日志值」，都要**拆成两个字段**。

---

## 6. 判据

### 6.1 成功判据

| # | 判据 | 通过线 |
| --- | --- | --- |
| 1 | 生成图是 **IHC 样**的（棕 + 蓝），不是 H&E 样的（粉 + 紫） | 人工看 + 通道均值落在真实 IHC 的分布范围内 |
| 2 | **实例级**：H-score（用 E0.3 定下来的 M）与真实 IHC **正相关** | Spearman **> 0.2** 就算"有信号" |
| 3 | `p_tok_rms` 不塌缩 | 与 step 0 相比量级不下降 1 个数量级以上 |
| 4 | `latent_clamp_frac` 可接受 | 记录基线值，**不设绝对阈值**，只看趋势 |

> **判据 2 是唯一真正说明问题的那个。** 判据 1 会骗人：模型可以学会"整片涂棕"。
> **分布级 ≠ 实例级**：FID 低不代表单张图对，必须同时给实例级证据。

### 6.2 反例判据（出现即停）

| 症状 | 最可能的诊断 | 动作 |
| --- | --- | --- |
| 生成图是「**H&E 变暗**」 | 可学习 token 塌缩到 0 | 查 `p_tok_rms`；确认零初始化后梯度确实传到了 token |
| 生成图**整片均匀棕色** | condition 只学到"全局染色"，没有空间结构 | 查 structure 通路（`controlnet_cond`）是否被正确喂入；查 `cond_rms` |
| **与 §2 的 T3 结果几乎一样** | 模型根本没在用 H&E 输入 | 条件通路断了。回查两个槽位是否真的接上 |

### 6.3 止损

- **阶段 1 三条判据全不过** ⇒ 先不要进阶段 2。**先确认是不是条件通路接错了**（这是最常见的、也最容易修的）。
- **判据 2 反复为负相关** ⇒ **这是个真信号**，说明条件里没有蛋白信息。回到 `p_tok` 的设计（是否该接完整的 Protein Branch 而不是裸 token）。

---

## 7. 三个 arm（必须做，否则无法归因）

| Arm | `encoder_hidden_states` | `controlnet_cond` | 回答什么问题 |
| --- | --- | --- | --- |
| **A** | 目标图 latent（原样） | 原始 RGB（原样） | **上限参照**。它是"偷看答案"的，不能当结果，但给出天花板 |
| **B** | **可学习 token** | **染色分解三通道** | **阶段 1 本体**。这是唯一可发表的设置 |
| **C** | 目标图 latent（保留泄漏） | 染色分解三通道 | **消融**：量化泄漏贡献了多少（配合 §2 的 T1/T2/T3） |

**三个 arm 用同一套超参、同一个 seed、同一批数据。** 只改条件，别的一律不动。

---

## 8. 禁止事项

1. ❌ **不要跳过 §2 的零训练检查。** 没有它，阶段 1 的任何提升都无法归因。
2. ❌ **不要同时换输出空间。** 那是阶段 2，且有独立止损判据。
3. ❌ **不要改 `controlnet_cond` 的通道数。** 3 通道是硬约束（会破坏 checkpoint 加载）。
4. ❌ **不要省掉 `p_tok` 的日志。** 零初始化层塌缩是静默的。
5. ❌ **不要为了让图好看而调 clamp 阈值。** 必须记录被 clamp 的比例。
6. ❌ **不要用"预计""应该"代替实测数字。**
7. ❌ **不要只报均值。** 报告分布（min / median / max），尤其是伪影类指标。

---

## 9. 与阶段 2 的接口

阶段 1 完成后，进阶段 2 之前要能回答：

1. **T1/T2/T3 的差值是多少？**（泄漏的实际量级）
2. **Arm B 的 H-score 相关性是多少？**（条件里有没有蛋白信号）
3. **`p_tok_rms` 稳定吗？**（可学习 token 这条路可不可行）
4. **E0.1 的 V1 / V3 是多少？**（染色空间这条路通不通）

**第 4 条是阶段 2 的真正门禁**——阶段 1 通过不代表染色空间成立。**染色空间成立与否，由 E0.1 决定；StainFuser 能不能用，由阶段 1 决定。两件事不要混。**
