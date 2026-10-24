# 内容地图（已知研究方向）

> 这份地图基于已掌握的协作背景和本地资料（论文 PDF、代码库）先立起来，
> 等 `raw_exports/` 里的对话导进来后，会逐条用真实对话内容填充、校正、扩写。

## 1. 主线：H&E → IHC 虚拟染色
- 任务定义：用深度学习把 H&E 切片生成对应的 IHC 染色（省试剂、省人力）
- 起点方法：PSPStain / CUT 系列
- 核心问题意识："这件事本质在干什么"——不是堆模块，是学染色的内在映射

## 2. 核心难题：2 通道浓度域路线 + 均值坍缩
- 想用"浓度域"做两通道建模
- 现象：输出坍缩成均值（mean collapse）
- 归因：InstanceNorm 的尺度不变性导致浓度信息丢失
- 这是一年里最纠结的一条线，值得单独成篇

## 3. 方法调研（横向）
本地已囤的相关论文（待从对话中提取当时怎么读、怎么评的）：
- Cross-channel Perception Learning for H&E-to-IHC
- Pathological Semantics-Preserving Learning
- UNIStainNet（Foundation-Model-Guided）
- VIMs（Text-to-Stain Diffusion）
- PAINT、Score-based Diffusion、Test-Time Stain Adaptation 等

## 4. 工程日常
- AutoDL 实例经常关机，本地无 GPU
- 远程调试、断点续训、环境迁移的折腾

## 5. 科普长文
- "深度学习到底在干什么"——面向自己、讲本质、不堆术语

## 6. 决策篇
- 论文框架偏弱时：继续深究 vs 收口投稿
- 反复自我推翻后的判断与停止规则

---
待办：对话导出后，用 `process_exports.py`（待写）解析 → 归类到上面 6 类 → 生成 articles/*.html。
