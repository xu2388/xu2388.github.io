---
title: Java 面向对象 · 继承、多态、异常与集合泛型
subject: JavaWeb
category: 课程笔记
source: 豆包对话 · Java 继承重写重载多态 final 精讲、泛型与集合框架测试、Java 异常处理题目、类与对象及内部类教材、接口与抽象类讲义
summary: 梳理 Java 面向对象主线：构造器与 this/static 取值规则、四级访问控制、重写四条约束（签名一致、协变返回、受检异常不得更宽、访问权限不得更严）、多态「编译看左边、运行看右边」与 instanceof 向下转型、abstract 与 interface 成员差异、final 引用不可变与内容可变之辨、四类内部类；给出 Throwable 体系、finally 先于 return 交付、try-with-resources 的 close 先于 catch 等执行序结论；集合与泛型覆盖 Collection/Map 双体系、Map.put 返回被覆盖旧值、Iterator 独占删除、类型擦除与通配符 PECS 原则。
---

# Java 面向对象 · 继承、多态、异常与集合泛型 · 学习笔记

## 一、概述

本文聚焦 Java 语言本身的面向对象机制与数据组织工具：类与对象及封装、继承与 super、重写与重载、多态与引用类型转换、abstract/interface/final/内部类、异常体系、集合框架与泛型。与仓库内已有的《Java 数组·字符串·正则》《Java IO 流与多线程》《JavaWeb》三篇互不重复：数组与字符串、IO 流与线程、Servlet/JSP 均不在本文展开。

原始材料为一系列逐题精讲式对话，题面、题号、选项标号已全部剥离，只保留知识点与最小可运行代码，按「问题—原因—结论」重排；原料结果与代码语义不符之处按 JLS 分析并显式勘误。

---

## 二、类与对象：构造器、this 与 static

### 2.1 类、对象与构造方法

类是模板、对象是实例；`new` 创建对象时实际执行构造方法。构造方法与成员方法的判定标准只有两条：

| 特征 | 构造方法 | 成员方法 |
|---|---|---|
| 方法名 | 必须与类名完全相同 | 任意合法标识符 |
| 返回值 | 没有任何返回值，连 `void` 都不写 | 必须声明返回值类型，`void` 也算 |
| 调用时机 | `new` 创建对象时由编译器自动调用 | 通过对象（或类名）显式调用 |
| 可否重载 | 可以 | 可以 |
| 可否被重写/继承 | 均不可以，只能经 `super` 或 `this` 转调 | 成员方法可被重写 |

```java
class Book {
    String title;
    double price;
    Book(String title, double price) {   // 构造方法：与类名同名、无返回值
        this.title = title;
        this.price = price;
    }
    void showInfo() {                    // 成员方法：有 void，名字任意
        System.out.println(title + ": " + price);
    }
}
```

一个高频编译陷阱：Java 只在「类中未定义任何构造方法」时才自动补充无参构造；一旦手写了有参构造，默认无参构造即消失，此时 `new Student()` 因找不到匹配构造器而编译失败，须显式补写无参构造或创建时给出实参。同一类的多个对象各持一份实例变量的独立副本（位于堆内存），这是「类是模板、对象是实例」的直接证据。

### 2.2 this 的两类用途

其一，区分同名参数与实例变量。构造方法内若写成 `name = name`，赋值发生在参数自身之间，实例变量仍是默认值 `null`——典型的「编译通过、结果与预期不符」的逻辑错误，正确写法 `this.name = name` 显式指向当前对象。同理，`void setX(int x) { x = x; }` 调用后字段保持初值，改为 `this.x = x` 才真正写入。

其二，构造方法中用 `this(实参)` 转调本类另一个构造方法，必须放第一行，且不得循环调用。

### 2.3 static：类成员与实例成员

`static` 修饰的成员属于类本身，类加载时初始化一次，所有对象共享同一份；实例成员则每个对象各存一份。由此派生的调用与访问规则：

| 项目 | 实例成员 | 静态成员 |
|---|---|---|
| 归属 | 每个对象独立一份 | 类级别，全部对象共享 |
| 调用方式 | 必须通过对象 | `类名.成员`，对象调用可编译但不推荐 |
| 能否使用 `this` | 可以 | 不可以（静态上下文无当前对象） |
| 相互访问 | 实例方法可直接调静态方法 | 静态方法不能直接访问实例成员 |

```java
class Car {
    String brand;            // 实例属性：每对象独立
    static int count = 0;    // 类属性：所有对象共享一份
    Car(String brand) {
        this.brand = brand;
        count++;             // 构造 3 个对象后 count 为 3
    }
    void showBrand() { System.out.println(brand); }
    static void showCount() { System.out.println(count); }
}
```

变量按位置分三类：实例变量、静态变量、局部变量（方法参数、方法体内、代码块内）。实例与静态变量有默认值（数值 `0`、引用 `null`），局部变量无默认值且随栈帧销毁。`main` 本身是静态方法，直接在其中访问非静态成员会编译失败，必须先创建对象。

### 2.4 参数传递是值传递

方法参数传递的永远是「引用的副本」。下面的代码里，`change` 让形参 `arr` 指向新数组，调用方的 `a` 不受影响，输出仍为 `1`；若改为 `arr[0] = 9` 修改元素则会反映到原数组，因为副本引用与原引用指向同一块堆内存。

```java
class Test {
    static void change(int[] arr) {
        arr = new int[]{9, 9, 9};   // 只改副本指向，原数组不动
    }
    public static void main(String[] args) {
        int[] a = {1, 2, 3};
        change(a);
        System.out.println(a[0]);   // 输出 1
    }
}
```

### 2.5 封装与四级访问控制

封装的落点是「字段私有化 + 提供公共读写方法」。Java 提供四个访问级别，其中包级私有（俗称 default）靠「不写关键字」获得，`default` 本身并非访问控制关键字（它在接口中表示默认方法）。

| 修饰符 | 本类 | 同包 | 子类 | 任意处 |
|---|---|---|---|---|
| `private` | 可见 | 不可见 | 不可见 | 不可见 |
| 不写（包级私有） | 可见 | 可见 | 不同包子类不可见 | 不可见 |
| `protected` | 可见 | 可见 | 可见（含不同包） | 不可见 |
| `public` | 可见 | 可见 | 可见 | 可见 |

结合继承的取态：子类继承父类的 `public`、`protected` 与同包下的包级私有成员；`private` 成员与构造方法不被继承——构造方法只能经 `super(...)` 转调，`private` 方法在子类中无法重写。

---

## 三、继承与 super

### 3.1 单继承与继承的边界

Java 类只允许单继承，一个类只能 `extends` 一个父类；「多继承」的效果由接口弥补（一个类可 `implements` 多个接口）。未显式写 `extends` 的类默认继承 `Object`。

构造器链规则：子类构造方法若未写 `super(...)`，编译器自动在首行插入 `super()` 调用父类无参构造；当父类只有有参构造（默认无参构造已被 2.1 的机制吞掉）时，自动插入的 `super()` 找不到目标而编译失败，必须第一行显式写 `super(实参)`。`super()` 只能出现在构造方法第一行，普通方法里调用直接编译错误；`super.方法名()` 不受此限，用于在被重写后仍调用父类版本。

```java
class Parent {
    Parent(int x) { }              // 只有有参构造
}
class Child extends Parent {
    Child() {
        super(1);                  // 必须显式调用，否则编译失败
    }
}
```

子类可在继承基础上自由新增字段与方法，新增成员同样可用 `static`、`final` 修饰。

---

## 四、重写与重载

重写（Override）发生在父子类之间，重载（Overload）发生在同一个类内部，判定维度对照如下：

| 维度 | 重写 Override | 重载 Overload |
|---|---|---|
| 所在位置 | 父类与子类之间 | 同一个类内部 |
| 方法名 | 必须相同 | 必须相同 |
| 参数列表 | 必须完全相同 | 必须不同（类型、个数或顺序） |
| 返回值 | 相同，或协变返回（子类型） | 不作要求，仅返回值不同不构成重载 |
| 异常 | 不能抛出更宽泛的受检异常 | 不作要求 |
| 访问权限 | 不能比父类更严格 | 不作要求 |
| 绑定时机 | 运行时（动态绑定） | 编译时（静态选择） |

重写的四条硬规则：签名（方法名加参数列表）必须一致；返回类型可「协变」，即子类重写方法的返回类型可以是父类返回类型的子类型；子类声明的受检异常范围不能大于父类；访问权限只能等于或宽于父类，不能收紧。构造方法既不能被继承也不能被重写；`private` 方法与 `static` 方法都不参与重写——`static` 方法若子类同名同签名，属于「隐藏」而非覆盖。重载属于「编译时多态」：调用哪个版本在编译期依据实参确定；重写配合父类引用指向子类对象才是「运行时多态」。

---

## 五、多态与向上、向下转型

### 5.1 向上转型：编译看左边，运行看右边

`Animal myAnimal = new Dog();` 是向上转型（自动完成，无需强转），它构成多态的基础：子类对象本身就是一个父类实例。可调用哪些成员由左边的声明类型决定，具体执行哪份实现由右边的实际对象决定。

```java
class Animal { void shout() { System.out.print("Animal "); } }
class Dog extends Animal {
    void shout() { System.out.print("Dog barks "); }
    void run()   { System.out.print("Dog runs "); }
}
public class Test {
    public static void main(String[] args) {
        Animal myAnimal = new Dog();
        myAnimal.shout();               // Dog barks：编译看左边，运行看右边
        // myAnimal.run();              // 取消注释则编译报错
        if (myAnimal instanceof Dog) {
            Dog myDog = (Dog) myAnimal; // 向下转型必须显式强转
            myDog.run();                // Dog runs
        }
    }
}
```

一个常见误解需要正面纠正：向上转型不等于「父类引用能用子类的一切功能」。声明类型是 Animal，`run()` 不在其成员表里，编译器直接拒绝，与对象真实类型无关。能调用什么看声明类型（左），执行谁的版本看实际类型（右）。

### 5.2 向下转型与 instanceof

向下转型必须显式强转；若实际对象并非目标子类，运行期抛出 `ClassCastException`，因此惯例是先用 `instanceof` 判定再转。接口引用同理：`Animal a = new Dog();`（Animal 为接口）时 `a.eat()` 执行 Dog 的实现，`a.bark()` 编译报错，`(Dog) a` 转回后即可调用子类特有方法——面向接口与面向父类的多态完全同构。多态只作用于实例方法，构造器没有「被多态调用」一说，`new` 哪个类就执行哪个类的构造链。

---

## 六、abstract 与 interface

### 6.1 抽象类

`abstract` 修饰的类不能实例化，但可以有构造方法——它不为「直接 new」服务，而是供子类构造链 `super(...)` 调用。抽象类可同时含抽象方法（只有声明）与具体方法，子类必须实现全部抽象方法，否则自身也得声明为抽象。

```java
abstract class Vehicle {
    String brand;
    Vehicle(String brand) { this.brand = brand; }  // 抽象类可以有构造方法
    abstract void start();                          // 无方法体
    void stop() { System.out.println(brand + " is stopping"); }
}
class Car extends Vehicle {
    Car(String brand) { super(brand); }
    void start() { System.out.println(brand + " car is starting"); }
}
public class TestAbstract {
    public static void main(String[] args) {
        Vehicle v = new Car("Toyota");   // 抽象类引用指向具体子类：多态
        v.start();
        v.stop();
        // Vehicle v2 = new Vehicle("BMW");  // 编译错误：抽象类不可实例化
    }
}
```

抽象类的继承链允许「抽象传抽象」：中间层子类只实现部分抽象方法时，只要保留 `abstract` 声明即编译合法，剩余抽象方法由后续具体子类补齐。`abstract` 与 `final` 修饰同一个类语义自相矛盾（一个要求被继承、一个禁止继承），不能并存。

### 6.2 接口

接口是比抽象类更纯粹的契约，成员有各自的隐含修饰规则：

| 接口成员 | 隐含修饰 | 备注 |
|---|---|---|
| 字段 | `public static final` | 不写也是常量，`int VERSION = 1;` 合法 |
| 抽象方法 | `public abstract` | 接口无构造方法，不可实例化 |
| `default` 方法 | 实例方法 | 必须有方法体，Java 8 起支持 |
| `static` 方法 | 类方法 | 经 `接口名.方法()` 调用 |
| `private` 方法 | 辅助方法 | Java 9 起允许，仅供接口内部其他方法调用，实现类不可见 |

结构性规则：接口可 `extends` 多个接口，类可 `implements` 多个接口，实现类必须实现接口的全部抽象方法。抽象类与接口还可混合编排——`abstract class Dog implements Animal` 只实现 `eat()` 而把 `sleep()` 留给下一级具体子类 `Puppy`，编译合法，体现「谁离具体谁兜底」的责任传递。函数式接口（有且仅有一个抽象方法的接口，可含 default/static 方法）是 Lambda 的前提；`@FunctionalInterface` 只是让编译器代为检查的标记，不标注该注解、单满足唯一抽象方法条件的接口依然是函数式接口。

---

## 七、final 的三种用法

`final` 分别作用于类、方法、变量时语义完全不同：

| 用法 | 效果 | 易错点 |
|---|---|---|
| `final` 类 | 不可被继承（如 `String`） | `final` 类中的方法天然无法被重写，等价于隐式 final |
| `final` 方法 | 不可被重写，但可随继承保留、可在本类中重载 | 用 `final` 方法名另写不同参数签名的方法属重载，合法 |
| `final` 变量 | 只能赋值一次，此后不可重新赋值 | 修饰引用类型时冻结的是「引用」，不是对象内容 |

`final` 变量须在声明处、构造方法或静态初始化块中完成初始化。引用不可变与内容可变之别，用一段代码即可看清：

```java
final int NUM = 10;
final StringBuilder SB = new StringBuilder("Hi");
NUM = 20;                       // 编译错误：对 final 变量二次赋值
SB.append(" Java");             // 合法：修改对象内容，未动引用
SB = new StringBuilder("Bye");  // 编译错误：试图让引用改指向
```

同理，`final List<String> list = new ArrayList<>();` 之后 `add`、`remove` 都合法——final 只禁止 `list = ...` 的重新指向。

---

## 八、内部类

内部类按位置与修饰分四类：非静态内部类、静态内部类、局部内部类、匿名内部类。其字节码文件名遵循「外部类名$内部类名」或「外部类名$序号」规则（如 `Outer$1.class`），匿名内部类的编号与它实现的接口或继承的抽象类无关。

### 8.1 非静态内部类与静态内部类

非静态内部类持有外部类实例的引用，必须先有外部类对象才能创建内部类对象；它可直接访问外部类全部成员，包括 `private`。静态内部类不持有外部类引用，可独立实例化，但只能访问外部类的静态成员。

```java
class Outer {
    private String secret = "Secret Content";
    String name = "Outer";
    class Inner {                 // 非静态：依赖 Outer 实例
        String name = "Inner";
        void show() { System.out.println(secret); }   // 直访 private
        void print(String name) {
            System.out.print(name + "-");             // 局部变量
            System.out.print(this.name + "-");        // Inner 的字段
            System.out.print(Outer.this.name);        // Outer 的字段
        }
    }
    static class SInner { }       // 静态：与 Outer 实例无关
}
public class Test {
    public static void main(String[] args) {
        Outer.Inner in = new Outer().new Inner();     // 挂在外部实例上
        in.show();                                    // Secret Content
        in.print("Local");                            // Local-Inner-Outer
        Outer.SInner sin = new Outer.SInner();        // 不需要外部实例
    }
}
```

三层 `name` 的取态是经典考点：裸名命中最近的局部变量，`this.name` 命中内部类字段，`外部类名.this.name` 命中外部类字段。前文的 `Map.Entry` 正是静态内部类语义——键值对实体不依赖 Map 实例存在。

### 8.2 匿名内部类

匿名内部类是「就地定义并使用」的一次性子类/实现类，语法为 `new 接口或抽象类名(实参) { 方法体 }`。两条常被误判的性质：它可以带参数——实参传给所继承抽象类的构造方法，`new Animal("旺财") { ... }` 在创建对象时先执行所继承抽象类的构造方法，而匿名类里写的那个抽象方法**要等到被调用时才执行**——构造与方法体不在同一个时点上，别把「定义了匿名类」当成「方法体跑过了」；接口一侧则没有构造方法可传参；它能直接访问外部类成员。Lambda 是函数式接口场景下匿名内部类的简写替代品，`MathOp op = x -> x * x;` 与手写匿名类效果一致而语法更省。

---

## 九、异常体系

### 9.1 体系结构与 checked/unchecked

`Throwable` 是所有错误与异常的顶层父类，其下分两支：`Error` 表示 JVM 层面的严重问题（如内存耗尽 OutOfMemory），程序通常无力恢复；`Exception` 表示程序级异常，再分「运行时异常（`RuntimeException` 及其子类，unchecked）」与其余「checked 异常」。注意 `NullPointerException` 挂在 `RuntimeException` 之下，而 `FileNotFoundException` 的直接父类是 `IOException` 而非 `Exception`——层次深度本身也是考点。

| 类别 | 典型代表 | 编译器是否强制处理 | 抛出方式 |
|---|---|---|---|
| Error | `OutOfMemoryError` | 否，一般不捕获 | JVM 抛出 |
| unchecked（运行时异常） | `NullPointerException`、`ArithmeticException`、`ArrayIndexOutOfBoundsException` | 否 | 多由 JVM 在运行中自动抛出 |
| checked（受检异常） | `IOException` 及其子类 | 是：要么捕获，要么继续声明 | 显式 `try-catch` 或 `throws` |

与异常相关的三类概念应予区分：语法错误（缺分号、括号不匹配）在编译期暴露；逻辑错误能通过编译并运行，只是结果与预期不符，JVM 不报错；异常是运行期被打断的控制流——方法创建含错误类型与程序状态的异常对象交给运行时系统，系统沿调用栈回溯查找匹配的 catch，直至 `main`；整条链无人处理时 JVM 中止程序并把跟踪栈打印到标准错误流。另注意 `getMessage()` 只返回描述字符串，`printStackTrace()` 才输出跟踪栈，两者常被混淆。

### 9.2 try-catch-finally 执行次序

基础模型：try 中异常点之后的语句被跳过，转入匹配的 catch，随后 finally 无论是否发生异常都会执行，finally 之后再回到 try 语句的下一条继续。`10 / 0` 抛 `ArithmeticException` 的骨架：

```java
try {
    System.out.print("A");
    int result = 10 / 0;      // 抛 ArithmeticException，B 不打印
    System.out.print("B");
} catch (ArithmeticException e) {
    System.out.print("C");
} finally {
    System.out.print("D");     // 恒执行
}
System.out.print("E");         // 输出序列：A C D E
```

嵌套结构中，内层 try 被内层 catch 消化后，外层 try 的后续语句照常执行，但外层 finally 仍然执行，输出序列即「1 → 2 → 3 → 4 → 6」，外层 catch 不会触发。catch 子句可用竖线并列多种异常类型合并捕获（JDK 7 起的 multi-catch），任一类型命中即进入该 catch；不用合并语法时，一个 catch 要兜住多种异常，参数类型须是它们共同的父类。一个例外必须单列：`System.exit(0)` 直接在 try 中终止 JVM 时，catch 与 finally 都不会执行——finally「几乎恒执行」的前提是 JVM 还活着。

### 9.3 finally 与 return 的先后

当 try 中已出现 `return`，finally 依旧要在返回值交付之前执行：返回值在离开 try 块时先被保存，finally 运行完毕后方法才真正返回。

```java
public class FinallyTest {
    static String checkResource() {
        try {
            System.out.print("Open");
            return "Result";
        } catch (Exception e) {
            return "Err";        // 补全分支
        } finally {
            System.out.print("Close");
        }
    }
    public static void main(String[] args) {
        System.out.print(checkResource());
    }
}
// 输出：OpenCloseResult
```

勘误：原料该题给出的代码只有 try 的 `return`，catch 与 finally 之后均无返回语句，其给出的运行结果为 `Open-CloseResult`；按 JLS 语义，此原样代码在编译期即因「缺少返回语句」被拒。上文示例对 catch 分支做了补全后，原料意图呈现的结论（finally 在 return 交付前执行、输出顺序 Open-CloseResult）才成立。

try-with-resources 给出另一条次序：资源实现 `AutoCloseable` 时，块内抛出异常会先触发自动 `close()`，再进入 catch，最后才轮到块外的显式 finally——带 `RuntimeException` 的资源类示例输出为 `Run → Close → Error`，叠加 finally 后为 `Using → Closed → Error → Finally`。资源「先关后捕」与直觉相反，是执行序的高频出错点。

### 9.4 throw、throws 与自定义异常

`throw` 是动作：在方法体内创建并抛出一个异常对象，抛出点之后的语句不再执行；`throws` 是声明：挂在方法签名上，把受检异常的处理责任移交调用方。三条推论：抛出 `RuntimeException`（unchecked）无需声明，调用方不处理也能编译，运行至抛出点即中止；抛出受检异常（如 `IOException`）必须 `throws` 声明或捕获，否则到不了运行期；`main` 也可以 `throws Exception`，等价于把异常一路交给 JVM——声明链逐级传递（level2 → level1 → main），运行时输出打印到抛出点为止，随后 JVM 打印跟踪栈并中止。

自定义异常的两种姿势由父类选择决定：继承 `Exception` 得到受检异常，调用方被强制处理；继承 `RuntimeException` 得到非受检异常，调用无感。空类体即可工作，语义完全由父类链承担：

```java
class MyError extends RuntimeException { }   // 非受检自定义异常
public class Test1 {
    public static void main(String[] args) {
        try {
            System.out.print("1");
            if (true) throw new MyError();
            System.out.print("2");            // 不执行
        } catch (MyError e) {
            System.out.print("3");
        }
        System.out.print("4");                // 异常被处理后继续：1 3 4
    }
}
```

---

## 十、集合框架

### 10.1 两条体系与选型依据

集合解决「数据量不确定」的对象存储问题：与定长数组不同，集合无固定初始大小、按需动态扩容。框架分两条独立主线——Collection 单列体系与 Map 键值对体系，两者无继承关系；Collection 继承 `Iterable`，所有单列集合都支持迭代器遍历。

| 接口/类 | 有序性 | 可重复 | 下标 | 体系归属 |
|---|---|---|---|---|
| `List` | 有存取顺序 | 允许重复 | 有 | Collection |
| `Set` | 无固定顺序 | 元素唯一 | 无 | Collection |
| `Queue` | 队列语义 | — | — | Collection（`HashSet` 与之无关） |
| `Map` | 键无序（按键值对存） | 键唯一，值可重复 | 无下标 | 独立双列体系 |

常用实现类的选型（具体性能材料未展开，此处仅记常见结论）：`ArrayList` 底层数组、随机访问强、中间插删代价高；`LinkedList` 底层链表、插删强、查找弱；`HashSet` 基于哈希、唯一无序；`TreeSet` 基于红黑树、排序去重。

### 10.2 Iterator 与 ListIterator

迭代器统一提供 `hasNext()`、`next()`、`remove()`。遍历期间的黄金规则：增删只能调用迭代器自身的 `remove()`，调用集合自身的 `add`/`remove` 会触发 `ConcurrentModificationException`（这是 fail-fast 机制对 `modCount` 变化的检测；规范只要求「尽力而为」，并不保证任何并发修改都必然抛出，但单线程遍历时改集合几乎必现，因此当作硬纪律执行）；用迭代器删除后，集合大小实时同步。`ListIterator` 是 List 专属增强版：可前后双向遍历（`hasPrevious()`/`previous()`），可 `set()` 替换当前元素、`add()` 在当前迭代位置插入。

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if (it.next().equals("B")) {
        it.remove();        // 只能这样删，list.remove 会抛并发修改异常
    }
}
```

### 10.3 Map 的方法语义

Map 的四组返回值规则是高频陷阱区：

| 操作 | 情形 | 返回值/效果 |
|---|---|---|
| `put(k, v)` | 键不存在 | 存入新键值对，返回 `null` |
| `put(k, v)` | 键已存在 | 覆盖旧值，返回被覆盖的旧值 |
| `remove(k)` | 键不存在 | 返回 `null`，集合不变 |
| `putAll(m)` | 存在重复键 | 以新 Map 的值覆盖旧值，键数不重复累加 |
| `keySet()` | — | 返回全部键，类型是 Set |
| `values()` | — | 返回全部值，类型是 Collection 而非 Set |

材料中的综合样例可作自检：`Map<Integer, String>` 依次放入键 1～3，先统计大于 1 的键个数（得 2），再遍历 `entrySet()` 找到值为 `"B"` 的条目并把其键加入结果（键为 2），最终输出 `4`；而向同一键 put 两次时，第二次 put 拿到的是第一次的值而非 `null`。

关于 `HashMap` 底层，材料未展开，此处仅记常见结论：哈希表数组加链表组织冲突，JDK 8 起在单桶链过长时转红黑树，初始容量与负载因子决定扩容节奏；具体阈值材料未涉及、版本行为亦有差异，不再展开。`Comparable`（类自身实现 `compareTo` 定义自然序）与 `Comparator`（外部比较器实现 `compare` 定义定制序）、`Collections` 工具类（`sort`、`unmodifiableList` 等静态方法）在本课程材料中均未讲授，仅按通用结论备忘，细节以官方文档为准。

---

## 十一、泛型

### 11.1 定位与边界

泛型的价值在编译期：类型安全检查、自动类型转换、免除强转并消除转型警告；它不提升运行速度。边界两条：泛型参数只能是引用类型，基本类型必须换用包装类；检查只在编译期发生，运行期不再检查。

### 11.2 类型擦除

Java 泛型采用类型擦除实现：编译后类型参数被替换为其上限（无上限则替换为 `Object`），运行时不保留泛型的具体类型信息。推论是「`List<Integer>` 运行时只认自己是 List」。类型擦除决定了泛型是编译期纪律而非运行期机制，也解释了泛型为何不产生额外运行时开销。

```java
public static <T> T processItem(T item) {   // <T> 必须声明在返回值之前
    System.out.println(item);
    return item;
}
String result = processItem("Java");        // 调用处自动推断为 String
```

泛型方法须在返回值类型之前声明类型参数，缺了这段声明编译器不认识 `T`，直接报错；泛型方法可以有返回值，调用时通常无需显式写实参类型。

### 11.3 菱形语法与类型推断

`<>` 菱形语法（JDK 7 起）只出现在 `new` 右侧，由左侧引用类型推断构造器的参数化类型；左侧引用声明本身不能写成裸 `Box<>`。集合的类型由「左侧声明」决定，而非按首个添加元素推断：

```java
List<Number> list = new ArrayList<>();   // 类型是 List<Number>
list.add(10);                             // Integer 自动装箱
list.add(3.14);                           // Double 自动装箱
// Number 是各数值包装类的父类，放子类元素属向上转型，合法
```

上面这类菱形写法里，实参 `2024` 把类型参数定成 `Integer`，而不是 `int`、更不是 `Object`：泛型的类型实参只能是引用类型，自动装箱发生在推断之前。但别把这条推广到 `var`——`var v = 2024;` 推断出的就是 `int`，`var` 不做装箱，它只是照字面量的本来类型声明局部变量。两者的差别在于是否有泛型参数需要落地。

### 11.4 通配符与 PECS（材料未展开，按通用结论备忘）

课程材料只涉及带类型参数的声明（`List<Number>`），未展开通配符。此处仅记通用结论：`? extends T` 把集合限定为「T 及其子类的读视图」，适合从中取值；`? super T` 限定为「T 及其父类的写视图」，适合向内放 T。一句话概括即 PECS——Producer 用 `extends`，Consumer 用 `super`。此节属超出原料的常识性补充，细节以官方规范为准。

---

## 十二、易错点汇总与勘误

| 主题 | 直觉说法 | 正确结论 |
|---|---|---|
| 构造器 | 定义了有参构造仍有免费无参构造 | 有参构造一旦手定，默认无参构造消失 |
| this | 参数与字段同名时直接赋值生效 | 需 `this.x = x`，否则参数自我赋值 |
| 向上转型 | 父类引用能调子类特有方法 | 可调成员以声明类型为准 |
| 重写 | 返回值必须与父类完全相同 | 支持协变返回；异常不得更宽、权限不得更严 |
| 构造方法 | 子类可重写父类构造 | 构造方法不继承、不重写，只可 `super` 转调 |
| `super()` | 普通方法里也能调父类构造 | 只能作构造方法第一句 |
| final | `final` 集合不能增删元素 | 冻结的是引用，不是对象内容 |
| finally | 永远执行 | `System.exit(0)` 时不执行 |
| finally 与 return | try 里 return 即出结果 | finally 在返回值交付前执行 |
| try-with-resources | 先 catch 再 close | 先自动 `close()` 再进 catch |
| Map.put | 返回 null | 键已存在时返回被覆盖的旧值 |
| `values()` | 返回 Set | 返回 Collection |
| 类型擦除 | 运行时保留泛型 | 擦除后只剩上限或 Object；实参不能传基本类型 |

勘误记录一处：异常篇 finally 与 return 的原始代码缺少返回语句，原料给出的运行结果 `Open-CloseResult` 只在补全 catch 分支后才成立，本文按 JLS 补全代码并保留「finally 先于返回值交付」的原意结论；其余执行序样例与代码语义一致，未作改动。

---

## 十三、小结

面向对象的语法骨架可压缩成三组判断：成员归谁、调用能否通过编译（声明类型说了算）、运行执行哪份（实际类型说了算）。`this`、`super`、`instanceof`、`final`、`abstract` 皆围绕这三组判断展开；异常体系补上「控制流被打断后由谁接住」——沿调用栈回溯、finally 恒兜底、资源先于 catch 关闭；集合与泛型把对象组织从单点推到批量：双体系分工、迭代器独占修改权、Map 返回值语义，配合类型擦除这条编译期纪律，构成从「写得出」到「写得稳」的完整一环。
