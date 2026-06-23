# 📚 Add Book to Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 一键将 PDF 学术书籍转为 MkDocs Material 数字图书馆页面。
> 把书拖给 Claude，聊几句天，剩下的全自动。 **[演示站点](https://yuanuite.github.io/digital-library/)**

## 🙏 致谢

本项目基于 [UynajGI/yuulibrary](https://github.com/UynajGI/yuulibrary) 开发，感谢原作者的开源精神。在此基础上扩展为完整的自动化管线：Claude Code Skill + MinerU VLM 识别 + 多阶段清洗校对 + 一键部署。

## 🚀 使用

```bash
# 1. 初始化图书馆仓库
cp -r templates/mkdocs.yml templates/extra.css templates/mathjax.js templates/deploy.yml my-library/
# 改 mkdocs.yml 的 site_url 为你的 GitHub Pages 地址

# 2. 在 Claude Code 中触发
add this book          # 或拖 PDF 进对话框说"把这本书加入图书馆"
```

8 阶段自动流转（支持断点续传）：归集 → 提取（MinerU VLM / pandoc）→ 清洗 → 分章 → AI 校对 → 格式化 → 导航接入 → 验证。

```bash
# 3. 部署
git push origin main   # GitHub Actions 自动构建 → GitHub Pages
```

## ✨ 特性

- **数学公式**：MathJax 3 `tex-chtml-full.js`，`\boldsymbol`/`\mathbb`/`\mathcal` 全支持，instant nav 下不消失
- **算法伪代码**：pseudocode.js，LaTeX algorithmic 原生语法
- **解答块**：扫描 `解答：` 自动包裹为绿色背景 `<div class="solution">`
- **表格增强**：数据表全宽居中、格子世界固定尺寸、表注居中小字、符号表 4 栏
- **交叉引用**：正文"第3章"自动转为 `[第3章](ch03.md)`
- **中英文检测**：CJK 比例自动设 `<html lang>`，优化字体和翻译
- **完整书内页**：封面目录 / 符号说明 / 算法列表 / 术语索引

## 📁 结构

```
my-library/
├── mkdocs.yml
├── docs/
│   ├── index.md              # 首页（卡片式书单）
│   ├── books/<category>/<book-slug>/
│   │   ├── index.md          # 封面 + 双栏目录
│   │   ├── ch01.md ~ …       # 章节
│   │   ├── notations.md      # 符号说明
│   │   ├── algorithms.md     # 算法列表
│   │   ├── index_term.md     # 术语索引
│   │   └── images/
│   ├── stylesheets/extra.css
│   └── javascripts/{mathjax,pseudocode-render,translate-toggle}.js
├── pdfs/                     # PDF 源文件（.gitignore）
└── .github/workflows/deploy.yml
```

## 📖 我的图书馆

**[yuanuite.github.io/digital-library](https://yuanuite.github.io/digital-library/)**

| 书名 | 作者 | 学科 |
|------|------|------|
| Trading and Exchanges · 市场微观结构 | Larry Harris | 金融 |
| Why Stock Markets Crash · 金融崩盘 | Didier Sornette | 金融 |
| 斯坦福机器学习教程笔记 | 黄海广 / Andrew Ng | 机器学习 |
| 与神对话 · 五卷 | 尼尔·唐纳德·沃尔什 | 灵性 |

## 🔧 技术栈

[MinerU VLM](https://github.com/opendatalab/MinerU) · [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) · [MathJax 3](https://www.mathjax.org/) · [pseudocode.js](https://github.com/SaswatPadhi/pseudocode.js) · [pandoc](https://pandoc.org/) · [GitHub Actions](https://github.com/features/actions)

## 📄 许可证

MIT License © 2025 Yuanuite · Inspired by [UynajGI/yuulibrary](https://github.com/UynajGI/yuulibrary)
