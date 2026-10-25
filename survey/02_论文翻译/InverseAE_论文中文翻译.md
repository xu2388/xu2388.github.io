# 明场多重 IHC 图像的标签高效深度颜色解卷积

**Label-Efficient Deep Color Deconvolution of Brightfield Multiplex IHC Images**

**期刊**：*IEEE Transactions on Medical Imaging*（IEEE TMI），2026 年 2 月，第 45 卷第 2 期，853–864 页
**DOI**：10.1109/TMI.2025.3609245
**PMC**：作者手稿，NIH 公共访问（HHS Public Access），PMC 上线日期 2026 年 7 月 6 日

**作者与单位**：
- Shahira Abousamra —— 斯坦福大学生物医学数据科学系，美国加州
- Danielle Fassler —— 石溪大学病理学系，美国纽约州
- Rajarsi Gupta —— 石溪大学生物医学信息学系，美国纽约州
- Tahsin Kurc —— 石溪大学生物医学信息学系，美国纽约州
- Luisa F. Escobar-Hoyos —— 耶鲁大学治疗放射学系，美国康涅狄格州
- Dimitris Samaras —— 石溪大学计算机科学系，美国纽约州
- Kenneth R. Shroyer —— 石溪大学病理学系，美国纽约州
- Joel Saltz —— 石溪大学生物医学信息学系，美国纽约州
- Chao Chen —— 石溪大学生物医学信息学系，美国纽约州

**通讯邮箱**：shsamra@stanford.edu

---

## 摘要

明场多重免疫组织化学（multiplex immunohistochemistry, mIHC）能够在同一张组织切片上同时标记多种蛋白质生物标志物。它使得研究者能够探索炎症微环境与肿瘤细胞之间的空间关系，并揭示肿瘤细胞形态如何与癌症生物标志物的表达相关联。要分析和量化由这些生物标志物所指示的不同细胞表型群体，颜色解卷积（color deconvolution）是必需的。然而，随着多重染色数量的增加，这一任务变得极具挑战性。在本工作中，我们提出了用于 mIHC 颜色解卷积的**自监督**与**半监督**方法。我们提出的方法基于深度卷积自编码器，并使用受物理学启发的新颖重建损失进行学习。我们展示了如何整合弱标注与大量可用的无标注数据，来训练一个模型以可靠地解混多重染色并生成染色分割图。我们通过在 7 重 IHC 图像的 mIHC 数据集上的实验，证明了所提方法的有效性。

**关键词（Index Terms）**：颜色解卷积；深度学习；多重；免疫组织化学；染色解混；自监督；半监督

---

## I. 引言

免疫组织化学（immunohistochemistry, IHC）利用抗体，结合灵敏的试剂，来检测组织切片中特定蛋白质的存在。IHC 仅能检测单一生物标志物，而多重免疫组织化学（multiplexed immunohistochemistry, mIHC）则扩展了 IHC，允许在同一张组织切片内同时染色多种生物标志物。通过对不同生物标志物使用颜色不同的染色剂（显色剂）的抗体，mIHC 图像能够对肿瘤微环境（tumor microenvironment, TME）给出更精细的表征。借助这类图像，我们可以刻画不同细胞表型群体的密度、它们的空间关系以及共定位情况。所有这些特征随后都可以与疾病诊断、预后和/或生存率相关联，从而帮助制定有效的治疗策略 [1]–[11]。

传统 IHC 每张玻片只染色一种生物标志物，而 mIHC 是一种多重成像技术，每张玻片可同时染色多达 10 个靶标 [6], [12]–[16]。这使得对肿瘤微环境（TME）的分析大为丰富。此外，由于无需任何专用扫描仪或软件，明场 mIHC 成为一种对大规模分析颇具吸引力的多重成像方案 [6], [12], [16]。然而，分析由此得到的 mIHC 图像并不简单。其中一个关键步骤是**解混染色**，即从单张 mIHC 图像中恢复所有生物标志物的染色浓度图，从而使我们能够定位不同生物标志物所在的位置（见图 1 和图 2）。但这是一个不适定的逆问题。当生物标志物数量大于 2 时，它需要求解一个欠定线性方程组，因而具有无穷多解。在本工作中，我们攻克了 mIHC 自动颜色解卷积这一难题，即将图像分解为其组成染色并生成染色分割图 [13], [16], [17]。

传统上，该问题通过颜色解卷积来求解，即将原始图像分解为彼此分离的染色浓度图。基于这些逐像素的浓度图，可以判定每个像素上哪种染色占主导，从而构成一张多标签的语义掩膜，称为**染色分割图**。图示见图 2。

若干无监督颜色解卷积方法 [18]–[21] 已被应用于传统 IHC 图像的分析。将其扩展到染色数量更多的 mIHC 并非易事。它涉及求解一个欠定线性方程组，可能产生许多不理想的解。为解决这一问题，[22], [23] 提出了 lasso 回归模型，以寻找具有稀疏浓度图的解。然而结果并不令人满意，主要原因是这些方法独立地处理各个像素，未能考虑上下文信息。有些方法选择为下游任务进行隐式解卷积 [24], [25]，即将图像分解为多个通道，但这些通道并不保证与不同的生物标志物一一对应。[26] 提出了一种弱监督深度学习方法，其中解卷积方法以点标注（dot annotation，标注不同生物标志物细胞的中心）进行监督。然而，该模型的性能高度依赖于对细胞中心的大量人工标注，因而在实践中极为耗时。

在本文中，我们提出了一种新颖的、无需标注的、自监督的深度学习方法，用于多重颜色解卷积，它能够扩展到更多数量的染色，且无需耗时的细胞人工标注。与传统颜色解卷积方法类似，我们唯一需要的监督是每个生物标志物手工挑选的颜色样本。给定一张多重图像和参考染色颜色，模型学习为每种染色生成一张浓度图，使得它们的组合能够重建出该 mIHC 图像。浓度图表示 mIHC 图像中染色色素的强度，据此我们可以导出相应生物标志物的染色分割图。我们的方法使用卷积神经网络，因而能够恰当地利用上下文信息，而不是独立地处理每个像素。

我们的模型学习预测各单一染色的浓度，使得它们的组合能够重建出 mIHC 图像。然而，在染色数量众多且没有训练标注的情况下，解并不唯一。换言之，不同的染色组合可以重建出相同的颜色。使用错误的组合会导致生物标志物的染色分割图出错。为应对这一挑战，我们引入了新颖的约束来限制解空间。更具体地说，我们提出了一种新颖的**逆重建损失（Inverse Reconstruction Loss）**，帮助网络仅使用参考染色颜色就学习到高质量的染色浓度图。我们通过定量与实证的方式展示了本方法的效力；即便没有任何标注，我们的方法也能生成与全监督方法相当的、高质量的浓度图和染色分割图。

然而，由于染色存在变异，且细胞可以同时表达多种生物标志物，仍存在需要专家监督来提升性能的情形。为此，我们提出了一种半监督方法。该方法利用大量无标注数据，同时通过一组相对较小的弱标注向专家学习。我们的方法表现具有竞争力，有时甚至优于全监督方法，因为它能够进一步从大量可用无标注图像的变异中学习。此外，我们提出的自监督方法可用作预训练步骤来生成初始标注。这样，病理学专家只需修正错误的预测，而不必从头标注。对自监督方法预测结果的评估显示，其性能与全监督相当。这证明了它在初始化训练数据标注方面的可靠性，从而加快了标注速度并降低了成本。由此得到的标注可用于从头训练半监督模型，或用于微调预训练模型。总结而言，我们的贡献是：

- **一种无需标注的自监督颜色解卷积方法。** 据我们所知，我们提出的方法是首个能扩展到 4 重以上染色、且性能可与有监督方案相媲美的方法。
- **为避免不适定颜色解卷积问题中的错误解，我们提出了一种新颖的逆重建损失来约束模型。**
- **我们将自监督方案扩展到半监督设置**，通过为带标注图像引入损失项，并研究了结合有监督与自监督损失的最佳方式。
- **我们将半监督方法与一种最先进（SoTA）的集成方法相结合**，用于多重 IHC。其结果是一个新的 SoTA 染色解混方案。

实验表明，我们的方法能够有效扩展到 7 重明场多重 IHC 图像。同时，半监督方案使我们能够利用专家知识，同时最小化标注成本，并达到新的最先进（SoTA）性能。

本工作是我们此前初步工作 [27] 的一次实质性扩展。那篇会议论文仅关注自监督设置（即第一、第二项贡献）。我们通过将自监督方法扩展为半监督方案，拓展了原有工作，从而创造出一个能够高效且准确地对多重 IHC 图像进行标注的强大算法。这一算法扩展采用了一项先前有监督方法 [26] 的监督损失。然而，直接引入该监督损失并不有效。通过充分的实证评估，我们提出了一种自监督损失项与监督损失的组合方式，以最大程度地利用有限的标注数据。

---

## II. 相关工作

颜色解卷积是一个经典问题，在通常含一种蛋白质生物标志物外加一种复染的 IHC 图像上已被广泛研究。为解决这一问题，大多数方法使用光密度（optical density, OD）颜色表示。在该表示中，IHC 图像中呈现的颜色是底层染色浓度的线性组合。光密度空间中的线性方程组将参考染色向量与染色浓度图联系起来 [21]。详见第 III 节。继 [21] 之后，人们提出了多种 IHC 颜色解卷积方法 [19], [20], [28]–[31]。

染色技术一直在快速发展。多重染色如今能够在同一张组织切片上同时染色 2 种以上的生物标志物。明场 mIHC 允许多种生物标志物 [6], [12]–[16] 在同一图像中同时可视化。随着多重染色数量的增加，颜色解卷积问题变得更具挑战性，而为 IHC 数据开发的方法并不能自然地扩展到 mIHC 领域。原因之一是，基于光密度的线性方程组变为欠定，众多解都能满足该方程组。[22], [23] 提出了 [21] 的一个扩展，通过使用 lasso 回归施加稀疏性先验来支持 2 种以上生物标志物。然而，当生物标志物超过 4 种时，稀疏性先验无法达到好的解，主要因为它独立地处理所有像素，因而未能考虑每个像素周围的上下文信息。

深度学习已被用于解决该问题。在 [26] 中，使用卷积自编码器以有监督方式估计浓度图。[13] 提出了一种结合自编码器与 UNet 的集成方法，以利用两种架构各自的优势。然而，这些有监督方法仍然需要大量标注，在实践中可能难以为继。为完整起见，我们也提及那些将颜色解卷积直接纳入下游任务的方法 [24], [25]，例如组织分割。然而，这些方法没有监督，因而无法保证捕获不同的染色浓度图。

---

## III. 预备知识

本节描述在比尔–朗伯定律下染色与其浓度之间的关系，这是包括我们在内的大多数颜色解卷积方法的基础。

### 比尔–朗伯定律下的线性染色混合

光密度（OD）衡量光穿过介质时的吸光度。像素 i 处的光密度记为 $y_i$，是其归一化 RGB 值 $[r_i, g_i, b_i]^\top \in [0,1]^3$ 的负对数：

$$y_i = [-\log r_i,\ -\log g_i,\ -\log b_i]^\top \tag{1}$$

比尔–朗伯定律（Beer Lambert Law, BL）规定，染色及其浓度在 OD 空间中呈线性关系。假设给定一组 m 个染色向量，其 OD 向量由矩阵 $S = [s_1, s_2, \cdots, s_m] \in \mathbb{R}^{3\times m}$ 表示，其中 $s_j \in \mathbb{R}^3$ 是第 j 种染色的 OD 向量。根据比尔–朗伯定律 [32]，对任意像素 i，其光密度 $y_i$ 与染色浓度向量 $c_i$ 满足线性关系，即 $y_i = S \times c_i$，其中 $c_i \in \mathbb{R}^m$ 表示像素 i 处不同染色的浓度。推广到含 n 个像素的图像，我们得到：

$$Y = [y_1, \cdots, y_n] = S \times C \tag{2}$$

其中 $Y \in \mathbb{R}^{3\times n}$ 是图像中所有像素的光密度矩阵，$C = [c_1, \cdots, c_n] \in \mathbb{R}^{m\times n}$ 是相应的染色浓度矩阵。

**求解线性方程。** 染色混合最早由 [21] 使用比尔–朗伯定律建模。给定参考染色矩阵 S，可以通过求解线性方程组（式 (2)）恢复染色浓度。在实践中，染色颜色向量通过对每种染色及背景组织的代表性像素进行采样获得。背景颜色向量可防止背景组织被错误地计算为其他染色的混合。对于高于 2 重的染色，即当染色矩阵 S 由 m > 3 个染色向量（2 种染色加背景）构成时，线性方程组是欠定的，没有唯一解。为应对这一挑战，文献中提出了多种 mIHC 颜色解卷积方法。

---

## IV. 方法

在第 IV-A 节中，我们描述所提出的自监督颜色解卷积方法 **InverseAE**。接着在第 IV-B 节中，我们展示如何将该方法扩展到半监督设置，从而能够同时用有标注和无标注数据训练，仅用一小部分有标注数据即可达到 SoTA 性能。

### A. 用于自监督多重颜色解卷积的 InverseAE

在本工作中，我们提出 **InverseAE**，一种自监督的深度学习颜色解卷积方法（首次发表于我们的初步会议论文 [27]）。我们假设每个像素上存在一种主导染色，在最终的染色分割图中应将其分配给该像素。因此，我们所提出的方法被设计为能够产生有意义的染色浓度图，从中可以直接推断出每个像素的主导染色/生物标志物。它只需要一组多重染色图像和一组参考染色颜色向量。

我们使用一个自编码器，基于给定的染色向量 S，为输入图像 Y 生成估计的染色浓度图 C。自编码器使用重建损失训练：$\mathcal{L}_{\mathrm{recon}}(Y, C) = \mathrm{MSE}(Y, S \times C)$，其目标是求解式 (2)，其中 MSE 表示均方误差函数。该损失使用均方误差，将图像 Y 与由估计浓度图重建的图像 $S \times C$ 进行比较。当染色向量数量 m > 3 时，式 (2) 变为可能有无穷多解的欠定方程组。事实上在实践中，当我们仅用重建损失训练自编码器时，模型往往收敛到次优解。为此，我们提出**逆重建损失（Inverse Reconstruction Loss）**以施加额外约束。

逆重建损失实现了一种正则化训练机制：它促进这样一个解，即估计的浓度图 C，使其既能重建图像本身，也能重建其逆图像。换言之，同一个解也应使用逆染色颜色向量重建出逆图像；图示见图 3。

形式上，逆图像是由各像素的互补颜色向量构成的图像。对任意归一化 RGB 颜色向量为 $[r, g, b]^\top$（$0 \le r, g, b \le 1$）的像素，其逆颜色向量为 $[1-r, 1-g, 1-b]^\top$，其逆光密度为：

$$y_{\mathrm{inverse}} = [-\log(1-r),\ -\log(1-g),\ -\log(1-b)]^\top \tag{3}$$

类似地，$S_{\mathrm{inverse}}$ 是染色矩阵光密度 S 的逆光密度。为对式 (2) 的解进行正则化，我们将逆方程加入该方程组。

对每个像素：

$$y_{\mathrm{inverse}} = S_{\mathrm{inverse}} \times c \tag{4}$$

对整个图像：

$$Y_{\mathrm{inverse}} = S_{\mathrm{inverse}} \times C \tag{5}$$

逆重建正则化损失定义为：

$$\mathcal{L}_{\mathrm{inverse}}(Y, C) = \mathrm{MSE}\left(Y_{\mathrm{inverse}},\ S_{\mathrm{inverse}} \times C\right) \tag{6}$$

我们用上标 i 指代第 i 个样本。对所有无标注样本 $D_U$ 的总体损失函数为：

$$\sum_{i \in D_U} \left[ \mathcal{L}_{\mathrm{recon}}\left(Y^i, C^i\right) + \mathcal{L}_{\mathrm{inverse}}\left(Y^i, C^i\right) \right] \tag{7}$$

模型被训练以生成浓度图 C。当与染色矩阵 S 结合时，C 重建输入图像 Y。同时，当与逆染色矩阵 $S_{\mathrm{inverse}}$ 结合时，C 重建逆图像 $Y_{\mathrm{inverse}}$。我们在实验中展示这种正则化如何将预测推向好的解，即在任何位置，与所观测主导颜色相对应的染色获得最高浓度。这使我们能够推断出高质量的染色分割图，并取得接近有监督方案的评价分数。接下来我们描述逆正则化背后的原理。

**原理。** 选择逆重建作为正则化器并非随机之举。一个合适的正则化器需要两个性质：（I）存在一个同时满足原始图像和正则化器的解；（II）该正则化器通过消除次优解、促进期望解来添加限制解空间的约束。这两个性质促成了我们对逆重建的选择。

首先，一种颜色与其互补色（或逆色）之间存在特殊关系。当一个物体吸收某种特定颜色的光时，我们感知到该物体呈现互补色，反之亦然。事实上，这种关系可以定量地表述。可以证明，一种颜色与其逆色在 HSL 颜色空间中具有相同的饱和度。饱和度衡量色相偏离白色的程度 [33]，因而与存在的色素量即其浓度相关。这些观察表明，一种颜色与其逆色可以共享同一个浓度向量，分别相对于原始染色和逆染色而言。换言之，同一个 c 可以同时满足 $y = S \times c$ 和 $y_{\mathrm{inverse}} = S_{\mathrm{inverse}} \times c$。这就是我们所期望的性质 I。

其次，在 HSL 颜色空间中，一种颜色与其逆色具有相反的亮度。亮度定义为红、绿、蓝三个颜色分量中最小值与最大值的平均。可以证明，当一种颜色的亮度为 L 时，其逆色的亮度为 1 − L。类似地，我们将一种颜色的**吸收能力**定义为其红、绿、蓝吸光度中最小值与最大值的平均。那么按定义，其亮度与吸收能力呈负相关。因此，由于一种颜色与其逆色具有相反的亮度，它们也具有相反的吸收能力。这一性质使逆正则化能够消除解空间中很大一部分不期望的解，并促进良好的稀疏解（性质 II）。下面我们进一步解释。

比尔–朗伯定律允许一种颜色由多种颜色按各自浓度加权相加构成。因此，在 OD 空间中，一个像素的颜色可以由多种染色（而非该像素处真实存在的那种染色）相加组合而成，只要它们的红、绿、蓝 OD（吸光度）值分别加和等于该颜色的红、绿、蓝 OD 值即可。这是一个不期望的解。然而，只要没有任何染色是另一种染色的倍数函数，这个解在逆空间中就不会成立。我们可以用一个涉及白色/背景染色的简单例子来说明这一点。可以证明，在原始空间中，白色染色可以以任意浓度加入解混结果中。但在逆解混解中，这是不被允许的。代表白色或浅色背景组织的染色向量具有极低的吸光度。根据 BL，它可以被加入任何像素而不显著改变该像素的 OD。另一方面，在逆空间中，逆颜色将具有高吸光度。因此，若被盲目地加入任何像素，它会显著改变该像素的 OD。这样，逆正则化有助于避免许多此类不期望的解，并促进好的解。

上述讨论论证了逆正则化如何带来对收敛到好的解至关重要的特殊性质，从而产生高准确率的染色分割图。

### B. 半监督多重颜色解卷积

虽然所提出的无需标注的自监督方法充分利用了无标注图像，但它在没有监督训练的情况下无法达到理想性能。本节讨论如何将该方法扩展到半监督设置。也就是说，通过加入一小部分有标注图像（即有限的人工输入），我们可以取得令人满意的颜色解卷积性能。正如实验部分将展示的，我们提出的方法 **Semi-Unmix-AE** 使模型能够用少得多的标注图像匹配全监督模型的性能。

为高效获取人工标注，我们使用**点标注（dot annotations）**，即标记细胞中心的点。每个点还带有一个与之关联的类别/染色标签。这种标注形式提供弱监督，以避免人工分割标签的负担。为将点标注用于逐像素监督，我们使用超像素算法 SLIC [34] 将其扩展到具有相似染色的邻近像素。每个点标签扩展到它所在的超像素区域。整个超像素随后被标记为该点的染色。这样便得到一张逐像素的伪分割图，其中每个像素被标记为某一种染色或背景。图示见图 4。

在训练期间，对于每张有标注图像，我们使用伪分割图来监督预测的浓度图。该损失称为**标签一致性损失（label consistency loss）**，它同样是一种重建损失。在每个像素处，使用来自伪分割图（图 4e）的标签染色来重建该像素颜色。标签一致性损失最小化重建图像与输入图像之间的距离。换言之，标签一致性损失训练模型生成这样的浓度图：在每个位置，标签染色具有最大的浓度，使得它本身就能在很大程度上重建出该多重图像像素。记 $\ell_i$ 为像素 i 处标签染色的独热（one-hot）向量，令 $L = [\ell_1, \cdots, \ell_n]$。标签一致性损失为：

$$\mathcal{L}_{\mathrm{label}}(Y, C) = \mathrm{MSE}\left(Y,\ S \times (L \odot C)\right) \tag{8}$$

其中 "⊙" 表示哈达玛积（Hadamard product）。

我们的总训练损失是重建损失 $\mathcal{L}_{\mathrm{recon}}$、逆重建损失 $\mathcal{L}_{\mathrm{inverse}}$ 和标签一致性损失 $\mathcal{L}_{\mathrm{label}}$ 之和。重建损失应用于所有图像，无论有标注还是无标注。逆重建损失应用于所有无标注图像 $D_U$。标签一致性损失应用于所有有标注图像 $D_L$。形式化地：

$$\mathcal{L}_{\mathrm{semi}}(D_U, D_L) = \sum_{i \in D_U \cup D_L} \mathcal{L}_{\mathrm{recon}}\left(Y^i, C^i\right) + \sum_{i \in D_U} \mathcal{L}_{\mathrm{inverse}}\left(Y^i, C^i\right) + \sum_{i \in D_L} \mathcal{L}_{\mathrm{label}}\left(Y^i, C^i\right) \tag{9}$$

有了这一总损失，网络学习生成这样的解：标签染色在相应像素处具有最高浓度。图 5 展示了模型架构与训练过程。需要指出的是，虽然逆重建损失既可以应用于有标注图像也可以应用于无标注图像，我们选择仅将其应用于无标注数据。我们假设：由于标签的作用是纠正模型感知和区分染色的方式，因此在同一数据上同时应用逆重建损失和标签一致性损失可能会在训练中产生冲突，从而可能降低模型区分不同染色的能力。我们在消融研究中对此做了更详细的探讨。

---

## V. 实验

我们在有标注和无标注数据上评估我们的方法，以展示所提出的自监督方法以及半监督方案的重要性。为此，我们既评估导出的染色分割图的质量，也评估预测的染色浓度图。我们与多种基线方法进行比较。结果表明，我们提出的自监督方法与 SoTA 有监督方案相比具有竞争性；此外，我们的半监督方法通过提升先前 SoTA 集成染色解混方法 [13] 的性能，成为新的 SoTA。此外，我们呈现了一组消融研究，以证明所提方案的效力。

### A. 实验设置

我们在 7 重 mIHC 染色的胰腺癌组织上进行实验。共有 7 种生物标志物，包括免疫细胞生物标志物：CD3（黄色）、CD4（青色）、CD8（紫色）、CD16（黑色）、CD20（红色），一种肿瘤生物标志物（棕色），此外还有作为核复染的苏木精（蓝色）。训练和评估中使用的点标注由一位病理学家人工设定。每个点标记一个细胞的中心，并被赋予单一染色标签，该标签是识别该细胞类型的生物标志物所对应的染色，推测也是该细胞中浓度最高的染色。

**有标注训练数据。** 训练集由来自 6 张全切片图像的 60 个有标注图像块构成。图像块在 40× 下尺寸为 1200×1920。来自 4 个病例的 40 个图像块用于训练，其余来自另外 2 个病例的 20 个图像块用于验证。对每种深度学习方法，训练重复 3 次，我们报告均值与标准差。每次使用不同的一对病例作为验证集，其余 4 个用于训练。训练图像被缩放到 20× 并切成 400 × 400 的重叠图像块，共得到 240 个有标注训练图像块。

**无标注训练数据。** 对于半监督训练，我们从另外 7 个病例中提取了额外的无标注图像块。每个病例随机选取 60 个 20× 下尺寸为 400 × 400 的图像块，共得到 420 个额外图像块。

**对比模型。** 我们比较所提出的方法：（i）**InverseAE**：自监督模型。它在 240 张有标注图像上训练，但不使用标签。（ii）**InverseAE+**：与 InverseAE 类似，如前所述用 240 张图像训练，再加上额外收集的无标注训练数据。该模型与半监督模型 Semi-Unmix-AE（见下）具有可比性，因为它在同一组图像上训练。（iii）**Semi-Unmix-AE**：所提出的半监督方法。它同时使用前述有标注数据和额外的无标注训练数据训练。表 VI 展示了模型架构。这些方法与以下方法进行比较：

- **无监督基线**：（i）**LassoReg**：[22] 中描述的 lasso 回归方法，设计用于 4 重以上多重染色图像。我们使用 L1 范数权重 λ = 10⁻³。（ii）**PseudoInv**：[21] 针对颜色解卷积的扩展，对超过 3 个染色向量的情形使用 S 的伪逆求解方程 $C = S^{-1} \times Y$。（iii）**最近邻（Nearest Neighbor）**：一个简单基线，为每个像素分配颜色距离最短的生物标志物。
- **弱监督基线**：（i）**ColorAE** [26]：弱监督方法。它在 240 个有标注图像块上训练。（ii）**UNet**：基于 UNet 模型架构 [36] 的深度学习模型。它是一种有监督方法。这里输出不是染色浓度图，而是似然图。对每个像素，输出是该像素属于各染色类别的概率。训练期间，超像素标注图被用作金标准标签。
- **集成方法**：（i）**Union anchor AE** [13]：SoTA 染色解混方法。它结合 UNet 和 ColorAE 的预测，同时利用交叉熵损失和图像重建损失。（ii）**Union anchor Semi-AE**：将前一个集成中的 ColorAE 替换为 Semi-Unmix-AE。它被证明是新的 SoTA。

**生成染色分割图。** 为计算染色分割图（图 2），我们假设每个像素上存在单一主导染色。在推理时，每张染色浓度图先使用滞后阈值（hysteresis thresholding）处理，然后应用 argmax 函数在每个位置选出浓度最大的染色。这样，所得分割图在每个像素上被赋予单一染色/生物标志物，反映了该位置预测的主导染色。滞后阈值确保对每种染色我们只获得高置信度存在该染色的区域，然后将其扩展以覆盖更大的细胞面积。阈值参数对每种染色固定，并在一个小的留出集上经验性地选取。对于有监督和半监督方法，预测的染色浓度图具有更高的置信度（图 9）。因此，我们可以直接应用 argmax 函数。对于 UNet，在每个像素选择预测似然最高的染色。

### B. 评价指标

**使用点标注评估。** 我们在来自 42 个测试病例的 96 个尺寸为 1200 × 1920 的图像块上测试模型。这些测试图像块对每种生物标志物都有人工点标注，标注标记了细胞的大致中心。我们使用该测试数据评估模型捕获逐像素主导染色的准确率。我们从各模型的预测生成染色分割图。每种生物标志物/细胞类型的 F 分数按如下计算：真阳性是与某个标注点相交的预测分割区域；假阴性是不与任何标注点相交的预测分割区域；假阴性是不与任何预测分割区域相交的标注点。这使我们能够评估预测浓度图用于直接下游分析的质量。结果见表 I。

**与伪金标准浓度图的比较。** 我们希望评估训练模型生成的浓度图的质量，然而该问题没有金标准。因此在这项评估中，我们使用单染 IHC 图像来评估我们的解卷积结果。这些单染 IHC 图像是经典的、相对简单的；它们只有用于细胞核的苏木精染色和另一种感兴趣的生物标志物。在此类单染玻片上，我们使用传统解卷积方法（Vahadane [20] 和 Bayesian K-SVD [18]）提取染色浓度图。其假设是：在此类单染样本上，使用 IHC 颜色解卷积方法得到的解卷积结果是相当可靠的，可用作伪"金标准"。而我们的模型会将这些图像视为多重 IHC 图像，从而使我们能够评估其解卷积性能。我们使用结构相似性指数（SSim）将我们的多重模型生成的浓度图与 [20] 和 [18] 生成的结果进行比较。结果见表 IV。所有平均分数都在 0.8 以上，表明所有模型性能可靠。在我们的实验中，Bayesian-K-SVD 似乎在几乎所有 CD16 图像上都解卷积失败。这就是表 IV 中相应列留空的原因。

**模型复杂度。** 所提方法使用一个轻量级模型，约有 200K 个可训练参数。实验在 RTX 8000 GPU 上运行。模型处理一张 900x600 的测试图像约需 1.5 秒，每个 epoch 的训练时间约为 94.7 秒/epoch。

### C. 自监督模型 InverseAE 的结果

**F 分数评估。** 表 I 展示了将预测与金标准点标注进行比较的 F 分数结果。我们的方法在自监督/无监督设置下表现更优。基线方法最近邻和 LassoReg 略逊于 InverseAE，而 PseudoInv 未能给出有意义的浓度图。虽然 InverseAE 表现优于 UNet，但正如预期，它并未超过有监督模型 ColorAE 和 Union Anchor AE 集成，不过其性能具有竞争力。在 InverseAE+ 中加入更多无标注训练数据并未带来显著提升。

**SSim 评估。** 表 IV 展示了在单染玻片上的 SSim 结果。除黑色巨噬细胞 CD16 外，所有分数都在 0.8 以上；CD16 可能具有挑战性，因为它往往不均匀且杂乱。见图 6（B 和 F）。

**消融研究：InverseAE 的设计选择。** 我们针对自监督模型 InverseAE 的设计选择进行消融研究。表 II 展示了在 96 个有标注图像块上、使用本方法各种变体的 F 分数结果。

首先，结果显示了逆重建损失的重要性。没有它时（第 1–3 行），预测图不能代表 mIHC 图像中视觉上存在的染色。这从极低的 F 分数中可以清楚看出。其次，将逆重建损失替换为 L1 稀疏约束（第 2 行）不足以得到有代表性的浓度图。我们注意到预测中存在稀疏性，但预测与所观测到的染色并不相关。我们发现预测中的主导染色主要是 CD3 的黄色和 CD8 的紫色，而肿瘤（棕色）和 CD16（黑色）生物标志物缺失，这从表中它们为零的 F 分数可以佐证。第三，我们用逆图像和逆染色作为数据增强（第 3 行）来替代逆正则化损失。我们观察到，与 L1 稀疏约束（第 2 行）相比性能略有提升，但它同样存在预测浓度图中生物标志物缺失的问题。最后，去掉条件自编码器（第 4 行），即在不提供目标染色条件输入的情况下一次性预测所有染色，分数更低且模型泛化不佳。条件输入可防止模型过拟合，并使模型更好地捕获图像中的目标染色。

### D. 半监督方法的结果

**F 分数评估。** 我们评估半监督方法，并在表 I 中报告相对于点标注的结果。Semi-Unmix-AE 在有监督和无监督方法中取得了最佳 F 分数。这证明了逆重建损失如何能够利用引入无标注数据所带来的变异来进一步提升性能。

**集成模型。** 表 I 中表现最好的模型是集成模型（最后 2 行）。我们尝试用 Semi-Unmix-AE 替换 Union Anchor AE [13] 中的 ColorAE。我们将该模型称为 **Union anchor Semi-AE**（表 I 最后一行）。使用 Semi-Unmix-AE 进一步提升了性能，并产生了新的 SoTA 模型。这些结果支持了我们关于所提半监督学习方法价值的论断。

**SSim 评估。** 预测质量进一步通过 SSim 分数评估。Semi-Unmix-AE 取得了最佳分数，尤其是对于更具挑战性的染色：棕色（肿瘤）和黑色（CD16 巨噬细胞），其性能提升更为显著。它在所有染色上也具有最高的平均 SSim。

**消融研究：半监督训练中有标注数据的数量。** 我们评估有标注与无标注训练数据量之间的权衡。我们在如前所述相同的数据上训练 5 个不同的模型，只是对于有标注图像，每个模型只用其中一部分图像的标签训练，其余被视为无标注。我们与使用 10%、30%、50% 和 70% 有标注图像训练的模型进行比较，见表 III。若查看表中的平均 F 分数，我们观察到 10% 模型的性能非常接近自监督模型 InverseAE。30% 和 50% 模型的性能非常接近弱监督模型 Semi-Unmix-AE。70% 和 100% 模型的性能则同时超过了 InverseAE 和 ColorAE。这证实了我们的假设：这两个损失相互补充。见图 7 中的曲线图。

**消融研究：逆重建损失在有标注数据上的权重。** 我们探索如何最好地对半监督模型中的训练建模。由式 9，我们仅将 $\mathcal{L}_{\mathrm{inverse}}$ 应用于无标注训练数据。为得出这一设计决策，我们针对 $\mathcal{L}_{\mathrm{inverse}}$ 应用于有标注数据时的权重 λ 进行了消融研究。在表 V 中，我们比较了以 λ ∈ {1, 0.75, 0.5, 0.25, 0} 训练的模型。我们发现最佳性能出现在 λ = 0 时，最差出现在 λ = 1 时。随着 λ 从 0 增至 1，性能逐渐恶化。我们认为这是由于在同一图像上应用有监督与自监督损失时二者产生冲突。监督的作用应是引导模型去修正那些仅凭自监督损失会出错的问题。观察平均值一列，性能随 λ 增大而单调下降。这些结果支持了我们的模型设计决策。

**消融研究：对伪分割标签变化的敏感性。** 我们评估伪分割标签生成算法变化带来的影响。在表 VII 中，我们展示了改变 SLIC 算法中紧凑度（compactness）参数以及使用 SAM 生成分割标签的效果。图 10 展示了使用不同变体得到的染色伪分割标签之间的差异。我们评估了有监督方法，即 UNet、ColorAE 和 Semi-Unmix-AE，并观察到对每种配置，三个模型的相对性能相似。最佳性能使用 compactness=10 的 SLIC，这也是我们在实验中采用的配置。此外，Semi-Unmix-AE 对伪标签的变化最不敏感，这支持了无监督损失分量的有效性。

值得一提的是，使用 SAM 生成分割标签有不同策略。我们探索了以下三种：

- 使用每种染色的所有正、负标签，即使用该染色的点标注作为正输入坐标，其他染色作为负坐标。
- 对每种染色只使用正标签，即提交该染色的所有点标注作为正输入坐标，不提供负输入。
- 对每种染色只使用正标签，每次只提交一个点的坐标，并分别获取每个点的结果。

我们发现最后一种策略提供了最合理的伪金标准分割图，我们将其用于训练。

**消融研究：模型架构的变化。** 模型架构见表 VI。在自编码器的设计中，我们考虑到它容易对输入中的颜色值过拟合。为此我们为网络选择了适中的深度和宽度，以避免过拟合并同时能够捕获关键特征。我们展示了增加自编码器深度与宽度的效果。所研究的配置见表 IX。在配置 B 和 C 中，我们尝试增加网络宽度，各层的通道数分别翻倍或变为四倍。在配置 D 中，我们通过编码器和解码器各增加一个模块来增加网络深度。在配置 E 中，我们同时将通道数翻倍并增加深度。我们在测试集上评估不同架构，并在表 VIII 中展示 F 分数。我们观察到，无论增加宽度（配置 B 和 C）还是深度（配置 D），性能都会下降，而同时增加二者（配置 E）则完全失败。这表明模型过拟合，其泛化到未见数据的能力下降，从而支持了我们对模型架构的选择。

**定性结果。** 不同方法的示例结果可视化于图 8 和图 6。从图 8 中我们观察到，在所有评估方法中，InverseAE、ColorAE 和 Semi-Unmix-AE 的分割图与样本图像块中所见的真实染色最为一致。在图 6 中更细致地比较这三种方法，我们看到 InverseAE 有时会漏掉浅染色或混淆光谱重叠紧密的颜色。Semi-UnmixAE 能够利用额外的无标注数据来避免 InverseAE 和 ColorAE 所犯的错误。图 9 展示了 InverseAE 和 Semi-UnmixAE 生成的原始浓度图。样本反映出 Semi-UnmixAE 在真实染色区域的预测置信度更高，这正是其染色分割图质量更高的原因。

---

## VI. 结论

随着明场多重 IHC 中同时染色数量的不断增加，以及其技术和经济可及性方面的优势，在实践中将所得多重图像分解为单个染色以进行分析仍然颇具挑战。在本工作中，我们攻克了染色数量相对较多的多重 IHC 图像中的颜色解卷积问题。我们同时提出了自监督与半监督方法。我们所提出的方法对病理学家的投入要求很低，其结果可直接用于获得染色分割图，捕获每个位置潜在的主导染色。从而将明场多重 IHC 转变为一种可用于研究与分析的实用多重染色方案。

## 致谢

本工作得到以下资助：美国国家科学基金会（NSF）资助 CCF-2144901，美国国立卫生研究院（NIH）资助 R01GM148970，NIH 与美国国家癌症研究所（NCI）资助 UH3-CA22502103、3U24CA215109-02、1UG3CA225021-01 和 R01CA253368，NIH 资助 DP2CA280625，AACR 胰腺癌研究职业发展奖，Pew 癌症研究学者项目，Pershing Square Sohn 奖，以及 Robert L. Fine 癌症研究基金会；此外还获得 Bob Beals 与 Betsy Barton 的慷慨私人支持。我们感谢石溪癌症中心生物样本库提供去标识化组织标本，感谢纽约州立大学石溪分校研究基金会。

---

## 参考文献

[1] Babu S, Horowitz M, Delgado-Coka LA, Roa-Peña L, Akalin A, Escobar-Hoyos LF, and Shroyer KR, "Keratin 17 and A2ML1 are negative prognostic biomarkers in non-small cell lung cancer," *Pathology - Research and Practice*, vol. 263, p. 155643, 2024.
[2] Jiao Y, Chen L, Zhang J, and et al., "Multiplex immunohistochemistry defines the tumor immune microenvironment and immunotherapeutic outcome in CLDN18.2-positive gastric cancer," *BMC Med*, vol. 20, no. 223, 2022.
[3] Ilié M, Beaulande M, Ben Hadj S, Chamorey E, Schiappa R, Long-Mira E, Lassalle S, Butori C, Cohen C, Leroy S. et al., "Chromogenic multiplex immunohistochemistry reveals modulation of the immune microenvironment associated with survival in elderly patients with lung adenocarcinoma," *Cancers*, vol. 10, no. 9, p. 326, 2018.
[4] Johnson DB, Bordeaux J, Kim JY, Vaupel C, Rimm DL, Ho TH, Joseph RW, Daud AI, Conry RM, Gaughan EM et al., "Quantitative spatial profiling of PD-1/PD-L1 interaction and HLA-DR/IDO-1 predicts improved outcomes of anti–PD-1 therapies in metastatic melanoma," *Clinical Cancer Research*, vol. 24, no. 21, pp. 5250–5260, 2018.
[5] Remark R, Merghoub T, Grabe N, Litjens G, Damotte D, Wolchok JD, Merad M, and Gnjatic S, "In-depth tissue profiling using multiplexed immunohistochemical consecutive staining on single slide," *Science Immunology*, vol. 1, no. 1, pp. aaf6925–aaf6925, 2016.
[6] Tan WCC, Nerurkar SN, Cai HY, Ng HHM, Wu D, Wee YTF, Lim JCT, Yeong J, and Lim TKH, "Overview of multiplex immunohistochemistry/immunofluorescence techniques in the era of cancer immunotherapy," *Cancer Communications*, vol. 40, no. 4, pp. 135–153, 2020.
[7] Stack EC, Wang C, Roman KA, and Hoyt CC, "Multiplexed immunohistochemistry, imaging, and quantitation: A review, with an assessment of tyramide signal amplification, multispectral imaging and multiplex analysis," *Methods*, vol. 70, no. 1, pp. 46–58, 2014.
[8] Jiménez-Sánchez D, Ariz M, Chang H, Matias-Guiu X, de Andrea CE, and Ortiz-de Solorzano C, "NaroNet: Discovery of tumor microenvironment elements from highly multiplexed images," *Medical Image Analysis*, vol. 78, p. 102384, 2022.
[9] Cohen E, Wang D, Engle E, Green B, Caushi J, Zhang J, Sunshine J, Uttam S, Fotheringham M, Fiorante A. et al., "CD8+ FoxP3+ cells represent early, effector T-cells and predict outcomes in patients with resectable non-small cell lung carcinoma (NSCLC) receiving neoadjuvant anti-PD-1-based therapy," *Journal for ImmunoTherapy of Cancer*, vol. 10, 2022.
[10] Jiménez-Sánchez D, López-Janeiro Á, Villalba-Esparza M, Ariz M, Kadioglu E, Masetto I, Goubert V, Lozano MD, Melero I, Hardisson D. et al., "Weakly supervised deep learning to predict recurrence in low-grade endometrial cancer from multiplexed immunofluorescence images," *NPJ Digital Medicine*, vol. 6, no. 1, p. 48, 2023.
[11] Wu E, Wu Z, Mayer AT, Trevino AE, and Zou J, "Pepsi: Pomaging suggest immune cell engagement," in *Pacific Symposium on Biocomputing*, 2024, pp. 492–505.
[12] Harms PW, Frankel TL, Moutafi M, Rao A, Rimm DL, Taube JM, Thomas D, Chan MP, and Pantanowitz L, "Multiplex immunohistochemistry and immunofluorescence: A practical update for pathologists," *Modern Pathology*, vol. 36, no. 7, p. 100197, 2023.
[13] Fassler D, Abousamra S, Gupta R, Chen C, Zhao M, Paredes D, Batool SA, Knudsen B, Escobar-Hoyos L, Shroyer K, Samaras D, Kurç T, and Saltz J, "Deep learning-based image analysis methods for brightfield-acquired multiplex immunohistochemistry images," *Diagnostic Pathology*, vol. 15, 2020.
[14] Hofman P, Badoual C, Henderson F, Berland L, Hamila M, Long-Mira E, Lassalle S, Roussel H, Hofman V, Tartour E, and Ilie M, "Multiplexed Immunohistochemistry for Molecular and Immune Profiling in Lung Cancer—Just About Ready for Prime-Time?" *Cancers (Basel)*, vol. 11, no. 3, Feb 2019.
[15] Dixon A, Bathany C, Tsuei M, White J, Barald K, and Takayama S, "Recent developments in multiplexing techniques for immunohistochemistry," *Expert Rev. Mol. Diagn*, vol. 15, no. 9, pp. 1171–1186, 2015.
[16] Taube JM, Sunshine JC, Angelo M, Akturk G, Eminizer M, Engle LL, Ferreira CS, Gnjatic S, Green B, Greenbaum S. et al., "Society for immunotherapy of cancer: updates and best practices for multiplex immunohistochemistry (IHC) and immunofluorescence (IF) image analysis and data sharing," *Journal for ImmunoTherapy of Cancer*, vol. 13, no. 1, p. e008875, 2025.
[17] Van Herck Y, Antoranz A, Andhari MD, Milli G, Bechter O, De Smet F, and Bosisio FM, "Multiplexed immunohistochemistry and digital pathology as the foundation for next-generation pathology in melanoma: Methodological comparison and future clinical applications," *Frontiers in Oncology*, vol. 11, 2021.
[18] Pérez-Bueno F, Serra JG, Vega M, Mateos J, Molina R, and Katsaggelos AK, "Bayesian K-SVD for H and E blind color deconvolution. Applications to stain normalization, data augmentation and cancer classification," *Computerized Medical Imaging and Graphics*, vol. 97, p. 102048, 2022.
[19] Macenko M, Niethammer M, Marron J, Borland D, Woosley J, Guan X, Schmitt C, and Thomas N, "A method for normalizing histology slides for quantitative analysis," in *IEEE International Symposium on Biomedical Imaging: From Nano to Macro*, 2009.
[20] Vahadane A, Peng T, Sethi A, Albarqouni S, Wang L, Baust M, Steiger K, Schlitter AM, Esposito I, and Navab N, "Structure-preserving color normalization and sparse stain separation for histological images," *IEEE Transactions on Medical Imaging*, vol. 35, no. 8, pp. 1962–1971, Aug 2016.
[21] Ruifrok A. and Johnston D, "Quantification of histochemical staining by color deconvolution," *Anal Quant Cytol Histol*, vol. 23, 01 2001.
[22] Chen T. and Chefd'hotel C, "Deep learning based automatic immune cell detection for immunohistochemistry images," in *Machine Learning in Medical Imaging*, 2014.
[23] Chen T. and Srinivas C, "Group sparsity model for stain unmixing in brightfield multiplex immunohistochemistry images," *Computerized Medical Imaging and Graphics*, vol. 46, pp. 30–39, 2015.
[24] Duggal R, Gupta A, Gupta R, and Mallick P, "SD-layer: Stain deconvolutional layer for CNNs in medical microscopic imaging," in *MICCAI*, 2017.
[25] Lahiani A, Gildenblat J, Klaman I, Navab N, and Klaiman E, "Generalizing multistain immunohistochemistry tissue segmentation using one-shot color deconvolution deep neural networks," *CoRR*, vol. abs/1805.06958, 2018.
[26] Abousamra S, Fassler D, Hou L, Zhang Y, Gupta R, Kurc T, Escobar-Hoyos LF, Samaras D, Knudson B, Shroyer K, Saltz J, and Chen C, "Weakly-supervised deep stain decomposition for multiplex IHC images," in *IEEE 17th International Symposium on Biomedical Imaging (ISBI)*, 2020, pp. 481–485.
[27] Abousamra S, Fassler D, Gupta RR, Escobar-Hoyos L, Shroyer KR, Saltz JH, and Chen C, "Unsupervised stain decomposition via inversion regulation for multiplex immunohistochemistry images," in *International Conference on Medical Imaging with Deep Learning*, 2023.
[28] Alsubaie N, Raza S, and Rajpoot NM, "Stain deconvolution of histology images via independent component analysis in the wavelet domain," in *13th IEEE International Symposium on Biomedical Imaging, ISBI 2016*, Prague, Czech Republic, April 13–16, 2016, pp. 803–806.
[29] Alsubaie N, Trahearn N, Raza SEA, Snead D, and Rajpoot NM, "Stain deconvolution using statistical analysis of multi-resolution stain colour representation," *PLOS ONE*, vol. 12, no. 1, pp. 1–15, 01 2017.
[30] Hidalgo-Gavira N, Mateos J, Vega M, Molina R, and Katsaggelos A, "Blind color deconvolution of histopathological images using a variational bayesian approach," in *2018 IEEE International Conference on Image Processing, ICIP 2018*, Aug. 2018, pp. 983–987.
[31] Pérez-Bueno F, López-Pérez M, Vega M, Mateos J, Naranjo V, Molina R, and Katsaggelos A, "A TV-based image processing framework for blind color deconvolution and classification of histological images," *Digital Signal Processing: A Review Journal*, vol. 101, Jun. 2020.
[32] Lambert J, "Photometria sive de mensura et gradibus luminis colorum et umbrae augsburg," Detleffsen for the widow of Eberhard Klett, 1760.
[33] Agoston M, *Computer Graphics and Geometric Modelling: Implementation & Algorithms*, Springer London, 2005, pp. 301–306.
[34] Achanta R, Shaji A, Smith K, Lucchi A, Fua P, and S. Süsstrunk, "SLIC superpixels compared to state-of-the-art superpixel methods," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 34, no. 11, pp. 2274–2282, Nov 2012.
[35] Kirillov A, Mintun E, Ravi N, Mao H, Rolland C, Gustafson L, Xiao T, Whitehead S, Berg AC, Lo W-Y, Dollár P, and Girshick R, "Segment anything," *arXiv:2304.02643*, 2023.
[36] Ronneberger O, Fischer P, and Brox T, "U-Net: Convolutional networks for biomedical image segmentation," in *MICCAI*, 2015.

---

## 图表说明与数据

### 图注

**图 1.** 一张明场多重 IHC 图像示例（左）与由我们所提方法生成的染色分割图（右）。

**图 2.** 染色浓度图与推理流程示意。首先，模型生成染色浓度图。随后这些图经过阈值化操作处理，只保留每种染色中的感兴趣区域。最后，在每个像素处选出浓度最高的染色作为预测的像素标签，从而得到最终的染色分割图。

**图 3.** 所提出的逆正则化（inversion regulation）。模型生成染色浓度图。依据比尔–朗伯定律（BL），这些图连同参考染色向量（上排）被用于重建输入图像。类似地，使用相同的浓度图连同逆参考染色向量（下排）重建逆输入图像。重建损失同时施加于重建图像和逆图像上。这样，逆正则化便将解推向同时满足图像及其逆图像的浓度图。

**图 4.** 将点标注转换为伪分割标签。多重图像被转换为超像素。与点标注相交的超像素被赋予相应的点标签，从而构成训练中使用的伪分割标签。

**图 5.** 半监督模型架构与训练。模型的输出以输入 mIHC 图像和目标参考染色为条件。它以重建损失训练。此外，逆重建损失应用于无标注图像（下分支），标签一致性损失应用于有标注图像（上分支）。

**图 6.** 染色分割结果示例，将 InverseAE 与 Semi-UnmixAE（分别为我们所提出的无监督与半监督方案）与由点标注生成的伪分割标签以及 ColorAE（有监督方法）进行比较。在 B 和 D 中，当肿瘤棕色染色较浅时，无监督方法（InverseAE）会漏掉它，而半监督方法（Semi-UnmixAE）即使在浅染色下也能最好地捕获整个棕色区域。在 E 中，InverseAE 和 ColorAE 的预测遗漏了部分青色染色（CD4），但半监督模型能够捕获它们。此外，非常深的棕色被误预测为黑色染色（CD16），而在有监督模型中则被正确预测。在 (A) 中，InverseAE 将黑色染色（CD16）误判为棕色（肿瘤），将紫色（CD8）误判为红色（CD20）。另一方面，Semi-UnmixAE 捕获到了被 InverseAE 和 ColorAE 方法都遗漏的青色染色（CD4）。

**图 7.** 使用不同百分比的数据标注子集训练时，有监督与半监督染色分割 F 分数的曲线图。两个模型都用一部分有标注数据训练。半监督模型额外利用了无标注数据。半监督模型的 F 分数随标注量增加而呈上升趋势，而有监督方案的 F 分数由于标注有限而保持在一个区间内。

**图 8.** 不同方法的染色分割结果示例。

**图 9.** InverseAE 与 Semi-UnmixAE 预测的染色浓度图比较。与无监督结果相比，半监督结果更好地反映了可见染色，并在预测中表现出更高的置信度。

**图 10.** 使用 SLIC [34] 与 SAM [35] 不同配置得到的伪染色分割标签比较。在我们的实验中我们使用 compactness=10 的 SLIC。

---

### 表 I. 在来自 42 个病例的 96 个图像块上，相对于点标注的染色分割 F 分数

> 模型分为自监督/无监督、弱监督/半监督以及集成模型三组。每组内最佳结果以**粗体**标出，所有模型中的最佳结果以下划线标出。

| 方法 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| PseudoInv | 0.158 | 0.208 | 0.441 | 0.267 | 0.265 | 0.403 | 0.290 |
| 最近邻（Nearest Neighbor） | 0.223 | 0.168 | 0.734 | 0.277 | 0.106 | 0.357 | 0.311 |
| LassoReg | 0.456 | 0.501 | 0.801 | 0.050 | 0.223 | 0.389 | 0.404 |
| **InverseAE（本文）** | 0.596 ± 0.036 | 0.526 ± 0.029 | 0.799 ± 0.014 | 0.671 ± 0.028 | 0.317 ± 0.015 | 0.591 ± 0.029 | 0.583 ± 0.005 |
| **InverseAE+（本文）** | 0.581 ± 0.018 | 0.555 ± 0.052 | 0.793 ± 0.010 | 0.684 ± 0.011 | 0.321 ± 0.018 | 0.572 ± 0.053 | 0.585 ± 0.005 |
| UNet | 0.579 ± 0.060 | 0.541 ± 0.035 | 0.820 ± 0.025 | 0.712 ± 0.032 | 0.348 ± 0.145 | 0.566 ± 0.118 | 0.595 ± 0.059 |
| ColorAE | 0.645 ± 0.006 | 0.583 ± 0.035 | 0.837 ± 0.006 | 0.740 ± 0.020 | 0.404 ± 0.036 | 0.563 ± 0.044 | 0.629 ± 0.013 |
| **Semi-Unmix-AE（本文）** | 0.665 ± 0.019 | 0.597 ± 0.014 | 0.824 ± 0.006 | 0.734 ± 0.017 | 0.378 ± 0.008 | 0.659 ± 0.01 | 0.643 ± 0.007 |
| Union-anchor-AE | 0.707 ± 0.003 | 0.633 ± 0.007 | 0.871 ± 0.011 | 0.810 ± 0.020 | 0.436 ± 0.033 | 0.707 ± 0.020 | 0.694 ± 0.010 |
| **Union-anchor-Semi-AE（本文）** | 0.701 ± 0.013 | 0.633 ± 0.037 | 0.874 ± 0.010 | 0.815 ± 0.022 | 0.452 ± 0.051 | 0.736 ± 0.052 | **0.702 ± 0.018** |

### 表 II. 对自监督模型设计 InverseAE 的消融研究

> 在来自 42 个病例的 96 个图像块上，相对于点标注的染色分割 F 分数。

| 逆正则化 | 条件 AE | L1 稀疏 | 逆增强 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|---|---|---|
| | ✓ | | | 0.235 | 0.307 | 0.409 | 0.121 | 0.326 | 0.147 | 0.257 |
| | ✓ | ✓ | | 0.215 | 0.228 | 0.337 | 0.000 | 0.300 | 0.000 | 0.180 |
| | ✓ | | ✓ | 0.407 | 0.411 | 0.716 | 0.000 | 0.117 | 0.000 | 0.275 |
| ✓ | | | | 0.482 | 0.501 | 0.753 | 0.324 | 0.274 | 0.220 | 0.426 |
| ✓ | ✓ | | | 0.644 | 0.530 | 0.813 | 0.632 | 0.327 | 0.556 | 0.584 |

### 表 III. 使用不同比例有标注训练数据子集的半监督模型消融研究

> 在来自 42 个病例的 96 个图像块上，相对于点标注的染色分割 F 分数。

| 方法 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| Semi-Unmix-AE（10%） | 0.622 | 0.591 | 0.827 | 0.620 | 0.357 | 0.505 | 0.587 |
| Semi-Unmix-AE（30%） | 0.647 | 0.623 | 0.834 | 0.671 | 0.348 | 0.577 | 0.617 |
| Semi-Unmix-AE（50%） | 0.672 | 0.616 | 0.815 | 0.674 | 0.310 | 0.622 | 0.618 |
| Semi-Unmix-AE（70%） | 0.671 | 0.614 | 0.834 | 0.712 | 0.406 | 0.652 | 0.648 |
| Semi-Unmix-AE（100%） | 0.686 | 0.616 | 0.831 | 0.710 | 0.385 | 0.654 | 0.647 |

### 表 IV. 在单染图像上使用结构相似性（SSim）分数评估浓度图

**参照：Vahadane [20]**

| 方法 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| ColorAE | 0.903 ± 0.004 | 0.886 ± 0.012 | 0.913 ± 0.006 | 0.621 ± 0.060 | 0.853 ± 0.001 | 0.844 ± 0.003 | 0.837 ± 0.013 |
| InverseAE | 0.934 ± 0.000 | 0.885 ± 0.012 | 0.881 ± 0.016 | 0.682 ± 0.001 | 0.867 ± 0.001 | 0.811 ± 0.009 | 0.843 ± 0.002 |
| Semi-Unmix-AE | 0.917 ± 0.001 | 0.866 ± 0.009 | 0.873 ± 0.002 | 0.715 ± 0.001 | 0.857 ± 0.003 | 0.848 ± 0.001 | 0.846 ± 0.002 |

**参照：Bayesian K-SVD [18]**

| 方法 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| ColorAE | 0.902 ± 0.007 | 0.885 ± 0.002 | 0.927 ± 0.006 | – | 0.887 ± 0.002 | 0.856 ± 0.001 | 0.892 ± 0.002 |
| InverseAE | 0.932 ± 0.001 | 0.860 ± 0.015 | 0.898 ± 0.004 | – | 0.891 ± 0.001 | 0.831 ± 0.004 | 0.882 ± 0.003 |
| Semi-Unmix-AE | 0.916 ± 0.001 | 0.844 ± 0.007 | 0.895 ± 0.002 | – | 0.892 ± 0.000 | 0.854 ± 0.001 | 0.880 ± 0.001 |

> 注：Bayesian K-SVD 在几乎所有 CD16 图像上解卷积失败，故该列留空（表中以"—"表示）。

### 表 V. 训练 Semi-Unmix-AE 时，逆重建损失在有标注数据上的权重的消融研究

| λ | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| 1 | 0.619 | 0.085 | 0.832 | 0.676 | 0.012 | 0.534 | 0.460 |
| 0.75 | 0.719 | 0.561 | 0.832 | 0.675 | 0.249 | 0.536 | 0.595 |
| 0.5 | 0.702 | 0.453 | 0.822 | 0.754 | 0.238 | 0.580 | 0.592 |
| 0.25 | 0.731 | 0.609 | 0.841 | 0.730 | 0.074 | 0.588 | 0.596 |
| 0 | 0.686 | 0.616 | 0.831 | 0.710 | 0.385 | 0.654 | 0.647 |

### 表 VI. InverseAE 与 Semi-Unmix-AE 的模型架构

| 编码器（Encoder） | 解码器（Decoder） |
|---|---|
| Conv2D（1×1，128 通道） | ConvTranspose2d（3×3，16 通道） |
| ReLU | Conv2D（3×3，32 通道） |
| Conv2D（3×3，64 通道） | ReLU |
| MaxPool2d | ConvTranspose2d（3×3，32 通道） |
| ReLU | Conv2D（3×3，64 通道） |
| Conv2D（3×3，32 通道） | ReLU |
| MaxPool2d | Conv2D（3×3，128 通道） |
| ReLU | ReLU |
| Conv2D（3×3，16 通道） | Conv2D（3×3，<染色数量> 通道） |
| ReLU | |

### 表 VII. 使用不同伪分割标签训练的模型评估

| 方法 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| **SLIC [34]，Compactness=0.1** | | | | | | | |
| UNet | 0.563 | 0.509 | 0.795 | 0.753 | 0.452 | 0.093 | 0.528 |
| ColorAE | 0.633 | 0.439 | 0.765 | 0.762 | 0.349 | 0.632 | 0.597 |
| Semi-Unmix-AE | 0.674 | 0.508 | 0.822 | 0.752 | 0.317 | 0.659 | 0.622 |
| **SLIC [34]，Compactness=1** | | | | | | | |
| UNet | 0.621 | 0.484 | 0.810 | 0.738 | 0.478 | 0.103 | 0.539 |
| ColorAE | 0.657 | 0.496 | 0.813 | 0.748 | 0.333 | 0.581 | 0.605 |
| Semi-Unmix-AE | 0.653 | 0.514 | 0.825 | 0.747 | 0.376 | 0.655 | 0.628 |
| **SLIC [34]，Compactness=10** | | | | | | | |
| UNet | 0.496 | 0.496 | 0.835 | 0.699 | 0.144 | 0.405 | 0.513 |
| ColorAE | 0.639 | 0.585 | 0.829 | 0.728 | 0.353 | 0.573 | 0.618 |
| Semi-Unmix-AE | 0.686 | 0.616 | 0.831 | 0.710 | 0.385 | 0.654 | 0.647 |
| **SLIC [34]，Compactness=25** | | | | | | | |
| UNet | 0.633 | 0.528 | 0.801 | 0.704 | 0.433 | 0.108 | 0.535 |
| ColorAE | 0.652 | 0.419 | 0.832 | 0.703 | 0.313 | 0.579 | 0.583 |
| Semi-Unmix-AE | 0.683 | 0.546 | 0.793 | 0.746 | 0.357 | 0.614 | 0.623 |
| **SLIC [34]，Compactness=100** | | | | | | | |
| UNet | 0.527 | 0.467 | 0.718 | 0.585 | 0.378 | 0.092 | 0.461 |
| ColorAE | 0.690 | 0.410 | 0.769 | 0.759 | 0.218 | 0.622 | 0.578 |
| Semi-Unmix-AE | 0.666 | 0.481 | 0.816 | 0.736 | 0.374 | 0.620 | 0.615 |
| **SAM [35]** | | | | | | | |
| UNet | 0.557 | 0.516 | 0.733 | 0.582 | 0.405 | 0.094 | 0.481 |
| ColorAE | 0.651 | 0.505 | 0.831 | 0.765 | 0.373 | 0.538 | 0.610 |
| Semi-Unmix-AE | 0.702 | 0.527 | 0.822 | 0.757 | 0.406 | 0.601 | 0.636 |

### 表 VIII. 模型架构消融研究

> 模型的详细架构见表 IX。

| 架构 | CD3 | CD4 | CD8 | CD16 | CD20 | 肿瘤 | 平均 |
|---|---|---|---|---|---|---|---|
| A（所提方法） | 0.686 | 0.616 | 0.831 | 0.71 | 0.385 | 0.654 | 0.647 |
| B（宽度+1） | 0.635 | 0.488 | 0.810 | 0.744 | 0.309 | 0.565 | 0.592 |
| C（宽度+2） | 0.568 | 0.559 | 0.791 | 0.747 | 0.255 | 0.572 | 0.582 |
| D（深度+1） | 0.649 | 0.486 | 0.794 | 0.726 | 0.305 | 0.562 | 0.587 |
| E（深度+2） | 0.158 | 0.127 | 0.249 | 0.282 | 0.030 | 0.590 | 0.239 |

### 表 IX. 架构设计选择消融研究中的模型配置

> 为简洁起见省略 ReLU 激活层。ConvT 表示转置卷积。Conv3–128 表示卷积核为 3×3、输出 128 通道的二维卷积。n 为染色或生物标志物的数量。

**编码器（Encoder）**

| A（所提方法） | B（宽度+1） | C（宽度+2） | D（深度+1） | E（深度+2） |
|---|---|---|---|---|
| Conv1–128 | Conv1–256 | Conv1–512 | Conv1–128 | Conv1–256 |
| Conv3–64 | Conv3–128 | Conv3–128 | Conv3–64 | Conv3–128 |
| MaxPool | MaxPool | MaxPool | MaxPool | MaxPool |
| Conv3–32 | Conv3–64 | Conv3–128 | Conv3–32 | Conv3–64 |
| MaxPool | MaxPool | MaxPool | MaxPool | MaxPool |
| Conv3–16 | Conv3–32 | Conv3–64 | Conv3–16 | Conv3–32 |
| | | | MaxPool | MaxPool |
| | | | Conv3–8 | Conv3–16 |

**解码器（Decoder）**

| A（所提方法） | B（宽度+1） | C（宽度+2） | D（深度+1） | E（深度+2） |
|---|---|---|---|---|
| ConvT3–16 | ConvT3–32 | ConvT3–64 | ConvT3–8 | ConvT3–16 |
| Conv3–32 | Conv3–64 | Conv3–128 | Conv3–16 | Conv3–32 |
| ConvT3–32 | ConvT3–64 | ConvT3–128 | ConvT3–16 | ConvT3–32 |
| Conv3–64 | Conv3–128 | Conv3–256 | Conv3–32 | Conv3–64 |
| Conv3–128 | Conv3–256 | Conv3–512 | ConvT3–32 | ConvT3–64 |
| Conv3-n | Conv3-n | Conv3-n | Conv3–64 | Conv3–128 |
| | | | Conv3–128 | Conv3–256 |
| | | | Conv3-n | Conv3-n |

---

*本译文由 AI 生成，仅供阅读参考；如需引用请以英文原文（DOI: 10.1109/TMI.2025.3609245）为准。*

