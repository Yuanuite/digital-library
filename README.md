# 📚 Yuan's Digital Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 个人数字图书馆 — Hugo + KaTeX + pseudocode.js，自动部署到 GitHub Pages。
> **[演示站点](https://yuanuite.github.io/digital-library/)**

## 🙏 致谢

本项目基于 [UynajGI/yuulibrary](https://github.com/UynajGI/yuulibrary) 开发，感谢原作者的开源精神。

## 🚀 使用

```bash
git clone --recurse-submodules git@github.com:Yuanuite/digital-library.git
hugo serve        # 本地预览 http://localhost:1313
git push          # CI 自动构建 → GitHub Pages
```

## 📝 添加书籍

使用 Claude Code 对话式添加：拖 PDF 进对话框 → 提取 → 清洗 → 分章 → 格式化 → 导航接入。`scripts/` 中的 Python 脚本辅助 Markdown 清洗和章节拆分。

## ✨ 特性

- **数学公式**：KaTeX auto-render，`$...$` / `$...$` 分隔符
- **算法伪代码**：pseudocode.js，LaTeX algorithmic 语法
- **解答块**：`{{</* solution */>}}` shortcode，绿色左边框
- **元素框**：`{{</* definition */>}}` / `{{</* theorem */>}}` / `{{</* example */>}}` / `{{</* key-point */>}}`
- **暗色模式**：☀️/🌙 切换按钮，localStorage 持久，无闪烁
- **表格增强**：全宽居中、格子世界固定尺寸、表注居中小字
- **书架**：分类分组、整行式列表，Hover 左移动画
- **标签系统**：标签云 + term 页卡片网格

## 📁 结构

```
digital-library/
├── hugo.toml
├── content/                    # 所有内容页
│   ├── _index.md               # 首页
│   ├── books/                  # 书籍（按学科分类）
│   │   └── <category>/<book-slug>/
│   │       ├── _index.md       # 封面 + 目录
│   │       ├── ch01.md ~ …
│   │       ├── notations.md
│   │       ├── algorithms.md
│   │       └── index_term.md
│   ├── notes/                  # 笔记
│   ├── papers/                 # 论文
│   └── reference/              # 参考
├── layouts/                    # Hugo 模板
│   ├── _shortcodes/            # solution / definition / theorem / caption …
│   └── _partials/docs/         # 侧栏、主题切换
├── static/                     # JS/CSS/字体
├── assets/                     # SCSS → CSS
├── themes/hugo-book/           # 主题（git submodule）
└── .github/workflows/deploy.yml
```

## 📖 书目

| 书名 | 作者 | 学科 |
|------|------|------|
| Trading and Exchanges · 市场微观结构 | Larry Harris | 金融 |
| Why Stock Markets Crash · 金融崩盘 | Didier Sornette | 金融 |
| 斯坦福机器学习教程笔记 | 黄海广 / Andrew Ng | 机器学习 |
| 与神对话 · 五卷 | 尼尔·唐纳德·沃尔什 | 灵性 |

## 🔧 技术栈

[Hugo](https://gohugo.io/) · [hugo-book](https://github.com/alex-shpak/hugo-book) · [KaTeX](https://katex.org/) · [pseudocode.js](https://github.com/SaswatPadhi/pseudocode.js) · [pandoc](https://pandoc.org/) · [GitHub Actions](https://github.com/features/actions)

## 📄 许可证

MIT License © 2025 Yuanuite · Inspired by [UynajGI/yuulibrary](https://github.com/UynajGI/yuulibrary)
