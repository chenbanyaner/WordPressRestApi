

# WordPress-Rest-API-Python-Library

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个用 Python 编写的轻量级 WordPress REST API 封装库。旨在简化对 WordPress 站点资源（文章、页面、分类、标签、用户、评论、媒体等）的自动化管理操作。

## 🌟 项目亮点

- **面向对象设计**：结构清晰，易于扩展。
- **功能全面**：支持用户 (User)、文章 (Post)、页面 (Page)、分类 (Category)、标签 (Tag)、媒体 (Media) 和评论 (Comment)。（支持 ACF 自定义类型和分类法）
- **批量处理**：集成 WordPress Batch API，大幅提高数据操作效率。
- **多线程加速**：媒体上传和删除支持多线程操作，适合处理大量素材。

## 🚀 快速开始

## 创建连接

```python
from wordpressrestapi import Connect

connect = Connect(
	site_url="https://example.com", 
    username="your username", 
    app_password="your app password"
)
```

## 管理文章 （Post）

参考文档：https://developer.wordpress.org/rest-api/reference/posts/

支持传递 fields，以过滤返回字段

支持 acf 文章类型

### 1. 获取所有文章

```python
# 获取所有文章
response = connect.post.fetch_all()
print(response.json())

# 获取自定义文章类型（ACF）
response = connect.post.fetch_all(post_type="book")
print(response.json())

# 获取所有已发布的文章
response = connect.post.fetch_all(status="publish")
print(response.json())

# 获取指定ids的文章
response = connect.post.fetch_all(include=[1, 2, 3])
print(response.json())

# 指定返回结果包含的字段
response = connect.post.fetch_all(fields="id,title,content,acf")
print(response.json())
```

### 2. 获取指定某篇文章

```python
response = connect.post.fetch_one(1)
print(response.json())
```

### 3. 创建文章

```python
# 创建普通文章
response = connect.post.create(title="test title", status="publish", content="test content")
print(response.json())

# 创建定时发布文章（2026-04-29 12:00:00）
from datetime import datetime

date = datetime(year=2026, month=4, day=29, hour=12, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%S")
response = connect.post.create(title="test title", status="publish", content="test content", fields="id,title,content,acf", date=date)
print(response.json())

# 创建自定义类型文章（ACF）
acf = {
    "book_name": "test book",
    "book_author": "test author",
    "book_price": 199
}
response = connect.post.create(title="test title", slug="test", post_type="book", status="publish", acf_data=acf)
print(response.json())
```

### 4. 批量创建文章

```python
# 批量创建普通文章
posts = [
    {
        "title": "title 1",
        "content": "body 1",
        "status": "publish",
    },
    {
        "title": "title 2",
        "content": "body 2",
        "status": "publish",
    }
]
response = connect.post.create_batch(posts)
print(response.json())

# 批量创建自定义文章类型（ACF）
posts = [
    {
        "title": "title 1",
        "content": "body 1",
        "status": "publish",
        "acf": {
            "book_name": "test book 1",
            "book_author": "test author 1",
            "book_price": 199
        }
    },
    {
        "title": "title 2",
        "content": "body 2",
        "status": "publish",
        "acf": {
            "book_name": "test book 2",
            "book_author": "test author 2",
            "book_price": 199
        }
    }
]
response = connect.post.create_batch(posts, post_type="book")
print(response.json())
```

### 5. 更新文章

```python
# 更新普通文章
response = connect.post.update(1, title="updated title", content="updated body")
print(response.json())

# 更新自定义文章类型（ACF）
acf_data = {
    "book_name": "test book updated",
    "book_author": "test author updated",
    "book_price": 19.9
}
response = connect.post.update(133, title="updated title", content="updated body", post_type="book", acf_data=acf_data)
print(response.json())
```

### 6. 批量更新文章

```python
# 批量更新普通文章
posts = [
    {"id": 1, "data": {"title": "updated title 1", "content": "updated content 1"}},
    {"id": 2, "data": {"title": "updated title 2", "content": "updated content 2"}}
]
response = connect.post.update_batch(posts)
print(response.json())

# 批量更新自定义文章类型（ACF）
posts = [
    {
        "id": 1,
        "data":
        {
            "title": "updated title 1",
            "content": "updated content 1",
            # ...
            "acf": {
                "book_name": "test book name 1",
                # ...
            }
        }
    },
    {
        "id": 2,
        "data":
        {
            "title": "updated title 2",
            "content": "updated content 2",
            # ...
            "acf": {
                "book_name": "test book name 2",
                # ...
            }
        }
    },
]
response = connect.post.update_batch(posts, post_type="book")
print(response.json())
```

### 7. 删除文章

```python
# 删除普通文章
response = connect.post.delete(1)
print(response.json())

# 强制删除，不进入回收站
response = connect.post.delete(1, force=True)
print(response.json())

# 删除自定义文章类型（ACF）
response = connect.post.delete(1, post_type="book")
print(response.json())

# 强制删除，删除自定义文章类型（ACF），不进入回收站
response = connect.post.delete(1, post_type="book", force=True)
print(response.json())
```

### 8. 批量删除文章

```python
# 批量删除普通文章
ids = [1, 2, 3]
response = connect.post.delete_batch(ids)
print(response.json())

# 批量删除自定义类型文章（ACF）
ids = [1, 2, 3]
response = connect.post.delete_batch(ids, post_type="book")
print(response.json())
```

## 管理页面 （Page）

参考文档：https://developer.wordpress.org/rest-api/reference/pages/

支持传递 fields，以过滤返回字段

### 1. 获取所有页面

```python
response = connect.page.fetch_all()
print(response.json())
```

### 2. 获取指定页面

```python
response = connect.page.fetch_one(1)
print(response.json())
```

### 3. 创建页面

```python
response = connect.page.create(title="page title", content="page content")
print(response.json())
```

### 4. 批量创建页面

```python
pages = [
    {
        "title": "page title 1",
        "content": "page body 1",
        "status": "publish",
    },
    {
        "title": "page title 2",
        "content": "page body 2",
        "status": "publish",
    }
]
response = connect.page.create_batch(pages)
print(response.json())
```

### 5. 更新页面

```python
response = connect.page.update(1, title="updated page title", content="updated page content")
print(response.json())
```

### 6. 批量更新页面

```python
pages = [
    {'id': 1, 'data': {'title': 'Updated Page 1', 'content': 'Updated content 1'}},
    {'id': 2, 'data': {'title': 'Updated Page 2', 'content': 'Updated content 2'}},
]
response = connect.page.update_batch(pages)
print(response.json())
```

### 7. 删除页面

```python
response = connect.page.delete(150)
print(response.json())
```

### 8. 批量删除页面

```python
ids = [1, 2]
response = connect.page.delete_batch(ids, force=False)
print(response.json())
```



## 分类管理 （Category）

参考文档：https://developer.wordpress.org/rest-api/reference/categories/

支持传递 fields，以过滤返回字段

支持 acf 分类法

### 1. 获取所有分类

```python
# 获取所有分类
response = connect.category.fetch_all()
print(response.json())

# 获取自定义分类法（ACF）所有分类
# 举例：分类法关键字为 book_categories
response = connect.category.fetch_all(taxonomy="book_categories")
print(response.json())
```

### 2. 获取指定分类

```python
# 获取指定分类
response = connect.category.fetch_one(1)
print(response.json())

# 获取自定义分类法（ACF）指定分类
# 举例：我的分类法关键字为 book_categories
response = connect.category.fetch_one(14, taxonomy="book_categories")
print(response.json())
```

### 3. 创建分类

```python
# 创建普通分类
response = connect.category.create(name="category")
print(response.json())

# 创建自定义分类法分类
# 举例：分类法关键字为 book_categories
response = connect.category.create(name="category", taxonomy="book_categories")
print(response.json()) 
```

### 4. 批量创建分类

```python
# 批量创建普通分类
categories = [
    {"name": "category 1"}, 
    {"name": "category 2"}
]
response = connect.category.create_batch(categories)
print(response.json()) 

# 批量创建自定义分类法分类
categories = [
    {"name": "stroy 1"}, 
    {"name": "stroy 2"}
]
response = connect.category.create_batch(categories, taxonomy="book_categories")
print(response.json()) 

```

### 5. 更新分类

```python
# 更新普通分类
response = connect.category.update(1, name="updated category")
print(response.json())

# 更新自定义分类法分类
response = connect.category.update(1, name="updated category", taxonomy="book_categories")
print(response.json())
```

### 6. 批量更新分类

```python
# 更新分类
categories = [
    {"id": 1, "data": {"name": "category 1 updated"}},
    {"id": 2, "data": {"name": "category 2 updated"}}
]
response = connect.category.update_batch(categories)
print(response.json()) 

# 更新自定义分类法分类
categories = [
    {"id": 1, "data": {"name": "category 1 updated"}},
    {"id": 2, "data": {"name": "category 2 updated"}}
]
response = connect.category.update_batch(categories, taxonomy="book_categories")
print(response.json()) 
```

### 7. 删除分类

```python
# 删除普通分类
response = connect.category.delete(1)
print(response.json())

# 删除自定义分类法分类
response = connect.category.delete(1, taxonomy="book_categories")
print(response.json())
```

### 8. 批量删除分类

```python
# 批量删除分类
ids = [1, 2]
response = connect.category.delete_batch(ids)
print(response.json())

# 批量删除自定义分类法分类
ids = [1, 2]
response = connect.category.delete_batch(ids, taxonomy="book_categories", force=True)
print(response.json()) 
```



## 标签管理 （Tag）

参考文档：https://developer.wordpress.org/rest-api/reference/tags/

支持传递 fields，以过滤返回字段

### 1. 获取所有标签

```python
# 获取所有标签
response = connect.tag.fetch_all()
print(response.json())
```

### 2. 获取指定标签

```python
# 获取指定标签
response = connect.tag.fetch_one(6)
print(response.json())
```

### 3. 创建标签

```python
# 创建标签
response = connect.tag.create("tag 1", "tag-1")
print(response.json())
```

### 4. 批量创建标签

```python
# 批量创建标签
tags = [
  {"name": "tag 1", "slug": "tag-1"},
  {"name": "tag 2", "slug": "tag-2"},
]
response = connect.tag.create_batch(tags)
print(response.json())
```

### 5. 更新标签

```python
# 更新标签
response = connect.tag.update(1, name="updated tag")
print(response.json())
```

### 6. 批量更新标签

```python
tags = [
  {"id": 1, "data": {"name": "tag 1 updated", "slug": "tag-1-updated"}},
  {"id": 2, "data": {"name": "tag 2 updated", "slug": "tag-2-updated"}},
]
response = connect.tag.update_batch(tags)
print(response.json())
```

### 7. 删除标签

```python
# 删除标签
response = connect.tag.delete(1)
print(response.json())
```

### 8. 批量删除标签

```python
ids = [1, 2]
response = connect.tag.delete_batch(ids, force=True)
print(response.json())
```

## 媒体管理 （Media）

参考文档：https://developer.wordpress.org/rest-api/reference/media/

支持传递 fields，以过滤返回字段

### 1. 获取所有媒体

```python
# 获取所有媒体
response = connect.media.fetch_all()
print(response.json())
```

### 2. 获取指定媒体

```python
# 获取指定媒体
response = connect.media.fetch_one(1)
print(response.json())
```

### 3. 上传媒体

```python
# 创建媒体
results = connect.media.upload(file_path, alt_text="test alt")
print(results)
```

### 4. 批量上传媒体

```python
medias = [
    {"file_path": file_path_1, "data": {"alt_text": "text 1"}},
    {"file_path": file_path_2, "data": {"alt_text": "text 2"}},
    # ...
]
results = connect.media.upload_batch(medias, max_workers=5)
print(results)
```

你也可以使用循环处理方式：

```python
medias = [
    {"file_path": file_path_1, "data": {"alt_text": "text 1"}},
    {"file_path": file_path_2, "data": {"alt_text": "text 2"}},
    # ...
]

results = []
for media in medias:
    res = connect.media.upload(media["file_path"], **media["data"])
    results.append(res)
print(results)
```

### 5. 更新媒体

```python
# 更新媒体
response = connect.media.update(1, title="updated title", alt_text="updated alt text")
print(response.json())
```

### 6. 批量更新媒体

```python
medias = [
    {"id": 1, "data": {"alt_text": "text 1"}},
    {"id": 2, "data": {"alt_text": "text 2"}},
]
results = connect.media.update_batch(medias)
print(results)
```



### 7. 删除媒体

```python
# 删除媒体
response = connect.media.delete(1)
print(response.json())
```

### 8. 批量删除媒体

```python
ids = [1, 2]
results = connect.media.delete_batch(ids)
print(results)
```

## 评论管理 （Comment）

参考文档：https://developer.wordpress.org/rest-api/reference/comments/

支持传递 fields，以过滤返回字段

### 1. 获取所有评论

```python
# 获取所有评论
response = connect.comment.fetch_all()
print(response.json())
```

### 2. 获取指定评论

```python
# 获取指定评论
response = connect.comment.fetch_one(1)
print(response.json())
```

### 3. 发布评论

```python
# 发布评论
response = connect.comment.create(1, author_name="test author", author_email="test@example.com", author_url="example.com", content="test comment")
print(response.json())
```

### 4. 更新评论

```python
# 更新评论
response = connect.comment.update(1, content="updated comment")
print(response.json())
```

### 5. 删除评论

```python
# 删除评论
response = connect.comment.delete(1)
print(response.json())
```

## 管理用户

参考文档：https://developer.wordpress.org/rest-api/reference/users/

支持传递 fields，以过滤返回字段

支持 acf 文章类型

### 1. 获取所有用户

```python
# 获取所有用户
response = connect.user.fetch_all()
print(response.json())
```

### 2. 获取指定用户

```python
response = connect.user.fetch_one(id=1)
print(response.json())
```

### 3. 创建用户

```python
response = connect.user.create(username="test user", password="123456", email="test@example.com")
print(response.json())
```

### 4. 批量创建用户

```python
users = [
    {"username": "test user 1", "password": "123456", "email": "test1@example.com"},
    {"username": "test user 2", "password": "123456", "email": "test2@example.com"},
]
response = connect.user.create_batch(users)
print(response.json())
```

### 5. 更新用户

```python
response = connect.user.update(1, nickname="test nickname")
print(response.json())
```

### 6. 批量更新用户

```python
users = [
    {"id": 7, "data": {"nickname": "test user 7"}},
    {"id": 8, "data": {"nickname": "test user 8"}},
]

response = connect.user.update_batch(users)
print(response.json())
```

### 7. 删除用户

```python
# 删除普通文章
response = connect.user.delete(2)
print(response.json())
```

### 8. 批量删除用户

```python
ids = [2, 3, 4]
response = connect.user.delete_batch(ids)
print(response.json())
```

## 📦 进阶：批量处理 (Batch)

由于 WordPress REST API 默认单次 Batch 请求上限为 **25** 个条目，如果你需要处理大量数据，建议参考以下分块（Chunking）调用方式：

```python
# 准备大量用户数据
users_to_create = [
    {"username": f"user_{i}", "email": f"user_{i}@example.com", "password": "StrongPassword123!"}
    for i in range(1, 101)
]

CHUNK_SIZE = 25

# 分块请求
for i in range(0, len(users_to_create), CHUNK_SIZE):
    chunk = users_to_create[i : i + CHUNK_SIZE]
    connect.user.create_batch(chunk)
```

---

## 🐾 作者

我是一名**健身教练**，目前正在自学 Python 和 Web 开发。这个项目是我在做拜拜肉博客时的副产品。

- **拜拜肉**: [拜拜肉.com](https://www.xn--ptua509t.com/)
- **Pet**: Buffer (一只可爱的蜗牛 🐌)

----

## ☕ 请我喝杯咖啡

如果你觉得这个库帮到了你，请我喝杯咖啡呗 ～

|                 微信支付                  |                  支付宝                   |
| :---------------------------------------: | :---------------------------------------: |
| <img src="https://github.com/chenbanyaner/WordPressRestApi/raw/master/asserts/qr2.png" width="200"> | <img src="https://github.com/chenbanyaner/WordPressRestApi/raw/master/asserts/qr1.png" width="200"> |
