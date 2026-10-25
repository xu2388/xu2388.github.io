---
title: Java Swing 实战 · 一个简易浏览器的设计与实现
subject: JavaWeb
category: 课程笔记
source: 豆包对话 · Java Swing 简易浏览器实现与课设汇报
summary: 以一个 Java Swing 简易浏览器为线索，串起 GUI、网络编程与项目组织这条实战线。核心结论有三条：其一，界面装配用 BorderLayout 分东南西北中，同一区域重复 add 只会保留最后一个；其二，只有事件分发线程（EDT）能改 UI，所有网络与文件耗时操作放进 SwingWorker 的 doInBackground，在 done 里回 EDT 更新；其三，JEditorPane 只支持 HTML 3.2，不执行 JS、不认 CSS3，大量现代网页渲染不出来是能力边界而非代码缺陷。此外还整理了 HttpURLConnection 的超时与字符集处理、前进后退的双栈与索引两种实现，以及中文乱码、构造期空引用等真实踩坑。
---

# Java Swing 实战 · 一个简易浏览器的设计与实现

## 一、为什么值得单独记一篇

Java 桌面程序在课程里常被拆成三块互不相干的知识：IO 流、网络编程、GUI。但一个「在地址栏输入网址、能显示网页、能前进后退、能另存为」的简易浏览器，恰好把三块拧成一股绳——GUI 负责交互，网络负责取页，IO 负责落盘，再加一条线程纪律把它们粘起来。

这篇笔记只做 GUI + 网络 + 项目组织这条实战线。至于字节流与字符流的分层装配、`Thread`/`Runnable`/`synchronized` 这些流与线程 API 的细节，前面《Java IO 流与多线程》笔记已经系统讲过，这里只在项目实际用到时简述并回指；继承、多态、集合与泛型的系统性讲解则属于《Java 面向对象》那篇，不重复。

原料是一次从零到能跑通、再到答辩复盘的完整过程，代码、报错、能力边界的吐槽都出自真实实现，笔记按实现顺序重排。

---

## 二、需求拆解与整体结构

### 2.1 功能需求

浏览器要做的事情说穿了就一句：把 URL 变成一个能看、能存、能回退的页面。拆细一点：

- 地址栏（`JTextField`）输入 URL，回车或点「转向」按钮加载；
- 网页显示区是一块带滚动条的 `JEditorPane`；
- 一个菜单栏（文件 / 编辑 / 视图）加两个工具栏（功能按钮 + 地址栏）；
- 核心功能：加载、前进、后退、刷新、另存为、查看源代码、全屏、退出。

菜单栏里每个菜单项都配了热键（`Alt+字母`）与快捷键（`Ctrl+字母`），例如「另存为」热键 A、快捷键 `Ctrl+S`，「查看源代码」热键 C、快捷键 `Ctrl+C`。这些只是事件绑定的不同入口，背后的处理方法是同一套。

### 2.2 分层结构

最初的版本是「一个 `SimpleBrowser` 类包打天下」，所有字段、组件、方法都堆在同一个 `extends JFrame` 的类里。功能一多就暴露出耦合问题，于是复盘时按职责重新划成「纵向四层 + 横向支撑」的组织方式。落到这个浏览器项目，可以抽象成四类角色：

| 层次 | 职责 | 项目里的具体落点 |
|---|---|---|
| 界面层 | 窗口、菜单、工具栏、显示区，只做渲染和接收点击 | `ui` 包：主窗口类 + 源码查看弹窗类 |
| 控制 / 业务层 | 流程编排：导航、历史、插件调度 | 导航服务、`HistoryManager` 历史管理 |
| 网络 / 解析层 | 取网页、解析资源链接、路径重写 | `URLConnection` 读取、正则提取 CSS/JS/图片 |
| 工具 / 持久层 | 公共能力与存取 | `util` 包的 `PageSaver`（IO 流另存）、配置存储 |

分层目的原料里讲得很直白：**代码解耦，改界面不用动保存逻辑，改保存不用动数据存取**。调用上遵循单向依赖——界面层调用业务层，业务层再往下走，界面不直接碰文件或网络。

目录结构也随分层收敛成几个包：

```
src/com/browser/
├── Main.java             # 程序入口，启动主窗口
├── ui/                   # 核心 UI 层（主窗口 + 源码弹窗）
├── history/              # 前进后退双栈历史管理
├── util/                 # PageSaver 等工具类（IO 流另存）
└── ...                   # 拓展的 db / model / service 包
```

对课程级的最小实现，其实只要保留 `ui` + `history` + `util` 三块，数据库和业务层都是后加的拓展。

---

## 三、Swing 组件树与容器

一个 Swing 桌面程序本质是一棵「容器套组件」的树。浏览器的树形如：`JFrame`（顶层窗口）里挂着 `JMenuBar`（菜单条），内容面板 `JPanel` 里再挂两块工具栏和一块滚动面板，滚动面板 `JScrollPane` 里包着真正显示网页的 `JEditorPane`。

| 组件 | 类型 | 在浏览器里干什么 |
|---|---|---|
| `JFrame` | 顶层窗口 | 程序主壳，`setTitle`/`setSize`/`setDefaultCloseOperation` |
| `JMenuBar` + `JMenu` + `JMenuItem` | 菜单 | 文件 / 编辑 / 视图三级菜单，绑快捷键 |
| `JToolBar` | 工具栏 | 功能按钮栏 + 地址栏两个 |
| `JTextField` | 单行文本框 | 地址栏输入 URL |
| `JButton` | 按钮 | 转向、后退、前进、另存为等 |
| `JEditorPane` | 富文本组件 | 渲染网页 HTML |
| `JScrollPane` | 滚动容器 | 包住 `JEditorPane` 提供滚动条 |
| `JTextArea` | 纯文本组件 | 源码查看窗口里显示 HTML 原文 |

组装窗口的关键几行：

```java
editorPane = new JEditorPane();
editorPane.setEditable(false); // 只读，禁止用户编辑网页内容
JScrollPane scrollPane = new JScrollPane(editorPane);

JPanel mainPanel = new JPanel(new BorderLayout());
mainPanel.add(toolBar1, BorderLayout.NORTH);
mainPanel.add(toolBar2, BorderLayout.NORTH);
mainPanel.add(scrollPane, BorderLayout.CENTER);
add(mainPanel);
```

源码查看另开一个子窗口，中部放 `JScrollPane` 包 `JTextArea`，底部放按钮面板：

```java
JFrame sourceFrame = new JFrame("网页源代码");
JTextArea textArea = new JTextArea(source.toString());
textArea.setFont(new Font("Consolas", Font.PLAIN, 14));
JScrollPane sp = new JScrollPane(textArea);
sourceFrame.add(sp, BorderLayout.CENTER);
sourceFrame.add(panel, BorderLayout.SOUTH); // panel 是默认的按钮面板
sourceFrame.setVisible(true);
```

这里有个容易被忽略的细节：新建的子窗口一定用 `dispose()` 关闭而不是 `System.exit(0)`，否则关掉源码窗口的同时整个程序都没了。原料里退出按钮和关闭窗口按钮就是刻意分开的：`sourceFrame.dispose()` 只关子窗，`System.exit(0)` 才结束进程。

---

## 四、布局管理器的实际取舍

Swing 不让你在容器里写死像素坐标，而是把摆放交给布局管理器。这个浏览器主要用到三种，它们的实际差异值得对比：

| 布局管理器 | 空间划分方式 | 本项目用它做什么 | 典型副作用 |
|---|---|---|---|
| `BorderLayout` | 东 / 西 / 南 / 北 / 中五个区 | 主窗口骨架：工具栏居北、网页区居中、按钮栏居南 | 同一区放两个组件只会保留最后加的那个；中间区会吃掉全部剩余空间 |
| `FlowLayout` | 从左到右一行排，排满换行 | `new JPanel()` 不给布局时的默认值，用来横排几个按钮 | 窗口缩放时会换行，不做拉伸 |
| `GridLayout` | 等宽等高的行列网格 | 适合九宫格这类整齐格子 | 所有格子一样大，一个组件撑不开 |

原料实际选的是 `BorderLayout` 作骨架，「灵活好用、Swing 自带」。这里踩到一个真实的坑值得单独讲：上面组装代码里 `toolBar1` 和 `toolBar2` 都 `add` 到了 `BorderLayout.NORTH`。按 `BorderLayout` 语义，同一个约束位重复放组件只会保留最后一次加入的那个，所以直接这样写，功能按钮栏会被地址栏覆盖掉。正确做法要么把一个放 `NORTH`、另一个放 `SOUTH`，要么把两条工具栏装进一个纵向堆叠的子面板再整体放 `NORTH`。

顺带说一句 `BoxLayout`：它按水平或垂直一条线排列组件，比 `FlowLayout` 可控（不会乱换行），比 `GridLayout` 灵活（组件可以有不同尺寸），当工具栏要纵向排时是比硬塞进同一个 `NORTH` 区更合适的选择——不过原料最终没走到这一步，这里只作选型对照。

---

## 五、事件监听模型

Swing 是「事件源—事件对象—监听器」三件套的委托事件模型。以地址栏为例，事件源是 `JTextField` 和「转向」`JButton`，用户操作产生一个 `ActionEvent` 对象，注册在源上的 `ActionListener` 回调收到它并做出反应。

```java
private JToolBar createAddressToolBar() {
    JToolBar bar = new JToolBar();
    JLabel label = new JLabel("地址：");
    urlField = new JTextField(30);
    JButton goBtn = new JButton("转向");

    // 点击转向 或 回车，都走同一个加载逻辑
    goBtn.addActionListener(e -> loadPage(urlField.getText().trim()));
    urlField.addActionListener(e -> loadPage(urlField.getText().trim()));

    bar.add(label);
    bar.add(urlField);
    bar.add(goBtn);
    return bar;
}
```

几个要点：

- **Lambda 写法**。`addActionListener(e -> loadPage(...))` 是函数式接口的简写，`e` 就是那个 `ActionEvent`。菜单项、按钮、文本框回车的监听都是同一形状，可读性比匿名内部类好很多。
- **同一逻辑多入口**。快捷键 `Ctrl+S`、菜单项、工具栏按钮指向的都是同一个 `savePage()`，只是绑定在不同组件上，避免功能重复实现。
- **超链接点击是另一类事件**。`JEditorPane` 里的链接点击不是 `ActionEvent`，而是 `HyperlinkListener`，要判断事件类型再处理：

```java
editorPane.addHyperlinkListener(e -> {
    if (e.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
        loadPage(e.getURL().toString());
    }
});
```

`EventType` 有 `ENTERED`（鼠标移入）、`EXITED`（移出）、`ACTIVATED`（点击）三种，只在 `ACTIVATED` 时跳转，否则鼠标一划过就刷新页面。

### 构造顺序的隐患

监听器常在构造期注册，而监听回调里引用的字段可能还没初始化。原料把初始化拆成了明确的先后顺序来规避这个问题：

```java
public MiniBrowser() {
    initWindow();     // 窗口基础属性
    initFields();     // 先建 backStack / forwardStack / currentUrl 等成员变量
    initComponents(); // 再建 Swing 组件并注册监听
    initListeners();  // 统一绑定事件
    loadUrl("https://www.baidu.com"); // 最后才加载，此时字段都就绪
}
```

关键纪律：`initFields` 必须早于 `initComponents`。如果在栈对象还没 `new` 出来之前就注册了一个会读写该栈的监听器，一旦提前触发（比如加载首页就触发了历史入栈），拿到的会是 `null`，抛 `NullPointerException`。最小版 `SimpleBrowser` 把 `historyList` 和 `currentIndex` 放在构造第一行初始化，也是同一考虑的另一种写法。

---

## 六、网络取页与字符集处理

浏览器的心脏是「把 URL 变成内容」。原料里有两条网络路径，分工不同：

| 用途 | 用到的 API | 读法 | 为什么这样选 |
|---|---|---|---|
| 显示网页 | `JEditorPane.setPage(url)` | 组件内部自己连接、下载、渲染 | 一步到位，但要受组件能力限制（见第七节） |
| 另存为原文件 | `new URL(str).openStream()` | 字节流 `InputStream` 转存 | 保真，不做编码转换，存下来和服务器一致 |
| 查看源码 | `URLConnection` / `HttpURLConnection` | 字符流 `BufferedReader` 按行读 | 要转成字符串显示，必须处理字符集 |

### 6.1 建立连接、伪装 UA、设超时

查看源码时用的是 `HttpURLConnection`，它比 `openStream()` 多几层控制：

```java
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestProperty("User-Agent", "Mozilla/5.0...");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
BufferedReader reader = new BufferedReader(
    new InputStreamReader(conn.getInputStream(), "UTF-8")
);
StringBuilder sb = new StringBuilder();
String line;
while ((line = reader.readLine()) != null) {
    sb.append(line).append("\n");
}
```

- `setRequestProperty("User-Agent", ...)`：把 Java 程序伪装成浏览器。部分网站会拒绝无 UA 的请求，不设这行会直接拿到错误页。
- `setConnectTimeout` / `setReadTimeout`：分别限制「建立连接」和「等待数据」的毫秒数。不设时，遇到连不上的服务器，请求会长时间挂着——如果这段跑在界面上，就是灾难（见第八节）。

### 6.2 中文乱码的成因与修复

`InputStreamReader` 把字节解码成字符，靠的是字符集。如果解码用的字符集和网页实际编码不一致，中文就成了乱码。而网页编码既可能是 UTF-8 也可能是 GBK，硬写死 `"UTF-8"` 并不保险。原料给出的稳妥做法是从响应的 `Content-Type` 里把 charset 抠出来：

```java
URLConnection conn = new URL(url).openConnection();
conn.setRequestProperty("User-Agent", "Mozilla/5.0");

String contentType = conn.getContentType();
String charset = "UTF-8"; // 兜底默认
if (contentType != null && contentType.contains("charset=")) {
    charset = contentType.substring(contentType.indexOf("charset=") + 8);
}

try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(conn.getInputStream(), charset))) {
    // 逐行读取源码
}
```

逻辑是：`getContentType()` 通常形如 `text/html; charset=UTF-8`，从 `charset=` 之后截出字符集名（`charset=` 本身长 8 个字符，所以偏移取 `+ 8`），再用这个字符集去构造 `InputStreamReader`。这也印证了《Java IO 流与多线程》里那条：**转换流是解决中文乱码的关键手段**，在这里就是 `InputStreamReader` 显式带上 charset。

顺带一条真实的辨析经验：原料里有这样一个文件，用浏览器打开能看到满满中文，可在文本编辑器里几乎看不到几个汉字。一开始怀疑是编码问题，细查后发现它是 Typora 导出的 HTML，正文里只有样式和结构、中文极少，浏览器上看到的中文内容其实是**脚本动态注入**进去的。这条对浏览器项目是双重提醒：一是乱码不一定是 charset 的锅，得先分清是「解码错」还是「内容本就不在源码里」；二是这类靠 JS 填进去的内容，`JEditorPane` 同样抓不到，因为它的源码读取只拿到静态 HTML。

---

## 七、HTML 展示的能力边界

原料里反复出现一句大实话：**很多现代网页显示不出来**。这不是代码写错，而是 `JEditorPane` 本身的天花板。

- `JEditorPane` 只支持很老的 **HTML 3.2** 标准，对现代 CSS、`<div>` 布局、以及 JavaScript 基本无能为力；
- 它不执行脚本，所以靠 JS 动态渲染内容的页面（如上一条那种），在浏览器里能看、在这里只能看到空壳或样式错乱。

原料的应对不是硬啃渲染，而是**工程上的取舍 + 用户提示**：把 `setPage` 能显示的基础页面作为满足需求的主路径，同时给兼容性差的页面「增加用户提示」，明确告诉用户某些现代网页无法正常渲染。选型阶段还设想过「智能双引擎」——检测到现代网页就切到能跑 JS/CSS3 的第三方内核，但最后收敛成了**只用内置引擎**的单一路线，代码更稳、无第三方依赖：

```java
private void loadWebPage(String url) {
    try {
        if (!url.startsWith("http")) {
            url = "http://" + url; // 协议自动补全，用户常漏写
        }
        mainEditorPane.setPage(url); // 唯一引擎：内置 JEditorPane
        addressBar.setText(url);
    } catch (Exception e) {
        // 加载失败时给一个可见的错误页，而不是崩溃
        mainEditorPane.setText("<html><body><h3>网页加载失败</h3><p>错误信息："
                + e.getMessage() + "</p></body></html>");
    }
}
```

复盘时对「技术沉淀」做过一次逐项核实，坦诚地把没真正落地的说法（比如某些声称的性能技巧）划掉，只保留有代码支撑的部分。这种「说了的要能对上代码」的自查，本身比堆功能更有价值，也是这条实战线最实在的一课。

---

## 八、前进 / 后退：两种数据结构

浏览器要有历史。原料先后给了两种实现，正好对比。

**方案 A：列表 + 游标。** 用一个 `List<String>` 存全部访问记录，一个 `currentIndex` 指向当前页。加载新页时，先把游标之后的记录全删掉（因为这些「未来页」在新分支下失效了），再追加、游标右移：

```java
// 清除当前位置之后的历史
while (historyList.size() > currentIndex + 1) {
    historyList.remove(historyList.size() - 1);
}
historyList.add(url);
currentIndex++;
```

后退是 `currentIndex--`，前进是 `currentIndex++`，判界看 `> 0` 与 `< size()-1`。

**方案 B：双栈。** 一个后退栈 `backStack`、一个前进栈 `forwardStack`，加一个 `currentUrl`。访问新页时把当前页压入后退栈、清空前进栈；后退时把当前页压入前进栈、从后退栈弹出作为当前页；前进反之：

```java
public void navigateTo(String newUrl) {
    backStack.add(currentUrl);
    forwardStack.clear();
    currentUrl = newUrl;
}

public void goBack() {
    if (!backStack.isEmpty()) {
        forwardStack.push(currentUrl);
        currentUrl = backStack.pop();
        loadUrl(currentUrl);
        updateNavigationButtons();
    }
}
```

| 维度 | 列表 + 游标 | 双栈 |
|---|---|---|
| 结构 | 一个 `List` + 一个下标 | 两个 `Stack` + 当前 URL |
| 开新分支 | 手动删除游标之后的元素 | `forwardStack.clear()` 一步清 |
| 前进后退 | 移动下标 | 两栈之间进出弹出 |
| 边界判断 | 下标比较 | `isEmpty()` |

两者的语义一致，双栈把「丢弃未来分支」这件事收敛成一次 `clear`，写起来更贴合「前进后退」这个动作直觉。配套还有一条状态联动：**栈空时对应按钮置灰**——`backStack` 为空就禁用后退按钮，由 `updateNavigationButtons()` / `updateButtonStates()` 统一维护。

---

## 九、后台线程与 EDT 纪律

这一节是整个项目最容易翻车的地方，也是最值得记的一条纪律：**只有事件分发线程（EDT）能改 UI**。Swing 的组件不是线程安全的，从别的线程直接动组件会出问题；反过来，耗时操作绝不能放在 EDT 上做，否则界面直接卡死。

于是分工很清楚：

| 线程 | 该做什么 | 不该做什么 |
|---|---|---|
| EDT（事件分发线程） | 建界面、响应点击、更新组件文字/状态 | 发网络请求、读写大文件 |
| 后台工作线程 | 下载网页、保存文件、递归抓资源等耗时活 | 直接调用组件的 setter 改界面 |

`SwingWorker` 正好把这两半缝起来：`doInBackground()` 在子线程跑耗时活，`done()` 完成后**回到 EDT 执行**，界面更新放这里就安全：

```java
new SwingWorker<Void, Void>() {
    @Override
    protected Void doInBackground() {
        loadWebPage(url);   // 网络请求在后台线程
        return null;
    }
    @Override
    protected void done() {
        updateUI();         // UI 更新回到 EDT 线程
    }
}.execute();
```

这个骨架对，但要和第五节那个 `loadWebPage` 对读才能落地：该方法的体内直接写着 `mainEditorPane.setPage(url)` 与 `addressBar.setText(url)`，若原封不动地把它塞进 `doInBackground`，等于**把 UI 更新搬到了后台线程**，恰好违反本节立的纪律。正确的切法是把两件事拆开——`doInBackground` 只负责连接、读取，把 HTML 文本或 `Document` 存进字段（或用 `SwingWorker<String, Void>` 的返回值 / `publish` 传出来），`done()` 里才调用 `setPage`、`setText` 刷界面；另一条路是让 `setPage` 在 EDT 上发起、靠它自身的异步加载与 `propertyChange` 监听回报状态，界面代码全程不离开 EDT。原料当时的写法正是「搬了线程、没拆方法体」的中间状态，本文按纪律补上这一步。

另存为这种写文件的活也照样包进 `SwingWorker`，避免「保存大页面时界面冻住」：

```java
SwingWorker<Void, Void> worker = new SwingWorker<Void, Void>() {
    @Override
    protected Void doInBackground() throws Exception {
        String content = editorPane.getText();
        try (FileWriter writer = new FileWriter(file)) {
            writer.write(content);
        }
        return null;
    }
};
worker.execute();
```

顺带一个编译层面的坑：匿名内部类后面那对尖括号必须写全类型实参。`new SwingWorker<>() {}` 这种「匿名类用菱形」要 JDK 9 起才允许，在 JDK 8 上直接编译不过；本例统一写成 `new SwingWorker<Void, Void>() {}`，八、九、十节的版本口径都能过。

程序入口也有对应的纪律：整个 GUI 的创建要放进 `invokeLater`，让它跑在 EDT 上。这是所有 Swing 程序的起手式：

```java
public static void main(String[] args) {
    // Swing 组件必须在事件调度线程运行
    SwingUtilities.invokeLater(() -> {
        new SimpleBrowser().setVisible(true);
    });
}
```

原料里对「IO / 网络操作阻塞 Swing 主线程导致界面卡死」这条风险是点名处理的，解法就是上面这套：耗时进子线程、更新回 EDT。至于 `wait`/`notify`、线程池调度这些线程 API 的原理，回看《Java IO 流与多线程》，此处不展开。

---

## 十、异常处理与资源释放

浏览器要对外部世界（网络、磁盘）频繁打交道，异常和流资源必须收尾好。

- **流一律用 try-with-resources 自动关闭**。另存为把网络输入流和本地输出流一起放进括号，读完自动释放：

```java
try (InputStream in = new URL(urlStr).openStream();
     FileOutputStream out = new FileOutputStream(file)) {
    byte[] buffer = new byte[1024];
    int len;
    while ((len = in.read(buffer)) != -1) {
        out.write(buffer, 0, len);
    }
    JOptionPane.showMessageDialog(this, "保存成功！");
} catch (Exception ex) {
    JOptionPane.showMessageDialog(this, "保存失败：" + ex.getMessage());
}
```

- **异常兜住并可见**。`loadPage` / `setPage` 失败时用 `JOptionPane.showMessageDialog` 弹提示，而不是让异常冲到控制台；加载失败还会渲染一个「网页加载失败」的提示页（见第七节代码）。
- **资源边界**。另存为用 `JFileChooser` 让用户选路径，取消就直接返回不写文件；文件名没带 `.html`/`.htm` 时自动补后缀。

关于「查看源码用的是输入流还是输出流」这个答辩高频追问，原料答得干净：显示源码**用输入流**（把网页内容从网络读进程序），保存源码**用输出流**（把内存里的字符串写到本地文件），一进一出配合；读取用 `BufferedReader` 包输入流提速，写出用 try-with-resources 自动关流。

---

## 十一、踩坑实录

把散落在开发过程中的真实问题归拢成一张对照表：

| 现象 | 根因 | 处理 |
|---|---|---|
| 两条工具栏只显示一条 | `BorderLayout` 同一区（都放 `NORTH`）后加的覆盖先加的 | 分开约束位，或用一个子面板纵向堆叠后再放 |
| 中文网页显示成乱码 | `InputStreamReader` 解码字符集与网页实际编码不符 | 从 `getContentType()` 解析 charset，兜底 UTF-8 |
| 「浏览器有中文、编辑器没有」 | 内容靠 JS 动态注入，静态源码本就少 | 认清这不是编码问题；`JEditorPane` 也拿不到这类内容 |
| 现代网页空白 / 样式错乱 | `JEditorPane` 只支持 HTML 3.2，不跑 JS/CSS3 | 内置引擎能力边界，做用户提示；不谎称渲染成功 |
| 点「转向」后界面卡死 | 网络请求跑在 EDT 上 | 放进 `SwingWorker.doInBackground`，`done` 回 EDT 更新 |
| 启动即 `NullPointerException` | 监听器提前触发时成员变量还没建 | `initFields` 先于 `initComponents`，字段先于监听就绪 |
| 关掉源码窗口整个程序退出 | 子窗关闭误用了 `System.exit(0)` | 子窗用 `dispose()`，主窗退出才用 `System.exit(0)` |
| 某些网站返回错误页 | 无 `User-Agent` 被服务器拒绝 | `conn.setRequestProperty("User-Agent", ...)` 伪装浏览器 |

---

## 十二、工程化收尾

**打包与运行。** 纯 Swing 项目对外无运行时依赖，打成 `.jar` 即可交付，别人下载即用。开发期 JDK 版本按原料建议选兼容性好的版本即可（原料提的是 JDK 1.8 / 11 / 17 一线，实测能跑就行）。源码读取里的 `Collectors.joining`、try-with-resources 这些语法要求较新的 JDK，注意别让运行环境低于编译环境。

**目录与命名。** 保持第 2.2 节的分包：`ui` 放界面、`history` 放双栈历史、`util` 放 `PageSaver`，一个类一个职责，答辩时能顺着一个功能讲出它经过哪几层。

**演示与答辩要点。** 原料整理出一套应对追问的口径，值得提炼成方法论：

- 讲加载：地址栏拿 URL → 补全 `http://` → 交给 `JEditorPane.setPage()` 渲染；
- 讲前进后退：双栈，出栈入栈配对，栈空置灰按钮；
- 讲另存为：`JFileChooser` 选路径 → `editorPane.getText()` 取内容 → `FileWriter` 写 → `SwingWorker` 后台跑防卡界面；
- 讲查看源码：`HttpURLConnection` + UA + 超时 → 字符集识别 → `BufferedReader` 逐行读 → 新窗口 `JTextArea` 显示 → 输出流保存。

被问到没做扎实的地方，与其含糊，不如像第十一节那样先承认边界（`JEditorPane` 就是渲染不了现代网页），再讲清楚做了哪些兜底与提示——诚实的能力边界陈述，比夸大更站得住。

---

## 十三、小结

一个简易浏览器，把 GUI 组件树、布局取舍、事件模型、网络连接、字符集、历史数据结构、线程纪律、资源收尾这八件事拧成了一根线。可以带走的核心结论：

1. **界面装配用 `BorderLayout` 分五区**，记住同一区重复 `add` 只保留最后一个；
2. **事件模型是「源—事件—监听器」三件套**，Lambda 只是注册糖，字段要在监听触发前就绪；
3. **网络取页三条路**：显示走 `setPage`、保真走 `URL.openStream()` 字节流、源码走 `HttpURLConnection` 字符流并显式处理 charset；
4. **`JEditorPane` 只认 HTML 3.2**，现代网页渲染不出来是能力边界，用提示兜底而非谎称成功；
5. **只有 EDT 能改 UI**：耗时进 `SwingWorker.doInBackground`，更新在 `done` 回 EDT，入口用 `SwingUtilities.invokeLater`；
6. **流用 try-with-resources、异常给可见提示、子窗用 `dispose`**。

流与线程的 API 细节见《Java IO 流与多线程》；若要走向真正的网页浏览，把内置渲染换成成熟内核是自然的下一步。
