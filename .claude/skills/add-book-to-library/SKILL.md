---
name: add-book-to-library
description: |
  将 PDF 书籍转换为 MkDocs 页面并加入个人数字图书馆。完整流程：PDF 提取（MinerU VLM）→ Markdown 清洗 → 章节拆分 → 格式化 → 导航与首页接入。
  触发词：add this book, 加入图书馆, 添加书籍, 把 PDF 转成网页, 把书加入图书馆, convert PDF to library, add book to library, 个人图书馆, digital library.
---

# Add Book to Library

将一本 PDF 学术书籍加入已有的 MkDocs 数字图书馆。

## 上传后自检清单

每本书加入导航和首页后，`mkdocs build` 前逐项检查：

| # | 检查项 | 症状 | 修复 |
|---|--------|------|------|
| 1 | `:material-xxx:` 图标显示为原始文本 | 首页/分区页卡片图标不显示 | `mkdocs.yml` 需启用 `pymdownx.emoji` (twemoji) |
| 2 | 点击分区/分类 tab 直接跳到第一本书 | 无中间过渡页 | 该层级需 `index.md` 作为 nav 第一项 |
| 3 | snippet 文件中的 `#` 标题渲染到页面 | 书籍封面出现无关 H1 标题 | snippet 用 `<!-- -->` 注释，不用 `#` / `##` |
| 4 | 新建分类后点击分类跳转错误 | 404 或跳到其他书 | `mkdocs.yml` nav 中该分类第一项加 `books/<cat>/index.md` |
| 5 | 新增书籍在分区页无入口 | 用户找不到新书 | `docs/books/<category>/index.md` 添加对应卡片 |
| 6 | 新增分区在首页无入口 | 首页没有该分区卡片 | `docs/books/index.md` 添加分区卡片 |

### 每次上传后需更新的文件

| 概率 | 文件 | 改什么 |
|------|------|--------|
| 100% | `mkdocs.yml` nav | 插入书名 + 章节列表 |
| 90% | `docs/books/<category>/index.md` | 添加新书卡片 |
| 30% | `docs/books/index.md` | 新分类时添加分区卡片 |
| 20% | `docs/books/<category>/index.md` | 新建（新分类时） |
| 10% | `docs/snippets/abbreviations.md` | 新领域术语 |
