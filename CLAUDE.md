# Yuan's Digital Library

MkDocs Material 个人数字图书馆，部署于 GitHub Pages。

## 上传书籍后自检

| # | 检查 | 症状 | 修复 |
|---|------|------|------|
| 1 | 图标 `:material-xxx:` 显示为文本 | 卡片图标不渲染 | `mkdocs.yml` 需 `pymdownx.emoji` (twemoji) |
| 2 | 点击分区 tab 直接跳书 | 无中间过渡 | nav 该层级第一项加 `index.md` |
| 3 | snippet `#` 标题污染页面 | 无关 H1 出现 | snippet 用 `<!-- -->` 不用 `#` |
| 4 | 新分类跳转 404 | 点击无效 | nav 第一项加 `books/<cat>/index.md` |
| 5 | 新书无入口 | 分区页找不到 | `docs/books/<category>/index.md` 加卡片 |
| 6 | 新分区首页无入口 | 首页找不到 | `docs/books/index.md` 加分区卡片 |

### 每次上传改动的文件

| 概率 | 文件 |
|------|------|
| 100% | `mkdocs.yml` nav |
| 90% | `docs/books/<category>/index.md` |
| 30% | `docs/books/index.md` |
| 20% | `docs/books/<category>/index.md`（新建） |
| 10% | `docs/snippets/abbreviations.md` |

## 导航设计

`navigation.indexes` + `navigation.prune` + `navigation.tabs`：每层 nav 第一项必须是 `index.md`，否则点击直接跳第一个子页面。
