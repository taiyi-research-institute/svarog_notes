# DKLS23 学习笔记

15 篇门限签名 / MtA 论文精读笔记。每篇是一个独立的 LaTeX **片段**(纯内容,
无 documentclass), 经 [main.tex](main.tex) 模板编译成独立 PDF, 产物在 `pdf/`。

## 阅读环境

### 读 PDF: 零依赖

字体已嵌入 PDF。**阅读不需要装任何东西** —— 不需要 TeX、不需要中文字体, 只要一个
PDF 阅读器。

### 跨笔记跳转: 需要原生 PDF 阅读器

笔记之间有交叉引用(点文字跳到另一篇 PDF)。用的是 PDF 的 **GoToR 远程跳转**,
它要求阅读器能"再打开另一个文件"。

- **VSCode 内置 PDF 预览**(pdf.js 跑在 webview 沙箱里)**不支持跨文件跳转**:
  链接显示蓝色但点不动, 是正常的, 不是链接坏了。
- 用 **Adobe Acrobat / Okular / PDF Expert / macOS 预览** 打开 `pdf/*.pdf`, 就能跳。

### 在 VSCode 里编辑 + 预览

装 LaTeX Workshop (James Yu) 扩展后:

- **Ctrl+S 自动构建**: 保存哪个片段就编哪个成同名 PDF(`pdf/<stem>.pdf`),
  辅助文件(aux/log)进 `_build/`。靠片段顶部的 `% !TEX root = <stem>.tex`
  + [.vscode/build-note.sh](.vscode/build-note.sh) 实现。
- 单篇 PDF 在 VSCode 预览里看没问题; **跨文件跳转点不动**(见上)。
- **反色(深色)浏览**: `latex-workshop.view.pdf.invert` 设为 `1`(已在
  [.vscode/settings.json](.vscode/settings.json) 配好, `0` 是白底)。改完重开
  viewer 生效。纯文字+公式的笔记反色效果干净。

## 重新编译(要改内容重编时才需要)

只阅读已编好的 PDF 不需要本节。

### 编译环境

- **TeX Live 2026**(scheme-full, 装于 `~/.local/texlive/2026`)。这台无头机缺
  `libfontconfig` / `libxml2` / `libicu`, 靠 conda 软链到 `~/.local/lib` 补上
  (见 `~/.config/fish/config.fish` 的 `LD_LIBRARY_PATH`)。
- **思源字体**静态实例(Noto Serif/Sans CJK SC), 装于
  `~/.local/texlive/texmf-local/fonts/truetype/google/noto/`, 装完跑
  `mktexlsr ~/.local/texlive/texmf-local`。可变字体(fvar)在 XeTeX 下无效,
  静态实例由 fontTools `varLib.instancer` 从 google/fonts 生成。

### 编译命令

    make                    # 全量 15 篇
    make pdf/06-rvole.pdf   # 只编一篇(也可: make 06-rvole)

任何片段改动 `make` 都会全量重编 —— 故意的: 交叉引用的编号依赖所有笔记, 全量重编
保证引用新鲜(想跳过时用单篇命令, 但会读 `_build/` 里其它篇的旧 aux)。

## 写作参考

- **标题**: 每篇 PDF 的标题来自片段顶部的 `% title: ...` 注释, 由
  [template/wrap.py](template/wrap.py) 注入。无作者 / 日期 / 摘要 / 关键词。
- **跨篇引用**: 被引方加 `\label{sec:...}`, 引方写 `\hyperref[label]{显示文字}`
  (显示文字 + 跳转; `\ref` 只显示编号)。xr-hyper 已在 [main.tex](main.tex) 配好
  `\externaldocument`, 引用方无需额外声明。

## 仓库结构

    main.tex        论文模板(字体 / 版式 / 标题注入占位)
    Makefile        编译入口
    pdf/            编译产物: 15 篇 PDF(入库, 只放 PDF)
    _build/         编译现场: 包装文件 + aux/log(不入库)
    template/       编译依赖: wrap.py + md→LaTeX 管线脚本 + 备选模板
    00-*.tex …      15 篇笔记片段(纯内容)

## md → LaTeX 管线(已归档, 重转时用)

`template/src/` 是 md 原稿, 根目录 `*.tex` 是成品片段。四步:
`preprocess.py → pandoc → postprocess.py → numberize.py`, 详见各脚本 docstring。
