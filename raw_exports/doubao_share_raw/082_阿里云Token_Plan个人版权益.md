---
source: Doubao(share)
title: 阿里云Token Plan个人版权益
msg_count: 6
url: https://www.doubao.com/thread/a63f8e820688b
conv_id: 38443730590674690
---

# 阿里云Token Plan个人版权益


### 我（提问）
aliyun 的token plan个人版啥权益啊，79


### 豆包（回答）
# ✅ 阿里云 Token Plan 个人版 Essential（79元/月，限时价，原价120）
> 就是你问的79套餐

## 核心额度
- **7天限额：5625 Credits**（不是按月一次性给，滚动7天窗口，从第一次调用开始计时；7天后重置，没用完额度不结转）
- 月度总上限：**25500 Credits**
- **并发Agent：2～3个**

## 权益（包含Lite全部能力）
1. ✅ 全模型调用：千问Qwen3.8 Max/Flash、DeepSeek、GLM、图像生成、语音TTS/ASR、实时语音对话、视频生成等多模态模型
2. ✅ 内置工具：联网搜索、代码解释器、网页抓取、文搜图/图搜图，全部走Credits抵扣
3. ✅ 兼容工具：Cursor、Claude Code、Qwen Code、Qoder、OpenClaw 等AI编程/Agent工具，套餐专属`sk-sp-xxx`的API Key
4. ✅ 夜间折扣：22:00–08:00，Qwen3.8系列4折，DeepSeek V4系列5折
5. ❗**注意：Essential（79元档不带Harness权益**，Harness是Standard(139)/Pro(499)才送）

## 补充规则
- 地域限制：**仅华北2（北京）**可用
- 超额度：7天额度耗尽就暂停调用；可以买100元的20000Credits用量包（不受7天窗口限制，最多同时持有5个用量包）
- 使用场景：仅限交互式使用，**禁止批量自动化/后端服务调用**；账号仅限本人，不能共享API Key
- 额度重置：官方不定期发放重置次数，可手动清零7天窗口重新计数

## 和上下档位对比
- Lite 39元：7天2500 Credits，并发1–2
- Essential 79元：7天5625 Credits，并发2–3（2.25倍Lite额度）
- Standard 139元：7天10000 Credits，并发3–4，**带Harness全套AgentStudio权益**

如果你需要，我可以简单对比：79 Essential vs 139 Standard，看要不要多花60上Harness。


### 我（提问）
GLM的模型可以用什么啊


### 豆包（回答）
# ✅ Token Plan个人版79元（Essential）可用GLM列表（华北2北京）
> 全部统一走套餐内 **Credits** 抵扣，OpenAI兼容接口，Cursor / Code / API都能调用
## 可用模型ID（直接填到model字段）
1. **glm-5.3（ZHIPU/GLM-5.3）**｜最新旗舰
    - 1M上下文（1048k），支持思考模式、Function Calling、结构化输出、前缀续写、上下文缓存
    - 适合长文档、复杂推理、代码、Agent工具调用
2. **glm-5.2**
    - 1M上下文，强推理、代码能力，支持thinking思维链
3. **glm-5.1**
    - 200K上下文，744B参数，长任务、代码
4. **glm-5**
    - 性价比基础版，推理/代码，适合日常
5. **glm-5.2-fast-preview**｜高速Prime模式（更快，Credits消耗更高）

> ❗注意：**glm-4.6 / glm-4.7 在10月10日下架**，不再推荐使用，套餐里也不建议选老版本4系GLM

## GLM在79套餐里的限制
1. **只有文本**：GLM全系**不支持图片识图**，不能传图；没有内置联网搜索（模型本身不带搜网）
2. 并发：受套餐2～3并发上限约束
3. 计费：**按Credits扣**，不是原价token计费，GLM消耗Credits会比Qwen Flash更高
4. 接口：OpenAI兼容接口，`sk-sp-xxx`这个套餐key直接调用，和千问写法一样

## 选型建议
- 写代码、长文档、复杂推理 → **glm-5.3**
- 想要更快响应、预算充足 → glm-5.2-fast-preview
- 简单问答、省credits → glm-5

## 调用示例（OpenAI兼容，Cursor可用）
```json
{
  "model": "glm-5.3",
  "messages": [...],
  "enable_thinking": true
}
```

## 补充
- GLM没有夜间折扣（夜间4/5折**只给Qwen3.8、DeepSeek系列**，GLM不参与）
- 套餐7天5625 Credits额度，GLM消耗偏大，大量跑GLM会比只用千问更快耗尽7天窗口

要不要我对比一下：**glm-5.3 vs qwen3.8-max** 的Credits消耗和代码能力，帮你判断79套餐优先用哪个？


### 我（提问）
给我他们的官网


### 豆包（回答）
# 阿里云 Token Plan（百炼Model Studio）
购买页：https://www.aliyun.com/benefit/scene/tokenplan
百炼Model Studio主站：https://dashscope.aliyuncs.com
Token Plan 帮助文档：https://help.aliyun.com/zh/model-studio/token-plan-overview

> Token Plan 是阿里云百炼的订阅套餐，里面调用GLM是**阿里云代理接入智谱模型**，不是智谱原生平台。

# 智谱GLM（智谱AI）官网
开放平台（API文档、GLM模型详情）：https://bigmodel.cn/
智谱清言网页端对话：https://chatglm.cn/
开发者文档：https://docs.bigmodel.cn/

## Token Plan调用地址（你配置Cursor要用）
OpenAI兼容endpoint：
`https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`

需要我直接给你Cursor完整配置参数（model+baseurl+key备注）吗？
