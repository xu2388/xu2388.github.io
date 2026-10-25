---
title: JavaWeb · Socket 网络编程与简易服务器
subject: JavaWeb
category: 课程笔记
source: 豆包对话 · Java SE 中 I/O、网络、GUI 的具体含义及用途 / JavaWeb 自学 / TCP 三次握手逐段精讲 / 功能流程及工作流描述
summary: Socket 是 Java 对一条 TCP 连接的进程内句柄，connect 触发三次握手，accept 返回的已是完成握手的连接。ServerSocket 负责绑定与监听，阻塞式服务器按每连接一线程扩展，受文件描述符、线程栈与上下文切换限制。TCP 只提供字节流，消息边界必须由应用层用分隔符、定长或长度字段划分。BIO、NIO 到 Netty 的演进，本质是把等待方式从阻塞改为就绪通知，并封装事件循环与编解码。
---

# JavaWeb · Socket 网络编程与简易服务器

## 一、概述：网络 API 在 Java SE 中的位置

Java SE 的网络能力集中在 `java.net` 包。原料把这一层的作用概括为「解决不同设备上的 Java 程序之间的数据传输问题」，并列出四组核心类型：

| 类型 | 协议/层次 | 典型用途 | 关键类 |
|---|---|---|---|
| TCP 编程 | 传输层，面向连接 | 聊天室、文件传输、自定义应用协议 | `Socket`、`ServerSocket` |
| UDP 编程 | 传输层，无连接 | 广播、音视频、可容忍丢包的场景 | `DatagramSocket`、`DatagramPacket` |
| HTTP 请求 | 应用层，通常跑在 TCP 上 | 抓取网页、调用接口 | `URL`、`HttpURLConnection` |
| IP 操作 | 网络层 | 解析域名、取本机地址 | `InetAddress` |

原料同时强调，网络 API「底层依赖了 I/O」：连接建立之后，收发数据仍然要通过输入流与输出流完成。因此 Socket 编程是 I/O 模型与网络协议的交汇点，`InputStream` 的阻塞语义、缓冲区的边界，都会直接决定服务器能承受多少连接、消息会不会粘在一起。

需要先划清一个概念：**Socket 不是协议，而是操作系统提供给进程的通信端点句柄**。TCP 的状态机、重传、流量控制都在内核里，Java 的 `Socket` 对象只是把「一个五元组（源地址、源端口、目的地址、目的端口、协议）」包装成可读写的对象。理解这一点，才能解释为什么 `accept()` 返回时握手已经完成，为什么 `close()` 之后还会出现 `TIME_WAIT`。

TCP 与 UDP 的差别，原料用「打电话」与「发短信」作比：TCP 面向连接、可靠、字节流；UDP 无连接、不保证到达、保留报文边界。这个比喻在工程上的落点是：TCP 的 `read()` 不保留发送方一次 `write()` 的边界，而 UDP 的 `receive()` 一次就是一个数据报。后文的粘包问题只属于 TCP。

## 二、三次握手在 Socket API 上的映射

### 2.1 握手报文回顾

原料对三次握手的拆解可以压缩成一张表。设客户端初始序号为 $x$，服务器初始序号为 $y$：

| 次序 | 方向 | 标志与序号 | 发送后状态 | 是否携带数据 | 是否消耗序号 |
|---|---|---|---|---|---|
| 第一次 | 客户端 → 服务器 | `SYN=1, seq=x` | 客户端 `SYN-SENT` | 否 | 是，消耗 $x$ |
| 第二次 | 服务器 → 客户端 | `SYN=1, ACK=1, seq=y, ack=x+1` | 服务器 `SYN-RCVD` | 否 | 是，消耗 $y$ |
| 第三次 | 客户端 → 服务器 | `ACK=1, seq=x+1, ack=y+1` | 双方 `ESTABLISHED` | 可以携带 | 纯 ACK 不消耗 |

原料特别标注了两条容易被忽略的规则：SYN 报文不能带用户数据，但一定消耗一个序号；纯 ACK 报文不消耗序号，所以第三次握手的 `seq` 仍是 $x+1$，客户端此后发送的第一条数据也从 $x+1$ 开始。确认号的含义是「期望收到的下一个字节序号」，即

$$
ack = \text{收到对方的 } seq + \text{收到的数据字节数}.
$$

握手的目的不是「打招呼」，而是双方各自确认两件事：对方的发送能力正常、自己的接收能力正常，同时交换并同步初始序号。只握手两次时，服务器无法确认客户端是否收到了自己的 SYN，也无法确认客户端的接收能力，因此需要第三次。

### 2.2 API 调用与内核状态的对应

把 Java 调用插到上面这张表里，时序如下：

| 阶段 | 客户端 | 服务器 | 内核动作 |
|---|---|---|---|
| 准备监听 | — | `new ServerSocket(port)` | 创建套接字、`bind`、`listen`，进入 `LISTEN` |
| 发起连接 | `new Socket()` 后 `connect(...)`，或直接 `new Socket(host, port)` | `accept()` 阻塞 | 客户端发送 SYN，进入 `SYN-SENT` |
| 握手完成 | `connect` 返回 | `accept` 返回一个新的 `Socket` | 服务器收到 ACK 后连接进入 `ESTABLISHED`，被放入 accept 队列 |
| 数据传输 | `getInputStream()` / `getOutputStream()` | 对返回的 `Socket` 取流 | 双向字节流 |
| 关闭 | `close()` | `close()` | 四次挥手，主动关闭方进入 `TIME_WAIT` |

这张表里最重要的一行是第三行：**`accept()` 不执行握手，它只是从已完成握手的队列里取出一条连接**。服务器内核在收到 SYN 后回 SYN+ACK，收到第三次 ACK 后就把连接标记为 `ESTABLISHED` 并挂到 accept 队列；应用程序调用 `accept()` 时，如果队列非空就立刻返回，如果队列为空就睡眠等待。因此：

- `accept()` 返回的 `Socket` 已经处于可读写状态，不需要再调用 `connect()`。
- 客户端 `connect()` 返回时，客户端一侧也已 `ESTABLISHED`；但服务器应用可能还没调用 `accept()`，这不影响客户端开始发送数据，数据会暂存在内核接收缓冲区。
- 如果应用程序长期不 `accept()`，队列会满，新的 SYN 可能被丢弃或收到 RST，表现为客户端连接超时或被拒绝。

`ServerSocket` 的构造方法可以指定 backlog：

```java
ServerSocket server = new ServerSocket(9000, 50, InetAddress.getByName("127.0.0.1"));
```

第二个参数是内核 accept 队列的提示长度，第三个参数限定绑定的网卡地址。绑定 `127.0.0.1` 只允许本机访问，绑定 `0.0.0.0` 或省略地址则监听所有网卡。很多「本机能连、别的机器连不上」的问题，根源不是防火墙，而是绑定了回环地址。

### 2.3 关闭过程与状态残留

连接关闭走四次挥手：主动关闭方发送 FIN，对方回 ACK，等对方数据发完再发 FIN，最后回 ACK。主动关闭方在发送最后一个 ACK 后进入 `TIME_WAIT`，等待 $2\,\mathrm{MSL}$ 才释放。原料在讲握手时没有展开四次挥手，但工程上必须知道两个后果：

1. **服务端主动关闭大量短连接会积累 `TIME_WAIT`**，占用本地端口与内核内存。HTTP/1.1 的 `keep-alive` 正是为了减少反复建连、断开，原料在 HTTP 章节明确写了「建立一次 TCP 连接之后，可以连续发送多次请求」。
2. **`close()` 不等于对方立刻收到 FIN**。如果输出缓冲区还有数据，正常关闭会先把数据发完；`setSoLinger(true, 0)` 则会丢弃缓冲区直接发 RST，属于异常关闭手段，不应作为常规优化。

Java 的 `Socket.close()` 会同时关闭输入流与输出流。如果只想单向结束发送，可以调用 `shutdownOutput()`，它发送 FIN，但仍可继续读取对方数据，这叫半关闭。协议设计里常用半关闭表示「请求发完了，等响应」。

### 2.4 半连接队列与握手失败

内核里其实有两个队列。收到 SYN、尚未收到第三次 ACK 的连接放在**半连接队列**（SYN queue），已经完成握手、等待应用 `accept` 的连接放在**全连接队列**（accept queue）。两个队列的长度都有上限，backlog 主要影响后者。

这个区分解释了三类常见现象：

- **客户端连接超时**：半连接队列满，新的 SYN 被丢弃，客户端按指数退避重传 SYN，最终超时。
- **客户端连上后长时间无响应**：全连接队列满，内核可能丢弃第三次 ACK，客户端以为自己已连接，服务器应用却取不到连接。
- **SYN Flood 攻击**：大量伪造源地址的 SYN 占满半连接队列，正常用户无法完成握手。SYN cookie 是常见的缓解手段，由内核参数控制，不需要应用层改代码。

从 API 角度看，`accept()` 只能看到全连接队列，半连接队列对 Java 程序完全透明。因此「调大 backlog」不一定能解决连接失败，还要看半连接队列与内核参数。

### 2.5 UDP 对照：没有握手，也没有连接

UDP 不建立连接，`DatagramSocket` 的 `send` 与 `receive` 直接以数据报为单位：

```java
DatagramSocket socket = new DatagramSocket(9001);
byte[] buf = new byte[1024];
DatagramPacket packet = new DatagramPacket(buf, buf.length);
socket.receive(packet);              // 阻塞到收到一个数据报
String text = new String(packet.getData(), packet.getOffset(),
                         packet.getLength(), StandardCharsets.UTF_8);
```

与 TCP 相比有三点关键差异：

| 维度 | TCP | UDP |
|---|---|---|
| 连接 | 三次握手建立，四次挥手释放 | 无连接，直接收发 |
| 边界 | 字节流，需应用层划界 | 一次 `receive` 就是一个数据报，天然有边界 |
| 可靠性 | 确认、重传、排序、流量控制 | 不保证到达、不保证顺序、可能重复 |
| 开销 | 握手、头部、状态维护 | 头部小，无状态 |
| 适用 | 文件、网页、需要可靠有序的业务 | 实时音视频、广播、可容忍丢包的探测 |

`DatagramPacket` 的 `getLength()` 必须使用，不能用 `buf.length`：接收缓冲区是复用的，`getData()` 返回整个数组，只有 `getLength()` 才是本次数据报的实际长度。这是 UDP 编程最常见的越界与脏数据来源。UDP 单个数据报还有大小上限，超过 MTU 会在 IP 层分片，任一分片丢失整个数据报就报废，因此应用层通常主动把消息控制在较小尺寸。

## 三、ServerSocket 与 Socket 的生命周期

### 3.1 ServerSocket 的四个动作

`ServerSocket` 的生命周期可以概括为绑定、监听、接受、关闭：

- **绑定**：`bind(SocketAddress)` 或构造方法完成，把套接字与本地地址、端口关联。端口被占用时抛 `BindException`。
- **监听**：`listen` 由构造方法或 `bind` 隐式完成，内核开始接收该端口的 SYN。
- **接受**：`accept()` 取出已完成握手的连接，返回新的 `Socket`。`accept()` 本身抛 `IOException`，在 `ServerSocket` 关闭时会以 `SocketException` 形式结束阻塞。
- **关闭**：`close()` 停止监听并释放端口。已接受的连接不受影响，需要各自关闭。

`setSoTimeout(milliseconds)` 可以让 `accept()` 最多阻塞指定时间，超时抛 `SocketTimeoutException`，这对「服务器要能响应退出信号」的场景很有用。

### 3.2 Socket 的选项

`Socket` 在连接前后都可以设置选项，常用的几个如下：

| 选项 | 作用 | 常见误用 |
|---|---|---|
| `TCP_NODELAY` | 关闭 Nagle 算法，小包立即发送 | 以为能解决粘包，其实只改变发送时机 |
| `SO_TIMEOUT` | 读操作的最长阻塞时间 | 设为 0 表示无限等待，容易永久挂起 |
| `SO_KEEPALIVE` | 让内核探测死连接 | 探测周期由系统决定，不能当应用层心跳 |
| `SO_RCVBUF` / `SO_SNDBUF` | 调整内核缓冲区 | 盲目调大只会增加内存占用 |
| `SO_REUSEADDR` | 允许绑定处于 `TIME_WAIT` 的地址 | 与「端口被占用」混淆 |

`TCP_NODELAY` 值得单独说明。Nagle 算法会把小数据攒起来等确认，减少网络上的小包；对交互式协议，这会造成额外延迟，所以聊天、游戏、RPC 通常开启 `TCP_NODELAY`。但它不提供消息边界，开启或关闭都不改变「TCP 是字节流」的事实。

### 3.3 常见异常与定位

| 异常 | 典型原因 | 定位方向 |
|---|---|---|
| `BindException: Address already in use` | 端口被其他进程占用，或处于 `TIME_WAIT` | 换端口、查占用进程、评估 `SO_REUSEADDR` |
| `ConnectException: Connection refused` | 目标端口没有监听，或绑定了错误地址 | 先确认服务端 `accept` 前是否已成功 `bind` |
| `SocketTimeoutException` | 连接或读取超时 | 检查网络、服务端处理耗时、是否忘记 `flush` |
| `UnknownHostException` | 域名无法解析 | 检查 DNS 与主机名拼写 |
| `SocketException: Connection reset` | 对端进程崩溃或被强制关闭，发送了 RST | 查对端日志与是否 `SO_LINGER` 强制关闭 |
| `SocketException: Broken pipe` | 向已关闭的连接写数据 | 协议是否缺少响应确认 |

这些异常的共同点是：**它们描述的是连接状态，不是业务错误**。捕获后打印堆栈只是最低要求，服务器还需要决定是关闭该连接、重试，还是把错误传给上层。

### 3.4 端口、地址与 InetAddress

端口号标识主机上的一个进程，原料把它比作「门牌号」。0 到 1023 是系统端口，普通进程通常无权绑定；1024 到 49151 是注册端口，应用一般从中选择；49152 以上是临时端口，客户端主动连接时由内核分配。服务器绑定 0 表示让内核挑一个空闲端口，随后用 `getLocalPort()` 取回实际值，这在测试中很方便：

```java
try (ServerSocket server = new ServerSocket(0)) {
    int actualPort = server.getLocalPort();
    System.out.println("bound to " + actualPort);
}
```

`InetAddress` 负责地址与域名的转换。`InetAddress.getByName("localhost")` 可能返回 IPv4 或 IPv6 地址，取决于系统的解析顺序；`InetAddress.getLocalHost()` 在多网卡机器上可能返回一个不可达的地址。需要精确控制时，应显式使用 `InetSocketAddress` 并指定地址族，而不是依赖默认解析。IPv6 与 IPv4 的兼容还涉及双栈套接字，绑定 `::` 是否能同时接受 IPv4 连接，取决于操作系统的 `IPV6_V6ONLY` 设置。

## 四、阻塞式服务器的线程模型与连接数上限

### 4.1 单线程循环：一次只能服务一个连接

最朴素的写法是在 `accept()` 之后直接在当前线程读写：

```java
try (ServerSocket server = new ServerSocket(9000)) {
    while (true) {
        try (Socket socket = server.accept()) {
            handle(socket);   // 读写都在当前线程完成
        }
    }
}
```

它的吞吐量上限不是 CPU，而是「一个连接停留多久」。只要 `handle` 里的 `read()` 阻塞，其他已经完成握手的连接就只能排在 accept 队列里。这个模型适合「同一时刻只有一个客户端」的演示，不适合任何真实服务。

### 4.2 每连接一线程

把 `handle` 交给新线程，`accept` 循环就能立刻回去接下一个连接：

```java
while (true) {
    Socket socket = server.accept();
    new Thread(() -> handle(socket)).start();
}
```

这是经典的 thread-per-connection 模型，也是教材讲 Socket 服务器时最常给出的形态。它的优点是编程模型简单：每个连接内部的读、写、解析都是顺序代码，不需要状态机。缺点是连接数直接换算成线程数：

- **文件描述符**：每个连接占一个 fd，进程的 `RLIMIT_NOFILE` 决定上限。Linux 上可用 `ulimit -n` 查看，耗尽后 `accept` 会失败。
- **线程栈**：每个平台线程都有独立的栈，大小由 JVM 的 `-Xss` 决定，默认值随平台与版本变化。线程越多，虚拟内存与页表开销越大。
- **上下文切换**：大量线程处于可运行状态时，调度开销会吞掉业务时间。
- **内存缓冲**：每个连接至少有一对输入/输出缓冲区，连接数上升时堆外与堆内占用同步上升。

### 4.3 线程池：把「无限」变成「有界」

把 `new Thread` 换成线程池，可以把并发处理数限制在可控范围：

```java
ExecutorService pool = Executors.newFixedThreadPool(16);
while (true) {
    Socket socket = server.accept();
    pool.execute(() -> handle(socket));
}
```

这时系统里同时存在的连接数仍然可以远大于 16：内核会继续完成握手，把连接放进 accept 队列，`accept` 也会继续取出并提交任务，任务在池的队列里等待。也就是说，**线程池限制的是「同时处理数」，不是「同时连接数」**。要限制连接数，需要在 accept 之后做信号量控制，或者干脆不 accept，让内核队列承担背压。

线程池大小的粗略依据是 Little 定律：

$$
L = \lambda W,
$$

其中 $L$ 是系统中同时处理的请求数，$\lambda$ 是到达率，$W$ 是每个请求的平均处理时间。若每个连接长期占用线程（长连接、长轮询），$W$ 会非常大，线程池就会成为瓶颈，这时应当转向 NIO。

### 4.4 连接数上限的组成

一个阻塞式服务器的实际上限由以下最小值决定：

| 约束 | 说明 | 观察方式 |
|---|---|---|
| 进程 fd 上限 | 每个连接一个 fd，监听套接字也占一个 | `ulimit -n`、`/proc/<pid>/limits` |
| 内核 accept 队列 | backlog 满后新连接被丢弃或拒绝 | `ss -lnt` 的 `Send-Q` |
| 线程数上限 | 受栈大小、内存、调度器影响 | 线程 dump、`jstack` |
| 堆内存 | 每连接缓冲区、会话对象 | GC 日志、堆 dump |
| 端口范围 | 客户端主动连接时受本地临时端口限制 | `ip_local_port_range` |

原料没有给出这些数字，也不应该给：它们全部依赖操作系统配置与 JVM 参数。工程上的结论是**先测量再调参**，而不是背一个「最大连接数」。

### 4.5 长连接与短连接的取舍

短连接是「一次请求一条连接」，用完立即关闭。它的优点是服务器不需要维护会话状态，连接故障的影响范围小；缺点是每次都要握手、挥手，且主动关闭方会留下 `TIME_WAIT`。长连接是「连接建立后反复复用」，省掉建连开销，适合高频交互；缺点是每条连接都要占资源，且需要心跳、空闲回收、断线重连。

判断依据是「建连成本与请求频率的比值」。请求稀疏且无状态时，短连接更简单；请求密集、需要服务端推送时，长连接更合适。HTTP/1.1 默认 `keep-alive`，但服务器必须设置空闲超时与最大请求数，否则大量空闲连接会把线程或 fd 占满。原料在 HTTP 章节强调的「减少建立和关闭连接的消耗和延迟」，正是长连接的价值；而「连接会被中间设备静默回收」则是长连接必须用心跳兜底的原因。

## 五、粘包与拆包

### 5.1 现象

客户端连续发送两条消息 `"hello"` 与 `"world"`，服务器一次 `read` 可能读到 `"helloworld"`，也可能第一次只读到 `"hel"`、第二次读到 `"loworld"`。前者叫粘包，后者叫拆包（半包）。这两种现象都不是 TCP 的缺陷，而是**字节流没有消息边界**的必然结果。

### 5.2 成因

- TCP 是字节流协议，不保留 `write()` 的调用边界。发送方的两次 `write` 可能被合并成一个报文段，也可能被拆成多个。
- Nagle 算法会攒小包；接收方的缓冲区会合并到达的数据。
- MSS 限制导致大消息被切分；网络路径上的分片与重组对应用层不可见。
- 接收方调用 `read(byte[])` 时，返回的是「当前缓冲区里已有的字节数」，不是「一条消息」。

因此「粘包」这个说法本身是应用层视角的错觉，准确的表述是：**应用层没有定义消息边界，却假设了 `read` 一次就是一条消息**。

### 5.3 三种划界方案

| 方案 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| 定长 | 每条消息固定 $n$ 字节，不足补齐 | 解析最简单 | 浪费带宽，长度受限 |
| 分隔符 | 用 `\n`、`\0` 等特殊字节结尾 | 可读性好，适合文本协议 | 消息内容不能含分隔符，或需要转义 |
| 长度字段 | 先写 4 字节长度，再写正文 | 二进制安全，边界精确 | 需要处理长度字段本身的半包 |

前两种在文本协议里常见：HTTP 头用 CRLF 分行，Redis 协议用 CRLF 加长度前缀，`BufferedReader.readLine()` 就是分隔符方案。第三种是自定义二进制协议的标准做法。

### 5.4 长度字段的实现

发送端：

```java
public static void writeMessage(OutputStream raw, String text) throws IOException {
    byte[] body = text.getBytes(StandardCharsets.UTF_8);
    DataOutputStream out = new DataOutputStream(raw);
    out.writeInt(body.length);   // 先写 4 字节大端长度
    out.write(body);             // 再写正文
    out.flush();
}
```

接收端必须用 `readFully`，因为它会一直读到指定字节数或流结束，不会像 `read` 那样「读多少算多少」：

```java
public static String readMessage(InputStream raw) throws IOException {
    DataInputStream in = new DataInputStream(raw);
    int length = in.readInt();          // 半包时在这里阻塞，直到 4 字节到齐
    if (length < 0 || length > 1 << 20) {
        throw new IOException("非法长度: " + length);
    }
    byte[] body = new byte[length];
    in.readFully(body);                 // 半包时继续等待
    return new String(body, StandardCharsets.UTF_8);
}
```

这段代码有两个工程要点。第一，长度字段必须做上限校验，否则对端声明一个超大长度会导致 `OutOfMemoryError`，这是典型的拒绝服务入口。第二，长度字段使用大端序，`DataOutputStream.writeInt` 已经保证，跨语言实现时要对齐字节序。

### 5.5 分隔符方案的坑

`readLine()` 以 `\n`、`\r\n` 为界，使用简单，但有两个限制：消息内容不能包含换行；如果对端只发送了半行就断开，`readLine()` 会返回已经读到的残余内容或 `null`。当消息本身是任意文本时，需要先转义分隔符（例如把 `\n` 替换为 `\\n`），否则解析必然错位。

## 六、BIO、NIO 与 Netty 的演进逻辑

### 6.1 BIO：等待发生在业务线程

BIO（Blocking I/O）指 `InputStream.read()`、`accept()` 这类调用会一直阻塞到有数据或出错。thread-per-connection 是 BIO 的典型形态：一个线程从读到写全程陪着一条连接。它的模型直观，但线程是昂贵资源，连接数一大就难以为继。原料在讲 Java SE 的 I/O 时把 `java.io` 称为「传统 I/O」，把 `java.nio` 称为「更高效的新 I/O」，这个「高效」指的就是不必为每条连接常驻一个线程。

### 6.2 NIO：把「等数据」变成「问就绪」

NIO 的三个核心组件是 Channel、Buffer、Selector：

- **Channel** 是双向通道，既可读也可写，替代了 InputStream/OutputStream 的单向模型。
- **Buffer** 是数据容器，读写通过 `flip()`、`clear()`、`compact()` 切换位置与界限。
- **Selector** 是就绪事件的多路复用器，一个线程可以注册多个 Channel，等待「哪些连接可读/可写/可接受」。

典型循环：

```java
Selector selector = Selector.open();
serverChannel.configureBlocking(false);
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select();                      // 阻塞到至少一个事件就绪
    Iterator<SelectionKey> it = selector.selectedKeys().iterator();
    while (it.hasNext()) {
        SelectionKey key = it.next();
        it.remove();                        // 必须手动移除，否则重复处理
        if (key.isAcceptable()) {
            SocketChannel client = serverChannel.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            // 从 Channel 读入 ByteBuffer，处理半包
        }
    }
}
```

`select()` 返回的是「就绪的通道数」，不是「数据条数」。可读只表示缓冲区里有字节，仍然可能只读到半条消息，所以 NIO 并没有消灭粘包与拆包，只是把等待方式换成了事件通知。

### 6.3 原生 NIO 的复杂度

直接用 NIO 写服务器，需要自己处理：

- 半包与粘包的缓冲区拼接；
- 写操作未写完时的 `OP_WRITE` 注册与取消，否则 `select()` 会空转；
- 连接建立、断开、异常时的资源回收；
- 编解码、心跳、空闲检测、流量控制。

这些逻辑与业务无关，却极易写错。Netty 的价值就在于把它们封装成可复用的组件。

### 6.4 Netty：事件循环与流水线

Netty 的核心抽象可以对应到 NIO 的概念：

| Netty 组件 | 对应概念 | 作用 |
|---|---|---|
| `EventLoopGroup` | Selector 线程池 | 一个 EventLoop 绑定一个线程，处理多个 Channel |
| `Channel` | SocketChannel | 连接的网络抽象 |
| `ChannelPipeline` | 责任链 | 入站/出站处理器依次经过 |
| `ByteBuf` | ByteBuffer | 读写索引分离，支持池化 |
| `LengthFieldBasedFrameDecoder` | 长度字段拆包 | 自动处理半包与粘包 |
| `IdleStateHandler` | 心跳 | 读写空闲超时回调 |

一个最小的 Netty 服务端骨架：

```java
EventLoopGroup boss = new NioEventLoopGroup(1);
EventLoopGroup worker = new NioEventLoopGroup();
try {
    ServerBootstrap bootstrap = new ServerBootstrap();
    bootstrap.group(boss, worker)
        .channel(NioServerSocketChannel.class)
        .childHandler(new ChannelInitializer<SocketChannel>() {
            @Override
            protected void initChannel(SocketChannel ch) {
                ch.pipeline()
                  .addLast(new LengthFieldBasedFrameDecoder(1 << 20, 0, 4, 0, 4))
                  .addLast(new StringDecoder(StandardCharsets.UTF_8))
                  .addLast(new SimpleChannelInboundHandler<String>() {
                      @Override
                      protected void channelRead0(ChannelHandlerContext ctx, String msg) {
                          ctx.writeAndFlush("echo: " + msg);
                      }
                  });
            }
        });
    ChannelFuture future = bootstrap.bind(9000).sync();
    future.channel().closeFuture().sync();
} finally {
    boss.shutdownGracefully();
    worker.shutdownGracefully();
}
```

`LengthFieldBasedFrameDecoder` 的参数依次是最大帧长、长度字段偏移、长度字段字节数、长度调整值、剥离字节数。它把「读满 4 字节长度、再读满正文」的循环封装进解码器，业务处理器收到的已经是完整消息。

### 6.5 演进逻辑一句话

BIO 用「线程等待连接」，NIO 用「一个线程轮询多个连接的就绪状态」，Netty 用「事件循环 + 流水线」把 NIO 的样板代码产品化。三者的分界不是协议不同，而是**等待成本由谁承担**：BIO 由业务线程承担，NIO 由 Selector 承担，Netty 由框架的事件循环承担。选择时先看连接规模与协议复杂度，再看团队对异步编程的掌握程度，不必为了「先进」而提前引入 Netty。

## 七、可运行的回显服务器骨架

下面给出一个基于线程池的 TCP 回显服务器。它使用 `BufferedReader.readLine()` 作为分隔符方案，客户端每发一行，服务器回一行；客户端关闭连接时 `readLine()` 返回 `null`，处理线程退出。

```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class EchoServer {
    private static final int PORT = 9000;
    private static final int POOL_SIZE = 16;

    public static void main(String[] args) throws IOException {
        ExecutorService pool = Executors.newFixedThreadPool(POOL_SIZE);
        try (ServerSocket server = new ServerSocket(PORT)) {
            System.out.println("echo server listening on " + server.getLocalPort());
            while (true) {
                Socket socket = server.accept();       // 已完成三次握手
                pool.execute(() -> handle(socket));    // 交给工作线程
            }
        } finally {
            pool.shutdown();
        }
    }

    private static void handle(Socket socket) {
        String remote = socket.getRemoteSocketAddress().toString();
        try (Socket s = socket;
             BufferedReader in = new BufferedReader(
                     new InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8));
             PrintWriter out = new PrintWriter(
                     new OutputStreamWriter(s.getOutputStream(), StandardCharsets.UTF_8), true)) {
            System.out.println("connected: " + remote);
            String line;
            while ((line = in.readLine()) != null) {
                out.println("echo: " + line);          // autoFlush 为 true，换行即发送
            }
        } catch (IOException e) {
            System.err.println("connection error: " + remote + " -> " + e.getMessage());
        } finally {
            System.out.println("closed: " + remote);
        }
    }
}
```

配套客户端：

```java
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class EchoClient {
    public static void main(String[] args) throws Exception {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress("127.0.0.1", 9000), 3000);
            socket.setSoTimeout(5000);

            PrintWriter out = new PrintWriter(
                    new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));

            out.println("hello");
            System.out.println(in.readLine());

            out.println("socket");
            System.out.println(in.readLine());
        }
    }
}
```

运行步骤：先启动 `EchoServer`，再运行 `EchoClient`，客户端应依次打印 `echo: hello` 与 `echo: socket`。若用 `telnet 127.0.0.1 9000` 或 `nc 127.0.0.1 9000` 手工连接，每输入一行并回车，服务器就回一行。

这个骨架刻意保留了三个可观察点：

1. **`accept()` 的返回时机**：客户端 `connect` 成功后，即使服务器还没执行到 `accept`，连接也已建立；`accept` 只是把它从队列取出。
2. **线程池的边界**：把 `POOL_SIZE` 调小，再开大量客户端，会看到部分连接已建立但没有响应，因为任务在池队列里排队。
3. **`readLine()` 的边界**：发送不带换行的内容，服务器不会回复，因为分隔符还没出现；这正是分隔符方案的语义。

如果要传输二进制或消息内含换行，应把 `readLine` 换成上一节的长度字段方案，并把 `PrintWriter` 换成 `DataOutputStream`。

### 7.1 心跳、超时与重连

TCP 的 `SO_KEEPALIVE` 由内核定时探测，周期长且不可控，不能替代应用层心跳。自定义协议通常约定三类控制帧：`PING`、`PONG`、`BYE`。客户端每隔固定间隔发送 `PING`，服务器回 `PONG`；连续多个周期没有收到任何数据，就判定连接失效并主动关闭。心跳间隔应小于中间设备（NAT、负载均衡）的空闲回收时间，否则连接会被静默丢弃。

读超时需要区分两种语义：`connect` 超时控制「握手最多等多久」，`SO_TIMEOUT` 控制「读最多等多久」。前者用 `socket.connect(address, timeout)` 设置，后者用 `socket.setSoTimeout(timeout)` 设置。两者都不设置时，失败可能表现为线程永久阻塞，而不是异常。

重连不能写成 `while (true) { try { connect(); } catch (...) {} }` 的紧循环，否则会瞬间打满 CPU 与对端 accept 队列。合理做法是指数退避加抖动：失败后等待一个逐渐增长、带随机偏移的时间，再尝试下一次，并设置最大重试次数。

### 7.2 从回显服务器到 HTTP 服务器

HTTP 本身就是「跑在 TCP 上的文本协议」。原料在 HTTP 章节给出的请求行格式是：

```
GET /index.html HTTP/1.1
Host: example.com
```

如果把 `EchoServer.handle` 换成「读第一行、按空格切出方法、路径、版本，再读头部直到空行」，就已经具备了一个极简 HTTP 服务器的雏形。Tomcat 做的事情更多：解析请求头、管理连接池与线程池、把请求封装成 `HttpServletRequest`、按 URL 映射到 Servlet、把响应写回套接字。原料把 Tomcat 描述为「负责解析 HTTP 协议、解析请求数据、并发送响应数据」的 Web 服务器，这个描述落到 Socket 层，就是「accept 连接、读字节、按 HTTP 语法切分、写字节」。

这个视角能解释两个 JavaWeb 常见现象：

- **HTTP/1.1 的 `keep-alive` 会长期占用连接**。对 BIO 容器，这意味着一个线程被一条连接占住；对 NIO 容器，连接只是 Selector 上的一个注册项。Tomcat 的连接器因此分为 BIO、NIO、APR 等实现。
- **请求体大小、头部大小都有上限**。服务器不能让客户端声明一个无限大的 `Content-Length` 然后照单全收，否则一个连接就能耗尽内存。这与长度字段必须校验上限是同一个道理。

## 八、易错点

1. **把 `accept()` 当成握手**。`accept()` 返回时连接已经建立；握手由内核完成。客户端 `connect` 返回也不代表服务器已经 `accept`。
2. **在 `accept` 循环里同步处理**。单线程读写会让服务器退化为「一次一个客户端」，第二个连接只能排队。
3. **忘记 `flush`**。`PrintWriter` 的 `autoFlush` 只对 `println`、`printf` 等格式化方法生效；直接 `write` 后不 `flush`，数据可能一直留在缓冲区。
4. **把 `read()` 的返回值当消息长度**。`read(byte[])` 返回本次读到的字节数，可能小于数组长度，也可能把多条消息读在一起。
5. **用平台默认字符集**。`new String(bytes)`、`getBytes()` 不带参数会依赖系统默认编码，跨平台时中文乱码。统一显式指定 `StandardCharsets.UTF_8`。
6. **`SO_TIMEOUT` 设为 0**。0 表示无限等待，客户端异常掉线时读线程可能永久挂起；应设置合理超时并处理 `SocketTimeoutException`。
7. **在 GUI 线程里做网络请求**。Swing 的事件分发线程被 `read()` 阻塞后，界面会假死；网络操作应放到工作线程，再用 `SwingUtilities.invokeLater` 更新界面。
8. **关闭顺序错误**。先关输入流再关输出流通常没问题，但包装流会级联关闭底层流；重复关闭一般安全，关闭后再读写会抛 `SocketException`。
9. **绑定地址错误**。绑定 `127.0.0.1` 只接受本机连接；容器或跨机访问需要绑定 `0.0.0.0`，同时确认防火墙与安全组。
10. **用 `TCP_NODELAY` 治粘包**。它只影响发送时机，不提供消息边界；治粘包只能靠应用层协议。
11. **忽略半包的长度字段**。长度字段本身也可能只到一半，必须用 `readFully` 或带状态的缓冲区累积。
12. **把 `close()` 当成「对方一定收到」**。正常关闭会尽量发送缓冲区数据，但网络中断、RST、对端崩溃都会让数据丢失，可靠语义需要应用层确认。

## 九、小结

Socket 编程的主线可以压缩成三句话：

- **连接由内核建立，Java 只负责发起与取出**。`connect` 触发三次握手，`accept` 从完成队列取连接，`close` 触发四次挥手。
- **阻塞式服务器的扩展单位是线程**。thread-per-connection 直观但受 fd、栈、上下文切换约束；线程池限制的是处理并发，不是连接总数。
- **TCP 是字节流，消息边界要自己划**。定长、分隔符、长度字段是三种基本方案，NIO 与 Netty 只改变等待与编解码方式，不改变这条约束。

| 问题 | 直接原因 | 处理位置 |
|---|---|---|
| 第二个客户端无响应 | `accept` 循环内同步处理 | 改为线程池 |
| 连接建立但无回显 | 任务排队、未 `flush`、缺分隔符 | 查池大小、`autoFlush`、协议 |
| 中文乱码 | 默认字符集不一致 | 显式 UTF-8 |
| 消息粘连或截断 | 未定义消息边界 | 长度字段或分隔符 |
| 端口被占用 | 旧进程或 `TIME_WAIT` | 查占用、换端口、评估 `SO_REUSEADDR` |
| 连接数上不去 | fd 上限、backlog、线程栈 | 逐项测量，不要盲调 |

把这六行记住，再回头看任何一段 Socket 代码，都能快速判断它卡在哪一层。
