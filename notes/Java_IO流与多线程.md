---
title: Java IO 流与多线程 · 学习笔记
subject: JavaWeb
category: 课程笔记
source: 豆包对话 · Java IO 操作题目答案与解析
summary: 以本科 Java 课程复习为线索，把 IO 流按处理单元（字节流 / 字符流）、流向（输入 / 输出）、角色（节点流 / 处理流）三个维度归位，梳理 `File`、缓冲流、`SequenceInputStream`、管道流、`RandomAccessFile` 与 `PrintStream` 标准流重定向的用法，讲清转换流对中文乱码的处理及 `Serializable`、`transient`、`serialVersionUID` 的序列化规则；多线程部分对比 `Thread` 继承与 `Runnable` 实现两种创建方式，展开 `Callable` 加 `FutureTask` 的带返回值线程、五种状态流转、`sleep`/`yield`/`join`/优先级调度、`synchronized` 同步与 `wait`/`notify` 通信，并补充线程池的通用用法。
---

# Java IO 流与多线程 · 学习笔记

## 一、概述

本文围绕 Java 核心语言的两条主线展开：其一为 **IO 流体系**，解决程序与外部世界（文件、内存、网络、控制台）之间的数据传输；其二为 **多线程**，解决单序执行流无法兼顾并发任务的问题。两条主线在「管道流用于线程间通信」「`synchronized` 与 `StringBuffer` 的线程安全」等处交汇。

原始材料是本校一套课程作业与期末复习题的逐题解答，题量很大且大量以「选项—标准答案」形式堆叠。笔记已把题目本身剥离，仅抽取题目背后的知识点按逻辑重排，不复现题干、题号、选项与任何「答案对应关系」；涉及校名、人名处一律泛化。学习过程中几处易混淆点（如 `start()` 与 `run()`、同步方法的锁对象、字符数与字节数）在正文单列标注。

全文结构为：IO 流体系 → 多线程 → 常见误区 → 总结要点。

---

## 二、IO 流体系

### 2.1 三个分类维度

Java 的 `java.io` 包提供输入输出能力。流可以从三个正交维度分类，初学时若把它们混为一谈极易出错。

按**处理单元**分，是字节流与字符流两条独立体系：

| 维度 | 字节流 | 字符流 |
|---|---|---|
| 处理单元 | 字节（8 位 `byte`） | 字符（16 位 `char`） |
| 输入抽象基类 | `InputStream` | `Reader` |
| 输出抽象基类 | `OutputStream` | `Writer` |
| 适用数据 | 二进制与文本皆可（图片、音视频、任意文件） | 仅文本 |
| 命名特征 | 多以 `Stream` 结尾 | 多以 `Reader` / `Writer` 结尾 |

按**流向**分（始终以程序内存为参照系）：输入流把外部数据读入内存，输出流把内存数据写出到外部。输出流只写不读，不存在「从输出流读数据」的用法。

按**在装配中的角色**分，是节点流与处理流（详见 2.2）。三个维度可叠加描述同一个对象，例如 `BufferedReader` 同时是「字符流 + 输入流 + 处理流」。

### 2.2 节点流与处理流

节点流（低级流）直接对接数据源，负责最基础的一次读或写；处理流（高级流 / 包装流）不直接面向数据源，而是套在节点流之上，用装饰器的方式增强功能。

| 类别 | 核心特点 | 常见示例 |
|---|---|---|
| 节点流 | 直接连接文件 / 内存 / 管道等数据源 | `FileInputStream`、`FileOutputStream`、`FileReader`、`FileWriter`、`ByteArrayInputStream`、`PipedInputStream` / `PipedOutputStream` |
| 处理流 | 必须包装节点流，提供缓冲、类型转换、序列化等附加能力 | `BufferedReader`、`BufferedWriter`、`InputStreamReader`、`DataInputStream`、`ObjectOutputStream` |

装配时遵循「处理流套节点流」的顺序，例如 `new BufferedReader(new FileReader("a.txt"))`。`InputStreamReader`、`OutputStreamWriter` 是**转换流**：把一个字节流包装成字符流，并在包装时指定字符集，这是解决中文乱码的关键手段（见 2.6）。

缓冲流的性能来源值得单独理解。缓冲区是内存中临时存放数据的中转区：写时先攒在缓冲区，攒满或调用 `flush()` 时才一次性落到设备；读时一次多取一些进缓冲区，后续直接从内存拿。其收益在于**减少了程序与磁盘 / 网络的交互次数**，因为设备读写远慢于内存。`flush()` 强制清空输出缓冲区并落盘，`close()` 在关闭前也会自动刷新。

### 2.3 File：路径抽象而非流

`File` 类不是流，它是文件或目录**路径的抽象表示**，只负责路径层面的操作（判断存在、取名、增删、列目录），不负责读写文件内容；读内容必须交给 IO 流。

常用构造与方法：

```java
File dir  = new File("data");           // File(String pathname)
File file = new File(dir, "a.txt");     // File(File parent, String child)

file.getName();        // 名称（含后缀），不含路径
file.exists();         // 是否存在
file.isFile();         // 是否普通文件
file.isDirectory();    // 是否目录
file.length();         // 文件字节数（long），空文件返回 0，不抛异常
file.createNewFile();  // 按需创建文件
file.mkdir();          // 创建单层目录
```

两点常被误解：其一，创建 `File` 对象时即便路径不存在也不会立刻报错，只有真正执行创建、删除等操作才可能抛异常；其二，`length()` 对空文件返回 0，不会抛空指针。目录过滤依赖 `FilenameFilter` 接口（它是接口，需用实现类或匿名内部类），重写 `accept(File dir, String name)`：对每个子项执行一次，返回 `true` 才保留，参数 `dir` 是父目录、`name` 是子项名称。

```java
File[] txts = dir.listFiles((d, name) -> name.endsWith(".txt"));
```

### 2.4 try-with-resources

Java 7 起推荐用 try-with-resources 自动关流，避免手动 `close()` 遗漏导致的资源泄漏：

```java
try (BufferedReader br = new BufferedReader(new FileReader("data.txt"))) {
    String line = br.readLine();   // 一次读一行；读到文件末尾返回 null
    if (line != null) {
        System.out.println(line);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

需牢记两个「末尾哨兵」的差异：`InputStream.read()` 读到末尾返回 **-1**，而 `BufferedReader.readLine()` 读到末尾返回 **null**，二者不可混用。

### 2.5 高级流

**SequenceInputStream（顺序输入流）** 继承自 `InputStream`，把多个输入流「串联」成一个逻辑流，按先后顺序依次读取，读完一个（其 `read()` 返回 -1）自动切到下一个。它做的是顺序拼接，不是并行读取，其价值在于合并流的逻辑而非提速。连接两个流用构造方法 `SequenceInputStream(InputStream s1, InputStream s2)`，多个流可用 `Enumeration` 版本。

**管道流** `PipedInputStream` / `PipedOutputStream` 专门用于**线程间通信**：一个线程写、另一个线程读。两者必须配对建立连接，连接有两种方式：构造时传入 `new PipedInputStream(out)`，或事后 `in.connect(out)`。一个关键约束是**不能在同一线程里同时读写**——管道缓冲区有限，写满会阻塞、读空会阻塞，同线程收发会相互死锁。

**RandomAccessFile（随机访问文件）** 是一个独立的类，直接继承 `Object`，**不继承** `InputStream` / `OutputStream`。它的核心能力是靠文件指针随机读写：`seek(long pos)` 绝对定位、`skipBytes(int n)` 相对跳过、`getFilePointer()` 取当前位置、`writeInt` / `readInt` / `writeUTF` / `readUTF` 读写基本类型。打开模式常见的有 `"r"`（只读，写会抛 `IOException`）、`"rw"`（读写，文件不存在则创建），以及 `"rws"`、`"rwd"`（在读写基础上要求更新同步落盘）。

```java
try (RandomAccessFile raf = new RandomAccessFile("data.txt", "rw")) {
    raf.writeInt(100);           // int 占 4 字节，写完指针移到 4
    raf.seek(0);                 // 跳回文件开头
    int v = raf.readInt();       // 重新读回 100
}
```

指针位置随写入数据类型自动移动（`int` 4 字节、`char` 2 字节），`seek` 从文件头算、`skipBytes` 从当前位置算，两者混用是易错点。

**PrintStream 与标准流重定向**。`System.out`、`System.err` 是 `PrintStream`（字节输出流），`System.in` 是 `InputStream`；程序默认把它们接到控制台。通过 `System` 的三个静态方法可改变其去向，实现「重定向」：

| 默认流 | 类型 | 重定向方法 | 参数类型 |
|---|---|---|---|
| `System.in` | 标准输入 | `System.setIn()` | `InputStream` |
| `System.out` | 标准输出 | `System.setOut()` | `PrintStream` |
| `System.err` | 标准错误 | `System.setErr()` | `PrintStream` |

把打印内容改写进文件的典型一行是：

```java
System.setOut(new PrintStream(new FileOutputStream("output.txt")));
```

要点：`setOut()` / `setErr()` 必须传 `PrintStream`，通常用 `new PrintStream(new FileOutputStream(...))` 包装文件输出流；`out` 与 `err` 相互独立，重定向其一不影响另一个；重定向后原目标（如键盘输入）失效，若要恢复可再次调用相应 `set` 方法。

### 2.6 字节流与字符流处理中文的差异

字节流以 8 位字节为单位，字符流以 16 位 `char` 为单位，中文在两种单位下的「计数」完全不同，这是乱码与误算的根源。

先厘清「字符数」与「字节数」两个概念：`String.length()` 统计的是 **char 个数**，英文、数字、汉字都各算 1 个字符；只有折算成字节时中英文占用才不同——在 **UTF-8** 下一个英文占 1 字节、一个汉字占 3 字节，在 **GBK** 下一个英文占 1 字节、一个汉字占 2 字节。

```java
"Abc中文".length();                 // 字符数 5（不分中英文）
"Abc中文".getBytes("UTF-8").length; // 字节数 3 + 2*3 = 9
"Abc中文".getBytes("GBK").length;   // 字节数 3 + 2*2 = 7
```

因此：读写纯文本首选字符流（它以字符为单位、能配合字符集，天然规避半个汉字被截断的问题）；读写图片、音视频等二进制必须用字节流。当数据源本身是字节流（例如网络、`System.in`）而内容是文本时，用转换流 `InputStreamReader` / `OutputStreamWriter` 在包装时指定一致的字符集来完成字节到字符的解码，读写两端编码不一致才会乱码。

### 2.7 序列化

序列化把对象转换成字节序列以便存盘或传输，反序列化再把字节还原成对象。前提是该对象所属类实现了标记接口 `java.io.Serializable`（无抽象方法，实现即生效；`Externalizable` 是其需自定义逻辑的变体）。负责读写的是一对处理流：`ObjectOutputStream.writeObject(Object)` 写对象、`ObjectInputStream.readObject()` 读对象，后者返回 `Object`，通常需强制类型转换。二者都不能直接连文件，要包装 `FileOutputStream` / `FileInputStream` 这类节点流。

```java
class User implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private transient String password;   // 敏感字段不参与序列化
}
```

几条规则值得记牢：

- `transient` 修饰的字段被跳过，不写入字节流，反序列化后取默认值，常用于口令、临时状态。
- `serialVersionUID` 是版本标识；类结构改动后若版本不一致，反序列化会失败。
- 序列化**不具继承性**：子类可序列化不代表父类可序列化。父类若未实现 `Serializable`，其成员不被保存，反序列化时通过父类无参构造初始化。
- 对象引用也要可序列化：类 A 若持有类 B 的引用字段，B 也必须实现 `Serializable`。
- **同一对象多次写入不会重复存储**：第一次写完整数据并分配一个序列号（句柄），后续只写该序列号的引用标记。这套机制同时避免了对象图循环引用导致的无限递归。

反序列化读回时，`readObject()` 无法预知具体类，故返回 `Object`，需要 `(User) ois.readObject()` 强转。

---

## 三、多线程

### 3.1 进程与线程

进程是操作系统中**拥有独立地址空间与系统资源**的执行实体，有新建、就绪、运行、阻塞、销毁的完整生命周期，进程之间相互隔离、崩溃互不影响。线程是进程内的更小执行单元：同一进程下的多个线程**共享该进程的地址空间与资源**，各自仅持有少量私有数据（如程序计数器、栈）。创建线程的开销远小于创建进程，因而并发多任务通常用多线程。

### 3.2 两种创建方式：Thread 与 Runnable

创建线程有两条路径。其一是继承 `Thread` 并重写 `run()`；其二是实现 `Runnable` 接口，再把任务对象交给 `Thread` 构造方法。

```java
// 方式一：继承 Thread
class MyThread extends Thread {
    public void run() {
        System.out.println(Thread.currentThread().getName());
    }
}
new MyThread().start();

// 方式二：实现 Runnable
class MyTask implements Runnable {
    public void run() {
        System.out.println(Thread.currentThread().getName());
    }
}
Thread t = new Thread(new MyTask(), "Download-Thread"); // 绑定任务并命名
t.start();
```

| 维度 | 继承 `Thread` | 实现 `Runnable` |
|---|---|---|
| 耦合度 | 任务与线程绑定在一个类里 | 任务（`Runnable`）与执行者（`Thread`）分离 |
| 继承限制 | 占用唯一继承名额，不能再继承别的父类 | 接口可实现，仍保留继承空间 |
| 传参 / 复用 | 每个线程一个实例 | 同一 `Runnable` 实例可被多个线程共享 |
| 推荐度 | 简单场景 | 更通用、更符合面向对象的推荐做法 |

贯穿两种方式的一条铁律是**必须调用 `start()` 而非 `run()`**：`start()` 会向操作系统申请线程资源、使线程进入就绪状态并异步执行 `run()`；直接调用 `run()` 只是一次普通的同步方法调用，不会开辟新线程。`Thread(Runnable target, String name)` 用于在建线程时一并指定名字。

### 3.3 带返回值的线程：Callable 与 FutureTask

`Runnable.run()` 没有返回值也不能抛检查异常。要「让线程算出一个结果并取回来」，用 `Callable<V>` 配合 `FutureTask<V>`。`Callable` 的 `call()` 有返回值且允许 `throws`，但它**不能直接**交给 `Thread`——`Thread` 只认 `Runnable`。`FutureTask` 同时实现了 `Runnable` 与 `Future` 两个接口，正好充当桥梁：把 `Callable` 包装成 `FutureTask`，就能既作任务传给 `Thread`，又能用 `get()` 取结果。

```java
class MyCall implements Callable<Integer> {
    public Integer call() throws Exception {
        return 100;
    }
}
FutureTask<Integer> task = new FutureTask<>(new MyCall());
new Thread(task).start();
Integer result = task.get();   // 子线程未算完时会阻塞调用线程，返回 call() 的结果
```

| 维度 | `Runnable` | `Callable<V>` |
|---|---|---|
| 执行方法 | `run()` | `call()` |
| 返回值 | 无（`void`） | 有（泛型 `V`） |
| 抛检查异常 | 不能 | 可以 `throws` |
| 直接传给 `Thread` | 可以 | 不行，须用 `FutureTask` 包装 |
| 获取结果 | 无 | `FutureTask.get()`（阻塞） |

`FutureTask` 的泛型应与 `Callable` 的返回类型一致；`get()` 在结果就绪前会阻塞当前线程，而非立刻返回 `null`。

### 3.4 线程生命周期与状态

课程采用经典的**五状态模型**：新建、就绪、运行、阻塞、死亡。其流转条件如下：

| 起点 → 终点 | 触发条件 |
|---|---|
| 新建 → 就绪 | 调用 `start()` |
| 就绪 → 运行 | 获得 CPU 资源 |
| 运行 → 就绪 | `yield()` 主动让出、时间片用完 |
| 运行 → 阻塞 | `sleep()`、`wait()`、`join()`、阻塞式 IO、等待同步锁 |
| 阻塞 → 就绪 | 睡眠到点、被 `notify()` / `notifyAll()` 唤醒、获得锁、IO 返回 |
| 运行 → 死亡 | `run()` 正常结束或抛出未捕获异常 |

需理解两个易错点。`yield()` 只是让运行线程回到就绪队列、可能马上又被调度，并不进入阻塞。阻塞的诱因很多，`sleep()` 只是其中一种；阻塞结束后先回**就绪**、必须重新抢到 CPU 才谈得上运行，而非直接回运行态。

一个值得记录的补充：JDK 里 `Thread.State` 实际枚举是 **NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED** 六个。五状态模型把「就绪」和「运行」合并在 `RUNNABLE`，又把「阻塞」细分为 `BLOCKED`（等锁）、`WAITING`（`wait()` / 无参 `join()` 无限等待）、`TIMED_WAITING`（`sleep()` / `wait(long)` 计时等待）。两套说法是同一现实的不同粒度，答题用五态、读源码按六态。

### 3.5 线程调度：sleep、join、优先级

| 手段 | 归属 | 行为 | 是否释放持有的锁 |
|---|---|---|---|
| `Thread.sleep(ms)` | 静态，作用于当前线程 | 让当前线程计时阻塞一段时间 | 否 |
| `Thread.yield()` | 静态 | 运行线程让出 CPU 回到就绪 | 否 |
| `t.join()` | 实例 | 使**调用它的（主）线程**阻塞，直到 `t` 结束 | —— |
| `interrupt()` | 实例 | 置中断标记；对阻塞中线程会抛 `InterruptedException` | —— |

优先级由 `setPriority(int)` 设置，取值范围用三个静态常量表达：

| 常量 | 数值 | 含义 |
|---|---|---|
| `Thread.MIN_PRIORITY` | 1 | 最低 |
| `Thread.NORM_PRIORITY` | 5 | 默认（普通） |
| `Thread.MAX_PRIORITY` | 10 | 最高 |

子线程默认继承创建它的父线程优先级，主线程默认即 `NORM_PRIORITY`。但优先级只是调度倾向，高优先级线程仍可主动 `yield()` / `sleep()`，并不意味着独占 CPU。守护线程（`setDaemon(true)`，需在 `start()` 前设置）为前台线程服务，JVM 的垃圾回收线程即属此类；当所有前台线程结束后 JVM 退出，守护线程随之自动消亡。

### 3.6 线程安全与同步

多个线程共享同一可变资源又无协调时，会出现读到旧值、更新丢失等线程安全问题。`synchronized` 提供两种写法：**同步代码块** `synchronized(锁对象){...}` 与**同步方法**（在方法上加 `synchronized`）。

```java
class DepositTask implements Runnable {
    private final Account account;          // 多线程共享的同一对象
    public void run() {
        synchronized (account) {            // 以共享对象为锁
            account.balance += 1000;
        }
    }
}
```

三条结论是笔者当时反复混淆之处：

其一，锁的对象必须是**多个线程共享的同一把锁**才能排队。同步方法的锁：非静态方法锁的是 `this`（当前实例），静态方法锁的是类对象。若两个线程各自 `new` 出不同实例再去调 `synchronized` 实例方法，`this` 不同，等于各拿各的锁，同步失效。

其二，**读—计算—写要整体放进锁内**。只在写操作外加锁、把读取与计算留在锁外，多线程仍会同时读到旧值并相互覆盖，结果并不确定。抢票防超卖的要点是「在锁内先判断余量再扣减」，不能先判断后加锁。

其三，锁的释放时机。执行完同步块、块内 `return`、块内抛出未捕获异常，以及调用锁对象的 `wait()`，都会释放锁；而 `sleep()` 与 `yield()` **不会**释放锁。

线程间的协作通信依赖 `Object` 的 `wait()` / `notify()` / `notifyAll()`：三者都必须在同步区内、以锁对象为调用者使用。线程调用 `wait()` 会释放锁并进入等待，直到被 `notify()` / `notifyAll()` 唤醒后重新竞争锁。

顺带一提，可变字符串两兄弟正对应「多线程共享」这一场景：

| 特性 | `StringBuffer` | `StringBuilder` |
|---|---|---|
| 线程安全 | 安全，方法均加 `synchronized` | 不安全，无锁 |
| 性能 | 因加锁开销较低 | 无锁，单线程更快 |
| 出现版本 | JDK 1.0 | JDK 1.5 |
| 适用 | 多线程共享同一字符串对象 | 单线程频繁拼接（日常首选） |

`String` 本身不可变（见配套数组与字符串笔记，此处不展开），可变性上 `StringBuffer` 与 `StringBuilder` 同类，差别几乎只在是否加锁。

### 3.7 线程池（通用用法补充）

原材料只在考纲里点到线程池、未展开。此处按其标准用法作一补述：频繁创建、销毁线程开销大，线程池通过**复用一批工作线程**来处理大量任务，降低创建成本并可控并发数。JDK 用 `java.util.concurrent` 提供这一能力，常见入口是 `Executors` 工厂方法配合 `ExecutorService`：

```java
ExecutorService pool = Executors.newFixedThreadPool(3);
pool.submit(new MyTask());          // 提交 Runnable
Future<Integer> f = pool.submit(new MyCall());  // 提交 Callable，经 Future 取结果
Integer r = f.get();
pool.shutdown();                    // 不再接收新任务，待已提交任务完成后终止
```

`submit` 提交 `Runnable` 返回 `Future<?>`、提交 `Callable<V>` 返回 `Future<V>`，取结果思路与 3.3 的 `FutureTask` 一致。该段为通用规范补充，非原题材料内容，实际生产更推荐用 `ThreadPoolExecutor` 显式指定核心线程数、队列与拒绝策略。

---

## 四、常见误区

- 只认「`Stream` 结尾即字节、`Reader` / `Writer` 结尾即字符」，却忘了 `PrintStream` 是**字节**输出流、`System.in` 声明类型是 `InputStream` 而非 `PrintStream`。
- 以为处理流能直连文件；实则必须套在节点流上，`ObjectOutputStream` 直接 `new` 一个文件路径的用法不成立。
- 把 `RandomAccessFile` 当成 `InputStream` 的子类——它继承自 `Object`，独立成套读写方法。
- 混淆 `writeObject()`（写对象）与 `write()`（写字节）；序列化对象用前者。
- 混淆末尾哨兵：`InputStream.read()` 返回 -1 表示结束，`BufferedReader.readLine()` 返回 null 表示结束。
- 把 `read(byte[] b, int off, int len)` 的 `off` 当成「流的偏移量」——它是**目标数组**的起始下标；返回值是本次实际读到的字节数，可能小于 `len`，到末尾为 -1。具体读到多少取决于流实现与剩余数据，不必死记某个固定数字。
- 记不清键盘输入的字节构成：每按一次回车会产生一个行结束字节，故 `System.in` 读到的字节数随输入与数组长度而变，同样不宜记成某个固定值。
- 同步只锁写、把读与计算放在锁外，或误以为「加了 `synchronized` 就一定安全」而忽视锁对象是否为同一把。
- 以为 `sleep()` / `yield()` 会释放锁——不会；只有 `wait()`（及退出同步块 / `return` / 异常）才释放。
- 把 `start()` 写成 `run()`，结果并未启动新线程。
- 把 `Callable` 直接传给 `new Thread(...)`——须用 `FutureTask` 包装；`get()` 是阻塞取结果，不会立刻返回 null。
- 用 `String.length()` 去估字节大小：它数的是 `char` 个数，中英文都算 1，字节数须走 `getBytes(charset)`。

## 五、总结要点

1. IO 流按处理单元（字节 / 字符）、流向（输入 / 输出）、角色（节点 / 处理）三维分类；四个抽象基类是 `InputStream`、`OutputStream`、`Reader`、`Writer`。
2. 节点流直连数据源，处理流包装节点流以增强；缓冲流靠减少设备交互次数提速，靠 `flush()` / `close()` 落盘；转换流 `InputStreamReader` / `OutputStreamWriter` 在指定字符集下打通字节与字符，是中文乱码的解法。
3. `File` 只管路径不管内容；`SequenceInputStream` 顺序串联输入流；管道流用于线程间通信且不可同线程收发；`RandomAccessFile` 独立于流体系、靠指针随机读写，模式有 `r` / `rw` / `rws` 等；`PrintStream` 与 `System.setIn/setOut/setErr` 实现标准流重定向。
4. 序列化靠 `Serializable`、`ObjectOutputStream.writeObject` / `ObjectInputStream.readObject`（返回 `Object` 需强转）；`transient` 跳过字段，`serialVersionUID` 标识版本，序列化不继承、同一对象靠句柄只存一份。
5. 多线程两种创建方式中 `Runnable` 更解耦；务必 `start()` 非 `run()`；带返回值用 `Callable` + `FutureTask`，`get()` 阻塞取结果。
6. 生命周期五态（新建 / 就绪 / 运行 / 阻塞 / 死亡）对应 JDK 的六枚举；`sleep` / `join` / `yield` / 优先级常量（`MIN`=1、`NORM`=5、`MAX`=10）控制调度，守护线程随前台线程耗尽而亡。
7. `synchronized` 是线程安全核心：锁须共享同对象、读计算写整体入锁、同步方法锁 `this`；`wait` / `notify` / `notifyAll` 在同步区内通信；`sleep` / `yield` 不放锁，`wait` 放锁。线程池以复用线程降低开销，为通用补充。
8. `StringBuffer` 因加锁线程安全而较慢，`StringBuilder` 无锁而快，单线程拼接优先后者。
