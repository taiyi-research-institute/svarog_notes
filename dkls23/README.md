# DKLS23 学习笔记

14 篇门限签名与 MtA 论文的精读笔记。
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
make                    # 全量 14 篇
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

### 单栏协议块

共享模板已加载 [ruledprotocol.sty](template/ruledprotocol.sty)。
`protocol` 基于修改后的 `cryptocode`，每行处于数学模式，用 `\\` 分隔。
标题横线与每行的横灰线占满正文行宽；行号及其英文句点使用较小的等宽字体，整体右对齐。
标题与标题横线之间留 `1pt`，标题横线与第一行之间留 `2pt`，
内容横线上下各留 `1pt`。
最后一行的下边沿使用与标题下方相同的黑实线。

```latex
\begin{protocol}{Nonce points}
  \pcfor i\in S\pcdo \\
    R_i\gets r_iG \pccomment{本地 nonce 点} \\
  \pcendfor \\
  \pcreturn{R_i}
\end{protocol}
```

`\pcfor`、`\pcif` 等命令自动生成缩进竖灰线，作用域必须显式结束。
源码空行会被忽略，不占行号；注释使用 `\pccomment{…}`，以正文衬线字体和灰色 `//` 显示。
每行公式无需 `$…$` 或 `equation`，返回值使用 `\pcreturn{…}`。
用 `\pcparty{S}` 标明执行方，标记显示在右侧独立小列，例如
`\pcparty{R}y_b\coloneq\sum_t m_{t,d_t}`；共同执行写作 `\pcparty{S,R}`。
控制块开头的执行方标签适用于整个块，最终输出归属仍由 `\pcreturn` 标明。
只有使用了 `\pcparty` 的协议才会预留执行方列，列宽在 `\ProtocolPartyColumn` 中调整。
第一行包含求和等高公式时，标题横线下方的留白会按公式高度自动增加。

`protocol` 默认允许跨页。表头参数内部用 `\\` 分行，表头内部使用细灰线
分隔，最后一行表头下方使用黑实线；短协议可以把名称、输入和 `\pcreturns` 写在同一行。
正文中的第一行代码仍从行号 1 开始。每一行代码单独排版，TeX 可以在
两行之间分页；单行公式不会被拆开，续页第一行上方显示一条满宽虚线。
旧名称 `breakableprotocol` 保留为同义写法。

带公式编号的行使用 `\label{…}\tag{…}`，正文照常用 `\eqref` 引用。
不带 `\tag` 的行上，`\label` 引用行号，正文使用 `\ref`。
协议块不支持直接嵌入 `cases` 等含内部换行的环境，复杂公式可放在协议块外。

竖线依赖两次 XeLaTeX 编译，现有 `make` 已包含这两次编译。
协议框本身不跨页，长协议按轮拆成作用域完整的多个框。

## 仓库结构

```
main.tex        论文模板（字体、版式、标题注入占位）
Makefile        编译入口
pdf/            编译产物：14 篇 PDF（入库，只放 PDF）
_build/         编译现场：包装文件 + aux/log（不入库）
template/       编译依赖：wrap.py + md→LaTeX 管线脚本 + 备选模板
refs.bib        参考文献
00-*.tex 等     14 篇笔记片段（纯内容）
```

## md → LaTeX 管线（已归档）

`template/src/` 是 md 原稿，根目录 `*.tex` 是成品片段。
转换分四步：`preprocess.py → pandoc → postprocess.py → numberize.py`，
详见各脚本 docstring。需要重转时用。

补丁框首段的 🛡️ 由 TeX Live 自带的 `twemojis` 提供。
图案来自 Twitter, Inc 及其他贡献者的 [Twemoji](https://github.com/twitter/twemoji)，
采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。
