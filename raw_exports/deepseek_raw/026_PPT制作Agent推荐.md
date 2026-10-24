---
source: DeepSeek
conversation_id: 535f656f-6941-4f21-9d44-e19573e4e37e
title: PPT制作Agent推荐
inserted_at: 2026-09-04T20:20:33.215000+08:00
updated_at: 2026-09-04T20:23:08.099000+08:00
message_count: 10
---

### THINK

用户想找一个能帮忙做PPT的AI Agent，类似Claude Code那样厉害。我需要提供一些推荐。为了全面覆盖，我会同时进行多项搜索，以获取不同角度的推荐信息。

### THINK

搜索结果显示了很多相关的工具和Agent。为了全面了解这些信息，我需要同时打开这些相关的链接。

### THINK

这些结果提供了很多关于AI PPT生成工具的信息。我的回答将涵盖多个类别，包括开源框架、商业产品等。回答会先进行简要介绍，然后以列表形式列出这些工具，并附上简要说明和来源。最后提供一些选择建议。

### DeepSeek

当然。Claude Code这类工具代表了AI智能体（Agent）在编程领域的深度应用，而在PPT制作领域，同样涌现出了一批能力很强的智能体。它们不再只是简单的模板填充，而是能像人类一样进行**研究、规划、设计、修改**的完整工作流。

下面我按不同需求，为你整理了几款目前比较有代表性的“PPT Agent”：

### 🎓 学术与研究导向

如果你需要制作专业性很强的学术报告、技术路演，且追求内容的深度与准确性，可以关注这两款：

*   **DeepPresenter (中科院PPTAgent第二代)**[reference:0][reference:1]：一款开源的本地幻灯片智能体[reference:2][reference:3]。它的特点是**深度调研**和**视觉反思**。它可以在沙箱环境中自主调用工具查阅arXiv、Google Scholar等学术文献[reference:4]，甚至运行Python代码生成数据图表[reference:5]。它还能通过“写→看→改”的闭环，像设计师一样审视自己的排版并自动优化[reference:6]。9B参数版本性能足以比肩GPT-5[reference:7]，且支持在单张3090显卡或Mac上一键部署[reference:8][reference:9]。
*   **MemSlides**[reference:10][reference:11]：一个**记忆驱动**的Slides智能体框架，由清华、上交、北邮等学者提出[reference:12][reference:13]。它的最大亮点是**擅长多轮修改**和**个性化风格记忆**。它能记住你偏好的风格（如低文字密度、多用图示），并精准执行局部修改，避免误改[reference:14]。实验数据显示，其闭环完成率达96.3%[reference:15]。该项目曾登顶Hugging Face Daily Papers第一名[reference:16][reference:17]。

### 🚀 通用与商业应用

如果你追求便捷、高效，希望快速产出可直接用于商务汇报、产品发布的精美PPT，可以看看这几款：

*   **Gamma**[reference:18]：以**设计感强、生成速度快**著称，输入一句话几十秒就能出成品[reference:19]，非常适合产品发布、融资路演等对外展示场景[reference:20]。免费版提供400积分，付费版$8/月起[reference:21]。需要注意的是，导出为PPTX格式时可能出现排版偏移[reference:22]。
*   **Beautiful.ai**[reference:23]：主打**自动化智能排版**，其“Smart Slide”引擎能根据内容自动调整布局[reference:24]，保证每一页都美观专业[reference:25]。它更适合对设计有高要求、希望保证PPT“下限”很高的用户[reference:26]。免费版限制较多（仅1个演示文稿且无法导出PPTX）[reference:27]，付费版$12-40/月[reference:28]。对中文支持可能存在一些小问题[reference:29]。
*   **Kimi Slides** (月之暗面)：依托Kimi大模型的长文本能力，擅长**基于完整文档（如整篇研报）生成PPT素材**[reference:30][reference:31]。它提供“自适应模式”（30-60分钟，深度研究）和“视觉模式”（5-10分钟，快速生成）两种选择[reference:32]。Web/App端有免费额度[reference:33]。
*   **通义千问AI PPT** (阿里巴巴)：升级了**智能体架构**后，能自动完成从内容构思到视觉排版的全流程[reference:34]。实测显示其生成的PPT大纲**结构清晰、逻辑连贯**[reference:35]。支持同时上传最多10个文件作为素材[reference:36]，并特别优化了**中英混排**能力[reference:37]。
*   **小浣熊3.0** (商汤科技)：定位为 **“AI办公搭子”** [reference:38][reference:39]，目标是交付可直接使用的“成果”而非“草稿”[reference:40][reference:41]。它具备长链条思考能力，支持百万级数据量分析[reference:42]，并能记住用户偏好[reference:43]。已服务大量企业用户[reference:44]。
*   **Manus**[reference:45][reference:46]：一个**通用型AI智能体**，采用更自主的方式[reference:47][reference:48]。你只需给它一个提示，它就会调动并行的子智能体进行**主题研究、资料整理**，最终生成一份完整的演示文稿[reference:49]。其AI幻灯片功能由Gemini 3 Pro驱动[reference:50]。免费版每日刷新300积分[reference:51]，Pro版$20/月起[reference:52]。

### ⚙️ 开发者与开源生态

如果你是开发者，或希望在自有环境中深度集成，这些开源项目很值得关注：

*   **PPT Master**[reference:53][reference:54]：一个开源的AI驱动PPT生成**标准化工作流**[reference:55]。它采用“三角色接力”机制，可将PDF、DOCX、网页链接等10+种输入转化为原生PPTX文件[reference:56][reference:57]。它最大的优势是**不绑定单一平台**，可兼容Claude Code、Cursor等任意AI IDE[reference:58]。
*   **PPT-Agent (SuTn)**[reference:59][!reference:60]：一个提供完整Web界面和可视化操作的开源项目[!reference:61]。它通过自然语言对话，自动完成**主题研究→大纲设计→幻灯片制作**的全流程[reference:62][!reference:63]。支持上传Word、Excel等文件作为素材[!reference:64]，内置9套模板[!reference:65]，并提供了“快速模式”和“标准模式”[!reference:66]。
*   **ai-agent-ppt**[reference:67]：一个**命令行工具**，适合习惯命令行操作的开发者[reference:68]。输入主题或截图即可生成专业演示文稿[reference:69]。
*   **PptGPT (OfficeAI.Chat)**[reference:70]：一个AI智能幻灯片生成**插件**[reference:71]，可结合个人知识库生成匹配答辩、演讲等场景的内容[reference:72]。

### 🧠 其他有潜力的智能体框架

以下是一些在学术或特定领域有亮点的框架，代表了前沿方向：

*   **PreGenie**[reference:73]：一个基于多模态大语言模型（MLLMs）的智能体框架，用于生成高质量视觉演示文稿[reference:74]。
*   **SlideCraft**[reference:75]：一个能感知上下文的生成式智能体，可根据“面向高管”或“项目技术评审”等不同语境自动选择模板[reference:76]。
*   **SlideBot**[reference:77]：一个多智能体框架，专注于生成信息丰富、可靠的多模态演示文稿[reference:78]。

---

总的来说，选择哪个“PPT Agent”，主要看你的核心需求：
*   如果追求**内容的专业深度**和**学术严谨性**，可以关注**DeepPresenter**和**MemSlides**。
*   如果追求**极致的效率**和**惊艳的视觉效果**，**Gamma**和**Beautiful.ai**会是不错的选择。
*   如果希望AI能**自主完成从研究到制作的全部工作**，**Manus**和**Kimi Slides**值得一试。
*   如果你是**开发者**，希望拥有最大的灵活性和掌控力，可以深入研究**PPT Master**等开源项目。

这些工具各有侧重，你可以根据自己的具体场景（是学术汇报、商业路演还是内部汇报）来选择最合适的一款。

### 我（提问）

我们都知道Claudecode ,我现在想要找一个可以帮我做PPT的厉害一点的agent ,有什么推荐吗

### THINK

用户想知道如何使用DeepPresenter。我需要提供具体的安装、配置和使用步骤。为了全面获取信息，我将同时进行多项搜索，涵盖中文和英文资源，以及可能存在的GitHub仓库。

### THINK

搜索结果显示了一些相关页面。为了全面获取信息，我需要同时打开这些页面。

### THINK

这些资料提供了详细的安装和使用说明。我的回答将涵盖前提条件、安装步骤、配置、运行、生成PPT以及常见问题等方面。我会引用这些来源。

### DeepSeek

使用DeepPresenter主要有两种方式，你可以根据自己的情况选择：

1.  **快速体验版**：直接通过命令行工具`uvx`运行，它会自动处理环境，适合想立刻试试看的用户[reference:0]。
2.  **本地部署版**：在本地电脑上完整安装和配置，数据更安全，也适合深度使用[reference:1]。

### ⚙️ 重要前提

开始前，请先注意以下几点：

*   **操作系统**：DeepPresenter **仅原生支持 Linux 和 macOS**。Windows 用户需要通过 WSL（Windows Subsystem for Linux）来运行[reference:2][reference:3]。
*   **硬件配置**：想要流畅运行，推荐配置为**单张 RTX 3090 或更高性能的显卡**，或者性能较强的 **Mac 电脑**[reference:4][reference:5]。
*   **核心依赖**：系统需要 **Python 3.11+** 和 **Node.js** 环境[reference:6][reference:7]。

---

### 🚀 方式一：快速体验（使用 `uvx`）

这是最快捷的方式，适合先感受一下DeepPresenter的能力。它会通过`uvx`工具自动处理大部分环境问题[reference:8]。

1.  **安装 `uv` 工具**：
    在终端中执行以下命令[reference:9]：
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **运行 `onboard` 命令进行配置**：
    这是**最关键的一步**。运行后，会进入一个交互式的引导程序，帮你完成所有必要的设置[reference:10][reference:11]。
    ```bash
    uvx pptagent onboard
    ```
    在这个过程中，你需要准备并填入以下**API密钥**（如果暂时没有，可以尝试了解离线模式，但功能会受限[!reference:12]）：
    *   **LLM API密钥**：用于驱动核心的“研究”和“设计”智能体[!reference:13]。
    *   **MinerU API密钥**：用于解析上传的PDF等文档[!reference:14]。
    *   **Tavily API密钥**：用于让AI智能体进行联网搜索资料[!reference:15]。

3.  **开始生成PPT**：
    配置完成后，就可以用 `generate` 命令来生成PPT了[reference:16]。
    ```bash
    uvx pptagent generate "你的PPT主题，例如：人工智能在医疗领域的应用"
    ```

---

### 🛠️ 方式二：本地部署（从源码安装）

这种方式能让你拥有完全的控制权，适合开发者或需要深度定制的用户[reference:17]。

1.  **克隆项目并进入目录**[reference:18]：
    ```bash
    git clone https://github.com/icip-cas/PPTAgent.git
    cd PPTAgent
    ```

2.  **创建并配置环境**：
    *   **复制配置文件模板**[reference:19][!reference:20]：
        ```bash
        cp deeppresenter/deeppresenter/config.yaml.example deeppresenter/deeppresenter/config.yaml
        cp deeppresenter/deeppresenter/mcp.json.example deeppresenter/deeppresenter/mcp.json
        ```
    *   **编辑 `config.yaml` 和 `mcp.json` 文件**，填入你的各种API密钥和配置[!reference:21]。

3.  **安装Python依赖**[reference:22]：
    ```bash
    pip install -e deeppresenter
    ```

4.  **安装浏览器依赖（Playwright）**[reference:23][reference:24]：
    ```bash
    playwright install-deps
    playwright install chromium
    ```

5.  **启动并使用**：
    安装完成后，可以使用 `pptagent` 命令，用法和快速体验模式类似。
    ```bash
    pptagent generate "你的PPT主题"
    ```

---

### 📝 常见问题与提示

*   **如何获取模型？**：DeepPresenter的核心模型`DeepPresenter-9B`可以在Hugging Face上找到GGUF量化版本[!reference:25]。你可以使用`llama.cpp`等工具来运行它[!reference:26]。
*   **什么是离线模式？**：如果无法获取上述API密钥，可以尝试在配置中开启离线模式。但请注意，**离线模式下，联网搜索、在线文档解析等依赖网络的功能将不可用**[!reference:27]。
*   **遇到问题怎么办？**：建议仔细阅读官方文档，或在GitHub仓库的Issue区寻求帮助[!reference:28]。

建议先从**方式一（快速体验）** 开始，成功运行并了解其工作流程后，再考虑**方式二（本地部署）** 进行深度使用。

### 我（提问）

DeepPresenter (中科院PPTAgent第二代)：一款开源的本地幻灯片智能体。它的特点是深度调研和视觉反思。它可以在沙箱环境中自主调用工具查阅arXiv、Google Scholar等学术文献，甚至运行Python代码生成数据图表。它还能通过“写→看→改”的闭环，像设计师一样审视自己的排版并自动优化。9B参数版本性能足以比肩GPT-5，且支持在单张3090显卡或Mac上一键部署

告诉我具体如何才能使用这个啊

