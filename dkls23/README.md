# DKLS23 学习笔记

15 篇门限签名与 MtA 论文的精读笔记。
每篇笔记的源码是一个独立的 LaTeX 片段（纯内容，无 documentclass），
经 [main.tex](main.tex) 模板编译成独立 PDF，产物在 `pdf/`。
下面依次说明阅读方式、编译方式与片段的写作约定。

## 2026 年后续论文修订与补丁标记

补丁就地保留在相应笔记中，用黑体标记、上下横线与【补丁结束】标出范围。
每个补丁块或标题注明论文编号，例如【补丁｜2026-929】、【补丁｜2026-976】；共同涉及时同时列出。
配套的编码约定与笔记勘误注明其性质，避免误认为都是论文直接提出的新步骤。
替换原有写法时，先列【初版笔记】，再列【补丁写法】；整节新增或重写也在标题标记【补丁】。
这里的「初版」指此次更新前的笔记，不能理解为论文的逐字原文；完整替换稿包含所需的原有步骤。

笔记已纳入 [Segev，2026/929](https://eprint.iacr.org/2026/929)
与 [Asharov，2026/976](https://eprint.iacr.org/2026/976) 的实施更新。
[随机 VOLE](06-rvole.tex) 采用修订后的 OT 数量、校验维度、transcript 绑定及指定输入转换，
并联动更新 [SoftSpoken](05-softspoken.tex) 与 [gadget 向量](misc-gadget.tex)。
[协议编排](07-orchestration.tex) 补充完整 nonce 点与符号检查、可选现场零分享，
以及独立的两方预处理流程；[再随机化](misc-rerand.tex) 给出零分享替换的细节。

默认多方流程保留三轮，使用 Variant III，扩展 OT 数量为 2688，校验负载数为 1。
多方 PreSign 现在要求预先确定消息；支持未知消息及未知密钥的离线预处理单独采用两方 Variant II。
论文的混合模型结论、具体 OT 组合条件与 Keygen 适用前提均在正文注明。

## 阅读 PDF

字体已嵌入 PDF，阅读不需要安装任何东西：
只要一个 PDF 阅读器，不需要 TeX，也不需要中文字体。

笔记之间有交叉引用，点文字可跳到另一篇 PDF。
实现是 PDF 的 GoToR 远程跳转，要求阅读器能再打开另一个文件。
因此不同阅读器的表现不同：

- VSCode 内置 PDF 预览（pdf.js 跑在 webview 沙箱里）不支持跨文件跳转；
  链接显示蓝色但点不动，是正常的，不是链接坏了。
- Adobe Acrobat、Okular、PDF Expert、macOS 预览等原生阅读器可以跳。

## 编辑与编译

只阅读编好的 PDF 不需要本节。需要改动内容、重新编译时才看。
下面的环境与命令按本机（Linux x86-64）记录。

### 在 VSCode 里编辑 + 预览

装 LaTeX Workshop（James Yu）扩展后，日常编辑流程如下：

- 【Ctrl+S 自动构建】：保存哪个片段就编哪个成同名 PDF
  （`pdf/<stem>.pdf`），辅助文件（aux/log）进 `_build/`。
  实现靠片段顶部的 `% !TEX root = <stem>.tex` 与 [.vscode/build-note.sh](.vscode/build-note.sh)。
- 单篇 PDF 在 VSCode 预览里看没问题；跨文件跳转点不动（见上）。
- 【反色（深色）浏览】：`latex-workshop.view.pdf.invert`
  已在 [.vscode/settings.json](.vscode/settings.json) 配为 `0.8`
  （`0` 是白底，`1` 是完全反色）。改完后重开预览才生效。
  纯文字 + 公式的笔记反色效果干净。

### 编译环境

- Linux x86-64；Debian/Ubuntu 需要系统运行库 `libfontconfig1`。
- TeX Live 2026（`scheme-full`），装于 `~/.local/texlive/2026`。
- Python 3，供 [template/wrap.py](template/wrap.py) 生成包装文件；
  本机是 uv 0.12.10 管理的 Python 3.14.7。
- 思源字体静态实例（Noto Serif/Sans SC），
  装于 `~/.local/texlive/texmf-local/fonts/truetype/google/noto/`。
  项目按文件名加载字体。

新装 Debian/Ubuntu 系统先执行：

```bash
sudo apt install libfontconfig1
export PATH="$HOME/.local/texlive/2026/bin/x86_64-linux:$HOME/.local/bin:$PATH"
```

XeTeX 不能直接使用这里所需的 OpenType 可变字体。
运行仓库里的安装脚本，会从固定的 Google Fonts 提交下载源字体，
经 SHA-256 校验后，用固定版本 fontTools 4.64.0 生成 400、500、700 字重的五个静态实例，
并刷新 TeX 文件数据库：

```bash
./template/install-fonts.sh
```

安装后可检查并编译：

```bash
kpsewhich NotoSerifSC-Regular.ttf
kpsewhich NotoSansSC-Medium.ttf
make
```

### 编译命令

```
make                    # 全量 15 篇
make pdf/06-rvole.pdf   # 只编一篇（也可：make 06-rvole）
```

任何片段改动，`make` 都会全量重编。
这是故意的：交叉引用的编号依赖所有笔记，全量重编保证引用新鲜。
想跳过时用单篇命令，但会读 `_build/` 里其它篇的旧 aux。

## 写作约定

- 标题：每篇 PDF 的标题来自片段顶部的 `% title: ...` 注释，
  由 [template/wrap.py](template/wrap.py) 注入。
  无作者、日期、摘要、关键词。
- 跨篇引用：被引方加 `\label{sec:...}`，引方写 `\hyperref[label]{显示文字}`
  （显示文字 + 跳转；`\ref` 只显示编号）。
  xr-hyper 已在 [main.tex](main.tex) 配好 `\externaldocument`，
  引用方无需额外声明。

## 仓库结构

```
main.tex        论文模板（字体、版式、标题注入占位）
Makefile        编译入口
pdf/            编译产物：15 篇 PDF（入库，只放 PDF）
_build/         编译现场：包装文件 + aux/log（不入库）
template/       编译依赖：wrap.py + md→LaTeX 管线脚本 + 备选模板
refs.bib        参考文献
00-*.tex 等     15 篇笔记片段（纯内容）
```

## md → LaTeX 管线（已归档）

`template/src/` 是 md 原稿，根目录 `*.tex` 是成品片段。
转换分四步：`preprocess.py → pandoc → postprocess.py → numberize.py`，
详见各脚本 docstring。需要重转时用。

补丁框首段的 🛡️ 由 TeX Live 自带的 `twemojis` 提供。
图案来自 Twitter, Inc 及其他贡献者的 [Twemoji](https://github.com/twitter/twemoji)，
采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。
