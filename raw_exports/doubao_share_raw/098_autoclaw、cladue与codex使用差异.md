---
source: Doubao(share)
title: autoclaw、cladue与codex使用差异
msg_count: 8
url: https://www.doubao.com/thread/a4827e736108e
conv_id: 38441369554354690
---

# autoclaw、cladue与codex使用差异


### 我（提问）
有个很严重的问题，国内的autoclaw,cladue用一下还得用自己的API，为啥codex直接能免费用啊


### 豆包（回答）
# AutoClaw / OpenClaw 需要自己填API，但Codex不用的核心原因
> 纠正：**Codex并不是真正完全免费无成本**，只是认证方式不一样，不是免API调用，只是不用你手动粘贴`sk‑xxx`密钥。

## 1. AutoClaw（OpenClaw）为什么必须自己提供API Key
AutoClaw/OpenClaw 是**开源Agent框架，本身不托管任何模型、没有后端计费账户**。
- 它只是本地运行的调度器：负责规划任务、读写本地文件、循环调用大模型；**模型算力完全依赖第三方LLM服务**。
- 开源项目不能把开发者自己的API密钥内置分发：如果作者内置Claude/GLM密钥，所有人共用，token瞬间被刷爆，直接封号。
- 所以设计成：**你自己去服务商申请API‑key，自己承担token费用**，框架只做转发请求。
> 国内版本AutoClaw可以用智谱GLM、DeepSeek等国内API；想跑Claude，你必须自己拿Claude的API key，框架不帮你兜底算力成本。

## 2. Codex为什么不用粘贴API Key
Codex有两套认证模式，二选一：
1. **ChatGPT账号OAuth登录（大家看到的“不用API key”模式）**：用你的ChatGPT会员身份登录，**走订阅套餐的额度，不是走按token计费的API接口**。
    - 本质：Codex复用ChatGPT网页端的会话token，后台会扣你账号内Codex专属配额，**依然有限流，免费账号额度很低，Plus/Pro额度更高**，不是无限白嫖。
    - 你没有看到`sk‑xxx`，但依然携带身份凭证做鉴权，只是密钥被隐藏在登录会话里面。
2. **传统API Key模式**：Codex同样支持填OpenAI API key，按token花钱，和AutoClaw逻辑一模一样，很多生产环境就是这么用的。

> 关键点：Codex是**OpenAI官方产品**，OpenAI自己握账号体系，可以直接对接ChatGPT订阅；而AutoClaw是第三方开源框架，没有官方账号体系，只能让用户自备API。

## 3. 两者本质差异对比
|项目|身份|鉴权方式|谁承担算力成本|
|---|---|---|---|
|AutoClaw/OpenClaw|第三方开源Agent框架|用户填入第三方服务商API‑Key|**用户自己付token钱**|
|Codex|OpenAI官方编码Agent|①ChatGPT账号OAuth（扣订阅配额）②填入OpenAI API Key|①扣会员额度；②用户API计费|

## 4. 容易踩坑的误区
1. ❌ Codex完全免费：**免费账号有严格限流，高频Agent任务很快打满限额；重度使用建议Plus/Pro订阅**。
2. ❌ Codex不用花钱：只是不用手动复制sk密钥；底层一样消耗OpenAI资源。
3. ❌ AutoClaw必须花钱：如果你本地跑Ollama大模型，AutoClaw可以配置本地模型地址，**完全不需要任何API‑key，零成本**，只是本地显卡吃性能。

## 5. 为什么Claude Code不能像Codex这样给第三方框架做订阅鉴权
Anthropic官方禁止第三方Agent工具复用Claude Pro网页订阅token，强制第三方只能走付费API接口，所以OpenClaw/AutoClaw调用Claude只能填API‑key，不能像Codex那样登录账号薅订阅额度，这是服务商策略差异。

简单总结：
> Codex不用粘贴API key，是因为它是OpenAI亲生工具，可以直接复用ChatGPT账号会话；AutoClaw是第三方开源工具，没有官方账号，只能让你自己拿API；两者底层都要消耗大模型算力，不存在真正无代价。

如果你需要，我可以给你一段极简示例，看AutoClaw配置本地Ollama实现**完全不用API‑key跑Agent**。


### 我（提问）
codex可以用中国的API吗


### 豆包（回答）
# Codex 能不能直接用国内API
**原版Codex不能直接填DeepSeek/智谱/通义千问原生官方API直接跑**。
> 核心坑：新版Codex CLI强制使用 **Responses API（`POST /v1/responses`）**，而国内几乎所有厂商只实现老标准 **Chat Completions（`/v1/chat/completions`）**，协议不一样，直接填会报错404/协议不兼容。

> 注意：**OAuth登录模式（不用API key那个模式）完全不能替换后端模型**，只能走OpenAI官方GPT；只有**API‑Key模式（config.toml自定义provider）** 才可以换后端模型。

## 三种可行接入国内API的方案
### 方案1：本地协议转换代理（最推荐，可控）
用开源桥接工具（`cc‑switch` / `codex‑cn‑bridge` / `codex‑cn‑bridge`）在本机跑一个小网关：
- Codex →（Responses）→本地代理 →转成 chat/completions → DeepSeek/GLM/Qwen国内官方API。

最小config.toml示例：
```toml
model_provider = "cn‑bridge"
model = "deepseek‑coder‑v3"

[model_providers.cn‑bridge]
name = "国内模型桥接"
base_url = "http://127.0.0.1:8080/v1"
wire_api = "responses"
env_key = "DEEPSEEK_API_KEY"
requires_openai_auth = false
```
设置环境变量`DEEPSEEK_API_KEY=你的密钥`，代理再转发给`api.deepseek.com/v1`。

### 方案2：找支持Responses API的中转服务商
有些聚合中转平台已经做好Responses适配，直接填它的base_url，后端实际跑国内模型（DeepSeek、GLM等），不用自己搭代理。
> ⚠️注意：第三方中转涉及你的代码、文件内容，敏感项目不建议用公有中转。

### 方案3：少数原生支持Responses的国内服务
目前国内原生实现Responses接口的极少，例如讯飞星火Coding MaaS，可直接填其base_url，不需要代理，但是选择少。

## 和AutoClaw对比，回到你上一个问题
|工具|协议|接入国内API难度|
|---|---|---|
|AutoClaw / OpenClaw|只用`chat/completions`|直接填国内官方API，零代理，开箱即用|
|OpenAI Codex CLI|新版强制`responses`|**必须一层协议转换代理，不能直连国内原生API**|

> 这就是为什么很多人踩坑：AutoClaw直接填DeepSeek key就跑；Codex同样填DeepSeek key直接报错，因为请求体格式完全不一样。

## 重要提醒
1. Codex的**桌面GUI版本**，如果你点登录走ChatGPT账号登录，这一路完全锁死OpenAI，不能换国内模型；只有关闭登录，用config.toml自定义provider才生效。
2. OSS模式（`codex --oss`）只是关闭OpenAI鉴权，**不解决Responses协议兼容问题**，仍然需要桥接代理。
3. 桥接后，Codex的工具调用、Agent能力取决于后端国内模型对Function‑call的支持，部分国产模型会丢能力。

如果你需要，我可以给你一段极简的Node.js小脚本，实现本地Responses→chat/completions桥接，不用装CC‑Switch这类GUI工具。


### 我（提问）
那么chatgpt免费额度是多少啊


### 豆包（回答）
# ChatGPT免费账号额度（2026‑09，区分普通聊天 / Codex，两者**完全隔离**）
> 重点：**普通聊天 ≠ Codex代码Agent额度**，很多人踩坑就在这里。

## 1、普通网页聊天（chat）免费账号
- 默认模型：**GPT‑5.6 Luna**，**纯文本聊天不限消息条数**，有防滥用风控，不会卡死硬数字上限。
- 不能用 Sol（强能力模型，Plus/Pro专属）。
- 文件上传、图片识图、DALL‑E绘图：**有独立限额，不能随便狂用**。

> ✅聊天可以随便聊；❌但这不等于 Codex 能随便跑工程任务。

## 2、Codex（你关心的，登录ChatGPT账号免API key模式）免费账号
**免费账号Codex额度非常少，重置周期是30天（按月重置，不是7天）**
1. 没有公开固定数字，社区实测等价于约**2美元token配额每月**，只能做小段代码、小脚本调试，**不能跑项目级Agent任务**。
2. 一旦做读文件夹、批量重构、多轮工程任务，很快直接打满限额，提示`rate limit exceeded`，要等整月重置。
3. 免费账号**Codex只能调用弱模型，拿不到Sol**，复杂代码容易崩、工具调用容易失败。

### 各档位Codex对比
|档位|Codex重置周期|Codex相对配额|能否用Sol|
|---|---|---|---|
|Free免费|**30天**|极低（试用）|❌|
|Plus $20/月|7天（每周重置）|基础额度，有5小时滚动限流|✅|
|Pro $100/月|7天|5倍Plus额度，取消5h限流|✅|

> 注意：Plus也**不是Codex无限**，重度工程也会限流；Pro才适合持续写项目代码。

## 3、OpenAI API（sk‑xxx密钥）免费额度
新注册账号送的免费信用：**现在已经取消新手免费余额**，注册就要充值，没有免费API token。
> 网页免费聊天账号，**余额和API账户完全隔离，聊天额度不能拿来抵扣API调用费**。

## 4、回到你最早的问题
> “为什么Codex登录账号就能用，AutoClaw要自己填API？”
1. Codex登录走**网页订阅配额（会话鉴权）**，但免费账号Codex额度很少，只能玩玩，重度直接限流。
2. AutoClaw是第三方开源Agent，拿不到OpenAI的账号会话，只能你自己出钱买API key。
3. Codex的API模式（填sk‑xxx），和AutoClaw逻辑一模一样，照样花钱。

### 现实建议
如果你想本地跑Agent写代码，免费ChatGPT账号的Codex基本**不适合做正经项目**，很容易直接锁额度。
两种更稳的替代：
1. AutoClaw填DeepSeek‑Coder API，花钱可控；
2. Ollama本地跑模型，**零API费用**。

如果你需要，我可以简单讲怎么看自己Codex剩余配额：`codex status`命令直接看还剩多少、什么时候重置。


### 我（提问）
cursor如何升级套餐啊


### 豆包（回答）
# Cursor升级套餐完整操作
> Cursor国内**不支持支付宝/微信**，只支持Visa/Mastercard国际信用卡、合规虚拟外币卡。
> 升级入口**不在编辑器内部**，在网页账单后台，编辑器只做状态同步。

## 一、官方升级路径（免费Hobby → Pro / Pro+ / Ultra）
1. 浏览器打开账单面板：**https://cursor.com/dashboard/billing**，登录你的Cursor账号（和编辑器登录同一个邮箱）
2. 在当前套餐卡片，点击 **Adjust plan（调整套餐）**
3. 选择目标套餐：
    - **Pro $20/月**：绝大多数人，日常写代码、轻度Agent够用
    - **Pro+ $60/月**：高频Agent、大量读文件夹重构项目，3倍额度
    - **Ultra $200/月**：极重度，20倍Pro额度，优先新功能，普通开发者不推荐
4. 进入Stripe支付页面，填国际信用卡完成付款。
✅ **升级立即生效，不需要等周期结束，剩余额度按比例折算抵扣**。

> 编辑器内：重启Cursor，`Settings → Usage`就会显示新套餐额度。

### 套餐简表（2026‑09）
|套餐|月价|核心|适合|
|---|---|---|---|
|Hobby（免费）|$0|少量高级模型，Agent严格限流|简单体验|
|Pro|$20|$20等价前沿模型额度|日常开发|
|Pro+|$60|$70等价额度，Agent重度|经常跑Agent读项目|
|Ultra|$200|$400等价额度，优先新功能|全天大量Agent|

> 可以选**年付，统一省20%**，在billing页面绿色横幅点Upgrade Now切换年付；**年付不能中途切回月付，只能到期后改**。

## 二、国内用户支付难点
1. 国内普通银联卡**直接扣款失败**，必须Visa/Master外币卡，或者合规虚拟外币卡（Wildcard等）填到Stripe页面完成订阅。
2. 不要找第三方代充账号，有被盗号、封号风险。

## 三、已经是Pro，升级到Pro+/Ultra
同样在 `cursor.com/dashboard/billing` → Adjust plan，直接选更高档位，补差价，**立刻生效**。

> ⚠️降级不一样：降级不会立刻降，会保留现有套餐直到当前计费周期结束，下个周期才切换低档位。

## 四、很关键的备选方案（不想花20刀订阅）
Cursor支持**自备OpenAI / DeepSeek / Claude API‑key**，不用买Cursor订阅套餐。
设置路径：编辑器`Settings → Models`，把官方后端关掉，填入自己API key，**消耗你自己的API余额，不受Cursor套餐额度限制**。
> 缺点：Cursor的Agent云端能力、MCP部分高级功能会缺失。

## 五、看自己还剩多少额度
网页后台：`dashboard → Usage`，可以看到各类模型消耗统计；还可以开启**按用量计费(on‑demand)**，套餐额度用光之后继续跑，记得设置消费上限防止爆单。

### 和你前面聊的工具对比小结
1. **Codex CLI**：可以登录ChatGPT账号复用订阅额度；
2. **Cursor**：**不能复用ChatGPT账号**，要么买Cursor订阅，要么自己填API key；
3. **AutoClaw**：全部自己填API，没有订阅套餐。

如果你需要，我可以告诉你Cursor填入DeepSeek API key的完整配置。
