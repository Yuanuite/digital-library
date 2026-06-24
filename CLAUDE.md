# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目本质

**Hugo 静态站点** — 个人数字图书馆，部署到 GitHub Pages。无 build 系统（Hugo 本身即构建器），内容为 Markdown + KaTeX + pseudocode.js。

## 站点架构

```
hugo.toml                  # Hugo 配置（hugo-book 主题）
content/                   # 所有内容页（Markdown）
  _index.md                # 首页
  books/<category>/<slug>/ # 书籍（_index.md 封面 + ch*.md 章节）
  notes/                   # 笔记
  papers/                  # 论文
  reference/               # 参考元素模板
layouts/                   # 覆写模板
  _shortcodes/             # solution / definition / theorem / caption 等
  _partials/docs/          # 侧栏菜单（含 theme-toggle 按钮）、head 注入
static/                    # JS/CSS/字体（KaTeX、pseudocode.js）
assets/_custom.scss        # 全局自定义样式
themes/hugo-book/          # Git submodule
```

## 关键设计约束

- **KaTeX** — `static/katex/` 本地托管，`auto-render.min.js` 处理 `$...$` 行内和 `$...$` 块级公式
- **pseudocode.js** — `<pre class="pseudocode">` + `\begin{algorithm}` 语法
- **暗色模式** — `html[data-theme="dark"]` CSS 选择器（特异性 0,1,1，覆盖主题 `:root`），`theme-toggle.js` 持久到 localStorage，`head.html` 内联脚本防闪烁
- **解答块** — `{{</* solution */>}}` shortcode，非 `<div>` 裸写
- **表格标题** — `{{</* caption */>}}` shortcode
- **章节标题** — `#` 为章标题，`##` 为节标题
- **hugo.toml** — `unsafe = true` 允许 HTML 混排，`uglyurls = true` 生成 `.html` 路径

## scripts/ 中的工具

内容处理脚本（格式无关，Hugo 和 MkDocs 通用）：
- `clean_markdown.py` — LaTeX 空白修复、去页眉/脚注
- `clean_epub.py` — EPUB 版权页清理
- `split_chapters.py` — 按 `# Chapter` 边界拆分
- `fix_double_question.py` / `fix_dq_final.py` — 双问号修复
- `migrate_to_hugo.py` — MkDocs→Hugo 迁移（已完成，保留参考）

## 添加书籍流程

1. 将 PDF/EPUB 放入项目根目录（不入库，gitignore `pdfs/`）
2. 提取为 Markdown（MinerU VLM / pandoc）
3. 运行 `scripts/clean_markdown.py` 清洗
4. 按章节拆分到 `content/books/<category>/<slug>/`
5. 格式化：封面 `_index.md`、算法、符号表、术语索引
6. 更新 `content/_index.md` 首页书架
7. `hugo serve` 预览 → push → CI 自动部署

## 通用原则

**奥卡姆剃刀（精简化代码）** — 任何改动尽可能小：能改一行不改两行，能复用不新建，能局部修改不重构。目标是解决当前问题，不顺便做"优化"。

**Hugo 主题覆盖** — 修改主题功能时，一律用项目级文件覆盖，不动子模块 `themes/hugo-book/`。优先级：`assets/` > `layouts/` > `i18n/` > CI deploy.yml patch。

**暗色模式 CSS 特异性** — 新增任何暗/亮双模式样式时，选择器必须写 `html[data-theme="dark"]` 而非 `[data-theme="dark"]`。后者特异性 (0,1,0) 与主题 `:root` 相同，主题后加载会覆盖自定义变量。加 `html` 前缀 → (0,1,1) 碾压主题。

**colorScheme 同步** — 新增涉及暗/亮切换的 JS 时，设置 `data-theme` 的同时必须设 `document.documentElement.style.colorScheme = t`，否则原生控件（滚动条、表单、`<select>`）不跟随。head 内联防闪烁脚本也要同步。

**head 防闪烁** — 新增依赖 localStorage 的 UI 状态时，必须在 `layouts/_partials/docs/inject/head.html` 加同步内联脚本，放在 `<link>` 之前，避免页面渲染后再切换导致闪烁。

## fix 流程
1. fix 之后需要询问用户是否 push
2. fix、push、添加内容等简单操作优先采用 haiku subagent
3. push之后整理提炼fix过程中预计在维护过程中的经验，筛选出可复用的经验，加入到CLAUDE.md中。需得用户授权。
