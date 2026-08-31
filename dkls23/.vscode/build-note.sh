#!/bin/sh
# LaTeX Workshop recipe 入口: 把 %DOCFILE% (root 文件的 stem) 映射为 make 目标.
#
#   - 笔记片段经 magic comment 声明 root=自己 → %DOCFILE%=片段 stem → make <stem>
#     (Makefile 在 _build/ 里编译, aux/log 落现场, PDF mv 到 pdf/<stem>.pdf)
#   - main.tex 保存时 root=main → 从 main.tex 的 \input 行提取当前笔记 stem
stem="$1"
if [ "$stem" = "main" ]; then
  stem=$(sed -n 's/.*\\input{\([^}]*\)}.*/\1/p' main.tex | head -1)
  [ -n "$stem" ] || { echo "!! 在 main.tex 里找不到 \\input 行" >&2; exit 1; }
fi
# 回到仓库根 (脚本在 .vscode/ 下), 不依赖 LaTeX Workshop 的 cwd
cd "$(dirname "$0")/.." || exit 1
exec make "$stem"
