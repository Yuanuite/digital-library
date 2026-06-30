---
name: add-book-to-library
description: |
  将 PDF 书籍转换为 Hugo 页面并加入个人数字图书馆。完整流程：PDF 提取（MinerU VLM）→ Markdown 清洗 → 章节拆分 → 格式化 → 导航与首页接入。
  触发词：add this book, 加入图书馆, 添加书籍, 把 PDF 转成网页, 把书加入图书馆, convert PDF to library, add book to library, 个人图书馆, digital library.
---

# Add Book to Library

将一本 PDF 学术书籍加入已有的 Hugo 数字图书馆。

## 极简状态机（4态马尔可夫链）

```
RAW --extract--> EXTRACTED --clean+split--> STRUCTURED --wire+build--> LIVE
```

| 状态 | 含义 | Phase |
|------|------|-------|
| RAW | 源文件在 pdfs/ | 0 |
| EXTRACTED | Markdown 在 out/，已清洗 | 1+2 |
| STRUCTURED | 章节在 content/，已格式化 | 3+4+5 |
| LIVE | 接入导航，hugo build 通过 | 6+7 |

失败处理：回退前一状态重试（马尔可夫性质：下一状态仅依赖当前状态）。

## 架构

```
content/                    <- 唯一内容源
  books/<cat>/<slug>/       <- _index.md + ch*.md + images/
  papers/<field>/<slug>/
  notes/
pdfs/                       <- 源文件（gitignored）
  <book-id>.state.json      <- 状态跟踪
scripts/
  clean_markdown.py         <- VLM输出清洗
  clean_epub.py             <- EPUB输出清洗
static/                     <- KaTeX, pseudocode.js
```

`<category>` 由用户在添加时指定，如 `finance`、`math`、`cs`、`physics` 等。

---

## 工作流

### 🛑 强制入口：状态文件

**处理任何书之前，必须先检查 `pdfs/<book-id>.state.json` 是否存在。**

- 存在 → 读取 `state` 字段，从中断点恢复
- 不存在 → **🛑 STOP，必须先完成 Phase 0 才能继续**

每个 phase 完成后**强制**写入状态文件，更新 `state` 和对应 phase 的 `status` 为 `done`。

---

### Phase 0：归集 PDF + 创建状态文件

将源文件复制到仓库的 `pdfs/` 目录（已 gitignore，不会发布）。支持 PDF、EPUB、MOBI 三种格式：

```bash
cp /path/to/book.pdf pdfs/    # PDF
cp /path/to/book.epub pdfs/   # EPUB
cp /path/to/book.mobi pdfs/   # MOBI
```

创建状态文件 `pdfs/<book-id>.state.json`，记录每本书的处理进度：

```json
{
  "book_id": "<book-id>",
  "pdf": "<filename>",
  "type": null,
  "category": null,
  "slug": null,
  "format": null,
  "state": "phase_0_done",
  "phases": {
    "phase_0": { "status": "done", "note": "Book copied to pdfs/ (format: pdf|epub|mobi)" },
    "phase_1": { "status": "pending", "note": "PDF to Markdown via MinerU VLM" },
    "phase_2": { "status": "pending", "note": "Clean markdown" },
    "phase_3": { "status": "pending", "note": "Choose category" },
    "phase_4": { "status": "pending", "note": "Split into chapters" },
    "phase_5": { "status": "pending", "note": "Format special pages" },
    "phase_6": { "status": "pending", "note": "Wire nav and homepage" },
    "phase_7": { "status": "pending", "note": "Build and verify" }
  }
}
```

**Phase 0 完成后**：写入 `state: "phase_0_done"`，`phase_0.status: "done"`。

### Phase 1：PDF → Markdown

调用 `/mineru-document-extractor`。学术书籍带公式：

```bash
mineru-open-api auth --verify
mineru-open-api extract book.pdf -o out/ -f md --model vlm --language en --timeout 3600
```

**失败分支**：MinerU API 超时或不可用 → 将 PDF 按 200 页拆分重试：
```bash
mineru-open-api extract book.pdf -o out_part1/ -f md --model vlm --language en --timeout 3600 --pages 1-200
mineru-open-api extract book.pdf -o out_part2/ -f md --model vlm --language en --timeout 3600 --pages 201-400
# 手动合并输出文件后继续
```

**EPUB → Markdown（pandoc，本地免费）：**

```bash
pandoc book.epub -t markdown --extract-media=images -o out/book.md
```

输出质量高于 OCR：无伪影，HTML 语义直接转换为 Markdown。

**MOBI → EPUB → Markdown（fallback）：**

```bash
ebook-convert book.mobi book.epub   # calibre，需先 brew install calibre
pandoc book.epub -t markdown --extract-media=images -o out/book.md
```

**Phase 1 完成后**：写入 `state: "phase_1_done"`，`phase_1.status: "done"`。

### Phase 2：清洗 Markdown

运行 `scripts/clean_markdown.py  # VLM` 处理：
- LaTeX 空白修复（`x _ {i}` → `x_{i}`）
- 数学内数字间距（`1 0 0` → `100`）
- 页眉泄露（章节名混入正文）
- 脚注上标（`$^{1}$`）

**失败分支**：脚本报错 → 检查输入是否为 MinerU VLM 输出格式，手动检查第一处报错行的原始内容。

**中文书注意**：`clean_markdown.py` 主要处理英文 LaTeX 问题。中文书额外手动清理：
- OCR 伪影（空字母碎片如 `A\nB C\nD`）
- 重复的标题/作者行
- ISBN、版权声明、客服联系方式
- 源代码下载链接和客服邮箱（保留 GitHub 链接即可）

**EPUB 书注意**：pandoc 输出无 OCR 伪影，但可能残留版权声明、ISBN、出版信息页、前言推荐语——手动删除即可。EPUB 内嵌图片已在 Phase 1 通过 `--extract-media=images` 提取，无需额外处理。

🔴 **CHECKPOINT**：清洗完成后，展示前 50 行的 before/after 对比。用户确认清洗质量后继续。

**Phase 2 完成后**：写入 `state: "phase_2_done"`，`phase_2.status: "done"`。

### Phase 3：选择分类

询问用户：
1. 这是书籍、论文还是笔记？（决定放 `books/`、`papers/` 还是 `notes/`）
2. 属于哪个学科分类？（如 `finance`、`math`、`cs`）
3. 书的 URL slug 是什么？（短横线命名，如 `quant-finance-interview`）

🔴 **CHECKPOINT**：确认路径 `content/<type>/<category>/<book-slug>/` 后继续。

**Phase 3 完成后**：写入 `state: "phase_3_done"`，更新 `type`、`category`、`slug` 字段。

### Phase 4：拆分章节

```bash
mkdir -p content/<type>/<category>/<book-slug>/images
```

找到 `## Chapter N` 或 `## 第N章` 边界，每个章节存为 `ch01.md`、`ch02.md` ……

修正标题层级：
- 章节标题 → `#`（H1）
- 节（N.M）→ `##`（H2）
- 问题/主题 → `###`（H3）

**章节命名规范**（写入 frontmatter `title` 字段）：
- 正文章节：`第X章 · 主题概括`（X 为数字）
- 序言/前言：`序言` 或 `前言`
- 附录：`附件 · 内容简述`
- 参考文献/索引：`参考文献` / `索引`
- description 字段：极度精简，4-8 字

页码 ≤ 15 的薄书不拆分，合并为一个文件。

**章节 weight 约定** — 每章 frontmatter `weight` 使用 10, 20, 30 递增值（步长 10），便于在已有章节间插入新章无需重新编号。

**丛书结构（多卷本）** — 父级 `_index.md` 用 `BookCollapseSection: true` + 手动目录表，每卷建子目录 `vol1/_index.md` + `vol1/ch*.md`。

**修复代码注释被误识别为标题**：遍历所有 `ch*.md`，将代码块（` ``` ` 包裹区域内）中以 `# ` 开头的行降级为 `## `，防止 Python 注释 `# 这是一段说明` 被渲染为 H1。

**失败分支**：`## Chapter` 模式匹配不到 → 改用 `# Chapter` 或 `### Chapter` 匹配；仍失败则让用户提供章节边界关键词。

**Phase 4 完成后**：写入 `state: "phase_4_done"`，`phase_4.status: "done"`。

### Phase 4.5：逐章审核（Haiku 并行）

每章 spawn 一个 Haiku agent 独立校对，所有章节并行处理。每个 agent 检查：

1. **OCR 错误** — 数学符号被误识别（λ→入、∑→Σ 空、∈→E）、中文字符混入公式
2. **算法伪代码格式** — 行是否被错误合并、缩进是否保留、变量名是否正确
3. **表格和图标题** — `表N.N　标题` 是否独立成行、`图N.N　标题` 是否正确关联
4. **标题层级** — 代码注释 `#` 是否被识别为 H1、节标题层级是否正确
5. **交叉引用** — 文中 `第N章` 是否已转为链接

每个 agent 返回：修复后的章节内容 + 修复清单。

**失败分支**：Haiku agent 不可用 → 主 agent 逐章过前 3 章，剩余章 spot-check 首尾。

**Phase 4.5 完成后**：写入 `state: "phase_4.5_done"`。

### Phase 5：格式化

#### 封面 + 目录（`_index.md`）

统一模板，三块结构：

```html
<section class="book-cover">
  <h1 class="book-cover-title">书名</h1>
  <p class="book-cover-subtitle">英文原标题 / 版本</p>
  <p class="book-cover-author">作者 · 译者</p>
</section>

<section class="book-intro">
  <h2>简介</h2>
  <p>优先用原书封底/简介原文。2-4 句，不宜过长。</p>
</section>

## 目录
{{< book-toc >}}
```

`{{< book-toc >}}` 自动列出当前 section 下所有章节（按 weight 排序，显示 title + description）。

**丛书结构（多卷本）**：父级 `_index.md` 用手动表格替代 `{{< book-toc >}}`（短代码不列子 section），每卷建 `vol1/_index.md` + `vol1/ch*.md`。

#### 符号说明（`notations.md`，如有）

**强制**：4 栏 markdown 表格：

```markdown
| 符号 | 含义 | 符号 | 含义 |
|------|------|------|------|
| E | 期望 | π | 策略 |
```

#### 算法列表（`algorithms.md`，如有）

**强制**：表格带章节链接：

```markdown
| # | 算法 | 章节 |
|---|------|------|
| 1 | Q 学习算法 | [第5章](ch05.md) |
```

#### 算法伪代码

使用 pseudocode.js（LaTeX algorithmic 语法）：

```html
<pre class="pseudocode">
\begin{algorithm}
\caption{算法 1: Sarsa算法}
\begin{algorithmic}
\STATE 输入: episodes, α, γ
\FOR{each episode in episodes}
    \STATE S ← first state of episode
    \REPEAT
        \STATE A = policy(Q, S)
        \STATE Q(S, A) ← Q(S, A) + α(R + γQ(S', A') - Q(S, A))
    \UNTIL{S is terminal state}
\ENDFOR
\end{algorithmic}
\end{algorithm}
</pre>
```

`_` 需转义为 `\_`。Phase 4.5 的 Haiku agent 负责将纯文本伪代码转换为上述格式。

#### 表格标题

将 `表N.N　标题` 包裹为 caption shortcode：
```markdown
{{</* caption */>}}表5.1　n步Q收获{{</* /caption */>}}
```
紧接在 `<table>` 之前。

#### 学术块（定义 / 定理 / 例题 / 要点）

Hugo 站点已内置以下 shortcode，教材类书籍必须使用：

**定义：**
```markdown
{{</* definition title="马尔可夫决策过程" */>}}
一个 MDP 由状态集 S、动作集 A、转移概率 P 和奖励函数 R 组成。
{{</* /definition */>}}
```
效果：紫色左边框 + `定义` 标签。

**定理 / 引理 / 命题 / 推论：**
```markdown
{{</* theorem type="定理" title="贝尔曼最优方程" */>}}
V*(s) = max_a [ R(s,a) + γ ∑ P(s'|s,a) V*(s') ]
{{</* /theorem */>}}
```
`type` 可选：`定理`(默认) | `引理` | `命题` | `推论`。蓝色左边框。

**例题：**
```markdown
{{</* example title="赌徒破产问题" */>}}
题目描述...
{{</* solution */>}}解答内容...{{</* /solution */>}}
{{</* /example */>}}
```
绿色左边框 + `例题` 标签。`{{</* solution */>}}` 可嵌套其中。

**要点（章末总结）：**
```markdown
{{</* key-point */>}}
本章核心结论：...
{{</* /key-point */>}}
```
橙色左边框 + `要点` 标签。

**通用提示框：**
```markdown
{{</* callout type="tip" title="小技巧" */>}}
使用向量化运算可以加速...
{{</* /callout */>}}
```
`type`：`tip`(蓝) | `note`(灰) | `warning`(橙) | `important`(红)。

#### 解答块

将 `解答：` 起头的内容包裹为 solution shortcode：
```markdown
{{</* solution */>}}
解答：...
{{</* /solution */>}}
```
绿色左边框，暗色模式自动适配。**禁止**裸写 `<div class="solution">`。

**失败分支**：shortcode 未闭合 → Hugo build 报错。每个 `解答：` 出现次数应等于 `{{</* solution */>}}` 出现次数。

#### 索引（`index_term.md`）

6 栏表格：`| 术语 | 章节 | 术语 | 章节 | 术语 | 章节 |`

跨页面锚点：先 `hugo`，从 `public/` 的 HTML 提取实际 `id` 属性，再回填链接。

**失败分支**：锚点 404 → 检查 Hugo 生成的 slug 与索引中引用的 slug 是否一致（Hugo 会去除中文标点、转小写英文）。

**Phase 5 完成后**：写入 `state: "phase_5_done"`，`phase_5.status: "done"`。

### Phase 6：接入导航和首页

#### 分类设置

在书籍 `_index.md` frontmatter 中填入 `categories`，用于侧栏分组和 footer 导航：

```yaml
categories: ["机器学习"]
```

#### 侧栏菜单（自动生成）

侧栏由 `menu-filetree.html` 根据 `categories` + content 结构自动渲染，无需手写 `hugo.toml` 菜单。章节标题从 `ch*.md` 的 `title` frontmatter 提取（`{{< book-toc >}}` 短代码），>50 字符则在 frontmatter 中截断。

#### Footer 导航约定

书封面 `_index.md` 的 prev 始终指向首页（Yuan's Library）；丛书卷封面指向父级丛书封面（`BookCollapseSection: true`）；第一章 prev 回退至书封面。由 `layouts/_partials/docs/inject/footer.html` 自动处理，无需手动配置。

#### 书架卡片

在 `content/_index.md` 的 bookshelf 区域和对应分类 `_index.md` 中添加：

```html
<a class="book-row" href="/books/<category>/<slug>/">
  <span class="book-row-title">书名</span>
  <span class="book-row-meta">作者</span>
  <span class="book-row-desc">一句话简介</span>
  <span class="book-row-arrow">›</span>
</a>
```

**Phase 6 完成后**：写入 `state: "phase_6_done"`，`phase_6.status: "done"`。

### Phase 7：验证

```bash
hugo
```

检查：
- 构建零错误
- 所有内部链接可点击
- 公式在页面中正确渲染
- 解答块样式正常

🔴 **CHECKPOINT**：`hugo` 通过后展示章节数、图片数、内部链接数。用户决定何时 push。

**Phase 7 完成后**：写入 `state: "phase_7_done"`，`phase_7.status: "done"`。整本书处理完毕。

---

## 失败模式速查

| 症状 | 一线修复 | 仍失败 |
|------|---------|--------|
| 公式不渲染 | 检查 `mathjax.js` 的 inlineMath/displayMath 是否含 `$` 分隔符 | hugo.toml 是否用 `tex-chtml-full.js`（非 `tex-mml-chtml.js`） |
| `\boldsymbol` 红色未渲染 | CDN 用 `tex-chtml-full.js`，包含所有 TeX 扩展包 | `tex-mml-chtml.js` 不含 boldsymbol 包 |
| 超宽公式溢出 | 改用 `\begin{aligned}` 手动断行 | `chtml.linebreaks.automatic` 对极长单行公式效果有限 |
| HTML 内 md 不解析 | hugo.toml 加 `md_in_html` | 改用 `<img src>` 替代 `![](path)` |
| 解答块颜色消失 | 检查 `extra.css` 中 `.solution` 定义 | 检查 `<div>` 是否有 `markdown="1"` |
| 嵌套解答块（问题文本也变绿） | 查 `<div>` 和 `</div>` 配对 | grep `解答：` 出现次数 = `<div class="solution">` 出现次数 |
| 索引锚点 404 | `hugo` 后从 HTML 提取 id | 手动比对 Hugo slug 规则 |
| 图片不显示 | 检查路径相对 `content/` 而非文件所在目录 | `![](images/x.jpg)` 不是 `![](../images/x.jpg)` |
| Build 报错 nav 路径 | 检查 `hugo.toml` 的 nav 路径文件存在 | `use_directory_urls: false` 确保 .md 链接稳定 |
| 图注/表注未与正文区分 | 包裹 `<p class="caption">图N.N 标题</p>` | CSS `.caption { text-align: center; font-size: .8rem; }` |
| 4×4 格子世界散落成数字 | 用 `<table class="grid-world">` 包裹 | CSS 加固定格子尺寸 + 边框 |
| OCR 伪影：`<details>natural_image</details>` | 删除空 `<details>` 块，只留 `![](image)` | Phase 4.5 Haiku 逐章审核 |
| OCR 错误：λ→入、S→.s. | 替换词表 + Phase 4.5 Haiku 校对 | 数学符号误识别需人工/LLM 上下文判断 |

---

## 反例黑名单（不要做）

| # | 禁止 | 原因 | 正确做法 |
|---|------|------|---------|
| 1 | 跳过清洗直接翻译/拆分 | 残留 `\text {word}` 等 LaTeX 垃圾会污染全书 | Phase 2 必须在 Phase 4 之前 |
| 2 | 用 `!!! admonition` | 每行需 4 空格缩进 + 空行，一处错整块崩 | 用 `<div class="solution" markdown="1">` |
| 3 | 直接编辑 `public/` 下的文件 | `public/` 是构建产物，下次 build 被覆盖 | 只改 `content/` 源文件 |
| 4 | 翻译时动 LaTeX 公式 | `$x_i$` 变成 `$x _ i$` 直接破坏数学内容 | 翻译 prompt 明确黑名单保护 |
| 5 | 章节标题用 `##` | Hugo 侧边栏 H2 会缩进过深 | 章节标题用 `#`，节用 `##` |
| 6 | 不 build 直接手写锚点 | Hugo slug 规则与直觉不同（去除中文标点等） | `hugo` → 从 HTML 提取 `id` |
| 7 | PDF 源文件放入 content/ | 会发布到网站上，浪费带宽和存储 | 放 `pdfs/`（已 gitignore） |
| 8 | 交叉引用用 `.html` 后缀 | hugo 会报 warning，期望 `.md` | 统一用 `.md` 后缀，Hugo 构建时自动转换 |
| 9 | `\boldsymbol` 不渲染 | `tex-mml-chtml.js` 不含 boldsymbol 包 → 红色未识别 | 用 `tex-chtml-full.js` CDN |
| 10 | 超宽公式出滚动条 | 用户不接受滚动条 | 用 `\begin{aligned}` 手动断行 |
| 11 | 表格数据挤在一起 | 默认表格无居中、无 padding | CSS `td { text-align: center; padding: .4rem .8rem; }` |

---

## 经验总结

以下是从实际转换 `强化学习入门` 全书（10 章，7565 行）中总结的关键经验。

### 基础设施要求

1. **MathJax CDN 必须用 `tex-chtml-full.js`** — `tex-mml-chtml.js` 缺少 `\boldsymbol` 等扩展包
2. **pseudocode.js 算法渲染** — 需要 CDN CSS + JS + `content/javascripts/pseudocode-render.js`
3. **lefthook pre-commit** — `hugo --strict` 阻断有 broken link 的提交
4. **mathjax.js** — `$`/`$$` 分隔符 + `document$.subscribe` 兼容 instant navigation

### 算法伪代码格式

```html
<pre class="pseudocode">
\begin{algorithm}
\caption{算法 1: 名称}
\begin{algorithmic}
\STATE 输入: ...
\FOR{each episode}
    \STATE ...
\ENDFOR
\end{algorithmic}
\end{algorithm}
</pre>
```

注意 `_` 转义为 `\_`。

### 常见 OCR 误识别

| 原文 | 误识别为 | 修复 |
|------|---------|------|
| λ | 入 | `\(λ)` 替换 `（入）` |
| S₁ | .s. | Phase 4.5 Haiku 上下文判断 |
| \mathrm{S} | \mathrm {~ s ~} | `\\[a-z]+ {` → `\\\1{` |

### 表格格式化

- 格子世界（4×4 等）：`<table class="grid-world">` + CSS 固定格子
- 数据表格：文字居中、padding
- 表注：`<p class="caption">表N.N 标题</p>`，置 `<table>` 上方

### 丛书（多卷本）分批次上传

从 `布鲁克斯价格行为` 四卷本（3 PDF + 1 EPUB）实践中总结的关键经验。

#### 目录结构

```
content/books/<category>/<series-slug>/
  _index.md          ← 丛书主页（BookCollapseSection: true, 手动目录表, categories）
  vol1/
    _index.md        ← 第一卷封面（BookCollapseSection: true, 无 categories, 无 tags）
    ch*.md
    images/
  vol2/ ...
```

#### 🔴 categories 铁律（防侧栏计数膨胀）

**categories 只放在丛书主页 `_index.md`，不得放在 volN/_index.md 中。**

侧栏 `menu-filetree.html` 按 `categories` 分组，**每个含 `categories` 的 `_index.md` 都被计为一个独立项**。若 vol1-4 各有 `categories: ["金融"]`，侧栏会把每卷当作独立书籍，导致计数 = 4 + 1（丛书主页）+ 其他同分类书籍 = 远超预期。

- ✅ 丛书主页：`categories: ["金融"]`
- ❌ vol1-4 `_index.md`：不加 `categories`（从父 section 继承）
- ❌ 分类页 `content/books/finance/_index.md`：不加 `categories` 和 `BookCollapseSection`（避免递归嵌套）

#### 分批处理流程

每卷独立走完整状态机（Phase 0–7），第一卷建丛书框架，后续卷复用：

1. **第一卷** — Phase 4 时创建 `vol1/` 和父级 `_index.md`（`BookCollapseSection: true` + 手动目录表，待填卷链接）
2. **第二卷** — 独立走 Phase 0–7，Phase 4 写入 `vol2/`，**更新**父级目录表添加 `vol2/` 行
3. **后续卷** — 同上，每卷处理完即更新父级目录表
4. **最终** — 全部卷上线后，父级目录表完整，`hugo` 零报错

#### MinerU 大 PDF 分页提取

PDF 超过 200 页或上传超时时，用 `--pages` 拆分：

```bash
# MinerU API 限制：单次 ≤200 页。上传超时（阿里云 OSS 网络不稳定）时也适用拆分策略
mineru-open-api extract book.pdf -o out/chunks/p1-200/ -f md --model vlm --timeout 3600 --pages 1-200
mineru-open-api extract book.pdf -o out/chunks/p201-400/ -f md --model vlm --timeout 3600 --pages 201-400
mineru-open-api extract book.pdf -o out/chunks/p401-417/ -f md --model vlm --timeout 3600 --pages 401-417

# 合并时按页码顺序拼接
cat out/chunks/p1-200/*.md out/chunks/p201-400/*.md out/chunks/p401-417/*.md > out/book-merged.md
```

**要点**：
- 每 chunk 用独立输出目录 `-o out/chunks/pX-Y/` 避免同名文件覆盖
- 页面范围必须精确（如 401-417 = 17 页），超出 200 页 API 直接拒绝
- 合并后运行 `scripts/clean_markdown.py` 处理 VLM 伪影
- **使用绝对路径**：后台任务（`run_in_background: true`）的 CWD 可能不同，导致相对路径找不到文件

#### EPUB 优先策略

EPUB 用 pandoc 本地转换，秒级完成，质量高于 OCR（无伪影、HTML 语义保留）。多格式混排的丛书优先处理 EPUB，用省下的时间对付 PDF 提取。

```bash
pandoc book.epub -t markdown --extract-media=out/images -o out/book.md
```

#### Haiku 并行清洗+拆分

两本以上书籍可并行委派 Haiku agent 做 Phase 2–4（清洗 + 图片收集 + 章节拆分 + 封面创建），主线程只做最终构建验证。每个 agent 处理一本书，报告章节数、图片数、构建结果。
