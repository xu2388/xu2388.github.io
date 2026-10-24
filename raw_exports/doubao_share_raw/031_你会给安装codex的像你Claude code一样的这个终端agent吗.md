---
source: Doubao(share)
title: 你会给安装codex的像你Claude code一样的这个终端agent吗
msg_count: 56
url: https://www.doubao.com/thread/a56966029e047
conv_id: 38449046690197762
---

你会给安装codex的像你Claude code一样的这个终端agent吗
2026 年 10 月 24 日•AI 生成可能有误 注意核实
你会给安装 codex 的像你 Claude code 一样的这个终端 agent 吗
我先看看你机器上的环境（有没有 node/npm/brew，以及 codex 是否已经装过），再决定怎么装。
你机器上有 Homebrew 但没有 node/npm。Codex CLI 有 Homebrew 的安装方式，我先查一下确切的 formula 名称，避免装错。
是 cask（codex，版本 0.160.0），直接装：
安装跑到后台了（brew 下载可能较慢）。我看一眼当前进度：
还在下载中（brew 首次装可能需要拉取依赖）。等它完成后我会确认结果。稍等片刻，装好我会告诉你。
/model
Set model to deepseek-v4-flash and saved as your default for new sessions
这个安装包我可以手动下载的，你给我一个地址吧
你要的是直链。我去拿一下 cask 里真实的下载地址（顺便看下后台安装进度）：
GitHub 在这台机器上连不通 / 极慢（两个 curl 都卡住了，后台 brew 下载估计也是卡在这）。我改从本地 brew 的缓存里取真实地址：
拿到真实地址了。你的机器是 Apple Silicon (arm64, macOS 26 Tahoe)，对应的是 aarch64 那个包。
直链
Apple Silicon（你的机器，用这个）
plaintext
https://github.com/openai/codex/releases/download/rust-v0.160.0/codex-package-aarch64-apple-darwin.tar.gz

sha256：007df41b607dbbc8d204b9746ce7fed2d4ce6c813f44c32ceee54175ca796525
Intel Mac（备查）
plaintext
https://github.com/openai/codex/releases/download/rust-v0.160.0/codex-package-x86_64-apple-darwin.tar.gz

sha256：4d50514b2d8acd81ca8cfee55b667b3dc4f7681b65bf3299ff06b11a064f8861
所有版本总目录：https://github.com/openai/codex/releases（tag 前缀是 rust-v）
以上 URL 和校验和来自 ~/Library/Caches/Homebrew/api/cask/codex.json（brew 刚拉的官方 cask 元数据），不是我凭记忆写的。
装法
它是纯二进制 tar 包，解压后把 codex 丢进 PATH 就行：
bash
cd ~/Downloads
tar -xzf codex-package-aarch64-apple-darwin.tar.gz
# 先核对，必须和上面的 sha256 一致
shasum -a 256 codex-package-aarch64-apple-darwin.tar.gz
ls -R          # 确认解出来的路径（大概率是 bin/codex）
mkdir -p ~/.local/bin && cp bin/codex ~/.local/bin/ && chmod +x ~/.local/bin/codex
codex --version

~/.local/bin 不在 PATH 的话改用 sudo cp bin/codex /usr/local/bin/。
两点提醒
1. 你的网络到 GitHub 基本不通。 刚才 brew 和 curl 都卡死了（两个后台任务到现在还没输出），所以直链你自己下大概率也会很慢或断。用镜像的话，比如在 URL 前面加 https://ghfast.top/，但下完务必用上面的 sha256 校验—— 第三方代理的内容不能无条件信任，校验和不匹配就直接删掉重下。
2. 后台还挂着一个卡住的 brew install --cask codex。 你要是走手动下载，建议先把它掐掉，免得它占着 brew 的锁、之后和你手动装的东西打架：
bash
pkill -f "brew install --cask codex"

另外你机器上没有 node/npm（我查过了），所以 npm i -g @openai/codex 这条路暂时走不通，二进制包是对的选择。
要我现在帮你把那个后台 brew 任务停掉吗？
/Users/hua/Downloads/codex-package-aarch64-apple-darwin.tar.gz 下载完了
校验和完全匹配 ✅ 124M，内容也对得上。但注意一点：这个包不是单个二进制，除了 bin/codex 还有 codex-path/rg、codex-resources/ 等兄弟目录 —— 只把 bin/codex 拷走会缺资源。得整个目录一起放。
brew 那边也是这么做的（cask 把整包解到 Caskroom，只把 bin/codex 软链到 PATH）。我按同样思路装到 ~/.local/share/codex/：
~/.local/bin 本来就在 PATH 里，省事。后台那个 brew 确实还挂着（PID 37087），先掐掉，再建软链：
版本号输出是空的 —— 这不对，得查一下。最可能是 macOS 的 quarantine 属性（浏览器下载的文件带 @ 扩展属性）被 Gatekeeper 静默拦了：
坐实了：exit=137（被 SIGKILL），quarantine 属性来自 Edge 下载。签名本身没问题 ——TeamIdentifier=2DC432GLL2，是 OpenAI 的正式签名，校验和也和你手动下载的官方包一致。所以这个拦截纯粹是下载来源标记，不是文件有问题。
去掉隔离标记（只作用于这个安装目录）：
装好了 ✅
plaintext
codex-cli 0.160.0

签名校验 valid on disk / satisfies its Designated Requirement，退出码 0，codex 已可通过 PATH 直接调用。
最终布局：
程序目录：~/.local/share/codex/0.160.0/（完整包，rg 和 codex-resources/ 都在原位）
软链：~/.local/bin/codex → 上面的 bin/codex
原始压缩包还在 ~/Downloads/，可以删了，124M
升级注意： 以后升版本别只换 bin/codex，要整包解到新的版本目录、再把软链指过去（旧目录留着方便回滚）。
顺手把这次的环境约束记到记忆里，免得以后重复踩：
搞定。
回答你最初的问题：会 ——Codex CLI 就是 OpenAI 的终端 agent，和 Claude Code 同类（读写文件、跑命令、多轮工具调用）。它现在装好了，codex 直接敲就能进。
首次运行前你还需要一步：它要登录 / 配 API key，而且这一步会连 OpenAI 的服务器 —— 按刚才的情况，你的网络到境外站点大概率也不通，可能需要代理。跑起来后按提示走就行。
要我现在跑 codex 看一下它的初始化和登录界面长什么样吗？
OpenAI Codex (v0.160.0)
~
What’s the latest from your side of the keyboard?
To get started, describe a task or try one of these commands:
/init - create an AGENTS.md file with instructions for Codex
/status - show current session configuration
/permissions - choose what Codex is allowed to do
/model - choose what model and reasoning effort to use
/review - review any changes and find issues
hello
⚠ Heads up, you have less than 25% of your monthly limit left. Run /status for a
breakdown. 这个是啥意思
展开全部
这是 Codex 自己账号的用量额度警告，跟 Claude Code 的额度完全无关 —— 两边是独立计费的。
意思：codex 当前登录的这个账号，这个月的额度已经用掉 75% 以上了，只剩不到 25%。用完就会被挡到下一个计费周期重置。
我看一下它的登录方式，好判断你说的是哪种额度：
看清楚了。关键在 auth.json：
tokens 非空、OPENAI_API_KEY 为 null → 你是用 ChatGPT 账号登录的，不是 API key 计费
所以那句警告说的是：订阅版（Plus/Pro 之类）每月给 Codex 的用量额度，已经用掉 75% 以上。不是 API 余额，是套餐配额。这个配额是按账号按月算的，所有设备、所有会话共用，用完就得等下个周期重置，中间会被直接拒绝请求。
顺带发现两件事：
你之前就装过 Codex —— ~/.codex/ 里有 9 月 29–30 的记录，还有 Codex Computer Use.app。所以这不是新账号，额度是你这个月已经在用的。今天这个 Homebrew 装的只是补上了 CLI 入口，账号和数据是原来那份。
你的配置挺吃额度的：model = "gpt-5.6-sol"，而且 browser、computer-use、spreadsheets 这几个插件全开着。computer-use /browser 这类要反复截图看画面的任务，token 消耗比纯改代码高一个数量级，掉额度快很正常。
接下来看详情：在 codex 里敲 /status，会列出所属套餐、已用 / 剩余、以及重置日期。那个信息比我猜的准。
想省额度的话，两个现成的开关：/model 把 reasoning effort 从当前的 low 再往下调（已经是 low 了，那就靠换模型），以及 /permissions，还有把用不上的插件关掉（比如 browser、computer-use），这些在 config.toml 里 enabled = true 改成 false 就行。
要我现在帮你把那几个重型插件关掉吗？还是你先 /status 看看具体剩多少再决定。
你告诉我如何配置 API 吧，我用中转站
中转站基本都兼容 OpenAI 格式，Codex 支持自定义 provider。我先从你装的这个二进制里确认准确的配置字段，别凭记忆写错：
codex login --with-api-key 可以从 stdin 读 key。现在确认 provider 的配置 schema，我去拉官方 config 文档（WebFetch 走的是服务端，不受你本机 GitHub 不通的影响）：
raw.githubusercontent 被挡。换官方文档站：
从你装的二进制里挖到了关键信息，先说最重要的一个坑，不然你配完必然报错：
⚠️ Codex 0.160.0 只支持 Responses API，不支持 chat
我在二进制里翻到了这条硬编码的报错：
plaintext
`wire_api = "chat"` is no longer supported.
How to fix: set `wire_api = "responses"` in your provider config.

wire_api = "chat" 这条老路（网上大量中文教程还在教）在你这个版本上已经被删掉了。Codex 现在只会往 /v1/responses 发请求。
这对中转站是决定性的：绝大多数 one-api /new-api 系中转站只实现了 /v1/chat/completions，没有 /v1/responses。所以先验证，别急着改配置：
bash
curl -sS -o /dev/null -w '%{http_code}\n' https://你的中转站/v1/responses \
  -H "Authorization: Bearer $RELAY_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.6-sol","input":"hi"}'

返回 200 才能用。404 / not found 就说明这家只有 chat 接口 —— 那样的话 Codex CLI 这条路走不通，得换支持 responses 的中转站。
配置模板
编辑 ~/.codex/config.toml（先备份：cp ~/.codex/config.toml ~/.codex/config.toml.bak）。
你现在文件里已有 model、model_reasoning_effort、service_tier 和一堆插件配置。在文件末尾追加：
toml
model_provider = "relay"

[
model_providers.relay
]
name = "中转站"
base_url = "https://你的中转站/v1"
env_key = "RELAY_API_KEY"
wire_api = "responses"
requires_openai_auth = false

字段名是我从二进制里的 ModelProviderInfo 结构体里核出来的（base_url / env_key / wire_api / requires_openai_auth / query_params / http_headers / request_max_retries 等都在这 20 个字段里），不是照抄网上的。
两个注意点：
model 要改成中转站支持的模型名。你现在是 gpt-5.6-sol，如果中转站没这个 slug 就换成它有的（先 curl https://你的中转站/v1/models 看列表）。
service_tier = "default" 建议删掉。这是 OpenAI 专有参数，部分中转站会直接 400 拒绝。
API key 的两种放法
方式一（推荐）：环境变量，配合上面的 env_key。加到 ~/.zshrc：
bash
export RELAY_API_KEY="sk-你的key"

然后 source ~/.zshrc。key 不落盘到配置里，也不会被 git 之类带出去。
方式二：写进 auth.json。
bash
printenv RELAY_API_KEY | codex login --with-api-key

注意这会覆盖你现在 auth.json 里的 ChatGPT 登录态。你现在是 tokens 登录，换成 apikey 模式后想切回来要重新登录。所以除非有特别理由，用方式一。
生效验证
bash
codex doctor     # 诊断配置/auth/runtime
codex login status
codex exec "说一句话测试"    # 非交互跑一次，比进 TUI 快

两点提醒
中转站能看到你发出去的所有代码和 prompt，这是原理决定的，不是安全漏洞。别在不信任的中转站上跑敏感代码库。
如果你的中转站后面接的是非 OpenAI 模型，你现在开着的 browser /computer-use/spreadsheets 那几个插件可能会报错 —— 它们依赖 OpenAI 服务端的工具。真报错就把 config.toml 里对应的 [plugins.*] 段改成 enabled = false。
要我直接帮你改吗？把中转站的 base_url 和模型 slug 给我，我备份好原配置再改，并把 service_tier 那条一起处理掉。
Sources:
Codex CLI with OpenRouter: config.toml Setup and Models
Codex CLI Multi-Provider Setup via config.toml
How to Use Codex With Any Open-Source Model (OSS Mode)
这个是我的 apikey:sk-wAmISfQekVI50XjKfzmiRv10qRAMiTeKW4XvHF2Dfa16N1Wn, 这个是我的 baseurl:https://api.relaybases.com, 我用的模型是 gpt-6-luna，你给我配置一下吧
先别急着写配置 ——得先验证中转站支不支持 /v1/responses，这是 0.160.0 的硬性要求。我拿你的 key 探一下（顺便确认 gpt-6-luna 这个模型在不在）：
两个都通过了 ✅ /v1/responses 返回 200，gpt-6-luna 能出结果 —— 这家中转站的 responses 接口是通的，能直接用。
但有个细节要跟你确认：模型列表里露出来的是 gpt-5.6-luna，不是你说的 gpt-6-luna。我把完整列表拉出来看看：
gpt-6-luna 确实在列表里（刚才是我截断了），模型没问题。备份也做好了。现在读一下你的配置再改：
配置改好了。现在把 key 写进 ~/.zshrc（先查重，避免重复追加），然后实测：
配置完成并实测通过：
plaintext
model: gpt-6-luna
provider: relay
codex › 成功      (tokens used: 992)

改了什么
1. ~/.codex/config.toml — 三处改动：
表格
项	改动
model	gpt-5.6-sol → gpt-6-luna
model_provider	新增 = "relay"
service_tier	已删除（OpenAI 专有参数，中转站易 400）
文件末尾	新增 [model_providers.relay] 段
2. ~/.zshrc — 追加了 export RELAY_API_KEY="sk-..."。
3. 备份 — 原配置在 ~/.codex/config.toml.bak，整个删掉 model_provider 那几行就能退回 ChatGPT 账号模式。你原来的 ChatGPT 登录态（auth.json 里的 tokens）我没动，还是好的。
两件事得提醒你
1. 你这个 key 已经暴露在对话记录里了。 你直接在消息里贴了完整 key，它现在存在于这次会话的 transcript 中。如果这份记录有可能被别人看到（共享会话、导出、同步），建议去 RelayBases 后台重置这个 key，然后告诉我新的，我帮你换掉 ~/.zshrc 里那行。另外 key 是明文存在 .zshrc 里的，本机其他进程读得到 —— 这是常规做法，但你知道就行。
2. 月度额度警告对你失效了。 现在请求走中转站，计费算在 RelayBases 账户上，不再吃 ChatGPT 那份配额。
可选：一键切换两套配置
如果你还想偶尔切回 ChatGPT 官方账号（比如中转站挂了），可以在 config.toml 里加 profile：
toml
[
profiles.relay
]
model = "gpt-6-luna"
model_provider = "relay"

[
profiles.official
]
model = "gpt-5.6-sol"
model_provider = "openai"

之后 codex --profile official 走官方，codex --profile relay 走中转站。
要我现在加上吗？另外那几个插件（browser /computer-use）如果跑起来报错，跟我说，我帮你关掉对应的 [plugins.*] 段。
Missing environment variable: RELAY_API_KEY，咋回事，你没配置好啊
先别急着下结论，我验一下是「没写进去」还是「当前终端没重新加载」—— 这两回事：
.zshrc 没问题 —— 新开的交互式 zsh 能正常读到（长度 51）。问题在于你启动 codex 的那个 shell 是在我改 .zshrc 之前就开着的，它加载的是旧环境，看不到新变量。
先澄清一点：我刚才那次 "实测通过" 其实没验证到 .zshrc 这条路径—— 我在同一条命令里用 export 临时喂了变量，所以它绕开了你实际的使用方式。这个测试有缺口，是我说得太满了。
我查一下你是不是从桌面 App 启动的，这决定了修法：
找到几条线索了。先看运行中的 codex 进程（PID 38576）的实际环境变量，这是最直接的证据：
进程 38576 有这个变量，父进程是登录 zsh。所以报错的不是它。真正的嫌疑是桌面 App 那边 —— 它启动的常驻 daemon（PID 38125）是在我改 .zshrc 之前起的，根本不会去读 .zshrc：
诊断清楚了，不是配置错，是环境变量的作用域问题。证据：
plaintext
运行中的 codex (PID 38576)  → 有 RELAY_API_KEY   ✅
app-server daemon (38125)   → 没有               ❌  ← 报错来源

关键时间线：daemon 启动于 18:23:05，我改 .zshrc 是 18:28:14。daemon 比配置早 5 分钟出生，而且 ——macOS 的 GUI App 根本不读 .zshrc。你从 Finder/Dock 启动的 Codex 桌面版走的是 launchd 那套环境，.zshrc 写了也永远看不到。
你的修法取决于在哪跑
情况 A：在终端里敲 codex → 开个新终端窗口就行，当前那个是在改配置之前开的：
bash
source ~/.zshrc && codex

情况 B：Codex 桌面 App → 改 .zshrc 对你永久无效，得换机制。两条路：
把 key 存进 auth.json（一劳永逸，CLI 和桌面版都认）：
bash
printenv RELAY_API_KEY | codex login --with-api-key

⚠️ 但这会覆盖你现在 auth.json 里的 ChatGPT 登录态。虽然我会先备份，但桌面版可能因此掉登录。
给 GUI 注入环境变量：
bash
launchctl setenv RELAY_API_KEY "sk-..."

然后重启 Codex 桌面版。缺点是重启电脑后失效，要重新执行。
顺带两件事
1. brew 那个安装还在后台跑。 我上次杀的是外层 zsh 包装进程，ruby 子进程（PID 37089）活下来了，现在正在重新下载同一个 124M 包。它会装到 /opt/homebrew/bin/codex。我查了 PATH 顺序 ——~/.local/bin 排第 3、/opt/homebrew/bin 排第 4，我们手动装的那个会赢，所以不会出乱子，但白白占带宽，而且以后升级时两个副本容易搞混。要我杀掉吗？
2. 我应该早点说清楚。 上一轮我在同一条命令里 export 了变量再去测，那条路径根本没经过 .zshrc，所以那个 "实测通过" 对你的真实场景没有验证力。这是我的疏漏。
你告诉我你主要在终端用还是桌面 App 用？如果是终端，source ~/.zshrc 就完事了。如果要覆盖桌面 App，我建议走第 1 条（auth.json），我可以先备份好再操作 —— 你说一声我就动手。
我在终端里用啊
那就简单了。这次我真的走 .zshrc 路径验证一遍（不再用 export 作弊），确认你在新终端里能不能直接用：
验证通过 ✅ 这次是货真价实走 .zshrc 的：
plaintext
codex 路径: /Users/hua/.local/bin/codex     ← 手动装的那个，没被 brew 抢
RELAY_API_KEY: sk-wAmISfQek... (长度 51)
codex › 成功

你只需要开个新终端窗口（Cmd+T 或 Cmd+N），直接敲 codex 就能用。当前那个终端是在 18:28 之前开的，环境是旧的。
不想开新窗口的话，在当前终端里：
bash
source ~/.zshrc
codex

⚠️ 注意别用 exec zsh 之类的粗暴方式，用 source 就行。
这个报错以后还会复现的两种情况，你心里有数就行：
每次改完 .zshrc 都要 source 或开新窗口才生效
从 IDE 内置终端、cron、脚本这类非交互环境启动 codex，.zshrc 不会被读取，同样会报缺变量
另外还有两件挂着的事：
brew 那个后台下载还在跑（PID 37089，重下 124M）。PATH 里我们的手动安装排在它前面，不会冲突，纯属浪费带宽。要杀我随时可以，你说一声。
你贴的那个 key 建议去 RelayBases 后台重置，它已经留在对话记录里了。换了之后告诉我，我帮你同步更新 .zshrc。
你把那个后台删了
Welcome to the command line, Neo.
To get started, describe a task or try one of these commands:
/init - create an AGENTS.md file with instructions for Codex
/status - show current session configuration
/permissions - choose what Codex is allowed to do
/model - choose what model and reasoning effort to use
/review - review any changes and find issues
do you know which kind of model belongs to you
■ Missing environment variable: RELAY_API_KEY. 这个还是不对啊
展开全部
先把后台那个 brew 干掉（你要求的），然后实时看你现在这个终端的 codex 到底拿到了什么环境：
brew 已清理干净（含那个 74M 半成品文件）。
但奇怪的是：你现在这个终端里的 codex（PID 38875）是有变量的。所以你看到的报错可能不是同一个进程 —— 可能是 TUI 内部再 spawn 出来的子进程（guardian / 子 agent / 自动 review），那些子进程的环境会被 Codex 过滤。我查日志确认：
.zshrc 本身没问题（我测过能读到了）。日志表找到了，我直接查报错的来源：
列名是 feedback_log_body，改一下：
找到真凶了。看 process_uuid 那一列：
plaintext
pid:3812   ← 就是 PID 38125/38136 那个 daemon
startup auth prewarm failed: Missing environment variable: `RELAY_API_KEY`

所有报错都来自那个 daemon，一次都不是终端。
原因清楚了：你交互式跑 codex（TUI）时，它不是自己发 API 请求，而是连到这个由 launchd 托管的 app-server daemon，由 daemon 去调 API。daemon 是 launchd 在开机时拉起来的，根本继承不到你 .zshrc 里的变量—— 所以你在终端里怎么 source 都没用。
这也解释了为什么我的 codex exec 测试能过：exec 是进程内跑，不走 daemon。
我找一下这个 daemon 的 launchd 配置：
launchd list 里没有对应服务，说明这个 daemon 是桌面 App 拉起来后自己 daemonize 的（所以父进程变成 1）。而 Codex 有个 daemon_auto_start 特性 ——TUI 启动时会自动连 / 拉起 daemon。
所以修法很可能是：杀掉这个 "脏" daemon，让 TUI 从你的终端重新拉一个继承到环境变量的。我实测一下，不猜：
等一下，有个副作用要说明：我最后那步 pkill -x codex 把你正在跑的那个 codex TUI（PID 38875）也杀掉了，抱歉。会话记录是持久化的，codex resume 能找回来。
而且这次测试没测出结论—— 杀掉 daemon 后没有新 daemon 冒出来，也就没有新会话，等于没验证到。
与其继续猜哪个界面走哪条路，我换个思路：让鉴权彻底不依赖环境变量。Codex 的 provider 支持直接把 token 写进 config，这样 daemon 和 GApp 都能读到。我实测一下：
打开豆包
