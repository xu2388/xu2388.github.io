---
title: Web开发 · Django 路由、ORM 与模板
subject: Web开发/前端
category: 课程笔记
source: 豆包对话 · Django URL 配置困惑及解决 / 创建 Django 项目用于学习 ORM / Django 报错处理 / Django 第二周学习任务明确 / Django 模板继承报错排查
summary: Django 把一次请求拆成 URL 解析、视图处理、模型取数、模板渲染四段，MTV 是它对 MVC 的改写。路由用 path 与 include 分层，命名后可用 reverse 反向生成；ORM 以模型类描述表结构，迁移文件是 Python 脚本而非 SQL；QuerySet 惰性求值，filter 与 Q 对象负责筛选，select_related 与 prefetch_related 负责减少查询次数。模板靠 extends 与 block 继承，POST 表单必须带 CSRF token。多数报错可按「路由名、模板路径、迁移状态」三步定位。
---

# Web开发 · Django 路由、ORM 与模板

## 一、概述：MTV 与 MVC 的对应关系

Django 官方把架构称为 MTV：Model（模型）、Template（模板）、View（视图）。它与 MVC 的对应关系常被误解，准确的说法是：

| MTV | 职责 | 对应 MVC | 说明 |
|---|---|---|---|
| Model | 描述数据结构、提供查询接口 | Model | 一个类对应一张表，字段对应列 |
| Template | 把数据渲染成 HTML | View（表现层） | 只负责展示，不写业务规则 |
| View | 接收请求、调用模型、选择模板 | Controller | 函数或类，返回响应 |
| URLconf | 把 URL 映射到 View | 路由表 | 独立的 `urls.py`，不属于 MTV 三要素 |

与「View 对应 View」的直觉相反，Django 的 View 承担的是控制器职责，真正决定页面长什么样的是 Template。理解这一点，才能解释为什么「业务逻辑写在视图里、页面结构写在模板里、数据访问写在模型里」是 Django 的默认分工。

原料中的项目都遵循这个结构：`models.py` 定义 `Post`、`Comment`、`KnowledgeDocument`，`views.py` 返回 `HttpResponse` 或 `render`，`templates/` 下放 HTML，`urls.py` 负责把 `/index/`、`/chat/<id>/` 分发给对应函数。原料还特别指出，视图属于**应用**而不是项目根目录：在项目级 `urls.py` 里 `from myproject import views` 会报导入错误，因为项目根目录通常没有 `views.py`。

## 二、请求生命周期

### 2.1 从浏览器到响应

一次请求在 Django 中的路径可以拆成八步：

1. **Web 服务器接收连接**。开发时是 `runserver`，生产时通常是 Gunicorn/uWSGI 加 Nginx。服务器按 WSGI 或 ASGI 协议把请求交给 Django。
2. **请求中间件**。按 `MIDDLEWARE` 列表从上到下执行，处理会话、CSRF、认证、安全头等。
3. **URL 解析**。Django 用 `urlpatterns` 逐条匹配路径，找到视图函数或类。
4. **视图中间件**。进入视图前的钩子。
5. **视图执行**。读取 `request`，调用 ORM 查询，组织上下文。
6. **模板渲染**。`render(request, "x.html", context)` 加载模板、替换变量、执行标签。
7. **响应中间件**。从下到上返回，可修改响应头、内容。
8. **返回响应**。WSGI 服务器把状态码、头部、正文写回连接。

原料里 `runserver` 的输出正好对应第 1 步与第 3 步之间的状态：系统检查、未应用迁移提示、开发服务器地址。原料对这段输出的解释是「Django 启动前会检查项目配置，此处显示无错误」「有未应用的迁移，需运行 `migrate`」。这两条提示出现在请求之前，说明它们属于应用启动阶段，而不是某个视图的错误。

### 2.2 请求对象与响应对象

`HttpRequest` 是视图的第一个参数，常用属性如下：

| 属性 | 含义 | 注意 |
|---|---|---|
| `request.method` | 请求方法，大写字符串 | 判断 `"GET"` / `"POST"` |
| `request.GET` | URL 查询参数 | 类似字典，取不到返回 `None` |
| `request.POST` | 表单编码的请求体 | 仅 `POST` 且 `Content-Type` 匹配时填充 |
| `request.FILES` | 上传文件 | 表单需 `enctype="multipart/form-data"` |
| `request.body` | 原始字节 | 读取后流被消费，不能再读第二次 |
| `request.path` | 路径部分 | 不含域名与查询串 |
| `request.user` | 当前用户 | 依赖认证中间件 |

响应有四种常见形态：

```python
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

def index(request):
    return HttpResponse("Hello World")

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "blog/post_list.html", {"posts": posts})

def api_posts(request):
    data = list(Post.objects.values("id", "title"))
    return JsonResponse({"items": data})

def old_url(request):
    return redirect("/new/")
```

原料在排查「`HttpResponse` 未定义」时给出的解释是：`HttpResponse` 必须从 `django.http` 导入，未导入时解释器不识别，编辑器会画波浪线。这个错误看似低级，但暴露了一个事实：Django 的响应对象不是内置类型，视图必须显式返回一个响应实例，返回字符串或 `None` 都会报错。

## 三、路由：urls.py 的匹配与命名

### 3.1 path 的四个参数

```python
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("chat/<str:chat_id>/", views.chat_detail, name="chat_detail"),
    path("api/", include("api.urls")),
]
```

`path(route, view, kwargs=None, name=None)` 的四个参数分别是：路径模式、视图、额外关键字参数、路由名。路径模式末尾的斜杠不是装饰，它参与匹配；`post/1` 与 `post/1/` 在默认配置下不是同一个 URL。

原料给出的第一个路由错误就是「用了 `include` 但没导入」：

```python
from django.urls import include, path   # 必须同时导入 include
```

第二个错误是 `urlpatterns` 列表里两条 `path` 之间漏了逗号。Python 会把两行解析成同一个表达式的一部分，编辑器报的「括号未关闭」只是表象，真实原因是列表元素没有分隔。原料对此的判断是准确的：**报错位置不等于错误位置**，先看列表分隔符，再看括号。

### 3.2 路径转换器

| 转换器 | 匹配 | 传给视图的类型 | 示例 |
|---|---|---|---|
| `str` | 除 `/` 外的任意字符串 | `str` | `chat/<str:chat_id>/` |
| `int` | 非负整数 | `int` | `post/<int:pk>/` |
| `slug` | 字母、数字、下划线、连字符 | `str` | `tag/<slug:slug>/` |
| `uuid` | 标准 UUID | `uuid.UUID` | `user/<uuid:uid>/` |
| `path` | 含 `/` 的字符串 | `str` | `files/<path:filepath>` |

转换器决定「什么形状的 URL 能进来」。`<int:pk>` 遇到 `abc` 直接不匹配，不会进入视图；`<str:chat_id>` 则接受任意非斜杠字符串。原料在讲层级 URL 时给出 `/chat/12345` 的例子，应用级路由写 `path('<str:chat_id>/', views.chat_detail)`，视图签名则是 `def chat_detail(request, chat_id)`，参数名必须一致。

### 3.3 匹配顺序与包含

`urlpatterns` 从上到下匹配，第一条命中就停止。因此：

- 具体路径应放在通配路径之前，否则 `post/new/` 可能被 `post/<int:pk>/` 抢先匹配（若类型允许）。
- `include` 把前缀之后的部分交给子路由，子路由看到的是「去掉前缀」的路径。
- 子路由可以继续 `include`，形成任意层级，原料给出的 `/chat/room/123/message/456` 就是两级包含。

`include` 的价值是解耦：项目级路由只知道「哪个前缀交给哪个应用」，应用级路由知道「具体路径对应哪个视图」。删除或复用应用时，不需要动项目级配置。

### 3.4 命名与反向解析

给路由起名后，代码与模板都不应硬编码 URL：

```python
from django.urls import reverse

url = reverse("post_detail", args=[42])       # /post/42/
url = reverse("post_detail", kwargs={"pk": 42})
```

模板中：

```html
<a href="{% url 'post_detail' pk=post.pk %}">{{ post.title }}</a>
```

反向解析的好处是「改路径不用改调用点」。代价是名字必须一致：`reverse` 找不到名字、参数个数不对、命名空间缺失，都会抛 `NoReverseMatch`。原料在讲动态 URL 时明确写了「为 URL 命名，方便在代码或模板中生成 URL」，并给出 `reverse('chat_detail', args=['...'])` 的用法。

### 3.5 末尾斜杠与 APPEND_SLASH

Django 默认 `APPEND_SLASH = True`。当请求 `/post/1` 而路由只定义了 `post/<int:pk>/` 时，`CommonMiddleware` 会先尝试补一个斜杠再匹配；若补斜杠后能匹配，就返回 301 重定向。这解释了两个现象：浏览器地址栏自动多出斜杠，以及 POST 请求为什么不应依赖这个机制——301 重定向后方法可能变成 GET，请求体丢失。

路由设计应统一风格：要么全部带斜杠，要么全部不带。Django 管理后台与默认教程都带斜杠，项目内保持一致即可。`APPEND_SLASH` 不是「自动纠错」，它只处理 GET 场景下的路径补全，不能替代正确的路由定义。

### 3.6 命名空间

当多个应用有同名路由（如都用 `index`）时，用命名空间隔离：

```python
path("blog/", include(("blog.urls", "blog"), namespace="blog")),
path("shop/", include(("shop.urls", "shop"), namespace="shop")),
```

反向解析写 `reverse("blog:index")`，模板写 `{% url 'shop:index' %}`。命名空间的好处是「应用可插拔」：同一个应用挂到两个前缀下，也不会有名字冲突。代价是调用点必须带前缀，漏写在大型项目里很常见。

## 四、视图：函数与类

### 4.1 函数视图

函数视图是最直接的形态：

```python
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comment_set.filter(parent_comment__isnull=True)
    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
    })
```

`get_object_or_404` 把「查不到」转成 404，比手动 `try/except DoesNotExist` 简洁。视图的职责是「取参数、调模型、选模板、装上下文」，不应该在里面写复杂的 SQL 或大段业务规则；那些应下沉到模型方法或服务层。

### 4.2 类视图

类视图把「按方法分发」封装起来：

```python
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

@method_decorator(csrf_protect, name="dispatch")
class PostCreateView(View):
    def get(self, request):
        return render(request, "blog/post_form.html")

    def post(self, request):
        title = request.POST.get("title", "").strip()
        if not title:
            return render(request, "blog/post_form.html", {"error": "标题不能为空"})
        Post.objects.create(title=title, content=request.POST.get("content", ""))
        return redirect("post_list")
```

原料提到「类视图需通过 `as_view()` 转换为可调用视图」，这是类视图接入 URLconf 的唯一方式：

```python
path("post/new/", PostCreateView.as_view(), name="post_create"),
```

### 4.3 请求方法的分支

同一个 URL 同时处理展示与提交时，必须区分方法：

```python
def post_create(request):
    if request.method == "POST":
        # 处理表单
        ...
    else:
        # 展示空表单
        ...
```

只判断「有没有 POST 数据」是不够的：`request.POST` 在 `GET` 请求里是空字典，无法区分「GET」与「POST 了空表单」。用 `request.method` 判断，语义明确。

### 4.4 装饰器与访问控制

登录校验、权限校验通常用装饰器：

```python
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@permission_required("blog.change_post", raise_exception=True)
def post_edit(request, pk):
    ...
```

`login_required` 未登录时重定向到 `LOGIN_URL`，并在查询串里带上 `next`；`permission_required` 在 `raise_exception=True` 时返回 403，否则重定向到登录页。装饰器可以叠加，执行顺序是从下到上，因此「先登录再验权限」应把 `login_required` 放在最上面。

类视图的装饰要作用到方法上：

```python
from django.utils.decorators import method_decorator

@method_decorator(login_required, name="dispatch")
class DashboardView(View):
    ...
```

直接给类加普通函数装饰器不会生效，因为请求进入的是 `as_view()` 返回的函数，再由它调用 `dispatch`。

### 4.5 视图里不该做的事

- **不要直接拼 SQL**。ORM 已经处理了参数绑定与转义，手写 SQL 会重新引入注入风险。
- **不要在视图里做耗时任务**。发邮件、生成报表、调用外部接口应放到异步任务或后台线程，否则请求会一直占用连接。
- **不要把所有业务规则塞进视图**。视图应薄，规则放在模型方法或服务层，才能被多个入口复用。
- **不要返回裸字符串**。视图必须返回 `HttpResponse` 或其子类，返回 `str` 会报 `ValueError`。

## 五、模型与迁移

### 5.1 模型定义

原料给出的博客模型覆盖了三种关系：

```python
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

| 关系 | 字段 | 生成的表结构 | 说明 |
|---|---|---|---|
| 一对多 | `ForeignKey(User)` | `author_id` 列 | 多篇文章属于一个用户 |
| 一对多 | `ForeignKey(Category)` | `category_id` 列，可空 | `SET_NULL` 需配合 `null=True` |
| 多对多 | `ManyToManyField(Tag)` | 独立的中间表 | Django 自动建表 |
| 自关联 | `ForeignKey('self')` | 指向本表主键 | 评论的父子关系 |

原料中的 `Comment` 用 `parent_comment = models.ForeignKey('self', ...)` 表示「评论的回复」，这是自关联的典型用法。`on_delete` 是必填参数，常见取值：

| 取值 | 删除父对象时 | 适用 |
|---|---|---|
| `CASCADE` | 级联删除子对象 | 强依赖，如文章与评论 |
| `PROTECT` | 阻止删除，抛异常 | 有引用就不能删 |
| `SET_NULL` | 子对象外键置空 | 弱依赖，需 `null=True` |
| `SET_DEFAULT` | 置为默认值 | 需设置 `default` |
| `DO_NOTHING` | 不动子对象 | 由数据库约束兜底，慎用 |

### 5.2 字段选项

原料用一整节列了字段选项，核心的几个必须分清：

| 选项 | 作用层级 | 典型用法 |
|---|---|---|
| `null` | 数据库 | 该列是否允许 `NULL` |
| `blank` | 表单校验 | 是否允许提交空值 |
| `default` | 两者 | 未提供时的默认值，可调用对象 |
| `unique` | 数据库 | 唯一约束 |
| `db_index` | 数据库 | 建普通索引 |
| `choices` | 表单与校验 | 限定可选值 |
| `primary_key` | 数据库 | 自定义主键 |
| `verbose_name` | 后台与表单 | 人类可读名称 |
| `help_text` | 表单 | 输入提示 |
| `validators` | 表单 | 自定义校验函数 |
| `db_column` | 数据库 | 自定义列名 |

最容易混淆的是 `null` 与 `blank`：`null=True` 只影响数据库，`blank=True` 只影响表单校验。字符串字段通常用 `blank=True` 加空串，而不是 `null=True`，因为「空串」与「未知」在语义上不同，且空串可以避免 `NULL` 带来的三值逻辑。

### 5.3 迁移的三个命令

```bash
python manage.py makemigrations      # 根据模型差异生成迁移文件
python manage.py migrate             # 把迁移应用到数据库
python manage.py sqlmigrate blog 0001  # 查看某个迁移对应的 SQL
```

原料对迁移文件的解释值得记住：**迁移文件是 Python 脚本，不是 SQL 文件**。它包含 `CreateModel`、`AddField` 等操作描述，`migrate` 时由 Django 翻译成具体数据库的 SQL。`django_migrations` 表记录「哪些迁移已经应用」，所以重复执行 `migrate` 不会重复建表。

原料还解释了 `migrate` 输出中的顺序：`contenttypes` 先于 `auth`，因为用户认证依赖模型与内容类型；内置应用的迁移与自定义应用的 `0001_initial` 一起列出，`OK` 表示每个迁移执行成功。这个顺序由迁移文件的依赖声明决定，不是人为排列。

### 5.4 迁移冲突的成因

迁移冲突通常来自三种情况：

1. **多人同时生成迁移**。两个分支各自基于 `0001` 生成了 `0002`，合并后出现两个 `0002`，Django 提示「多个叶节点」。
2. **数据库与迁移记录不一致**。表已经手工建过，但 `django_migrations` 没有记录，`migrate` 再次建表时报「表已存在」。
3. **删除了迁移文件但数据库没回滚**。模型与迁移历史脱节，`makemigrations` 生成的差异与库中实际结构不符。

处理原则是「先看状态，再动数据」：

```bash
python manage.py showmigrations        # 查看每个迁移是否应用
python manage.py makemigrations --merge  # 合并多个叶节点
python manage.py migrate --fake-initial  # 表已存在时，只记录初始迁移
python manage.py migrate app 0001 --fake # 手工对齐记录，不执行 SQL
```

`--fake` 只改记录、不动数据库，属于「修复历史」而不是「修复结构」，必须在确认库中结构已经正确后使用。生产环境执行前应备份，并先在副本上演练。

### 5.5 Meta、模型方法与 Manager

模型的 `Meta` 内部类集中描述表级选项：

```python
class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "文章"
        verbose_name_plural = "文章"
        indexes = [models.Index(fields=["title", "created_at"])]
        constraints = [
            models.UniqueConstraint(fields=["title", "author"], name="uniq_title_author")
        ]

    def __str__(self):
        return self.title

    def is_editable_by(self, user):
        return user.is_staff or self.author_id == user.id
```

`ordering` 定义默认排序，会影响 `first()`、`last()` 与分页的稳定性；没有排序的分页可能在不同请求间重复或遗漏记录。`indexes` 与 `constraints` 会进入迁移，是数据库层的真实约束，不是应用层的「建议」。

模型方法适合放「只依赖本对象数据」的规则，例如「是否可编辑」「计算总价」。需要跨表、跨服务的规则，应放到服务层，避免模型变成什么都做的上帝对象。

自定义 Manager 可以封装常用查询：

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class Post(models.Model):
    objects = models.Manager()
    published = PublishedManager()
```

`Post.published.all()` 会自动带上 `is_published=True`。注意保留默认的 `objects`，否则后台、关联查询等依赖默认 Manager 的地方会出问题。

## 六、ORM 查询

### 6.1 QuerySet 的惰性

`Post.objects.all()` 不会立刻发 SQL，它返回一个 `QuerySet`，只有在被迭代、切片、`len()`、`list()`、`bool()` 时才求值。这意味着：

```python
qs = Post.objects.filter(is_published=True)
qs = qs.filter(author__username="alice")   # 仍然没有 SQL
for post in qs:                            # 这里才执行
    ...
```

惰性带来的好处是「可以链式拼接条件」，坏处是「以为执行了其实没有」。排查时可以用 `str(qs.query)` 查看即将执行的 SQL，或开启 `connection.queries` 记录已执行语句。原料在讲查询优化时明确建议用 `print(results.query)` 观察 ORM 生成的 SQL。

### 6.2 常用查询方法

| 方法 | 返回 | 说明 |
|---|---|---|
| `all()` | QuerySet | 全部记录 |
| `filter(**kwargs)` | QuerySet | 满足全部条件 |
| `exclude(**kwargs)` | QuerySet | 排除满足条件的记录 |
| `get(**kwargs)` | 单个对象 | 查不到或多于一条都抛异常 |
| `first()` / `last()` | 对象或 `None` | 按默认排序取首尾 |
| `exists()` | `bool` | 只查是否存在，比 `count()` 轻 |
| `count()` | `int` | 计数 |
| `order_by("field")` | QuerySet | 排序，`-field` 降序 |
| `values()` / `values_list()` | 字典/元组 | 只取指定列，减少对象构造 |
| `distinct()` | QuerySet | 去重 |

字段查询使用双下划线：

```python
Post.objects.filter(title__icontains="django")
Post.objects.filter(created_at__year=2025)
Post.objects.filter(category__name="技术文档")
Post.objects.filter(tags__name__in=["Python", "Django"])
Post.objects.exclude(author__isnull=True)
Post.objects.filter(pk__in=[1, 2, 3]).order_by("-created_at")
```

原料中的知识库示例用了 `title__iexact`、`title__icontains`、`category__name`、`tags__name`，分别对应「忽略大小写精确匹配」「忽略大小写包含」「跨外键」「跨多对多」。跨关系的双下划线会自动生成 `JOIN`，不需要手写关联条件。

### 6.3 Q 对象与逻辑组合

`filter` 的关键字参数之间是「与」，要实现「或」「非」必须用 `Q`：

```python
from django.db.models import Q

docs = KnowledgeDocument.objects.filter(
    Q(title__icontains="优化") | Q(content__icontains="索引")
)

docs = KnowledgeDocument.objects.filter(
    Q(category__name="技术文档") & ~Q(title__icontains="草稿")
)
```

`Q` 对象可以组合、取反、嵌套。原料给出的两个例子正是「或」与「与」的写法。注意 `filter(A, B)` 等价于 `filter(Q(A) & Q(B))`，但 `filter(Q(A) | Q(B))` 不能拆成两个 `filter`，因为两次 `filter` 的连接方式与一次「或」不同。

### 6.4 关联查询与 N+1

假设要展示文章列表及每篇的作者：

```python
posts = Post.objects.all()
for post in posts:
    print(post.author.username)   # 每篇一次查询
```

若列表有 $n$ 篇，就会执行 $1+n$ 次查询，这就是 N+1。解决办法是预加载：

```python
posts = Post.objects.select_related("author", "category")
posts = Post.objects.prefetch_related("tags", "comment_set")
```

| 方法 | 适用关系 | 实现 | 查询次数 |
|---|---|---|---|
| `select_related` | 外键、一对一 | SQL `JOIN` | 1 |
| `prefetch_related` | 多对多、反向外键 | 先查主表，再按 `IN` 查关联表，内存拼接 | 2 |

选择依据是关系类型：`ForeignKey` 用 `select_related`，`ManyToManyField` 与「一对多的反向」用 `prefetch_related`。用错不会报错，但可能仍然产生多次查询。原料在讲知识库查询优化时明确写了「使用 `select_related`、`prefetch_related` 预加载关联数据，避免 N+1 查询问题」。

### 6.5 聚合与注解

```python
from django.db.models import Count, Sum, Avg

# 每个分类下的文章数
Category.objects.annotate(post_count=Count("post"))

# 全站文章总数
Post.objects.aggregate(total=Count("id"))

# 每个作者的平均评论数
User.objects.annotate(avg_comments=Avg("post__comment__id"))
```

`aggregate` 返回一个字典，作用于整个 QuerySet；`annotate` 给每一行附加一个计算字段，返回 QuerySet。两者的区别是「一行结果」与「每行一个附加列」，混用会导致结果数量与预期不符。

### 6.6 更新与删除

```python
Post.objects.filter(pk=1).update(title="新标题")   # 直接 UPDATE，不触发 save()
post = Post.objects.get(pk=1)
post.title = "新标题"
post.save()                                        # 触发 save() 与信号
Post.objects.filter(is_published=False).delete()    # 批量删除
```

`update` 与 `save` 的差异不只是性能：`save` 会走模型的 `save()` 方法、触发 `pre_save`/`post_save` 信号、支持 `auto_now` 字段；`update` 直接生成 SQL，绕过这些逻辑。需要审计或时间戳自动更新时，不能用 `update` 替代 `save`。

## 七、模板：继承与上下文

### 7.1 模板查找顺序

`settings.py` 中的 `TEMPLATES` 决定模板从哪里找：

```python
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [...]},
}]
```

- `DIRS` 是项目级模板目录，优先查找。
- `APP_DIRS=True` 时，Django 还会在每个已注册应用的 `templates/` 下查找。
- 应用级模板建议放在 `应用名/templates/应用名/` 下，避免不同应用的同名模板互相覆盖。

原料排查 `TemplateDoesNotExist: base.html` 时，检查的正是这三件事：`DIRS` 是否包含模板目录、`APP_DIRS` 是否为 `True`、应用是否在 `INSTALLED_APPS` 中注册。三者缺一，模板都不会被找到。

### 7.2 继承与块

`base.html` 定义骨架与可替换区域：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}我的站点{% endblock %}</title>
</head>
<body>
  <header>{% block header %}<h1>站点标题</h1>{% endblock %}</header>
  <main>{% block content %}{% endblock %}</main>
  <footer>{% block footer %}版权所有{% endblock %}</footer>
</body>
</html>
```

子模板继承并覆盖：

```html
{% extends "base.html" %}
{% block title %}文章列表{% endblock %}
{% block content %}
  {% for post in posts %}
    <article>
      <h2><a href="{% url 'post_detail' pk=post.pk %}">{{ post.title }}</a></h2>
      <p>{{ post.content|truncatechars:80 }}</p>
    </article>
  {% empty %}
    <p>暂无文章</p>
  {% endfor %}
{% endblock %}
```

规则有三条：`extends` 必须是子模板的第一个标签；子模板只能覆盖父模板中已定义的 `block`；父模板的 `block` 内可以写默认内容。原料把 `{% extends "base.html" %}` 放在 `form.html` 第一行，正是这个要求。

### 7.3 变量、过滤器与标签

| 语法 | 作用 | 示例 |
|---|---|---|
| `{{ var }}` | 输出变量 | `{{ post.title }}` |
| `{{ var|filter }}` | 过滤器 | `{{ post.content|truncatechars:80 }}` |
| `{% for x in xs %}` | 循环 | 可配 `{% empty %}` |
| `{% if cond %}` | 条件 | 支持 `and`、`or`、`not` |
| `{% url 'name' %}` | 反向解析 | `{% url 'post_detail' pk=post.pk %}` |
| `{% static 'path' %}` | 静态文件 URL | 需 `{% load static %}` |
| `{% include 'x.html' %}` | 嵌入片段 | 适合页头、页脚 |

模板中的变量查找顺序是「字典键 → 属性 → 列表索引 → 方法调用」，找不到时返回空字符串而不是报错。这个设计让模板对缺失字段更宽容，但也掩盖了拼写错误：`{{ post.titel }}` 不会抛异常，只会显示空白。调试时应先确认上下文里到底有什么。

### 7.4 自动转义

Django 默认对变量做 HTML 转义，`<script>` 会变成 `&lt;script&gt;`，这是防 XSS 的第一道防线。确实需要输出 HTML 时用 `|safe`，但只对可信内容使用；用户输入加 `|safe` 等于主动打开 XSS 入口。`{% autoescape off %}` 的作用范围更大，应尽量避免。

## 八、表单与 CSRF

### 8.1 一个可提交的表单

```html
<form method="post" action="{% url 'post_create' %}">
  {% csrf_token %}
  <label>标题 <input type="text" name="title"></label>
  <label>正文 <textarea name="content"></textarea></label>
  <button type="submit">发布</button>
</form>
```

`{% csrf_token %}` 会输出一个隐藏字段，值是本次会话的 CSRF token。Django 的 `CsrfViewMiddleware` 在 POST 时校验「表单里的 token」与「Cookie 里的 token」是否匹配；缺失或不匹配返回 403。原料在多个 Django 表单示例里都保留了这一行，说明它不是可选装饰。

CSRF 的原理是「攻击者可以伪造请求，但读不到目标站点的 Cookie」。token 放在页面里，攻击者的跨站表单无法提前知道，于是伪造的 POST 缺少正确 token 而被拒绝。GET 请求不需要 token，因为它不应产生副作用；把「删除」写成 GET 链接，既违反语义，也绕过了 CSRF 防护。

### 8.2 Form 与 ModelForm

手写 `request.POST.get` 适合简单场景，字段一多就需要表单类：

```python
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "tags"]

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 2:
            raise forms.ValidationError("标题至少两个字符")
        return title
```

视图中：

```python
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form})
```

`is_valid()` 会依次执行字段类型转换、内置校验、`clean_<field>` 方法、`clean()` 方法，全部通过后 `cleaned_data` 才是可信数据。直接使用 `request.POST` 跳过了这一整套校验，是很多脏数据进入数据库的起点。

### 8.3 GET 与 POST 的分工

| 维度 | GET | POST |
|---|---|---|
| 参数位置 | URL 查询串 | 请求体 |
| 幂等性 | 是 | 通常否 |
| 可否缓存 | 可以 | 不可以 |
| 长度限制 | 受 URL 长度限制 | 受服务器配置限制 |
| 典型用途 | 查询、分页、筛选 | 创建、修改、删除 |

原料在 HTTP 章节把「GET 与 POST 的区别」列为必背点，并指出 POST 更适合提交敏感或大量数据。Django 的表单默认 `method="post"`，不是为了「安全加密」，而是为了语义与幂等性；真正的机密性要靠 HTTPS。

## 九、常见报错的定位顺序

### 9.1 NoReverseMatch

现象：模板渲染或 `reverse()` 时抛 `NoReverseMatch`。原因按概率排序：

1. **名字拼错**。`reverse("post-detail")` 与 `name="post_detail"` 不一致。
2. **参数缺失或多余**。`post_detail` 需要 `pk`，调用时没传。
3. **命名空间缺失**。路由在 `include(..., namespace="blog")` 下，反向解析要写 `blog:post_detail`。
4. **应用未注册**。`include` 的模块没有被加载，路由根本不存在。

定位顺序是「先看名字，再看参数，再看命名空间」，因为名字错误最常见，参数错误次之，命名空间只在大型项目里出现。

### 9.2 TemplateDoesNotExist

现象：`TemplateDoesNotExist: base.html`。按以下顺序检查：

1. 模板文件是否真的存在，路径与大小写是否一致。
2. `TEMPLATES["DIRS"]` 是否包含项目级模板目录。
3. `APP_DIRS` 是否为 `True`，应用是否在 `INSTALLED_APPS`。
4. 应用级模板是否放在 `应用名/templates/应用名/` 下。
5. `extends` 中的路径是否相对于模板根目录，而不是相对于当前文件。

原料给出的排查步骤与这个顺序一致：先看 `TEMPLATES` 配置，再验证文件存在性，最后修正 `extends` 路径。若 `base.html` 放在项目级 `templates/`，子模板写 `{% extends "base.html" %}`；若放在应用级，则要保证目录层级正确。

### 9.3 迁移冲突与表不存在

| 报错 | 原因 | 处理 |
|---|---|---|
| `Table 'x' already exists` | 表已建，迁移记录没有 | `migrate --fake-initial` 或手工对齐 |
| `no such table` | 迁移没跑，或跑到了别的库 | `showmigrations` 后 `migrate` |
| `Multiple leaf nodes` | 两个分支各生成一个迁移 | `makemigrations --merge` |
| `InconsistentMigrationHistory` | 依赖顺序与记录矛盾 | 查 `django_migrations`，评估 `--fake` |

迁移问题的核心是「模型、迁移文件、数据库」三者是否一致。先看 `showmigrations` 的勾选状态，再看 `sqlmigrate` 生成的 SQL，最后才考虑 `--fake`。直接删库重来在开发环境可行，在生产环境等于数据丢失。

### 9.4 其他高频错误

- **`ModuleNotFoundError: No module named 'views'`**：在项目级 `urls.py` 导入了项目根的 `views`，应改为 `include("app.urls")` 或 `from app import views`。
- **`IndentationError`**：Python 对缩进敏感，复制代码时混入空格与制表符会直接报错。
- **`OperationalError: (1045, "Access denied")`**：数据库账号、口令或主机权限不对，与 ORM 无关。
- **`DisallowedHost`**：`ALLOWED_HOSTS` 未包含访问域名，开发环境可临时加 `localhost`，生产环境应显式配置。
- **静态文件 404**：开发环境需配置 `STATIC_URL` 与 `STATICFILES_DIRS`，生产环境由 Nginx 或白名单服务接管。

## 十、易错点

1. **把 MTV 的 View 当成 MVC 的 View**。Django 的 View 是控制器，Template 才是表现层。
2. **在项目根目录找 `views.py`**。视图属于应用，项目级 `urls.py` 应通过 `include` 分发。
3. **`urlpatterns` 漏逗号**。报错可能显示「括号未关闭」，实际是列表元素没有分隔。
4. **路径顺序颠倒**。通配路由放在具体路由之前，会把具体路径吞掉。
5. **硬编码 URL**。路径一改，所有 `<a href>` 都要改；应使用 `{% url %}` 与 `reverse`。
6. **`get()` 当 `filter()` 用**。`get()` 查不到抛 `DoesNotExist`，多于一条抛 `MultipleObjectsReturned`。
7. **在循环里查关联**。这是 N+1 的典型形态，应使用 `select_related` 或 `prefetch_related`。
8. **`null` 与 `blank` 混用**。前者管数据库，后者管表单，字符串字段优先用空串。
9. **迁移文件当 SQL 改**。迁移是 Python 脚本，手改容易与模型脱节；需要自定义 SQL 时用 `RunSQL`。
10. **模板变量拼错**。Django 不报错，只显示空白；调试时先打印上下文。
11. **POST 表单漏 `{% csrf_token %}`**。表现为 403，而不是表单校验失败。
12. **用户输入加 `|safe`**。等于关闭自动转义，XSS 风险直接引入。

## 十一、小结

Django 的学习曲线主要不在语法，而在「一条请求到底经过哪些层」。把下面的对应关系记住，多数问题都能定位：

| 现象 | 先查 | 再查 |
|---|---|---|
| 页面 404 | `urlpatterns` 是否有匹配 | 路径顺序、斜杠、转换器 |
| `NoReverseMatch` | 路由名 | 参数、命名空间 |
| `TemplateDoesNotExist` | 文件是否存在 | `DIRS`、`APP_DIRS`、应用注册 |
| 数据没更新 | 是否调用了 `save` / `update` | 事务是否提交 |
| 查询很慢 | 是否 N+1 | 索引、`select_related` |
| 表单 403 | `{% csrf_token %}` | Cookie、中间件 |
| 表不存在 | `showmigrations` | `migrate`、数据库配置 |

MTV 的分工可以压成一句话：**URL 决定「找谁」，View 决定「做什么」，Model 决定「数据从哪来」，Template 决定「长什么样」**。四者各守边界，项目才能在小规模时简单、大规模时可维护。
