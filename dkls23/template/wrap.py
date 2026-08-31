#!/usr/bin/env python3
"""从 main.tex 生成单篇包装文件 _build/<stem>.tex.

做两件事:
  1. 把唯一的 \\input{...} 行替换成 \\input{../<stem>}
     (包装文件在 _build/, 片段在根目录)
  2. 从片段顶部 "% title: ..." 注释提取标题, 注入到 \\doctitle
     (main.tex 里是 \\providecommand{\\doctitle}{未命名笔记} 占位)
"""
import re
import sys

stem = sys.argv[1]

main = open('main.tex', encoding='utf-8').read()

# 提取片段标题 (pandoc 遗留的 "% title: xxx" 元数据注释)
title = stem  # 缺省用文件名
for line in open(f'{stem}.tex', encoding='utf-8'):
    m = re.match(r'^%\s*title:\s*(.*)$', line)
    if m:
        title = m.group(1).strip()
        break

# 替换 \input 行
main, n1 = re.subn(r'\\input\{[^}]*\}', lambda m: f'\\input{{../{stem}}}', main)
# 注入标题 (title 原样放回, Python 无 shell/sed 的转义坑)
main, n2 = re.subn(
    r'\\providecommand\{\\doctitle\}\{[^}]*\}',
    lambda m: f'\\def\\doctitle{{{title}}}',
    main,
)
assert n1 == 1, f'\\input 行应恰好一处, 实际 {n1}'
assert n2 == 1, f'\\doctitle 占位应恰好一处, 实际 {n2}'

sys.stdout.write(main)
