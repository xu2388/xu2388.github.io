---
title: JavaWeb · 学习笔记
subject: JavaWeb
category: 课程笔记
source: 007_javaweb自学.md
summary: 按“页面结构—样式—脚本—数据描述—通信协议—服务器”的顺序，系统整理 HTML/CSS/JavaScript 基础、XML 的 DTD 与 XSD 约束、C/S 与 B/S 架构、HTTP 请求响应报文及 Tomcat 与 Servlet 的运行流程。
---

# JavaWeb · 学习笔记

## 一、概述

JavaWeb 指以 Java 技术构建、通过浏览器访问的 Web 应用。其运行基础是 **B/S（Browser/Server，浏览器/服务器）架构**：客户端只需浏览器，业务逻辑与数据集中在服务器端，浏览器与服务器之间通过 **HTTP 协议**通信。

一个 JavaWeb 项目由三类资源构成：

| 类别 | 内容 | 职责 |
|---|---|---|
| 静态资源 | HTML、CSS、JavaScript、图片 | 页面结构与展现，内容固定 |
| 动态资源 | Servlet、JSP | 执行 Java 代码，处理业务逻辑 |
| 数据库 | MySQL 等 | 持久化存储数据 |

整体知识链条为：**HTML 搭结构 → CSS 做样式 → JavaScript 加交互 → XML 描述配置与数据 → HTTP 规定通信格式 → Tomcat 作为 Web 容器运行 Servlet/JSP**。其中 XML 的 DTD、XSD 约束与 HTTP 报文结构是笔试与面试的高频考点。

## 二、核心知识点

### 2.1 HTML 文档结构与标签分类

HTML（HyperText Markup Language，超文本标记语言）不是编程语言，没有变量与逻辑，只负责描述页面结构，文件后缀为 `.html` 或 `.htm`。

标准骨架如下：

```html
<!DOCTYPE html>          <!-- 文档声明：告诉浏览器使用 HTML5 标准，不是标签 -->
<html>                   <!-- 根标签，整份文档唯一的根节点 -->
  <head>                 <!-- 头部：配置信息，页面不直接显示 -->
    <meta charset="UTF-8">   <!-- 设置编码，防止中文乱码 -->
    <title>网页标题</title>   <!-- 浏览器标签页文字 -->
    <link rel="stylesheet" href="style.css">
  </head>
  <body>                 <!-- 主体：所有可见内容 -->
  </body>
</html>
```

标签分两类：

- **单标签（自闭合）**：`<br>`、`<hr>`、`<img>`、`<input>`、`<link>`；
- **双标签（容器）**：`<p>…</p>`、`<div>…</div>`，成对出现。

注释写法为 `<!-- 注释内容 -->`。浏览器会忽略无法识别的标签，若要在页面上显示 `<abc>` 这样的字面文本，必须使用转义字符：`&lt;` 表示 `<`，`&gt;` 表示 `>`，`&nbsp;` 表示不间断空格。

### 2.2 常用标签

**段落与文本**：`<p>` 为块级元素，独占一行并自带上下间距；`<span>` 为行内元素，不换行，用于给局部文字单独设置样式；`<br>` 强制换行；`<font face="微软雅黑" size="5" color="blue">` 为旧版文本样式标签，多个属性以空格分隔。

**表格**：

```html
<table border="1px" cellspacing="0" cellpadding="3" align="center">
  <tr>                    <!-- table row：一行 -->
    <td>单元格内容</td>    <!-- table data：一个单元格 -->
  </tr>
</table>
```

- `border`：边框粗细；`cellspacing`：单元格之间的间距；`cellpadding`：文字与单元格边框的内边距；`align`：表格整体水平对齐。
- 跨列合并用 `colspan="2"`，跨行合并用 `rowspan="2"`；合并后须删除被合并位置多余的 `<td>`。
- `<td>` 必须嵌套在 `<tr>` 内，`<tr>` 必须嵌套在 `<table>` 内。

**表单**：用于收集用户输入并提交给服务器。

```html
<form action="后端接口地址" method="post" name="loginForm">
  <input type="text" name="username">
  <input type="password" name="password">
  <input type="radio" name="gender" value="male">男
  <input type="radio" name="gender" value="female">女
  <input type="checkbox" name="hobby" value="read">阅读
  <input type="file" name="avatar">
  <input type="submit" value="提交">
  <input type="reset" value="重置">
</form>
```

`action` 指定接收数据的 URL，`method` 只有 GET 与 POST 两种。`type` 常用值包括 `text`、`password`、`radio`、`checkbox`、`file`、`submit`、`reset`。**同一组单选按钮或多选框的 `name` 必须完全相同**，否则无法实现互斥或分组提交。

**多行文本框与下拉框**（同属表单元素）：

```html
<textarea cols="25" rows="25">默认内容</textarea>

<select name="country">
  <option value="China">中国</option>
  <option value="Korea">韩国</option>
</select>
```

`cols` 与 `rows` 分别控制列数与行数；`option` 的 `value` 是提交给服务器的值，标签之间的文字是页面显示值。`<fieldset>` 用于给一组表单加边框分组，`<legend>` 为该组加标题。

**列表**：

```html
<ul type="disc"><li>条目</li></ul>   <!-- 无序：disc 实心圆、square 方块、circle 空心圆 -->
<ol type="a"><li>条目</li></ol>      <!-- 有序：可指定数字、字母、罗马数字 -->
<dl>
  <dt>红色</dt><dd>代表热情</dd>       <!-- dt 为术语，dd 为解释 -->
</dl>
```

**超链接与图片**：

```html
<a href="https://www.example.com" target="_blank">链接文字</a>
<img src="images/logo.png" width="160" height="130" border="0">
```

`target` 取值：`_self`（当前窗口，默认）、`_blank`（新标签页）、`_parent`（父窗口）、`_top`（顶层窗口）。`img` 为单标签，`src` 支持绝对路径与相对路径；只设置宽或高其中之一时按比例缩放。

### 2.3 CSS 语法与四种引入方式

CSS（Cascading Style Sheets，层叠样式表）负责颜色、字号、边框、布局等表现层设置。基本语法为“选择器 + 声明块”：

```css
div {
  border: 1px solid red;
  width: 600px;
  height: 400px;
}
```

声明块内是若干“属性: 值”键值对，以分号结尾。四种引入方式：

| 方式 | 写法 | 作用范围 | 特点 |
|---|---|---|---|
| 行内式 | `<p style="color:red;font-size:20px;">` | 单个标签 | 结构与样式完全耦合，优先级最高，仅用于临时调试 |
| 内嵌式 | `<head>` 内 `<style>…</style>` | 当前 HTML 文件 | 实现简单分离，但多页面无法复用 |
| 外链式（链入式） | `<link href="style.css" rel="stylesheet" type="text/css">` | 所有引用该文件的页面 | 结构与样式彻底分离，可复用、可缓存，企业开发标准写法 |
| 导入式 | `<style>` 内 `@import url(style.css);` | 当前文件 | 先加载完 HTML 再下载 CSS，页面会短暂无样式；JS 无法动态控制，已淘汰 |

```html
<head>
  <link href="css/style.css" rel="stylesheet" type="text/css">
</head>
```

`href` 为 CSS 文件路径；`rel="stylesheet"` 声明所引入文件为样式表，必须书写；`type="text/css"` 在 HTML5 中可省略。优先级由高到低为：**行内式 > 内嵌式 > 外链式**（同权重时后定义者覆盖先定义者）。

### 2.4 CSS 选择器

- **标签选择器**：`p { color: green; }`，批量作用于所有同名标签；
- **类选择器**：`.box { font-size: 14px; }`，HTML 中以 `class="box"` 引用，同一个类可被多个标签使用，开发中最常用；
- **id 选择器**：`#box { background: pink; }`，HTML 中以 `id="box"` 引用，**同一页面内 id 必须唯一**，多用于 JavaScript 定位元素；
- **通配符选择器**：`* { margin: 0; padding: 0; }`，选中全部标签，常用于全局样式初始化。

### 2.5 JavaScript 的组成与引入

JavaScript 由三部分组成：

1. **ECMAScript**：语法核心，包括变量、运算符、数据类型、函数、流程控制；
2. **DOM（Document Object Model，文档对象模型）**：把 HTML 解析为树形结构，供脚本操作标签；
3. **BOM（Browser Object Model，浏览器对象模型）**：以 `window` 为核心，操作浏览器窗口。

引入方式有三种：行内式（写在标签的事件属性中，如 `onclick="fn()"`）、内嵌式（`<script>…</script>`）、外链式（`<script src="app.js"></script>`）。

运算符优先级由高到低大致为：括号与成员访问 `.` `[]` `()` → 自增自减与 `!`、`new`、`typeof` → 乘除取余 → 加减 → 移位 → 关系运算 → 相等运算 → 按位与、异或、或 → 逻辑与、逻辑或 → 三元运算符 → 赋值。

### 2.6 DOM、BOM 与内置对象

DOM 将文档解析为一棵树：`document → html → head/body → 各标签`。节点之间存在父子关系，`parentNode` 返回父节点。获取元素的常用方法：

```javascript
// 通过 id 获取，返回单个元素
var el = document.getElementById("userId");

// 通过 name 获取，返回类数组，多个同名元素时需用下标取用
var first = document.getElementsByName("userName")[0];
```

BOM 的顶层对象是 `window`，其他对象均作为其属性存在，全局作用域中声明的变量也挂载在 `window` 上。常用属性：

| 属性 | 含义 |
|---|---|
| `innerWidth` / `innerHeight` | 文档显示区域（可视区）的宽高 |
| `outerWidth` / `outerHeight` | 整个浏览器窗口的宽高 |
| `document` | 当前文档对象 |
| `history` | 浏览历史，用于前进后退 |
| `location` | 地址栏信息，可用于跳转 |
| `parent` / `self` / `top` | 父窗口、当前窗口、顶层窗口 |

常用方法：`open()` / `close()` 打开或关闭窗口；`alert()` / `confirm()` / `prompt()` 分别弹出警告框、确认框、输入框；`setTimeout()` / `clearTimeout()` 设置或清除定时器。

页面加载事件有两个，区别必须掌握：

```javascript
// 页面全部资源（图片、样式、视频）加载完成后执行，只执行一次
window.onload = function () {};

// 仅 DOM 结构解析完成后执行，不等待图片与样式，触发更早
document.addEventListener("DOMContentLoaded", function () {});
```

内置对象方面，`Date` 必须先 `new` 才能使用：

```javascript
var d = new Date();
d.getFullYear();  // 四位年份
d.getMonth();     // 月份 0~11，0 表示一月
d.getDate();      // 日期 1~31
d.getDay();       // 星期 0~6，0 表示周日
d.getHours();     // 小时 0~23
d.getMinutes();   // 分钟 0~59
d.getSeconds();   // 秒 0~59
d.getTime();      // 1970-01-01 至今的毫秒数（时间戳）
```

对应的 `setFullYear()`、`setMonth()`、`setDate()`、`setHours()`、`setMinutes()`、`setSeconds()`、`setTime()` 用于设置时间。`String` 对象提供字符串截取、替换、大小写转换等方法，同样需要创建实例后调用。

### 2.7 函数与事件

```javascript
function functionName(parameter1, parameter2) {
  // 函数体
  return expression;   // 可选，未写 return 时返回 undefined
}
functionName(actualArg1, actualArg2);
```

规则：函数名区分大小写（`Test` 与 `test` 是两个不同函数）；参数列表最多 255 个；`return` 既返回值也终止函数执行。

事件是用户或浏览器触发的动作，常用三类：

- **焦点事件**：`onfocus` 获得焦点、`onblur` 失去焦点、`onchange` 内容改变，常用于输入校验；
- **表单事件**：`onsubmit` 表单提交、`onreset` 表单重置；
- **页面事件**：`onload` 页面加载完成。

事件绑定有两种方式：HTML 内联绑定（`<button onclick="fn()">`）与 DOM 绑定（`btn.onclick = function () {}`）。前者写法直观但结构与行为耦合，后者是正式项目的主流做法。

### 2.8 Bootstrap

Bootstrap 是一套开源的 HTML + CSS + JS 前端框架，提供样式库、组件（按钮、导航栏、弹窗）与插件，核心特性是**响应式布局**：同一套页面可自动适配电脑、平板与手机屏幕。使用时引入其 CSS 与 JS 文件，在标签上添加预定义类名即可获得样式，适合快速搭建后台界面与课程设计页面。

### 2.9 XML 语法

XML（Extensible Markup Language，可扩展标记语言）用于**存储与传输结构化数据**，也是 Java 项目（Spring、MyBatis、Tomcat）配置文件的主要格式。

三个特点：标签成对出现且必须正确嵌套；标签名可自定义（可扩展）；整份文档只能有一个根标签。

XML 与 HTML 的区别：

| 维度 | HTML | XML |
|---|---|---|
| 目的 | 展示数据、排版页面 | 存储与传输数据 |
| 大小写 | 不区分 | 严格区分 |
| 空格 | 自动合并 | 原样保留 |
| 标签 | 预定义 | 自定义、可扩展 |
| 闭合 | 较宽松 | 必须闭合、严格嵌套 |

文档声明必须位于第一行，其前不得有空格或注释：

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
```

`version` 一般写 1.0；`encoding` 常用 UTF-8 以防止中文乱码；`standalone` 表示是否依赖外部约束文件，`yes` 为独立文档，`no` 表示引用外部 DTD 或 Schema。

文档由四部分组成：文档声明、元素、属性、注释。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<书架>
    <书 版本="第2版">
        <书名>JavaWeb入门</书名>
        <售价 单位="元">68</售价>
    </书>
</书架>
```

`<`、`>`、`&` 等符号需转义为 `&lt;`、`&gt;`、`&amp;`；若大段内容含大量特殊符号，可用 CDATA 段避免逐个转义：

```xml
<![CDATA[ 这里可以自由书写 < > & 而不报错 ]]>
```

### 2.10 DTD 约束

DTD（Document Type Definition）用于规定 XML 中可出现哪些标签、嵌套顺序与出现次数，文件后缀为 `.dtd`。使用流程为三步：编写 `.dtd` 约束文件 → 在 XML 中引入 → 按约束书写，违反即报错。

元素定义格式为 `<!ELEMENT 元素名 内容类型>`：

```dtd
<!ELEMENT 书架 (书+)>
<!ELEMENT 书 (书名,作者,售价)>
<!ELEMENT 书名 (#PCDATA)>
<!ELEMENT 作者 (#PCDATA)>
<!ELEMENT 售价 (#PCDATA)>
```

- `#PCDATA`：元素内为普通文本（Parsed Character Data）；
- `(子元素1,子元素2)`：嵌套子元素，逗号表示**顺序固定**；
- `EMPTY`：空元素，如 `<img/>`；
- `ANY`：任意内容，约束力最弱，实际不用。

频次与组合符号：`+` 表示 1 次或多次，`*` 表示 0 次或多次，`?` 表示 0 次或 1 次，`,` 表示顺序出现，`|` 表示多选一，`()` 用于分组。

属性定义格式为 `<!ATTLIST 元素名 属性名 类型 设置说明>`：

```dtd
<!ATTLIST 书 版本 CDATA #REQUIRED>
```

四种设置说明：

| 关键字 | 含义 |
|---|---|
| `#REQUIRED` | 必须填写，缺失即报错 |
| `#IMPLIED` | 可选，可写可不写 |
| `#FIXED "值"` | 固定值，不写时自动填充，写了也只能是该值 |
| `"默认值"` | 不写时取默认值，写了可覆盖 |

属性类型常用三种：`CDATA`（字符串）、枚举（如 `(男|女)`，只能取其中之一）、`ID`（全文档唯一，类似主键，且不能设默认值，必须 `#REQUIRED`）。

引入方式有三种：内嵌式（直接写在 `<!DOCTYPE 根标签 [ … ]>` 内，仅供当前文件使用）、外部本地引入（`<!DOCTYPE 书架 SYSTEM "book.dtd">`）、公共引入（`<!DOCTYPE 书架 PUBLIC "DTD名称" "URL">`）。

### 2.11 XSD（Schema）约束

XSD（XML Schema Definition）文件后缀为 `.xsd`，本身即是一份合法的 XML 文档，用以替代 DTD。相较 DTD 有五点优势：语法即 XML，易读易写；与 XML 共享同一套合法性校验机制；完整支持命名空间；内置丰富数据类型；约束粒度更细（可限定数值范围、字符串长度、正则格式）。

固定根结构：

```xml
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
</xs:schema>
```

**元素与属性定义**：

```xml
<xs:element name="lastname" type="xs:string"/>
<xs:element name="age" type="xs:integer"/>
<xs:element name="dateborn" type="xs:date"/>
<xs:attribute name="price" type="xs:decimal"/>
```

内置类型常用六种：`xs:string` 字符串、`xs:integer` 整数、`xs:decimal` 小数、`xs:boolean` 布尔、`xs:date` 日期（`yyyy-MM-dd`）、`xs:time` 时间。`element` 约束标签内部内容，`attribute` 约束标签上属性的值。

**简单类型**用于在基础类型上追加限制，结构固定为 `simpleType → restriction → 具体规则`：

```xml
<!-- 数值区间：年龄 18~58 -->
<xs:element name="age">
  <xs:simpleType>
    <xs:restriction base="xs:integer">
      <xs:minInclusive value="18"/>
      <xs:maxInclusive value="58"/>
    </xs:restriction>
  </xs:simpleType>
</xs:element>

<!-- 枚举：只能取三个值之一 -->
<xs:element name="car">
  <xs:simpleType>
    <xs:restriction base="xs:string">
      <xs:enumeration value="Audi"/>
      <xs:enumeration value="Golf"/>
      <xs:enumeration value="BMW"/>
    </xs:restriction>
  </xs:simpleType>
</xs:element>

<!-- 正则：仅允许单个小写字母 -->
<xs:element name="letter">
  <xs:simpleType>
    <xs:restriction base="xs:string">
      <xs:pattern value="[a-z]"/>
    </xs:restriction>
  </xs:simpleType>
</xs:element>
```

空白字符处理用 `xs:whiteSpace`，取值 `preserve`（原样保留）、`replace`（换行与制表符替换为空格）、`collapse`（连续空白合并为一个并删除首尾空白）。

**复杂类型** `xs:complexType` 用于含属性或含子元素的标签，分四种场景：

1. **空元素**（只有属性，无内容）：`<product proid="1345"/>` 对应在 `complexType` 内仅声明 `xs:attribute`；
2. **仅含文本**（文本 + 属性，无子元素）：结构为 `complexType → simpleContent → extension`，用 `extension` 在基础类型上追加属性；
3. **仅含子元素**：用 `xs:sequence` 规定子元素顺序，作用等同 DTD 的逗号；另有 `xs:choice` 表示多选一、`xs:all` 表示顺序任意；
4. **文本与子元素混合**：必须设置 `mixed="true"`，默认值为 `false`，即不允许游离文本出现。

```xml
<!-- 场景 2：文本 + 属性 -->
<xs:element name="shoesize">
  <xs:complexType>
    <xs:simpleContent>
      <xs:extension base="xs:integer">
        <xs:attribute name="country" type="xs:string"/>
      </xs:extension>
    </xs:simpleContent>
  </xs:complexType>
</xs:element>

<!-- 场景 3：仅含子元素 -->
<xs:element name="person">
  <xs:complexType>
    <xs:sequence>
      <xs:element name="firstname" type="xs:string"/>
      <xs:element name="lastname" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>
</xs:element>
```

区分要点：`simpleType` 内部只有纯文本，不能有子元素与属性；`complexType` 可含属性、可嵌套子元素；`simpleContent` 是 `complexType` 的分支，表示“只有文本与属性”；`mixed="true"` 表示文本与子元素混排。

**命名空间**用于区分不同约束文件中的同名标签，声明格式为 `xmlns:前缀="唯一URI"`：

```xml
<ns315:书架 xmlns:ns315="http://www.ns315.org/xmlbook/schema">
    <ns315:书>
        <ns315:书名>Java基础案例教程</ns315:书名>
    </ns315:书>
</ns315:书架>
```

`xmlns` 为固定关键字；前缀可自定义；URI 仅作唯一标识，无需可访问。作用域为声明该属性的元素及其全部后代元素。保留前缀 `xml` 与 `xmlns` 不得用作自定义前缀。

XML 引入 XSD 有两种方式：带命名空间时用 `xsi:schemaLocation="命名空间URI xsd文件路径"`（两个 URI 以空白分隔）；无命名空间时用 `xsi:noNamespaceSchemaLocation="book.xsd"`。

### 2.12 C/S 与 B/S 架构

**C/S（Client/Server）** 需安装专用客户端，如 QQ、桌面网游。三点固有缺陷：每台机器都需安装，部署工作量大；业务逻辑在客户端，升级须逐台更新；客户端直连数据库，受数据库最大连接数限制，并发能力有限。

**B/S（Browser/Server）** 只需浏览器，业务逻辑与数据均在服务器端，典型三层结构为：

```
浏览器 ←HTTP 请求/响应→ Web 服务器（Tomcat：Servlet、JSP、静态资源） ←JDBC→ 数据库服务器
```

优点：免安装、跨设备；服务器升级后客户端无需任何部署即用到新版本；浏览器不直接连接数据库，由 Web 服务器作为中间层访问，缓解了 C/S 的并发瓶颈。信息管理系统普遍采用 B/S 架构。

### 2.13 HTTP 协议

HTTP（HyperText Transfer Protocol，超文本传输协议）规定浏览器与服务器之间数据传输的规则。三个特点：基于 TCP，面向连接、可靠传输；采用请求—响应模型，一次请求对应一次响应，服务器不会主动推送；**无状态**，服务器不记忆此前的请求，优点是速度快、负担小，缺点是无法复用会话数据，由此引出 Cookie 与 Session。

版本差异：HTTP/1.0 使用短连接，一次 TCP 连接只处理一个请求，页面含多个资源时需反复建立与断开连接，开销大；HTTP/1.1 支持持久连接（`Connection: keep-alive`），一次连接可发送多个请求，服务器按请求顺序返回响应，显著降低延迟。

**请求消息**由请求行、请求头、（可选的）请求体组成：

```
GET /index.html HTTP/1.1
Host: www.itcast.cn
Connection: keep-alive
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0
Accept: text/html,image/png
Accept-Language: zh-CN,zh
Accept-Encoding: gzip, deflate
```

请求行由“请求方式 + 资源路径 + 协议版本”构成，三者以空格分隔，以回车换行结束。常用请求方式：

| 方法 | 含义 |
|---|---|
| GET | 获取 URI 标识的资源 |
| POST | 向指定资源提交数据，如提交表单、上传文件 |
| HEAD | 只获取响应头，不返回实体内容 |
| PUT | 将资源放置到指定 URI 位置 |
| DELETE | 删除指定资源 |
| TRACE | 回送请求信息，用于诊断 |
| CONNECT | 建立隧道，多用于 HTTPS 代理 |

GET 与 POST 的核心区别：

| 维度 | GET | POST |
|---|---|---|
| 参数位置 | 拼在 URL 的 `?` 之后（请求行内），无请求体 | 放在请求体中 |
| 数据大小 | 受 URL 长度限制 | 理论上无限制 |
| 可见性 | 地址栏明文可见 | 不在地址栏显示，相对隐蔽 |
| 缓存 | 浏览器可能缓存 | 默认不缓存 |

必须澄清的误区：**POST 不是加密**，只是参数不在地址栏显示，使用抓包工具仍可看到请求体内容；真正的加密依赖 HTTPS。

请求头用于向服务器传递附加信息。常见字段：`Host` 指定目标主机（一台服务器可承载多个站点，依靠 Host 区分）；`User-Agent` 标识浏览器与操作系统；`Accept` 声明可接收的 MIME 类型；`Accept-Language` 声明语言偏好；`Accept-Encoding` 声明支持的压缩格式（gzip、deflate）；`Referer` 记录来源页面，可用于访问统计与**防盗链**（校验来源非本站则拒绝返回图片资源）；`If-Modified-Since` 携带上次获取资源的 GMT 时间，资源未变更时服务器返回 304，否则返回 200 与新资源；`If-None-Match` 与 `ETag` 配合，按内容标识判断是否变更；`Range` 与 `If-Range` 用于断点续传，前者指定字节区间，后者判断文件在断点期间是否被修改；`Authorization` 携带身份凭证，与 401 响应配合；`Cookie` 携带会话标识。

**响应消息**由响应状态行、响应头、空行、响应体组成：

```
HTTP/1.1 200 OK
Server: Apache-Coyote/1.1
Content-Type: text/html;charset=utf-8
Content-Length: 1024
Content-Encoding: gzip
Cache-Control: max-age=300

<html>...</html>
```

响应状态行由“协议版本 + 状态码 + 状态描述”构成。状态码为三位数字，首位决定类别：

| 类别 | 含义 | 代表状态码 |
|---|---|---|
| 1XX | 信息，请求已接收，需继续处理 | 100 |
| 2XX | 成功，请求已被接收、理解并处理 | 200 OK |
| 3XX | 重定向，需进一步操作或使用缓存 | 302 Found、304 Not Modified |
| 4XX | 客户端错误 | 400 Bad Request、404 Not Found |
| 5XX | 服务器端错误 | 500 Internal Server Error |

- **200**：请求成功，返回正常结果；
- **302**：资源临时由另一 URI 响应，后续仍使用原地址，配合 `Location` 头实现跳转；
- **304**：资源未修改，客户端应继续使用本地缓存，响应无实体内容；
- **400**：请求语法错误，参数格式不合法；
- **404**：服务器找不到请求的资源，地址写错或被删除；
- **500**：服务器内部程序异常，需查看日志排查。

常用响应头：`Content-Type` 声明响应内容的类型与字符集；`Content-Length` 声明响应体字节数；`Content-Encoding` 声明压缩算法；`Cache-Control` 控制缓存策略（如 `max-age=300` 表示可缓存 300 秒）；`Last-Modified` 与 `ETag` 供缓存校验；`Location` 配合 3xx 指定新地址，此时不应同时出现 `Content-Type`；`Server` 暴露服务器软件与版本（生产环境通常隐藏）；`Set-Cookie` 下发会话标识；`Content-Disposition` 控制浏览器是内联打开（`inline`）还是下载保存（`attachment; filename="a.zip"`）；`Refresh` 指定若干秒后自动刷新或跳转；`WWW-Authenticate` 配合 401 指示认证方式，`Proxy-Authenticate` 则针对代理服务器认证；`Retry-After` 配合 503 或 3xx 告知客户端何时重试。

一条响应中，状态行恒为一行，响应头可有零至多行（每调用一次 `setHeader()` 即新增一行），头部与实体之间必须以空行分隔，响应体长度不受行数限制。

### 2.14 Tomcat 与 Servlet 执行流程

Web 服务器的作用有两点：封装 HTTP 协议、简化开发；承载 Web 项目并对外提供浏览服务。Tomcat 是轻量级 Web 服务器，支持 Servlet/JSP 等少量 Java EE 规范，也称为 Web 容器或 Servlet 容器。

基本使用：启动执行 `bin\startup.bat`；正常关闭执行 `bin\shutdown.bat` 或按 `Ctrl+C`，直接关闭窗口属于强制关闭。控制台中文乱码时，修改 `conf/logging.properties`，将 `java.util.logging.ConsoleHandler.encoding` 设为 `UTF-8`。

一次请求的完整流程为：浏览器组装 HTTP 请求报文 → Tomcat 解析并定位对应 Servlet → 调用 `service(request, response)` → Servlet 从 `request` 取参数、向 `response` 写数据 → Tomcat 将 `response` 封装为 HTTP 响应报文返回浏览器。

```java
@WebServlet("/demo3")
public class ServletDemo3 extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        // 1. 读取 URL 参数，如 /demo3?name=zhangsan
        String name = request.getParameter("name");

        // 2. 设置响应头，声明内容类型与字符集，防止中文乱码
        response.setHeader("Content-Type", "text/html;charset=utf-8");

        // 3. 获取字符输出流，向浏览器写出内容
        response.getWriter().write("<h1>" + name + "，欢迎您！</h1>");
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        System.out.println("Post...");
    }
}
```

要点：`@WebServlet` 配置访问路径；自定义 Servlet 必须继承 `HttpServlet`；GET 请求进入 `doGet`，POST 请求进入 `doPost`，二者由父类 `service()` 自动分派；`request.getParameter()` 用于获取请求参数；`response.setHeader()` 可多次调用以设置多条响应头，`setStatus()` 用于设置状态码；`getWriter()` 输出文本，`getOutputStream()` 输出二进制，二者在同一响应中不可同时使用。

## 三、典型例题 / 关键问答

**例 1** 判断：调用事件处理程序主要分为在 JavaScript 中调用和在 HTML 中调用两种。

答：正确。HTML 内联绑定写在标签事件属性中（`<button onclick="fn()">`），DOM 绑定在脚本中进行（`btn.onclick = function () {}`），题干归纳成立。

**例 2** 判断：链入式是使用频率最高、最实用的 CSS 样式表，它将 HTML 与 CSS 分离为两个或多个文件，实现了结构与表现的完全分离。

答：正确。外链式通过 `<link>` 引入独立 `.css` 文件，多页面可共用，改一处即全站生效，且可被浏览器缓存，是企业开发的标准做法。

**例 3** 判断：在 JavaScript 中，函数名不区分大小写。

答：错误。JavaScript 严格区分大小写，`function Test(){}` 定义后调用 `test()` 会报未定义错误，变量名、函数名、关键字均大小写敏感。

**例 4** 判断：通过对 `<tr>` 标记应用属性，可以对表格中的某一个单元格进行控制。

答：错误。`<tr>` 表示整行，属性作用于该行全部单元格；控制单个单元格应使用 `<td>`。

**例 5** 判断：`<td>` 用于定义单元格，且必须嵌套在 `<tr></tr>` 中。

答：正确。标准嵌套为 `table > tr > td`，`<td>` 不能直接置于 `<table>` 之下。

**例 6** 说明 GET 与 POST 的区别，并指出常见误解。

答：GET 参数拼在 URL 上、无请求体、受长度限制、可能被缓存，适合查询；POST 参数置于请求体、理论无大小限制、默认不缓存，适合登录、注册与文件上传。常见误解是“POST 更安全”，实际上 POST 仅是不在地址栏显示，报文仍为明文，抓包可见，安全性须由 HTTPS 提供。

**例 7** 访问一个需要登录的页面，服务器返回 302 并带有 `Location` 头；浏览器再次请求时带上 `If-Modified-Since`，服务器返回 304。分别解释这两个状态码的作用。

答：302 表示资源临时迁移，浏览器应依据 `Location` 自动向新地址发起请求，原地址后续仍然有效；304 表示资源自 `If-Modified-Since` 指定时间以来未修改，服务器不返回实体内容，浏览器直接使用本地缓存，从而节省带宽、加快加载。

**例 8** 页面显示中文乱码，从 HTTP 与 Servlet 角度应如何排查？

答：首先确认响应头 `Content-Type` 是否声明了 `charset=utf-8`，Servlet 中需在获取输出流之前调用 `setHeader` 或 `setContentType`；其次确认 HTML 中 `<meta charset="UTF-8">` 与文件实际保存编码一致；再次检查数据库连接与页面传参是否统一使用 UTF-8。三处编码一致方可消除乱码。

**例 9** 简述 `simpleType`、`complexType`、`simpleContent`、`mixed="true"` 的区别。

答：`simpleType` 表示元素内部只有纯文本，不能嵌套子元素；`complexType` 表示元素可拥有属性或嵌套子元素；`simpleContent` 是复杂类型的分支，表示“只有文本与属性、没有子元素”，需配合 `extension` 追加属性；`mixed="true"` 表示复杂类型内部文本与子元素可以混排，默认为 `false`。

**例 10** 一份 XML 同时引入两个 XSD，二者都定义了 `<book>` 标签，如何避免冲突？

答：为两套约束分别声明不同的命名空间前缀（`xmlns:a="URI1"`、`xmlns:b="URI2"`），XML 中使用 `a:book` 与 `b:book` 加以区分，并通过 `xsi:schemaLocation` 依次声明命名空间与对应 XSD 文件位置。DTD 几乎不支持命名空间，无法解决此类冲突，这也是 XSD 取代 DTD 的重要原因。

**例 11** 为什么一条 HTTP 响应中响应头可以有很多行，而状态行只有一行？

答：状态行描述本次请求的整体处理结果，一次请求只对应一个结果，故恒为一行；响应头是若干独立的“键: 值”附加指令（内容类型、长度、缓存、跳转地址等），彼此正交，可任意增减。Servlet 中每调用一次 `setHeader()` 就新增一行，故行数取决于业务需要。

**例 12** C/S 架构有哪三点缺陷？B/S 如何化解？

答：C/S 需逐台安装客户端、升级须重新部署全部客户端、客户端直连数据库受连接数限制。B/S 以浏览器为统一客户端，免安装；业务集中在服务器，升级只需更新服务端；浏览器经 Web 服务器中转访问数据库，中间层可连接池化与横向扩展，从而缓解并发瓶颈。

## 四、小结

1. HTML 负责结构，由文档声明、`head`、`body` 构成；标签分单标签与双标签，表格依靠 `tr`/`td` 与 `colspan`、`rowspan` 完成布局，表单依靠 `form` 与各类 `input` 收集数据，其中同组单选与多选的 `name` 必须一致。
2. CSS 负责表现，语法为“选择器 + 声明块”；四种引入方式中，外链式因彻底分离、可复用、可缓存而成为工程标准，导入式因加载顺序缺陷被淘汰；常用选择器为标签、类、id 与通配符。
3. JavaScript 由 ECMAScript、DOM、BOM 组成；DOM 提供 `getElementById`、`getElementsByName` 等定位方法，BOM 以 `window` 为核心提供弹窗、定时器与加载事件；函数名区分大小写，事件绑定分内联与 DOM 两种。
4. XML 用于存储与传输数据，声明必须在首行，标签自定义且严格闭合，全文档唯一根元素；DTD 以元素、属性、频次符号约束结构，XSD 以 XML 语法描述约束，支持丰富数据类型、正则与命名空间，是当前主流。
5. C/S 与 B/S 的根本差异在于客户端形态与业务部署位置；B/S 以免安装、易升级、中间层访问数据库的优势成为 Web 应用的标准架构。
6. HTTP 基于 TCP、请求—响应、无状态；1.1 以持久连接解决 1.0 的短连接开销；请求消息为“请求行 + 请求头 + 请求体”，响应消息为“状态行 + 响应头 + 空行 + 响应体”；GET 与 POST 的差异在参数位置与长度限制，而非加密与否。
7. Tomcat 是 Servlet 容器，负责解析 HTTP 并调度 Servlet；`request` 承载请求数据，`response` 承载响应数据，`service()` 按请求方式分派到 `doGet` 或 `doPost`，输出前设置字符集是避免乱码的关键。
