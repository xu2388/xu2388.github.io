---
source: DeepSeek
conversation_id: d878b575-49c7-43cb-9c40-6d36c2e972d1
title: OpenClaw修改API密钥配置
inserted_at: 2026-06-12T16:05:37.119000+08:00
updated_at: 2026-06-12T16:38:50.309000+08:00
message_count: 24
---

### THINK

用户想了解如何在OpenClaw中修改API密钥的配置。我需要查找相关文档。为了全面覆盖，我将同时进行多项搜索，涵盖不同可能的关键词和配置方式。

### THINK

搜索结果显示了一些相关页面。为了全面了解如何修改API密钥配置，我们需要同时打开这些页面。

### THINK

这些资料涵盖了多种配置方法：使用向导、命令行工具（如openclaw-csdn-apikey、yuomoz、302oc）、环境变量、直接编辑JSON配置文件等。我的回答将涵盖多种修改方式，并提供常见API key提供商的环境变量名称。

### DeepSeek

要在 OpenClaw 中修改 API Key，最简单的办法就是重新运行它的引导向导。下面列出了几种主要的方式，你可以根据自己的习惯选择最顺手的一种。

### 方法一：使用交互式向导 (推荐)
这是最安全、最不容易出错的方式，适合日常使用，特别是当你需要为新的大模型提供商添加或更换 API Key 时[reference:0]。

1.  **执行命令**：在终端中运行 `openclaw onboard`，这会重新进入配置界面[reference:1]。
2.  **开始配置**：脚本会检测到现有的配置文件，并提供“保留、修改或重置”的选项。选择“修改”以更新 API Key[reference:2]。
3.  **选择模型提供商**：在引导流程的 `模型和凭证` 设置部分，选择一个提供商（如 `OpenAI`、`Anthropic`），或选择 `Custom Provider (OpenAI Compatible)` 来连接第三方 API[reference:3][reference:4]。
4.  **输入 API Key**：根据提示选择 `Paste API key now`，然后粘贴你的 API Key[reference:5][reference:6]。
5.  **完成后续步骤**：按向导提示完成剩余的 Gateway、渠道等配置，修改即可生效。

### 方法二：编辑配置文件 (高级用户)
适合熟悉 JSON 格式，需要批量或精确修改配置的场景。OpenClaw 的主配置文件是 `~/.openclaw/openclaw.json`（Linux/macOS）[reference:7][reference:8]。

> **请注意**：这是一种高级操作，修改前强烈建议先备份此文件，以便在配置出错时恢复。

1.  **打开配置文件**：使用你熟悉的文本编辑器（如 `nano`, `vim`, VS Code 等）打开它：
    ```bash
    nano ~/.openclaw/openclaw.json
    ```
2.  **定位 API Key 配置**：在文件中找到 `"models"` 下的 `"providers"` 部分，为你的提供商修改 `"apiKey"` 的值。对于某些第三方 API，你可能还需要调整 `"baseUrl"`[reference:9][reference:10]。
    ```json
    {
      "models": {
        "mode": "merge",
        "providers": {
          "my_custom_provider": { 
            "baseUrl": "https://api.your-provider.com/v1", // 修改为正确的 API 地址
            "apiKey": "YOUR_NEW_API_KEY", // 在这里粘贴你的新 API Key
            "api": "openai-completions", 
            "models": [ ... ]
          }
        }
      }
    }
    ```
3.  **保存并重启**：保存文件并退出编辑器。最后，**必须重启 Gateway 网关**才能使改动生效：
    ```bash
    openclaw gateway restart
    ```

### 方法三：通过环境变量
环境变量适合在自动化部署或需要临时覆盖配置的场景。这对于生产环境部署或自动化场景来说也是一种可靠的方式[reference:11]。

1.  **设置环境变量**：你可以直接在终端会话中设置，例如：`export ANTHROPIC_API_KEY="sk-your-new-key-here"`[reference:12]。
2.  **写入 `.env` 文件 (推荐)**：为了永久保存，建议将 Key 写入 `~/.openclaw/.env` 文件中。这样即使系统重启，配置也会生效[reference:13]。
3.  **保存并重启**：和编辑配置文件一样，设置或修改环境变量后，同样需要通过 `openclaw gateway restart` 命令重启 Gateway 网关[reference:14]。

> **注意**：不同服务商的环境变量名称不同，比如 `ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`DEEPSEEK_API_KEY` 等，请查阅具体提供商的文档[reference:15]。

### 方法四：使用第三方配置工具
社区也提供了一些一键式的命令行工具，可以简化配置过程，但请注意，使用第三方工具需要自行评估其安全性和可靠性。

*   **`npx yuomoz`**
    *   这是一个交互式向导，用于快速切换模型和 API Key，并自动完成基础配置修复和 Gateway 重启[reference:16][reference:17]。
    *   你可以直接运行交互式命令 `npx yuomoz`，或在非交互模式下直接指定 Key：`npx yuomoz --api-key sk-xxxxx`[reference:18]。
*   **`npx 302oc`**
    *   一个用于配置 302.AI API 的工具。运行 `npx 302oc` 后，在主菜单选择“配置 API Key”即可更新[reference:19]。
*   **`npx openclaw-csdn-apikey`**
    *   专门用于更新 CSDN Custom Provider API Key 的工具[reference:20]。
    *   使用方式：`npx openclaw-csdn-apikey sk-your-new-api-key-here`

### 💡 修改后：验证与故障排查
修改完 API Key 后，最好验证一下 OpenClaw 是否正常工作。

1.  **运行健康检查**：使用 `openclaw doctor` 命令，它可以帮你诊断常见配置问题，如语法错误或 API Key 无效[reference:21][reference:22]。
2.  **检查配置状态**：通过 `openclaw status` 命令快速查看 Gateway 的运行状态和已配置的模型。
3.  **重启 Gateway**：任何配置修改后，请务必通过 `openclaw gateway restart` 重启 Gateway。
4.  **使用官方客户端 (Windows)**：如果你使用的是 Windows 客户端，可以直接在软件设置中的“模型配置”页面，找到对应的提供商粘贴新的 API Key[reference:23]。

更新完 API Key 之后，你是不需要把旧 Key 放在围巾里的。保持环境的整洁和安全就好。

### 我（提问）

openclaw修改 apikey的配置围巾

### THINK

用户想了解如何启动 OpenClaw。回顾历史，我们之前已经讨论过修改 API 密钥的配置。现在用户可能想知道启动 OpenClaw 的具体步骤。我需要提供详细的启动指南。为了全面获取信息，我需要同时进行多项搜索，涵盖不同的启动方式、常见问题以及相关文档。

### THINK

搜索结果显示了一些相关页面。为了全面了解如何启动 OpenClaw，我们需要同时打开这些页面。

### THINK

这些资料提供了启动 OpenClaw 的详细信息。我的回答将涵盖安装、初始配置、启动 Gateway、打开仪表板以及常见问题排查。回答会引用多个来源。

### DeepSeek

启动 OpenClaw 主要包括运行安装向导和启动后台网关服务这两个步骤。

### 🚀 如何启动 OpenClaw

#### 1. 运行安装向导 (推荐)
这是初次使用时必须的步骤，它会引导你完成从初始化到启动的全过程：

*   **运行向导**：在终端中执行 `openclaw onboard` 命令。
*   **完成向导**：按照终端提示，完成**选择大模型、设置 API Key（从 OpenAI 或 Anthropic 等提供商获取）[reference:0][reference:1]、配置网关和工作区**等步骤[reference:2]。整个过程大约只需2分钟[reference:3][reference:4]。
*   **（可选）安装守护进程**：为了让 OpenClaw 能在后台自动运行，可以在运行向导时加上 `--install-daemon` 参数：`openclaw onboard --install-daemon`[reference:5]。

#### 2. 启动网关服务
网关是 OpenClaw 的核心进程，只有在它运行时才能与你的 AI 助手对话。
*   **验证网关状态**：启动后，可以运行 `openclaw gateway status` 命令来检查网关服务是否在 **127.0.0.1:18789**[reference:6] 上成功监听[reference:7][reference:8][reference:9]。
*   **停止网关**：`openclaw gateway stop`
*   **重启网关**：`openclaw gateway restart` （修改配置后常用命令）[reference:10]

### 🌐 打开管理面板
服务启动后，可以通过以下两种方式进入 OpenClaw 的图形操作界面：

*   **自动打开浏览器**：执行 `openclaw dashboard`，你的默认浏览器会自动打开管理面板[reference:11][reference:12][reference:13]。
*   **手动访问**：打开浏览器，手动输入本地地址：`http://127.0.0.1:18789/`[reference:14]。

### 💡 其他管理命令
除了上述命令，你可能会用到以下常用命令：

*   **前台调试**：`openclaw launch`。该命令会在当前终端直接启动 OpenClaw，并实时打印日志，适合开发调试[reference:15]。
*   **诊断问题**：`openclaw doctor`。当你遇到问题时，它可以自动诊断常见的配置和运行问题[reference:16]。
*   **查看实时日志**：`openclaw logs -follow`。查看详细的运行日志，有助于排查 API 或网络错误[reference:17]。
*   **查看网关深度状态**：`openclaw status --deep`。显示包括网关健康探测在内的更多状态信息[reference:18]。
*   **配置 Web 搜索**：`openclaw configure --section web`。为 AI 助手配置网络搜索功能[reference:19]。
*   **列出技能**：`openclaw skill list`。查看当前所有已安装的技能模块[reference:20]。
*   **添加技能**：`openclaw skill add <skill_名称>`。安装新的技能模块以扩展 AI 的能力[reference:21]。
*   **仅初始化工作区**：`openclaw init`。仅创建 `~/.openclaw/` 工作区目录，而不会启动服务[reference:22]。

### ❗ 常见问题与处理
如果在启动过程中遇到问题，可以试试下面这些方法：

*   **“openclaw: command not found” (命令未找到)**
    *   **原因**：OpenClaw 尚未安装。
    *   **解决方法**：请先确保已完成安装[reference:23]。
*   **Web UI 无法访问或服务异常**
    *   **原因**：网络、API 配置等问题。
    *   **解决方法**：先尝试 `openclaw gateway restart` 重启，如果无效，可使用 `openclaw logs -follow` 查看日志以定位具体错误。若访问 Web UI 需要 Token，可在 `~/.openclaw/openclaw.json` 配置文件中找到[reference:24][reference:25]。
*   **安装或启动时被杀毒软件拦截**
    *   **原因**：杀毒软件误报。
    *   **解决方法**：Windows 用户在安装和首次启动时，可**暂时关闭杀毒软件**[reference:26]，并确保**右键以管理员身份运行**[reference:27]。
*   **双击程序无响应**
    *   **原因**：路径含中文、未解压或在压缩包内运行。
    *   **解决方法**：确保**安装路径为纯英文**，并且已经将程序**完整解压**后再尝试运行[reference:28]。
*   **Gateway 一直显示离线**
    *   **原因**：服务启动失败。
    *   **解决方法**：尝试**关闭并重启服务**，或**重新以管理员身份打开软件**。首次启动可能需要等待 **1-3 分钟**初始化[reference:29]。
*   **启动时报错 “Node.js 版本过低”**
    *   **原因**：Node.js 版本不符合要求。
    *   **解决方法**：请确保你的 Node.js 版本满足 **v22.16+** 或 **v24** 的要求[reference:30][reference:31]。
*   **API Key 验证失败**
    *   **原因**：API Key 无效、格式错误或对应的模型配置不正确。
    *   **解决方法**：**仔细检查并重新配置你的 API Key**。根据错误信息确认 Key 以正确的格式（如 `sk-` 开头）输入，并检查是否正确选择了对应的模型提供商[reference:32]。

希望这份指南能帮助你顺利启动 OpenClaw！如果在过程中遇到具体的报错信息，可以随时发给我帮你分析～

### 我（提问）

如何启动opanclaaw

### THINK

我们分析这个错误信息：用户尝试重启Gateway，显示“Gateway service restarted”但又报错“gateway port 18789 is still busy before restart”。这表明重启过程中端口仍然被占用，可能旧的进程没有完全退出。

需要给出解决方案：如何解决端口占用问题，比如找到占用端口的进程并杀掉，或者使用强制重启命令。同时建议用户检查是否有多个OpenClaw实例在运行。

提供具体的Windows命令：netstat -ano | findstr :18789 找到PID，然后taskkill /PID <pid> /F。或者使用openclaw gateway stop 后再 start。

### DeepSeek

你遇到的这个错误信息看起来有点矛盾：`Gateway service restarted` 和后面的 `port 18789 is still busy before restart` 同时出现，通常是因为**旧的 Gateway 进程没有完全退出**，新进程尝试绑定同一个端口时发现仍被占用。

## 🔧 解决方法（Windows）

### 方法一：手动终止占用 18789 端口的进程（最有效）

1. **查找占用端口的进程 PID**
   ```powershell
   netstat -ano | findstr :18789
   ```
   你会看到类似这样的输出：
   ```
   TCP    0.0.0.0:18789          0.0.0.0:0              LISTENING       12345
   ```
   最后一列的数字（如 `12345`）就是进程的 PID。

2. **强制结束该进程**
   ```powershell
   taskkill /PID 12345 /F
   ```
   （把 `12345` 换成你查到的实际 PID）

3. **重新启动 Gateway**
   ```powershell
   openclaw gateway start
   ```
   或直接使用：
   ```powershell
   openclaw gateway restart
   ```

### 方法二：使用 openclaw 自带的停止命令（更安全）

```powershell
openclaw gateway stop
# 等待几秒钟，确保进程完全退出
openclaw gateway start
```

如果 `stop` 后端口仍然占用，说明停止命令没能杀死残留进程，还是得用方法一。

### 方法三：检查是否同时启动了多个 OpenClaw 实例

有时你可能会不小心开了多个终端窗口或后台进程。可以：

```powershell
# 查看所有 node 或 openclaw 相关进程
tasklist | findstr -i "node openclaw"
```

如果看到多个相关进程，可以全部结束：
```powershell
taskkill /F /IM node.exe
```
> **注意**：这会结束所有 Node.js 进程，确保你没有运行其他重要的 Node 服务。

## 🧹 清理后验证

启动成功后，用这个命令确认端口正常监听：
```powershell
netstat -ano | findstr :18789
```
应该能看到 `LISTENING` 状态且 PID 是新进程的。

## 💡 为什么会发生这种情况？

- `openclaw gateway restart` 在内部执行 `stop` 和 `start`，但如果 `stop` 阶段进程没有及时退出（比如正在处理请求或卡住），新进程启动时旧进程还占用着端口，就会报这个错误。
- **Windows 上比较常见**，尤其是快速连续执行 restart 命令时。

## ✅ 推荐的操作习惯

以后修改配置后，可以依次执行：
```powershell
openclaw gateway stop
openclaw gateway start
```
中间停顿 2-3 秒，给旧进程足够的退出时间。

如果频繁出现端口占用，也可以考虑通过 `openclaw status --deep` 查看详细状态，或者查看日志看看是否有进程挂起的线索：
```powershell
openclaw logs -follow
```

按照上面的方法手动杀掉占用的进程后，应该就能正常启动了。如果还有问题，可以把执行 `netstat -ano | findstr :18789` 的输出发给我看看。

### 我（提问）

│  Restart
│
◇  Gateway service restarted.
Error: gateway port 18789 is still busy before restart
(base) PS C:\Users\hua>

### THINK

我们看到了端口18789被进程PID 175632监听，并且有很多连接处于CLOSE_WAIT状态，还有对应的客户端的FIN_WAIT_2状态，这些客户端进程PID都是202888。这说明旧进程175632仍然在运行，并且有一些僵尸连接。需要终止PID 175632。同时注意到还有一个进程202888也有连接，但它只是客户端，可能不是gateway本身。主要占用端口的是175632。

用户应执行 `taskkill /PID 175632 /F`。然后重新启动。

回答中应提供准确命令。

### DeepSeek

从你提供的 `netstat` 输出可以看到，端口 **18789** 被 **PID 175632** 的进程占用，并且有大量 `CLOSE_WAIT` 状态的连接，说明这个旧的 Gateway 进程已经卡住了，需要强制终止。

## ✅ 立即解决步骤

### 1. 强制终止占用端口的进程
在 PowerShell 中执行：
```powershell
taskkill /PID 175632 /F
```
执行后应该会显示类似 `成功: 已终止 PID 为 175632 的进程。` 的信息。

### 2. 重新启动 Gateway
```powershell
openclaw gateway start
```
或者直接使用：
```powershell
openclaw gateway restart
```

### 3. 验证启动成功
```powershell
netstat -ano | findstr :18789
```
现在应该只看到一个 `LISTENING` 状态的连接，且 PID 是新的（不再是 175632）。

## 🧹 清理多余的客户端进程（可选）

输出中还有一个 **PID 202888**，它是这些 `CLOSE_WAIT` 连接的客户端（`FIN_WAIT_2` 状态），可能是之前连接 Gateway 的旧客户端进程（比如浏览器或某个插件）。为了彻底干净，也可以一并终止：
```powershell
taskkill /PID 202888 /F
```
不过这不是必须的，因为 Gateway 重启后它也会失去连接。

## 📌 防止再次发生

- **不要快速连续执行 `restart`**：最好先 `stop`，等待 2-3 秒，再 `start`。
- 如果问题频繁出现，可以在 `openclaw gateway stop` 后，手动检查端口是否真的释放了：
  ```powershell
  netstat -ano | findstr :18789
  ```
  直到没有输出后再执行 `openclaw gateway start`。

执行完上述命令后，OpenClaw 应该就能正常启动了。如果还有其他报错，欢迎继续贴出来～

### 我（提问）

(base) PS C:\Users\hua> netstat -ano | findstr :18789
  TCP    127.0.0.1:18789        0.0.0.0:0              LISTENING       175632
  TCP    127.0.0.1:18789        127.0.0.1:51002        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:53022        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:55346        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:56241        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:56913        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:57391        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:58210        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:59199        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:59842        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:60144        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:60356        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:60461        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:61748        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:62611        ESTABLISHED     175632
  TCP    127.0.0.1:18789        127.0.0.1:62824        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:63246        CLOSE_WAIT      175632
  TCP    127.0.0.1:18789        127.0.0.1:63849        CLOSE_WAIT      175632
  TCP    127.0.0.1:51002        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:53022        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:55346        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:56241        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:56913        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:57391        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:58210        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:59199        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:59842        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:60144        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:60356        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:60461        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:61748        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:62611        127.0.0.1:18789        ESTABLISHED     202888
  TCP    127.0.0.1:62824        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:63246        127.0.0.1:18789        FIN_WAIT_2      202888
  TCP    127.0.0.1:63849        127.0.0.1:18789        FIN_WAIT_2      202888
(base) PS C:\Users\hua>

### THINK

用户想为OpenClaw更换一个启动端口。之前的端口是18789，但由于进程占用问题，用户希望更换。我需要提供如何修改OpenClaw端口的指导。为了全面获取信息，我需要同时进行多项搜索，涵盖OpenClaw的配置文件、命令行参数、环境变量以及可能的相关文档或问题。

### THINK

搜索结果显示了一些相关页面。为了全面了解如何更改端口，我们需要同时打开这些页面。

### THINK

这些资料提供了多种修改端口的方法。我的回答将涵盖几种方法：使用命令行参数、修改配置文件、使用环境变量、通过配置命令设置。我还会提供一些验证步骤和注意事项。

### DeepSeek

更换端口是个好办法，这样既能解决端口冲突，也不需要去杀掉别的进程。

这里有几种改端口的方法，你可以选一种最顺手的试试：

### 🧵 方法一：使用 `--port` 临时参数
临时换个端口启动，只在当前窗口生效，适合先快速跑起来看看。

```bash
openclaw gateway --port 18790
```
*   **新访问地址**：启动成功后，需要通过 `http://127.0.0.1:18790` 访问。
*   **注意**：Gateway 服务停止后，下次启动若不指定 `--port` 则会回到默认的 `18789` 端口[reference:0]。
    > **一个小技巧**：如果你的电脑上安装了 `lsof` 命令，还可以在命令后加上 `--force` 参数，让 OpenClaw 自动“接管”被占用的端口[reference:1]。
> **验证**：重新执行 `netstat -ano | findstr :18790`，检查新端口是否已正常监听。

### 🧵 方法二：修改配置文件 (永久生效)
这个方法改动一次后，每次都会固定用新端口，一劳永逸。

1.  **找到配置文件**：用记事本打开 `%USERPROFILE%\.openclaw\openclaw.json`。
2.  **修改端口**：找到 `"gateway"` 下面的 `"port"` 字段（默认是 `18789`）。
3.  **填入新端口**：把它改成你想要的新端口，比如 `18790`[reference:2]。
4.  **重启网关**：保存文件后，在命令行里执行 `openclaw gateway restart` 就能生效了。

### 🧵 方法三：`config set` 命令 (CLI 推荐)
与方法二原理相同，但通过命令直接修改更快捷。
```bash
# 将 Gateway 端口修改为 18790
openclaw config set gateway.port 18790

# 重启 Gateway 使更改生效
openclaw gateway restart
```
修改完成后，可以直接用 `openclaw gateway status` 查看服务是否在新端口上正常运行。

### 🧵 方法四：环境变量 `OPENCLAW_GATEWAY_PORT`
适合在自动化脚本或需要隔离配置的场景下使用。
1.  **设置变量**：在终端执行以下命令（仅当前会话生效）：
    ```bash
    # Windows PowerShell
    $env:OPENCLAW_GATEWAY_PORT="18790"
    # Windows CMD
    set OPENCLAW_GATEWAY_PORT=18790
    ```
2.  **固定变量 (可选)**：你可以在系统环境变量里永久新增一个 `OPENCLAW_GATEWAY_PORT`，值设为 `18790`。
3.  **启动服务**：设置好后，用 `openclaw gateway start` 启动，新端口就会自动生效。

> **端口优先级**：需要留意的是，OpenClaw 端口定义的优先级是：`--port` 命令行参数 ＞ `OPENCLAW_GATEWAY_PORT` 环境变量 ＞ `gateway.port` 配置文件 ＞ 默认 18789[reference:3]。

### ⚠️ 更换端口后的注意事项
改完端口，下面这几点也别忘了检查：

*   **API 调用与集成**：如果你有用代码或外部工具直接调用 OpenClaw 的 API，记得把请求 URL 里的端口号一并修改[reference:4]。
*   **防火墙规则 (Windows)**：新端口（如 `18790`）默认可能被 Windows 防火墙拦截，需要去**控制面板**手动添加入站规则放行[reference:5]。
*   **云服务器部署**：如果你在云服务器（如阿里云、腾讯云等）上部署，除了服务器的防火墙，还需要在云控制台的**安全组规则**里放行新端口[reference:6]。
*   **虚拟环境 (VM/WSL)**：如果你在虚拟机或 WSL 中运行，建议设置绑定地址为 `0.0.0.0` 并检查网络模式，然后通过 `http://虚拟机IP:新端口` 访问。

### 我（提问）

那我换一个端口启动

### THINK

我们注意到用户贴出了OpenClaw网关启动的日志。日志显示网关在端口18791上启动成功（浏览器控制监听），但有一个模型预热超时的警告。用户可能想知道是否正常，或者是否需要处理。需要解读这个日志，告诉用户这是正常现象（模型预热超时不影响使用），并解释如何解决或忽略。同时也可以确认端口已经换成18791，解决了之前的问题。

### DeepSeek

很好！从日志看，你的 OpenClaw 已经成功在 **新端口 18791** 上启动并运行了。

## ✅ 日志解读

| 行 | 含义 | 是否正常 |
|---|------|----------|
| `[gateway] starting channels and sidecars...` | 启动插件和辅助进程 | ✅ 正常 |
| `[hooks] loaded 5 internal hook handlers` | 加载了5个内部钩子 | ✅ 正常 |
| `[browser/server] Browser control listening on http://127.0.0.1:18791/ (auth=token)` | 浏览器控制服务已在 `18791` 端口监听，使用 token 鉴权 | ✅ **启动成功** |
| `[gateway] ready` | 网关就绪 | ✅ 成功 |
| `[heartbeat] started` | 心跳检测开始 | ✅ 正常 |
| `[gateway] startup model warmup timed out after 5000ms; continuing without waiting` | 模型预热超时（5秒），继续启动 | ⚠️ **可忽略** |

## 💡 关于「模型预热超时」的警告

这个**不是错误**，只是一个提示：
- **原因**：启动时，OpenClaw 会尝试预先调用一下你配置的大模型 API，以验证配置并减少首次请求的延迟。如果 API 响应较慢（网络延迟或模型服务端冷启动），5秒内没收到回复就会超时。
- **影响**：**不影响正常使用**。只是首次对话可能稍微慢一点点（因为需要等模型真实响应），后续对话完全正常。
- **如何消除**：如果不想看到这个警告，可以：
  - 检查 API Key 配置是否正确（`openclaw doctor`）
  - 增加预热超时时间：在配置文件中设置 `"startupModelWarmupTimeoutMs": 15000`（15秒）
  - 或者直接忽略，不影响使用

## 🌐 访问管理面板

现在可以通过浏览器访问：
```
http://127.0.0.1:18791/
```
注意：日志里提示 `(auth=token)`，说明可能需要 token 认证。如果打开后提示输入 token，可以在 `~/.openclaw/openclaw.json` 中找到 `gateway.auth.token` 的值，或者直接在命令行执行 `openclaw dashboard` 让它自动打开。

## ✅ 检查端口占用

现在可以确认新端口正常工作：
```powershell
netstat -ano | findstr :18791
```
应该看到只有一个 `LISTENING` 状态的连接，PID 是新的。

## 🎉 总结

你已经成功更换端口并启动了 OpenClaw，模型预热超时的警告可以放心忽略。现在可以开始使用你的 AI 助手了！如果后续遇到 API 调用失败或者对话没反应的问题，再运行 `openclaw doctor` 检查一下 API Key 配置即可。

### 我（提问）

claw security audit`.
15:53:11 [gateway] starting channels and sidecars...
15:53:17 [hooks] loaded 5 internal hook handlers
15:53:18 [browser/server] Browser control listening on http://127.0.0.1:18791/ (auth=token)
15:53:18 [gateway] ready
15:53:18 [heartbeat] started
15:53:27 [gateway] startup model warmup timed out after 5000ms; continuing without waiting

