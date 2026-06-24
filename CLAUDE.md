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

## 内容约定

- **章节标题统一格式** — 全部书籍的章标题使用 `第X章 · 主题`（空格+中点+空格分隔），description 控制在 4-8 字。序言保留"序言"，附录用 `附件 · ...`。此规则已写入 add-book-to-library skill 的 Phase 4。
- **书籍简介用原文** — `_index.md` 的 `.book-intro` 优先使用原书封底/简介原文。仅当原文过长（如 600+ 行出版商标语）才截断。AI 摘要质量显著低于原书文案。
- **中文 OCR 空格修复** — VLM 提取中文后字间可能插入空格（`多 变 量` → `多变量`）。修复方式：递归 `re.sub(r'([一-鿿])\s+([一-鿿])', r'\1\2', text)` 直到无匹配。

## Hugo 特有坑点

- **book-toc 短代码不列子章节** — `{{< book-toc >}}` 只列出 `IsSection eq false` 的叶子页面。有卷/分部结构的书（如《与神对话》分 5 卷），主 `_index.md` 需手写目录表格。
- **主题子模块必须初始化** — 克隆仓库后务必 `git submodule update --init --recursive`，否则全站 404 且 Hugo 无错误提示。
- **批量改 frontmatter 后重启 Hugo** — Fast Render Mode 缓存旧 frontmatter。改完多文件后必须 `kill $(lsof -ti :1313) && hugo server -D -p 1313`。
- **书封 CSS 精简** — `.book-cover` 的内边距保持 `padding: 2rem 1rem 1rem`，上方留白过大影响视觉平衡。
- **Footer prev 感知来源** — 书封面 prev 不能硬编码 `/books/`。先查 `.Params.categories`，有则指向分类页（如 `/categories/工程/`），fallback 到 `/books/`。
- **Chapter prev/next 惯用法** — Hugo 遍历有序页面找 prev：`range $pages → if not $found → eq $p $ → found → else prev=$p`。`$found` 前最后一个页面即为 prev。
- **首页 prev 回退父级** — 第一章无 prev 同级页，用 `{{ if not $prev }}{{ $prev = $parent }}{{ end }}` 回退到书封面，不能取 range 末元素。

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

**侧栏分组回退** — 侧栏按 `categories` frontmatter 分组，缺失时自动取 `tags` 第一项作为分类。书籍 `_index.md` 只需设置 `tags` 即可，不再强制要求 `categories`。

**中文搜索** — CI deploy.yml 在构建前 patch `themes/hugo-book/i18n/zh.yaml` 注入双语分词器，否则中文搜索整词匹配不返回结果。详见 `deploy.yml` 中 `Patch Chinese search tokenizer` 步骤。

**章节权重** — 每章 frontmatter 使用 `weight: 10, 20, 30`（步长 10），便于在已有章节间插入新章无需重新编号。

**暗色模式三条铁律**：

1. **选择器用 `html[data-theme]` 前缀** — 特异性 (0,1,1) 碾压主题 `:root` (0,1,0) 和 `@media`。任何时候不能只用 `[data-theme]` 或依赖 `@media (prefers-color-scheme)`。

2. **三处同步** — 每个 CSS 变量必须同时出现在：
   - `assets/_custom.scss` 的 `html[data-theme]` 块（CSS 级兜底）
   - `layouts/_partials/docs/inject/head.html` 防闪烁脚本（页面加载前，inline 最高优先级）
   - `static/theme-toggle.js` 的 `setTheme()`（点击时 `setProperty` 覆盖旧值）
   缺一处就会在对应时机失效。

3. **JS toggle 用 `setProperty`，不靠 `dataset`** — `dataset.theme` 触发 CSS 规则，但 head.html 加载时已用 `setProperty` 设了 inline 值（优先级最高）。toggle 时必须同样 `setProperty` 逐变量覆盖，否则 var() 永远取加载时的旧值。

## 任务委派（Haiku 模型）

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
2. fix、push、添加内容等简单操作优先采用 Haiku 模型（Agent 工具设 `subagent_type: "general-purpose"`, `model: "haiku"`）
3. push之后整理提炼fix过程中预计在维护过程中的经验，筛选出可复用的经验，针对其适用性分别加入CLAUDE.md和skill中。需得用户授权。
