---
title: 数据库与 MySQL · 复习与实操笔记
subject: 数据库/MySQL
category: 课程笔记
source: 012_MySQL安装指导与作业说明.md
summary: 以学生选课数据库的四个实验为主线，梳理 MySQL 8.0 的安装配置与排错、Navicat 图形化操作、建表与约束、触发器、索引与视图、交互式 SQL 查询及用户权限管理，并归纳常见报错的成因与解决办法。
---

# 数据库与 MySQL · 复习与实操笔记

## 一、概述

本笔记以"学生选课数据库"的四个实验为主线，记录从环境搭建到权限控制的完整实操路径：

| 实验 | 主题 | 核心能力 |
|---|---|---|
| 实验一 | 认识 DBMS 系统 | 安装配置、连接服务、建库建表、增删改查 |
| 实验二 | 交互式 SQL 语句 | DDL、DML、DQL、索引、视图 |
| 实验三 | 数据完整性 | 主键、外键、唯一、非空、CHECK、默认值、触发器 |
| 实验四 | 用户鉴别与数据控制 | 创建用户、GRANT / REVOKE、权限验证 |

贯穿四个实验的统一对象是三张表：`Student`（学生）、`Course`（课程）、`SC`（选课）。数据库系统采用本地 MySQL 8.0 服务端，客户端使用 Navicat（或官方 MySQL Workbench），二者关系为：**服务端负责存储与执行，客户端只提供交互界面**，图形化工具与命令行执行的是同一套 SQL。

## 二、核心知识点

### 2.1 MySQL 8.0 安装与配置

**安装包选择**：官网 `dev.mysql.com/downloads/installer/` 提供在线安装器（体积小、需联网下载组件）与离线完整包（体积约 556 MB、一次到位）。网络不稳定时应选离线完整包。

**安装类型**：

| 类型 | 含义 | 适用 |
|---|---|---|
| Server only | 仅服务端 | 不需要本地客户端工具 |
| Client only | 仅客户端 | 连接远程服务器 |
| Full | 全部组件 | 推荐，作业够用 |
| Custom | 自定义 | 有经验者精简安装 |
| Developer Default | 开发者默认全量 | 官方推荐给新手 |

Full 安装完成后程序文件约占 1.5 GB；若磁盘紧张可选 Custom，只勾选 `MySQL Server 8.0` 与 `MySQL Workbench`，约 600–800 MB。

**配置向导关键步骤**：

1. **Type and Networking**：`Config Type` 选 `Development Computer`；必须勾选 `TCP/IP`；端口默认 `3306`（若端口号旁出现感叹号，说明端口被占用，可改为 3307/3308 并牢记）；勾选 `Open Windows Firewall ports for network access`；`Named Pipe`、`Shared Memory` 不勾；`X Protocol Port`（33060）保持默认。
2. **Authentication Method**：`Use Strong Password Encryption`（`caching_sha2_password`）安全性高，但旧版客户端可能不兼容；`Use Legacy Authentication Method`（`mysql_native_password`）兼容性最好。本地做作业建议选后者。
3. **Accounts and Roles**：设置 `root` 密码，必须牢记；无需新建其他用户。
4. **Windows Service**：服务名 `MySQL80`，勾选 `Start the MySQL Server at System Startup`，运行账户选 `Standard System Account`。
5. **Server File Permissions**：保持默认第一项（由安装器自动授予数据目录权限）。
6. **Apply Configuration**：全部步骤出现绿色对勾即成功。

**安装路径的硬性约束**：安装目录与数据目录**必须为纯英文、无空格、无特殊字符**，且**两者不能相同**，数据目录必须是空文件夹。中文路径会导致初始化失败，日志中表现为乱码目录名，例如：

```
mysqld: Can't create directory 'D:\鏁版嵁搴撳疄楠孿MySQL\MySQL Server 8.0\Data\'
(OS errno 2 - No such file or directory)
The designated data directory ... is unusable. ... Aborting
```

`鏁版嵁搴撳疄楠孿` 即"数据库实验"的 GBK/UTF-8 错码，属典型中文路径问题。

**安装失败的清理与手动初始化**：卸载全部 MySQL 组件后，还需删除 `C:\ProgramData\MySQL`、`C:\Users\<用户名>\AppData\Roaming\MySQL` 以及原安装目录，必要时删除注册表项 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\MySQL80`。若仍失败，可手动初始化：

```cmd
cd D:\MySQL\MySQL Server 8.0\bin
mysqld --initialize --datadir=D:\MySQL\Data --console
mysqld --install MySQL80
net start MySQL80
```

`--initialize` 会在控制台输出临时 root 密码，登录后须立即修改：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';
FLUSH PRIVILEGES;
```

**安装后的验证**：开始菜单打开 `MySQL 8.0 Command Line Client`，输入 root 密码，出现 `mysql>` 提示符即成功；或在服务管理器（`services.msc`）中确认 `MySQL80` 处于"正在运行"。

### 2.2 Navicat 连接与常用操作

新建连接需填写：连接名（任意）、主机 `localhost`、端口（安装时设定，如 3306 或 3310）、用户名 `root`、密码。点击"测试连接"成功后方可保存。

常用操作路径：

- 新建数据库：右键连接 → 新建数据库 → 字符集 `utf8mb4`、排序规则 `utf8mb4_general_ci`（避免中文乱码）。
- 执行 SQL：顶部"新建查询" → 粘贴 → 运行（`Ctrl+R`）。可选中部分语句单独执行。
- 查看数据：右键表 → 打开表。
- 查看索引：右键表 → 设计表 → "索引"标签。
- 查看视图：左侧"视图"文件夹展开，双击查看数据，右键"设计视图"查看定义。

### 2.3 表结构与约束

三张表的结构（实验二、三使用）：

```sql
CREATE TABLE Student (
    Sno CHAR(8) PRIMARY KEY,
    Sname CHAR(8) NOT NULL,
    Ssex CHAR(2) CHECK (Ssex IN ('男','女')),
    Sage SMALLINT,
    Sdept CHAR(20),
    Sclass CHAR(4) NOT NULL,
    Stotal SMALLINT DEFAULT 0
);

CREATE TABLE Course (
    Cno CHAR(4) PRIMARY KEY,
    Cname CHAR(40) NOT NULL UNIQUE,
    Cpno CHAR(4),
    Ccredit SMALLINT,
    FOREIGN KEY (Cpno) REFERENCES Course(Cno)
);

CREATE TABLE SC (
    Sno CHAR(8),
    Cno CHAR(4),
    Grade SMALLINT CHECK (Grade BETWEEN 0 AND 100),
    PRIMARY KEY (Sno, Cno),
    FOREIGN KEY (Sno) REFERENCES Student(Sno),
    FOREIGN KEY (Cno) REFERENCES Course(Cno)
);
```

五类约束及其作用：

| 约束 | 关键字 | 保证的完整性 | 违反时的表现 |
|---|---|---|---|
| 主键 | `PRIMARY KEY` | 实体完整性（唯一且非空） | 重复或空值插入失败 |
| 外键 | `FOREIGN KEY` | 参照完整性（子表值须存在于主表） | 插入/修改不存在的引用失败；删除被引用行失败 |
| 唯一 | `UNIQUE` | 用户自定义（列值不重复，允许一个 NULL） | 重复值插入失败 |
| 非空 | `NOT NULL` | 用户自定义（禁止空值） | 插入 NULL 或省略该列失败 |
| 检查 | `CHECK` | 用户自定义（值域限制） | 超出范围失败（MySQL 8.0 起生效，5.x 仅解析不校验） |
| 默认值 | `DEFAULT` | 用户自定义（缺省填充） | 不违反，仅自动补值 |

`Course.Cpno` 是**自引用外键**（先修课引用本表 `Cno`），这是插入顺序问题的根源：若先插入"数据库系统原理（先修课 5）"而课程 5 尚未存在，外键将拒绝插入。

### 2.4 触发器

触发器用于在指定表的指定事件发生时自动执行一段逻辑，实现**比约束更复杂的完整性控制**。

**触发器一：选课自动累加总学分**

```sql
DELIMITER //
CREATE TRIGGER tri_insert_sc
AFTER INSERT ON SC
FOR EACH ROW
BEGIN
    DECLARE cred SMALLINT;
    SELECT Ccredit INTO cred FROM Course WHERE Cno = NEW.Cno;
    UPDATE Student SET Stotal = Stotal + cred WHERE Sno = NEW.Sno;
END //
DELIMITER ;
```

`NEW` 代表插入后的新行，`OLD` 代表删除或更新前的旧行。`DELIMITER //` 用于临时改变语句结束符，避免触发器体内的分号提前终止语句；结束后必须改回 `DELIMITER ;`。

**触发器二：操作日志登记**

```sql
CREATE TABLE LOG_TABLE (
    username CHAR(20),
    date DATETIME,
    Sno CHAR(8),
    Cno CHAR(4)
);

DELIMITER //
CREATE TRIGGER tri_log_sc_insert
AFTER INSERT ON SC
FOR EACH ROW
BEGIN
    INSERT INTO LOG_TABLE VALUES (CURRENT_USER(), NOW(), NEW.Sno, NEW.Cno);
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER tri_log_sc_update
AFTER UPDATE ON SC
FOR EACH ROW
BEGIN
    INSERT INTO LOG_TABLE VALUES (CURRENT_USER(), NOW(), NEW.Sno, NEW.Cno);
END //
DELIMITER ;
```

> MySQL 规定**一个触发器只能绑定一个事件**（INSERT / UPDATE / DELETE 三选一），无法像 SQL Server 那样写 `FOR INSERT, UPDATE`。要实现"插入与更新都记日志"，必须拆成两个触发器。

### 2.5 索引与视图

**索引**用于加速查询，代价是占用空间并降低写入速度。

```sql
CREATE INDEX iCname ON Course(Cname);
CREATE UNIQUE INDEX iSname ON Student(Sname);
CREATE INDEX iSnoCno ON SC(Sno, Cno DESC);
CREATE UNIQUE INDEX iCno ON Course(Cno);
```

MySQL 不支持 `CREATE CLUSTERED INDEX`（聚集索引由主键自动决定），只能创建普通索引与唯一索引。

**视图**是由查询定义的虚拟表，不存储数据，用于简化复杂查询与限制可见列。

```sql
CREATE VIEW IS_Student AS
SELECT Sno, Sname, Sage FROM Student WHERE Sdept = 'IS';

CREATE VIEW Student_VIEW(学号,姓名,性别,年龄,系,班级) AS
SELECT Sno, Sname, Ssex, Sage, Sdept, Sclass FROM Student;

CREATE VIEW S_G(学号, 平均成绩) AS
SELECT Sno, AVG(Grade) FROM SC GROUP BY Sno;

CREATE VIEW XK_VIEW AS
SELECT Student.*, Course.*, Grade
FROM Student
JOIN SC ON Student.Sno = SC.Sno
JOIN Course ON SC.Cno = Course.Cno;
```

删除索引与视图时，`DROP INDEX` 在部分 MySQL 版本不支持 `IF EXISTS`，须直接 `DROP INDEX 索引名 ON 表名`。

### 2.6 交互式 SQL 查询

**单表查询**：条件、范围、集合、模糊、空值、排序、去重。

```sql
SELECT Sname FROM Student WHERE Sdept = 'CS';
SELECT Sname, Sdept, Sage FROM Student WHERE Sage BETWEEN 20 AND 23;
SELECT Sname, Ssex FROM Student WHERE Sdept IN ('IS','MA','CS');
SELECT Sname, Sno, Ssex FROM Student WHERE Sname LIKE '刘%';
SELECT Sno, Cno FROM SC WHERE Grade IS NULL;
SELECT * FROM Student ORDER BY Sdept, Sage DESC;
SELECT DISTINCT Sno FROM SC;
```

结果集可使用汉字列名（别名）：`SELECT Sno 学号, Sname 姓名, Sage 年龄 FROM Student;`

**聚集函数**（又称集合函数，二者同义）：对一组值统计并返回单个结果，包括 `COUNT`、`SUM`、`AVG`、`MAX`、`MIN`。

**分组统计**：`GROUP BY` 按列分组后对每组计算聚集函数，`HAVING` 过滤分组后的统计结果。

```sql
SELECT Cno 课程号, COUNT(*) 人数, AVG(Grade) 均分, MAX(Grade) 最高分
FROM SC GROUP BY Cno HAVING AVG(Grade) > 90;
```

> 关键规则：**WHERE 过滤原始行，不能使用聚集函数；HAVING 过滤分组结果，可以使用聚集函数**。执行顺序为 WHERE → GROUP BY → 聚集函数 → HAVING。

**连接查询**：等值连接、三表连接、左外连接、自连接。

```sql
-- 三表连接
SELECT Student.Sno, Sname, Cname, Grade
FROM Student, SC, Course
WHERE Student.Sno = SC.Sno AND SC.Cno = Course.Cno;

-- 左外连接：未选课的学生也保留
SELECT Student.Sno, Sname, Cno, Grade
FROM Student LEFT JOIN SC ON Student.Sno = SC.Sno;

-- 自连接：查询间接先修课
SELECT first.Cno, second.Cpno
FROM Course first, Course second
WHERE first.Cpno = second.Cno;
```

**嵌套查询**：`IN`、`ALL`、`EXISTS`、相关子查询。

```sql
-- 与刘晨同系的学生
SELECT Sno, Sname, Sdept FROM Student
WHERE Sdept IN (SELECT Sdept FROM Student WHERE Sname = '刘晨');

-- 成绩超过本人平均分的课程（相关子查询）
SELECT Sno, Cno FROM SC x
WHERE Grade >= (SELECT AVG(Grade) FROM SC y WHERE y.Sno = x.Sno);

-- 选修 1 号课程的学生
SELECT Sname FROM Student
WHERE EXISTS (SELECT * FROM SC WHERE Sno = Student.Sno AND Cno = '1');
```

**集合查询**：`UNION` 可用；`INTERSECT`、`EXCEPT` 在 MySQL 中不支持，须用 `IN` / `NOT IN` 或 `JOIN` 改写。

**数据修改**：

```sql
UPDATE Student SET Sage = Sage + 1;
UPDATE SC SET Grade = Grade + 5
WHERE Sno IN (SELECT Sno FROM Student WHERE Sdept = 'CS');
DELETE FROM Student WHERE Sno = '20100022';
```

### 2.7 用户与权限

MySQL 的用户由**用户名 + 主机**共同标识，`'李刚'@'localhost'` 与 `'李刚'@'%'` 是两个不同账户。

```sql
-- 创建用户
CREATE USER '王明'@'localhost' IDENTIFIED BY '123456';
CREATE USER '李刚'@'localhost' IDENTIFIED BY '123456';

-- 授权
GRANT SELECT ON data1.Student TO '王明'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON data1.Student TO '李刚'@'localhost';
GRANT SELECT ON data1.Course TO '李刚'@'localhost';

-- 追加权限
GRANT SELECT, INSERT, UPDATE, DELETE ON data1.SC TO '李刚'@'localhost';

-- 撤销权限
REVOKE SELECT, INSERT, UPDATE, DELETE ON data1.Student FROM '李刚'@'localhost';
FLUSH PRIVILEGES;

-- 查询当前登录用户
SELECT CURRENT_USER();
```

**权限验证必须在目标用户的连接中执行**。用 root 执行测试语句永远成功，无法体现权限差异；须在 Navicat 中另建以 `李刚` / `王明` 为用户的连接，再执行测试语句，观察是否出现 `1142 - ... command denied to user`。

### 2.8 与教材金仓数据库的主要差异

| 方面 | MySQL | 金仓 KingbaseES |
|---|---|---|
| 用户标识 | 用户名 + 主机（`@localhost`） | 无强制主机绑定 |
| 权限刷新 | 修改后需 `FLUSH PRIVILEGES` | 一般自动生效 |
| 聚集索引 | 不支持 `CLUSTERED INDEX` | 支持直接定义 |
| 集合运算 | 不支持 `INTERSECT` / `EXCEPT` | 支持 |
| CHECK 约束 | 8.0 生效，5.x 仅解析 | 直接生效 |
| 触发器事件 | 单触发器仅一个事件 | 支持多事件绑定 |
| 外键开关 | `SET FOREIGN_KEY_CHECKS` | 无对应语句 |

## 三、典型例题 / 关键问答

### 例 1：实验数据准备（注意插入顺序）

```sql
SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO Course VALUES
('1','数据库系统原理','5',4),
('2','高等数学',NULL,2),
('3','管理信息系统','1',4),
('4','操作系统原理','6',3),
('5','数据结构','7',4),
('6','数据处理',NULL,2),
('7','C语言',NULL,4);

INSERT INTO Student VALUES
('20100001','李勇','男',20,'CS','1001',0),
('20100002','刘晨','女',19,'CS','1001',0),
('20100021','王敏','女',18,'MA','1002',0),
('20100031','张立','男',19,'IS','1003',0),
('20100003','刘洋','女',NULL,NULL,'1001',0),
('20100010','赵斌','男',19,'IS','1005',0),
('20100022','张明明','男',19,'CS','1002',0);

INSERT INTO SC VALUES
('20100001','1',92),
('20100001','2',85),
('20100001','3',88),
('20100002','1',90),
('20100002','2',80),
('20100003','1',NULL),
('20100010','3',NULL);

SET FOREIGN_KEY_CHECKS = 1;
```

**顺序原则**：先主表（`Student`、`Course`）后子表（`SC`）。`Course` 因自引用外键，即使同为一张表也需临时关闭外键检查才能一次插入，否则报 1452。

### 例 2：报错 1062 — 主键重复

```
1062 - Duplicate entry '001' for key 'course.PRIMARY'
```

成因：向 `Course` 重复插入 `Cno='001'`，或向 `SC` 重复插入相同的 `(Sno, Cno)` 组合（联合主键）。解决：换用未使用的主键值，或先 `DELETE` 清空再插入；彻底方案是 `DROP TABLE` 重建。

> 该报错说明主键约束正常生效，是完整性的正面表现。

### 例 3：报错 1451 — 删除被引用行

```
1451 - Cannot delete or update a parent row: a foreign key constraint fails
(`data1`.`course`, CONSTRAINT `course_ibfk_1` FOREIGN KEY (`Cpno`) REFERENCES `course`(`Cno`))
```

成因：`Course` 被 `SC.Cno` 引用，且表内 `Cpno` 自引用，删除父行会破坏参照完整性。解决：先删除子表相关记录（`DELETE FROM SC WHERE Cno='6'`），再删父行；或临时 `SET FOREIGN_KEY_CHECKS = 0`，操作完毕立即恢复。

### 例 4：报错 1452 — 插入不存在的引用

```
1452 - Cannot add or update a child row: a foreign key constraint fails
```

成因：`SC` 中插入的 `Sno`/`Cno` 在主表不存在；或 `Course` 的 `Cpno` 指向尚未插入的课程。解决：按主表→子表顺序插入，或临时关闭外键检查。

### 例 5：报错 1060 / 1061 / 1091 — 对象重复或不存在

| 报错 | 含义 | 解决 |
|---|---|---|
| `1060 Duplicate column name 'Stotal'` | 字段已存在，重复 `ADD` | 去掉该 `ALTER` 语句 |
| `1061 Duplicate key name 'iCname'` | 索引已存在 | 先删除再创建 |
| `1091 Can't DROP 'iCname'; check that column/key exists` | 索引不存在却执行删除 | 确认对象是否存在，MySQL 低版本 `DROP INDEX` 不支持 `IF EXISTS` |

> MySQL 8.0 不支持 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`，该写法会报 1064 语法错误。

### 例 6：报错 1064 — 触发器多事件

```
1064 - You have an error in your SQL syntax ... near 'AFTER INSERT,UPDATE ON SC'
```

成因：沿用 SQL Server 的 `FOR INSERT, UPDATE` 写法。解决：拆成 `tri_log_sc_insert` 与 `tri_log_sc_update` 两个触发器。

### 例 7：报错 1406 — 数据超长

```
1406 - Data too long for column 'username'
```

成因：`LOG_TABLE.username CHAR(10)` 无法容纳 `CURRENT_USER()` 返回的 `root@localhost`（13 个字符）。解决：

```sql
ALTER TABLE LOG_TABLE MODIFY COLUMN username CHAR(20);
```

### 例 8：报错 1045 — 登录被拒绝

```
1045 - Access denied for user '李刚'@'localhost' (using password: YES)
```

排查顺序：① 用户是否存在——`SELECT user, host FROM mysql.user WHERE user='李刚';`；② 密码是否一致——`ALTER USER '李刚'@'localhost' IDENTIFIED BY '123456';`；③ 主机是否匹配——连接必须使用 `localhost`，与创建时的 host 完全一致；④ 执行 `FLUSH PRIVILEGES;` 刷新缓存。

### 例 9：报错 1142 — 权限不足

```
1142 - INSERT command denied to user '李刚'@'localhost' for table 'Course'
```

这是实验四期望出现的正确结果：李刚对 `Course` 仅有 `SELECT` 权限，故 `INSERT/UPDATE/DELETE` 被拒绝。若报的是外键或非空错误，说明测试语句本身有问题，应先修正语句，使报错类型唯一指向权限。

### 例 10：触发器效果验证

```sql
INSERT INTO SC VALUES('20100031','4',95);
SELECT Sno, Sname, Stotal FROM Student WHERE Sno='20100031';
SELECT * FROM LOG_TABLE;
```

预期：`20100031` 的 `Stotal` 由 0 变为课程 4 的学分 3；`LOG_TABLE` 新增一条 `root@localhost` 的记录。若插入的组合已存在，会先触发 1062 主键冲突而无法进入触发器，应改用未使用的 `(Sno, Cno)`。

### 例 11：指定查询（文档"自行完成"任务）

```sql
-- 结果集属性名使用汉字
SELECT Sno 学号, Sname 姓名, Ssex 性别, Sage 年龄, Sdept 所在系, Sclass 班级 FROM Student;

-- 信息系且年龄大于 23
SELECT Sno 学号, Sname 姓名 FROM Student WHERE Sdept = 'IS' AND Sage > 23;

-- 年龄为 17、18、20、23
SELECT Sno, Sname, Sage, Sdept FROM Student WHERE Sage IN (17, 18, 20, 23);

-- 年龄不在 21~24
SELECT Sname, Sdept, Sage FROM Student WHERE Sage NOT BETWEEN 21 AND 24;

-- 每名学生选课数、平均分、最高分
SELECT Sno 学号, COUNT(*) 选课数, AVG(Grade) 平均成绩, MAX(Grade) 最高成绩
FROM SC GROUP BY Sno;

-- 每班每门课的选课人数、均分、最高分
SELECT Sclass 班级, Cno 课程号, COUNT(*) 人数, AVG(Grade) 均分, MAX(Grade) 最高分
FROM Student JOIN SC ON Student.Sno = SC.Sno
GROUP BY Sclass, Cno;
```

### 例 12：约束验证的预期现象

| 测试语句 | 预期 | 说明 |
|---|---|---|
| 插入已存在学号 | 失败（1062） | 主键唯一 |
| 插入 `Sclass` 为 NULL 或省略 | 失败（1048） | 非空约束 |
| 插入成绩 102 | 失败（3819） | CHECK 约束 |
| 插入性别 `''` | 失败（3819） | CHECK 约束 |
| 插入不存在的学号/课程号到 `SC` | 失败（1452） | 外键约束 |
| 只填必填字段、不填 `Stotal` | 成功，`Stotal` 自动为 0 | 默认值约束 |
| 插入重复课程名 | 失败（1062） | 唯一约束 |

## 四、小结

1. **环境是第一步**：安装路径必须纯英文、无空格，安装目录与数据目录分离，数据目录须为空；中文路径是初始化失败的首要原因。安装完成后以 `mysql>` 提示符与服务状态双重验证。
2. **服务端与客户端分离**：Navicat 只是前端，真正执行 SQL 与存储数据的是 MySQL 服务；服务未启动时任何客户端都无法连接。
3. **完整性由约束与触发器共同保证**：主键与非空保证实体完整性，外键保证参照完整性，唯一、CHECK、默认值实现用户自定义完整性，触发器承担跨表、跨事件的复杂维护（如学分累加、日志登记）。
4. **插入顺序即依赖顺序**：主表在前、子表在后；自引用外键需临时关闭 `FOREIGN_KEY_CHECKS`。删除则相反，先子后父。
5. **报错即约束生效**：1062（主键/唯一）、1451（删除父行）、1452（引用不存在）、1406（超长）、1048（非空）都应被理解为完整性机制正常工作的证据，而非程序缺陷。
6. **权限验证必须换身份**：用 root 执行无法验证权限，须以目标用户建立独立连接；MySQL 用户由"用户名 + 主机"标识，授权需写明"库.表"，修改后需 `FLUSH PRIVILEGES`。
7. **WHERE 与 HAVING 的分工**：WHERE 过滤原始行、不可用聚集函数；HAVING 过滤分组结果、可用聚集函数，执行顺序为 WHERE → GROUP BY → 聚集函数 → HAVING。
