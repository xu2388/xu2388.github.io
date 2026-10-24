---
source: Doubao(share)
title: step5preview模型介绍
msg_count: 2
url: https://www.doubao.com/thread/a7edbbfdb88c4
conv_id: 38447311473372162
---

# step5preview模型介绍


### 我（提问）
step5preview这个是什么模型啊


### 豆包（回答）
# Step‑5‑Preview（阶跃星辰 step‑5‑preview）
**出品方**：阶跃星辰 StepFun，2026‑09‑20 发布的旗舰 MoE 基座大模型（不是图像扩散模型，是文本为主的多模态大语言模型）。

## 核心参数
- 架构：**稀疏MoE**，总参数量 **600B**，每次token激活 **27B**
- 上下文窗口：**1M tokens**
- 输入：文本、图片、视频；输出：仅文本
- 最大输出：64k tokens
- 支持 Function‑calling（工具调用），**不支持微调**
- API模型ID：`step‑5‑preview`

## 定位与强项
面向**Agent智能体、工程编程、专业知识、金融分析**复杂长任务：
1. 百万级长文档理解、多份资料综合分析
2. 软件工程：读大项目代码、排错、写测试、工程级代码修改
3. 多步骤Agent任务：拆解复杂目标，反复调用工具完成完整工作流
4. 多模态：看截图、图表、短视频内容做问答分析

&gt; 计划2026‑10‑15开源完整权重，现阶段主要通过API调用使用。

## 简单对比
- 和普通对话模型不同：侧重**把一件复杂任务从头到尾做完**，适合做AI Agent底座，而不是简单闲聊。
- 同公司还有 Step‑Video 是文生视频扩散模型，不要和 Step‑5‑preview 混淆。

如果你需要，我可以给你一份极简openai兼容格式调用示例。
