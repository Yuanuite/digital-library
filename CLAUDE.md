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

仅有两个活跃脚本：
- `clean_markdown.py` — VLM 输出清洗（LaTeX 空白修复、去页眉/脚注）
- `clean_epub.py` — EPUB pandoc 输出清洗（版权页、CSS 残留）

## 添加书籍流程（4态马尔可夫链）

参见 `.claude/skills/add-book-to-library/SKILL.md`。状态机：

```
RAW --extract--> EXTRACTED --clean+split--> STRUCTURED --wire+build--> LIVE
```

| 状态 | Phase | 含义 |
|------|-------|------|
| RAW | 0 | pdfs/ 有源文件 + 状态文件 |
| EXTRACTED | 1+2 | out/ 有清洗后 Markdown |
| STRUCTURED | 3+4+5 | content/ 有章节 + 格式化 |
| LIVE | 6+7 | 接入导航，hugo build 通过 |

### 关键规则

1. **PREFLIGHT（Phase 0.5）**：处理前检查 `test -f hugo.toml` 确认框架为 Hugo
2. **每阶段写状态文件**：`pdfs/<book-id>.state.json` 含 `schema_version: 2` 和 `state` 字段
3. **写完即构建**：Phase 2 和 Phase 4 之后各跑 `hugo --quiet 2>&1 | head -5`
4. **失败回退**：当前状态失败 → 回退至前一状态，删除该阶段产物，重试
5. **PUBLISHED 终端态**：`git push` 后 state 写为 `PUBLISHED`

### SKILL.md 单一真相源

`~/.claude/skills/add-book-to-library` 是 symlink，指向本项目的 `.claude/skills/add-book-to-library/`。编辑项目版本即编辑活跃 skill。Git 自动版本化。

### 状态文件 schema

```json
{
  "schema_version": 2,
  "book_id": "<id>",
  "pdf": "<filename>",
  "state": "RAW|EXTRACTED|STRUCTURED|LIVE|PUBLISHED",
  "type": "books|papers|notes",
  "category": "<cat>",
  "slug": "<slug>",
  "format": "pdf|epub",
  "phases": { "phase_0": {...}, ... }
}
```

## 通用原则

**奥卡姆剃刀（精简化代码）** — 任何改动尽可能小：能改一行不改两行，能复用不新建，能局部修改不重构。目标是解决当前问题，不顺便做"优化"。

**Hugo 主题覆盖** — 修改主题功能时，一律用项目级文件覆盖，不动子模块 `themes/hugo-book/`。优先级：`assets/` > `layouts/` > `i18n/` > CI deploy.yml patch。

**暗色模式 CSS 特异性** — 新增任何暗/亮双模式样式时，选择器必须写 `html[data-theme="dark"]` 而非 `[data-theme="dark"]`。后者特异性 (0,1,0) 与主题 `:root` 相同，主题后加载会覆盖自定义变量。加 `html` 前缀 → (0,1,1) 碾压主题。

**colorScheme 同步** — 新增涉及暗/亮切换的 JS 时，设置 `data-theme` 的同时必须设 `document.documentElement.style.colorScheme = t`，否则原生控件（滚动条、表单、`<select>`）不跟随。head 内联防闪烁脚本也要同步。

**head 防闪烁** — 新增依赖 localStorage 的 UI 状态时，必须在 `layouts/_partials/docs/inject/head.html` 加同步内联脚本，放在 `<link>` 之前，避免页面渲染后再切换导致闪烁。

## 任务委派（Haiku subagent）

**规则**：需要理解 >2 个文件的因果链 → 主线程。单文件、确定目标、无判断 → Haiku。

**委派 Haiku**：
- commit / push / 查 git 状态 / 检查文件是否存在
- 单文件读写（更新列表、替换固定文本）
- grep 扫全仓（搜索引用、找未使用文件）
- 格式化（排序、对齐、去重）

**保留主线程**：
- CSS 层叠诊断（特异性、加载顺序、变量级联）
- 架构决定（删/留哪些文件、采用哪种技术方案）
- 跨文件根因分析（JS + CSS + HTML + 配置联动）
- 变量继承链追踪（`var()` 从哪里来、哪个选择器覆盖了它）

## fix 流程
1. fix 之后需要询问用户是否 push
2. fix、push、添加内容等简单操作优先采用 haiku subagent
3. push之后整理提炼fix过程中预计在维护过程中的经验，筛选出可复用的经验，加入到CLAUDE.md中。需得用户授权。
