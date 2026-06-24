# Yuan's Digital Library

Hugo + hugo-book 主题，部署于 GitHub Pages。

## 上传书籍后自检

| # | 症状 | 根因 | 修复 |
|---|------|------|------|
| 1 | KaTeX 公式不渲染 | `<script>` 内联 `$$` 被 Hugo 模板吞掉 | KaTeX 初始化放独立 `.js` 文件 |
| 2 | 黑夜模式字体色不变 | `BookTheme=auto` 缺少 `theme-auto` mixin | `_custom.scss` 补全 `theme-light/dark/auto` |
| 3 | 中文书字体/间距异常 | `_index.md` 有孤立 `</div>` | 删除多余闭合标签 |
| 4 | 目录链接不可点击 | TOC 用纯文本表格 | 改用 `- [标题](chXX.md)` 列表 |
| 5 | 侧栏无分区层级 | `books/` 下书是扁平的 | 每书 `_index.md` 加 `categories: ["分类"]` |
| 6 | 页脚双份导航 | `docs/footer` + `inject/footer` 并存 | 删 `post-prev-next` 调用，只留 inject |

## 每次上传改动的文件

| 概率 | 文件 | 改什么 |
|------|------|--------|
| 100% | `content/books/<book>/_index.md` | 写入封面内容 + 目录链接 |
| 100% | `content/books/<book>/ch*.md` | 章节文件 |
| 30% | `assets/_custom.scss` | 新增书特有样式 |
| 10% | `layouts/` | 新增 shortcode 或 partial |

## 关键架构规则

**Hugo 模板**：`$` 和 `$$` 在 `.html` 模板的 `<script>` 标签内会被 Hugo 解析。含 `$` 的 JS 一律放 `static/*.js`。

**Goldmark**：`unsafe = true`（raw HTML 穿透），`passthrough` 保留 `$`/`$$` 给 KaTeX。需显式启用 `[markup.goldmark.extensions.footnote]`。

**BookTheme**：`_custom.scss` 内必须定义 `theme-light`、`theme-dark`、`theme-auto` 三个 mixin（主题只提供 `theme-contrast-*` 等，不提供无前缀版本）。

**内容规范**：
- 书封面 TOC 必须用 `- [标题](file.md)`，禁止纯文本表格
- 章节文件用 `weight` 控制排序（升序）
- 禁止孤立 HTML 标签（`</div>` 无对应开标签）
