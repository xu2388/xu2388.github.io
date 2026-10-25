---
title: JavaWeb · JDBC 与 DAO 分层
subject: JavaWeb
category: 课程笔记
source: 豆包对话 · 数据库连接类型讲解 / JavaWeb 自学 / 带数据库的论坛系统部署方案 / Java 课程设计浏览器实现讲解 / 功能流程及工作流描述
summary: JDBC 是 Java 访问关系型数据库的统一接口，核心是驱动、连接、语句、结果集与资源关闭五件事。DriverManager 每次取连接都要重新建连，DataSource 把连接交给池管理，省掉握手与认证成本。PreparedStatement 用占位符绑定参数，把数据与 SQL 结构分离，既预编译也阻断注入。事务边界应放在 Service 层，DAO 只负责单表读写，连接必须同源，回滚与关闭都要在 finally 或 try-with-resources 中完成。
---

# JavaWeb · JDBC 与 DAO 分层

## 一、概述：JDBC 在 B/S 架构中的位置

原料在讲 B/S 架构时给出了一条清晰的链路：浏览器通过 HTTP 访问 Web 服务器，Web 服务器内部的 Servlet、JSP 处理业务逻辑，再通过 JDBC 访问数据库服务器。原文的标注是「Web服务器 ←JDBC→ 数据库」，并把 JDBC 定义为「Java 程序连接数据库的技术」。这句话点出了 JDBC 的定位：它不负责页面、不负责业务规则，只负责让 Java 代码执行 SQL 并取回结果。

从分层角度看，一次请求的路径是：

```
浏览器 → HTTP → Tomcat → Servlet/Controller → Service → DAO → JDBC → 数据库
```

JDBC 位于最底层，向上暴露 `Connection`、`PreparedStatement`、`ResultSet` 等接口。Java 通过「驱动 + 统一接口」屏蔽数据库差异：MySQL、PostgreSQL、Oracle 各自提供驱动，应用代码只面向 `java.sql` 包编程。原料在课程设计文档里描述浏览器项目「使用 SQLite 嵌入式数据库，通过 JDBC 连接，采用 PreparedStatement 防止 SQL 注入，支持事务处理」，这四件事正好覆盖了 JDBC 的核心关注点：连接、语句、安全、事务。

### 1.1 资料边界说明

任务列出的《数据库连接类型讲解》实际讲的是 SQL 中的等值连接、自然连接与一般连接，不涉及 JDBC；《带数据库的论坛系统部署方案》给出的是 Python + Flask + SQLite 的实现，也不是 Java JDBC。原料中能直接支撑 JDBC 的内容只有三处：B/S 架构中的「Web 服务器 ←JDBC→ 数据库」、课程设计文档中关于 `PreparedStatement` 与事务的一句话、以及一道「负责管理 JDBC 驱动、获取连接的是 `DriverManager`」的选择题。本文其余部分依据 JDBC 标准接口与关系型数据库的通用语义展开，不引用原料中不存在的数字或项目结论。

## 二、JDBC 的六步流程

### 2.1 六个动作

| 步骤 | 动作 | 关键 API | 说明 |
|---|---|---|---|
| 1 | 加载驱动 | `Class.forName(...)` 或 SPI 自动加载 | JDBC 4 起，驱动 jar 在类路径上可自动注册 |
| 2 | 获取连接 | `DriverManager.getConnection(url, user, password)` | 建立 TCP 连接、认证、选择数据库 |
| 3 | 创建语句 | `conn.prepareStatement(sql)` | 预编译 SQL，得到语句对象 |
| 4 | 执行 | `executeQuery()` / `executeUpdate()` | 查询返回结果集，增删改返回影响行数 |
| 5 | 处理结果 | `ResultSet.next()`、`getInt()`、`getString()` | 按行游标读取，列可用序号或列名 |
| 6 | 关闭资源 | `close()` 或 try-with-resources | 顺序与打开顺序相反 |

第 1 步在现代驱动里通常可以省略。JDBC 4 引入了基于 `META-INF/services/java.sql.Driver` 的服务发现，驱动 jar 放进类路径后，`DriverManager` 会自动找到它。显式 `Class.forName("com.mysql.cj.jdbc.Driver")` 仍然常见，原因是老代码兼容、以及在某些容器里类加载器隔离导致 SPI 失效。两类写法都不是「必须」，关键是驱动版本与数据库版本匹配。

`Class.forName` 的作用不只是「加载类」，它会执行驱动类的静态初始化块，而驱动正是在静态块里把自己注册进 `DriverManager`。这解释了为什么只写 `Class.forName` 而不 `newInstance` 也能生效，也解释了为什么类加载失败会直接抛 `ClassNotFoundException`：驱动 jar 根本没在运行时类路径上。Web 应用部署时，驱动 jar 应放在 `WEB-INF/lib` 或由容器提供，不能只放在 IDE 的编译路径里。

### 2.2 连接串的组成

MySQL 的连接串形如：

```
jdbc:mysql://localhost:3306/shop?useUnicode=true&characterEncoding=UTF-8
  &serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
```

| 部分 | 含义 | 常见错误 |
|---|---|---|
| `jdbc:mysql://` | 协议与子协议 | 写成 `mysql://`，驱动无法识别 |
| `localhost:3306` | 主机与端口 | 端口写成 Web 端口，连接被拒绝 |
| `shop` | 数据库名 | 库不存在，报 `Unknown database` |
| `characterEncoding` | 客户端字符集 | 与库表字符集不一致导致乱码 |
| `serverTimezone` | 时区 | 时区不匹配导致时间偏移 |
| `useSSL` | 是否加密 | 生产环境不应随意关闭 |

用户名与口令应来自配置或环境变量，不要硬编码在源码里；示例中的口令一律以 `***` 代替。连接串里的参数不是越多越好，`allowPublicKeyRetrieval=true` 只在特定认证插件下需要，生产环境应配合 TLS 使用。

### 2.3 最小可运行示例

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class JdbcDemo {
    private static final String URL =
            "jdbc:mysql://localhost:3306/shop?useUnicode=true&characterEncoding=UTF-8"
            + "&serverTimezone=Asia/Shanghai&useSSL=false";
    private static final String USER = "app";
    private static final String PASSWORD = "***";

    public static void main(String[] args) throws SQLException {
        String sql = "SELECT id, name, price FROM product WHERE price >= ? ORDER BY id";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setBigDecimal(1, new java.math.BigDecimal("10.00"));
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    long id = rs.getLong("id");
                    String name = rs.getString("name");
                    java.math.BigDecimal price = rs.getBigDecimal("price");
                    System.out.println(id + "\t" + name + "\t" + price);
                }
            }
        }
    }
}
```

这段代码把六步压缩进了两个 try-with-resources。`Connection`、`PreparedStatement`、`ResultSet` 都实现了 `AutoCloseable`，关闭顺序由编译器按声明的逆序生成：先关 `ResultSet`，再关 `PreparedStatement`，最后关 `Connection`。这正是手工 `finally` 嵌套想要达到的效果。

### 2.4 执行方法的选择

| 方法 | 适用语句 | 返回值 | 注意 |
|---|---|---|---|
| `executeQuery` | `SELECT` | `ResultSet` | 只能用于返回结果集的语句 |
| `executeUpdate` | `INSERT`、`UPDATE`、`DELETE`、DDL | `int` 影响行数 | DDL 返回 0，不能据此判断失败 |
| `execute` | 不确定类型 | `boolean` | `true` 表示有结果集，需再取 |
| `executeBatch` | 批量增删改 | `int[]` | 配合 `addBatch`、`clearBatch` |

`executeUpdate` 的返回值是「受影响行数」，不是「SQL 是否成功」。更新一条不存在的记录会返回 0，但语句本身执行成功；要区分「没找到」与「执行失败」，需要结合业务语义判断，或者先查询再更新。

## 三、DriverManager 与 DataSource

### 3.1 职责差异

| 维度 | `DriverManager` | `DataSource` |
|---|---|---|
| 所在包 | `java.sql` | `javax.sql` |
| 连接来源 | 每次调用新建物理连接 | 从池中借出，用完归还 |
| 配置方式 | 代码传 URL、用户名、口令 | 由容器或连接池配置，应用只取对象 |
| 是否池化 | 否 | 通常由连接池实现 |
| 关闭语义 | 真正关闭物理连接 | 归还给池，物理连接保留 |
| 适用场景 | 学习、脚本、一次性任务 | 服务器、Web 应用 |

原料中的选择题问「负责管理 JDBC 驱动、获取数据库连接的是谁」，答案是 `DriverManager`，这是就「驱动注册与直连」而言。在真实 Web 应用里，应用代码更常见的是从 `DataSource` 取连接，`DriverManager` 退到连接池内部。

### 3.2 连接建立的成本

一次 `DriverManager.getConnection` 并不只是返回一个对象，它至少包含：

1. **TCP 三次握手**：客户端与数据库之间建立连接。
2. **认证**：发送用户名、口令，数据库校验并加载权限。
3. **会话初始化**：设置字符集、时区、事务隔离级别、会话变量。
4. **数据库侧资源分配**：为连接分配内存、记录会话状态。

这四步都发生在「拿到 `Connection` 之前」。如果每个请求都直连，请求量一高，握手与认证就会成为主要开销，数据库的连接数也会迅速达到上限。连接池的作用就是把这四步做一次，之后反复复用：

```
请求 → DataSource.getConnection() → 池中有空闲则直接借出
                              → 池空且未达上限则新建
                              → 池满则等待或超时
归还 → connection.close() → 放回池中，物理连接不关闭
```

### 3.3 连接池的关键参数

| 参数 | 作用 | 设置过大的后果 | 设置过小的后果 |
|---|---|---|---|
| 最小空闲连接 | 常驻连接数 | 空闲资源浪费 | 突发流量时频繁新建 |
| 最大连接数 | 池的上限 | 数据库连接耗尽、内存上升 | 请求排队、响应变慢 |
| 获取连接超时 | 等待空闲连接的最长时间 | 故障时线程长期挂起 | 正常抖动就报错 |
| 空闲超时 | 连接空闲多久被回收 | 连接长期占用数据库 | 频繁创建销毁 |
| 最大生命周期 | 连接的最长存活时间 | 连接老化、被中间件断开 | 频繁重建 |
| 连接检测 | 借出前执行 `SELECT 1` 或 `isValid` | 每次多一次往返 | 可能借到失效连接 |

最大连接数不是越大越好。数据库能同时处理的活跃连接有限，应用侧把池调得很大，只会把压力转移给数据库，表现为锁等待、上下文切换和内存上涨。合理的做法是先测数据库在目标延迟下的吞吐，再反推每个应用实例的池大小；多个实例的总和不能超过数据库的连接上限。

### 3.4 连接池与线程池的区别

两者都叫「池」，但管理的资源不同：

- **线程池**管理执行任务的线程，解决「线程创建销毁昂贵」。
- **连接池**管理数据库连接，解决「建连认证昂贵」。
- 线程池的线程在任务期间从连接池借连接，任务结束归还；如果事务跨多个 DAO 调用，连接必须在这一整段业务里保持同一个。

这也解释了为什么「在 DAO 里各自 `getConnection`」会破坏事务：两次调用可能借到两条不同的物理连接，`commit` 只对其中一条生效。事务的连接必须由 Service 层统一持有并向下传递。

### 3.5 连接失效的三种来源

池里的连接不是永远可用。常见的失效来源有三类：

- **数据库主动断开空闲连接**。MySQL 的 `wait_timeout` 会关闭长时间空闲的会话，池若不知道，借出的就是一条已被对端关闭的连接。
- **中间设备回收空闲连接**。NAT、防火墙、负载均衡通常有自己的空闲超时，且不通知两端，表现为「读的时候才发现连接已断」。
- **数据库故障切换**。主库切换后，旧连接指向的会话消失，池必须能识别并重建。

对应的治理手段是「最大生命周期 + 借出检测 + 归还检测」。最大生命周期保证连接不会活过中间设备的回收时间；借出检测用 `isValid(timeout)` 或 `SELECT 1` 确认连接可用；归还检测在放回池时排除已损坏的连接。检测频率要权衡：每次借出都检测会增加一次往返，完全不检测则可能把坏连接交给业务。

### 3.6 多数据源与读写分离

一个应用可能同时访问多个库：业务库、日志库、只读库。每个库对应一个 `DataSource`，DAO 必须明确自己使用哪一个，不能共用一个全局连接。跨库操作如果要求原子性，需要分布式事务（两阶段提交或补偿事务），普通 JDBC 事务只能保证单连接内的原子性。

读写分离的常见做法是「写走主库、读走从库」，但主从复制有延迟：刚写入的数据立刻从从库读，可能读不到。这类问题不能靠「加重试」掩盖，业务上要么强制读主库（如写后短时间内），要么接受最终一致并在界面提示。连接池层面，读写各自一个池，池大小要按各自负载配置，不能简单复制。

## 四、Statement 与 PreparedStatement

### 4.1 拼接 SQL 的注入路径

`Statement` 直接执行完整 SQL 字符串，参数只能拼进去：

```java
String sql = "SELECT id FROM users WHERE username = '" + username
           + "' AND password = '" + password + "'";
Statement st = conn.createStatement();
ResultSet rs = st.executeQuery(sql);
```

若 `username` 传入 `' OR '1'='1' -- `，拼接结果是：

```sql
SELECT id FROM users WHERE username = '' OR '1'='1' -- ' AND password = ''
```

`--` 之后被视为注释，口令条件被抹掉，`'1'='1'` 恒真，查询返回全部用户。攻击者不需要知道任何口令，就能绕过登录。这不是「输入了特殊字符」的小问题，而是**数据被当成了 SQL 结构**。

### 4.2 占位符如何阻断注入

`PreparedStatement` 先用 `?` 占位，再绑定参数：

```java
String sql = "SELECT id, username FROM users WHERE username = ? AND password_hash = ?";
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.setString(1, username);
    ps.setString(2, passwordHash);
    try (ResultSet rs = ps.executeQuery()) {
        if (rs.next()) {
            long id = rs.getLong("id");
        }
    }
}
```

驱动把 SQL 模板发给数据库做语法分析与预编译，参数通过独立的协议消息传输。参数值无论包含引号、注释符还是分号，都只被当作「值」，不会改变 SQL 的结构。这是预编译带来的安全收益，与「预编译更快」是两个独立的优点。

### 4.3 预编译的性能收益

预编译的收益来自「一次解析、多次执行」：

- 数据库只需对 SQL 模板做一次语法分析、权限检查、执行计划生成。
- 批量插入时，同一模板反复绑定不同参数，节省解析开销。
- 某些数据库会缓存执行计划，参数变化不影响计划复用。

但预编译不是无条件更快。短连接、一次性 SQL、执行计划本身很便宜时，预编译的额外往返可能抵消收益。连接池与语句缓存（如 `cachePrepStmts`）配合时，收益才稳定。

### 4.4 占位符管不到的地方

`?` 只能替换**值**，不能替换**标识符**。下面两类写法仍然需要拼接：

```java
String sql = "SELECT * FROM " + tableName + " ORDER BY " + sortColumn;
```

如果 `tableName`、`sortColumn` 来自用户输入，注入风险依旧存在。正确做法是白名单映射：

```java
private static final Map<String, String> SORTABLE = Map.of(
        "price", "price",
        "created", "created_at");

String column = SORTABLE.getOrDefault(userInput, "id");
String sql = "SELECT * FROM product ORDER BY " + column;
```

白名单把「用户输入」变成「有限集合中的键」，拼接的最终值不再受输入控制。`LIKE` 的模糊匹配也有类似问题：`%` 与 `_` 是通配符，用户输入需要转义，否则查询语义会被改变；但转义只影响匹配范围，不是注入漏洞。

### 4.5 批量操作

逐条 `executeUpdate` 会产生多次往返。批量插入应使用 `addBatch` 与 `executeBatch`：

```java
String sql = "INSERT INTO order_item(order_id, product_id, quantity, unit_price) "
           + "VALUES (?, ?, ?, ?)";
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    for (OrderItem item : items) {
        ps.setLong(1, item.getOrderId());
        ps.setLong(2, item.getProductId());
        ps.setInt(3, item.getQuantity());
        ps.setBigDecimal(4, item.getUnitPrice());
        ps.addBatch();
    }
    int[] counts = ps.executeBatch();
}
```

批量执行要配合事务：默认自动提交时，每条语句各自提交，失败后前面的数据已经落库，无法整体回滚。批量大小也要控制，一次提交过多会占用大量内存与锁。

### 4.6 SQL 日志与审计

排查问题时，能看到「真实执行的 SQL 与参数」比看代码更快。JDBC 本身不打印 SQL，需要驱动或代理层支持。记录日志时有三个注意点：

- **参数要脱敏**。口令、手机号、身份证号不能原样进日志，日志系统往往是权限最宽的存储。
- **批量语句不要逐条打印**。一次插入上万条会把日志打爆，应记录条数与耗时。
- **慢 SQL 单独统计**。按执行时间阈值筛选，比在全部日志里搜索更有效。

审计与调试的诉求不同：调试关心「这条 SQL 为什么慢」，审计关心「谁在什么时间改了哪条数据」。后者通常需要业务层的操作日志，而不是 JDBC 层的 SQL 日志。

## 五、事务边界与回滚

### 5.1 事务的四个特性

| 特性 | 含义 | 破坏后的表现 |
|---|---|---|
| 原子性 | 一组操作要么全成功，要么全失败 | 扣了库存没生成订单 |
| 一致性 | 事务前后满足约束 | 余额为负、外键悬空 |
| 隔离性 | 并发事务互不干扰 | 脏读、不可重复读、幻读 |
| 持久性 | 提交后即使崩溃也不丢 | 提交成功但数据消失 |

JDBC 默认 `autoCommit = true`，每条语句自动提交。要使用事务，必须显式关闭自动提交：

```java
Connection conn = dataSource.getConnection();
try {
    conn.setAutoCommit(false);
    orderDao.insert(conn, order);
    itemDao.insertBatch(conn, items);
    stockDao.decrease(conn, productId, quantity);
    conn.commit();
} catch (SQLException e) {
    conn.rollback();
    throw e;
} finally {
    conn.setAutoCommit(true);   // 归还池前恢复默认状态
    conn.close();               // 连接池环境下是归还
}
```

这段代码有四个关键点：

1. **同一个 `Connection`**：所有 DAO 方法都接收 `conn` 参数，不能各自去池里取。
2. **`commit` 与 `rollback` 成对**：捕获异常后必须回滚，否则未提交的变更会随连接归还而处于不确定状态。
3. **恢复 `autoCommit`**：连接池会复用连接，若把 `autoCommit=false` 的状态带回池中，下一个使用者会莫名其妙地「不提交」。
4. **异常要向上抛**：回滚后不能吞掉异常，否则上层会以为事务成功。

### 5.2 保存点

一个事务内部可以设置保存点，实现部分回滚：

```java
Savepoint sp = conn.setSavepoint("after_order");
try {
    itemDao.insertBatch(conn, items);
} catch (SQLException e) {
    conn.rollback(sp);          // 只回滚订单项，订单头保留
}
```

保存点适合「主记录必须成功、附属记录允许失败」的场景，但会让事务语义变复杂。多数业务用「全部成功或全部失败」更清晰。

### 5.3 隔离级别与并发异常

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 说明 |
|---|---|---|---|---|
| `READ UNCOMMITTED` | 可能 | 可能 | 可能 | 几乎不用于生产 |
| `READ COMMITTED` | 不可能 | 可能 | 可能 | 许多数据库的默认级别 |
| `REPEATABLE READ` | 不可能 | 不可能 | 可能（取决于实现） | MySQL InnoDB 默认 |
| `SERIALIZABLE` | 不可能 | 不可能 | 不可能 | 串行化，并发度最低 |

隔离级别越高，一致性越强，并发度越低。设置方式：

```java
conn.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
```

需要注意的是，「幻读是否可能」依赖数据库实现。InnoDB 在 `REPEATABLE READ` 下用间隙锁在很大程度上避免了幻读，但不同版本与不同查询方式仍有差异；不能把标准表格当成所有数据库的精确行为。

### 5.4 事务超时与死锁

长事务会持有锁、占用连接、阻塞其他请求。应设置事务超时：

```java
conn.setNetworkTimeout(executor, 5000);
```

死锁是数据库检测到循环等待后主动牺牲一个事务，通常抛出与死锁相关的 `SQLException`。应用侧的正确反应是**回滚并有限重试**，而不是无限重试；重试次数与退避时间要有上限，否则会把数据库拖入更严重的拥塞。

### 5.5 嵌套调用与事务传播

Service 方法互相调用时，事务边界容易失控。上层框架通常用「传播行为」描述「进入方法时如何对待已有事务」：

| 传播行为 | 有事务时 | 无事务时 | 典型用途 |
|---|---|---|---|
| `REQUIRED` | 加入 | 新建 | 默认，绝大多数业务 |
| `REQUIRES_NEW` | 挂起原事务，新建 | 新建 | 独立记账、日志，不能随主事务回滚 |
| `NESTED` | 建保存点 | 新建 | 子步骤失败只回滚子步骤 |
| `SUPPORTS` | 加入 | 不用事务 | 只读查询 |
| `NOT_SUPPORTED` | 挂起 | 不用事务 | 长耗时、不需要一致性的操作 |
| `MANDATORY` | 加入 | 抛异常 | 强制要求调用方已开事务 |
| `NEVER` | 抛异常 | 不用事务 | 明确禁止事务 |

手写 JDBC 时没有传播机制，只有「传不传同一个 `Connection`」。如果 Service A 开了事务，调用 Service B 时 B 又去池里取新连接，B 的操作就不在 A 的事务里。这类 bug 在测试中很难发现，因为单步都成功，只有中途抛异常时才会暴露「部分提交」。因此事务边界应尽量只在一层（通常是 Service 的入口方法）控制，内部方法通过参数接收连接，而不是各自开事务。

## 六、DAO、Service、Controller 分层

### 6.1 各层职责

| 层 | 职责 | 不应该做的事 |
|---|---|---|
| Controller | 接收请求、参数校验、调用 Service、返回响应 | 写 SQL、控制事务 |
| Service | 业务规则、事务边界、组合多个 DAO | 直接拼 HTML、依赖 Servlet API |
| DAO | 单表或单聚合的 CRUD、SQL 与结果集映射 | 决定事务提交、包含业务判断 |
| Entity | 表结构的对象映射 | 携带请求上下文 |
| DTO | 层间传输、接口出入参 | 直接暴露数据库字段 |

原料在课程设计文档里把这种分层的目的说得很直接：「改界面不用动保存逻辑，改保存不用动数据库」。分层不是为了多写几个类，而是把变化限制在局部：换数据库只改 DAO，改业务流程只改 Service，改页面只改 Controller 与模板。

### 6.2 一个 DAO 的形态

```java
public interface OrderDao {
    long insert(Connection conn, Order order) throws SQLException;
    Order findById(Connection conn, long id) throws SQLException;
    List<Order> findByUser(Connection conn, long userId, int offset, int limit) throws SQLException;
    int updateStatus(Connection conn, long id, String from, String to) throws SQLException;
}
```

接口的每个方法都接收 `Connection`，这是把事务控制权交给 Service 的显式信号。实现类只做三件事：写 SQL、绑定参数、映射结果：

```java
public class OrderDaoJdbc implements OrderDao {
    @Override
    public long insert(Connection conn, Order order) throws SQLException {
        String sql = "INSERT INTO orders(order_no, user_id, status, total_amount, created_at) "
                   + "VALUES (?, ?, ?, ?, NOW())";
        try (PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1, order.getOrderNo());
            ps.setLong(2, order.getUserId());
            ps.setString(3, order.getStatus());
            ps.setBigDecimal(4, order.getTotalAmount());
            ps.executeUpdate();
            try (ResultSet keys = ps.getGeneratedKeys()) {
                if (keys.next()) {
                    return keys.getLong(1);
                }
                throw new SQLException("未返回主键");
            }
        }
    }
}
```

`RETURN_GENERATED_KEYS` 用于取回自增主键。它依赖驱动与数据库支持，不是所有数据库都返回同一列；跨库时应显式指定主键生成策略，而不是假设自增。

### 6.3 Service 的事务模板

```java
public class OrderService {
    private final OrderDao orderDao;
    private final OrderItemDao itemDao;
    private final DataSource dataSource;

    public long placeOrder(Order order, List<OrderItem> items) {
        try (Connection conn = dataSource.getConnection()) {
            conn.setAutoCommit(false);
            try {
                long orderId = orderDao.insert(conn, order);
                for (OrderItem item : items) {
                    item.setOrderId(orderId);
                }
                itemDao.insertBatch(conn, items);
                conn.commit();
                return orderId;
            } catch (SQLException e) {
                conn.rollback();
                throw new RuntimeException("下单失败", e);
            } finally {
                conn.setAutoCommit(true);
            }
        } catch (SQLException e) {
            throw new RuntimeException("获取连接失败", e);
        }
    }
}
```

这段模板把「连接获取」「事务提交/回滚」「状态恢复」集中在一个方法里。DAO 不感知事务，Controller 不感知连接，职责边界清晰。实际项目中可以用 Spring 的 `@Transactional` 替代手工模板，但底层语义完全相同：同一个连接、同一段边界、异常回滚。

### 6.4 异常转换

`SQLException` 是受检异常，直接向上抛会污染接口。常见做法是转换为业务异常：

```java
catch (SQLException e) {
    if ("23000".equals(e.getSQLState())) {   // 完整性约束
        throw new DuplicateOrderException(order.getOrderNo(), e);
    }
    throw new DataAccessException("数据库访问失败", e);
}
```

`SQLState` 是五位字符串，前两位表示错误类别，`23` 开头是完整性约束冲突。依赖 `SQLState` 比依赖具体错误码更可移植，但不同数据库的具体值仍有差异，关键分支应写测试覆盖。

### 6.5 依赖方向与包结构

分层是否成立，看依赖方向是否单向。推荐的结构是：

```
controller/
  OrderController.java      // 只依赖 service
service/
  OrderService.java         // 依赖 dao 接口、entity、dto
dao/
  OrderDao.java             // 接口
  JdbcOrderDao.java         // 实现，依赖 entity
entity/
  Order.java
  OrderItem.java
dto/
  PlaceOrderRequest.java
  OrderSummary.java
config/
  DataSourceFactory.java
```

依赖只能自上而下：Controller 认识 Service，Service 认识 DAO 接口，DAO 实现认识 Entity，Entity 不认识任何上层。这样替换 DAO 实现（JDBC 换 MyBatis）时，Service 不需要改；替换 Controller（Servlet 换 Spring MVC）时，Service 也不需要改。

DTO 与 Entity 的分离常被省略，直到出现两个问题：一是接口返回 Entity 时把数据库字段（如内部状态、逻辑删除标记）暴露给前端；二是前端需要的字段是多个表的组合，Entity 装不下。DTO 的作用是定义「这一层需要什么」，而不是「表里有什么」。

### 6.6 一次请求的完整调用链

以「新增商品」为例，把各层串起来：

1. **Controller** 从请求中取名称、价格、库存，做格式校验（非空、价格为正、库存为整数），把参数装进 DTO。
2. **Service** 校验业务规则（名称是否重复、分类是否存在），开启事务，调用 DAO。
3. **DAO** 执行 `INSERT`，绑定参数，取回自增主键，返回给 Service。
4. **Service** 提交事务，把主键与结果封装成 DTO 返回。
5. **Controller** 把 DTO 转成 JSON 或页面，写回响应。
6. **连接** 在 Service 方法结束时归还池；任何一步抛异常，事务回滚，异常转换为对外的错误码。

这条链路里，每一层只知道自己下一层：Controller 不知道 SQL，DAO 不知道 HTTP，Service 不知道页面。出现问题时也能快速定位：参数错在 Controller，规则错在 Service，SQL 错在 DAO，连接错在池配置。

## 七、资源关闭与 try-with-resources

### 7.1 关闭顺序

资源打开的逆序关闭：`ResultSet` → `Statement` → `Connection`。原因很简单：结果集依赖语句，语句依赖连接，先关上层再关下层可以避免「语句已关闭但结果集还在读」的异常。

### 7.2 三种写法

```java
// 写法一：try-with-resources，推荐
try (Connection conn = ds.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql);
     ResultSet rs = ps.executeQuery()) {
    while (rs.next()) { /* ... */ }
}

// 写法二：finally 逐层关闭，冗长但兼容老代码
Connection conn = null;
PreparedStatement ps = null;
ResultSet rs = null;
try {
    conn = ds.getConnection();
    ps = conn.prepareStatement(sql);
    rs = ps.executeQuery();
    while (rs.next()) { /* ... */ }
} finally {
    closeQuietly(rs);
    closeQuietly(ps);
    closeQuietly(conn);
}
```

写法一的关闭由编译器生成，即使 `executeQuery` 抛异常也会关闭已打开的资源。写法二需要自己处理 `null` 与关闭异常，容易漏掉某一层。`closeQuietly` 的作用是吞掉关闭时的异常，避免它覆盖业务异常，但吞掉后至少要记录日志。

### 7.3 连接池环境下的「关闭」

在连接池中，`Connection.close()` 不是关闭物理连接，而是把包装对象归还给池。因此：

- 忘记 `close` 会导致连接泄漏，池耗尽后所有请求在 `getConnection` 处超时。
- 关闭后再使用会抛 `SQLException`，即使物理连接仍然存活。
- 归还前要恢复 `autoCommit`、隔离级别、只读标志等会话状态，否则会污染下一个使用者。

连接池通常提供泄漏检测：借出超过阈值未归还时打印堆栈。它不是万能的，但能把「忘记关闭」从偶发故障变成可定位的日志。

### 7.4 结果集映射与类型处理

`ResultSet` 是一个指向当前行的游标，初始位置在第一行之前，每调用一次 `next()` 前进一行并返回是否还有数据。读取列有两种方式：列序号从 1 开始，列名不区分大小写（取决于驱动）。列序号略快，列名更可读；重构时列名更安全，因为增删列不会让序号整体错位。

| SQL 类型 | 推荐读取方法 | 注意事项 |
|---|---|---|
| `INT` | `getInt` | `NULL` 返回 0，需 `wasNull` 判断 |
| `BIGINT` | `getLong` | 主键超过 `int` 范围时必须用 `long` |
| `DECIMAL` | `getBigDecimal` | 不要用 `getDouble`，会丢精度 |
| `VARCHAR` | `getString` | 注意字符集与 `NULL` |
| `DATE` / `TIMESTAMP` | `getDate` / `getTimestamp` | 时区转换依赖连接配置 |
| `BLOB` | `getBinaryStream` | 大对象不要一次性读入内存 |

`getObject` 可以按列类型返回对应包装类，适合泛化映射；但它的返回类型依赖驱动，跨库时行为不完全一致。手写映射时，最容易被忽略的是 `NULL`：`getInt` 对 `NULL` 返回 0，与真实的 0 无法区分，必须配合 `wasNull()`：

```java
int age = rs.getInt("age");
Integer ageOrNull = rs.wasNull() ? null : age;
```

金额字段必须用 `BigDecimal`。`getDouble` 会把数据库的定点数转成二进制浮点，`0.1` 这类值无法精确表示，累加后会出现分位误差。这一点与订单金额的计算是同一个问题，后文订单系统会展开。

### 7.5 从 JDBC 到 ORM

JDBC 的优点是透明：SQL 是什么、参数怎么绑、结果怎么映射，全部可见。缺点是样板代码多：每个实体都要写一套增删改查、结果集映射、参数绑定。ORM（如 MyBatis、Hibernate、JPA）把这些重复劳动封装起来，但底层仍然走 JDBC：

- **MyBatis** 保留手写 SQL，只自动做参数绑定与结果映射，适合 SQL 复杂的项目。
- **Hibernate/JPA** 以对象模型为中心，自动生成 SQL，适合领域模型稳定的项目。
- 两者的连接、事务、连接池仍然由 JDBC 与 `DataSource` 提供。

因此学习 JDBC 不是为了从此手写所有 SQL，而是为了在 ORM 出问题时能看懂它生成的 SQL、能判断事务边界在哪、能定位连接泄漏。原料在课程设计里选择「JDBC + SQLite」而不是 ORM，正是因为项目规模小、SQL 简单，直接控制更省心。

## 八、易错点

1. **把 `executeUpdate` 返回 0 当成失败**。更新不存在的行也返回 0，语句本身是成功的。
2. **在 DAO 里各自取连接**。事务跨多个 DAO 时，必须共用同一个 `Connection`，否则 `commit` 只覆盖其中一条。
3. **忘记回滚**。捕获异常后只打印不 `rollback`，连接归还时事务状态不确定，可能被池回滚，也可能残留锁。
4. **把 `autoCommit=false` 带回池**。下一个借到该连接的业务会「执行成功但不提交」。
5. **用 `Statement` 拼接用户输入**。引号、注释符、分号都会改变 SQL 结构，注入无法靠「过滤关键字」根治。
6. **以为 `?` 能替换表名或列名**。占位符只绑定值，标识符必须白名单。
7. **`LIKE` 不转义通配符**。用户输入的 `%` 会匹配任意内容，查询结果与预期不符。
8. **结果集列名大小写不一致**。不同数据库对别名大小写处理不同，用列序号或显式别名更稳。
9. **`getInt` 遇到 `NULL` 返回 0**。需要先用 `rs.wasNull()` 判断，或使用 `getObject`。
10. **批量操作没有事务**。默认自动提交下，批量中途失败会留下前半批数据。
11. **连接串硬编码口令**。源码、日志、版本库都会泄露，应使用配置中心或环境变量。
12. **长事务不设超时**。锁持有时间过长会拖垮并发，事务应尽量短。

## 九、小结

JDBC 的知识点可以收束为一张对照表：

| 问题 | 答案 |
|---|---|
| 连接怎么来 | `DriverManager` 直连，或 `DataSource` 从池借 |
| 为什么用池 | 建连要握手、认证、初始化会话，复用省掉这些成本 |
| SQL 怎么执行 | `PreparedStatement` 预编译，`executeQuery` / `executeUpdate` |
| 注入怎么防 | 值用 `?` 绑定，标识符用白名单 |
| 事务怎么开 | `setAutoCommit(false)`，同一连接，`commit` / `rollback` |
| 边界放哪里 | Service 层，DAO 只读写下传连接 |
| 资源怎么关 | try-with-resources，逆序关闭，池环境是归还 |
| 异常怎么处理 | 回滚后向上抛，按 `SQLState` 转业务异常 |

把这八行落实到代码，就是一个可维护的 JDBC 数据访问层；剩下的是参数调优与数据库特性适配，而不是另一套理论。

### 9.1 一条可执行的练习路径

先脱离 Web 容器，在 `main` 方法里跑通「建表 → 插入 → 查询 → 更新 → 删除」，确认驱动、连接串、字符集都正确。然后引入 `PreparedStatement`，用一段故意构造的注入输入对比 `Statement` 与占位符的结果差异，理解「数据与结构分离」不是口号。接着把连接获取抽到 `DataSource`，观察池的借出与归还；再用两个 DAO 方法模拟转账，故意在中间抛异常，验证 `rollback` 确实把两边都恢复。最后把这段代码搬进 Servlet 或 Controller，用浏览器触发，观察一次请求从 HTTP 到 SQL 的完整路径。

每一步都只引入一个新变量：先证明「能连」，再证明「能防注入」，再证明「事务能回滚」，最后才谈分层。顺序反过来，一旦出错就很难判断是驱动、SQL、事务还是分层的问题。
