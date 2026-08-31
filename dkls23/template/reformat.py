#!/usr/bin/env python3
"""规范化 tex 片段的行文格式(中文标点、公式排版、section 合并)。

五条规则:
  (1) 英文标点 → 中文标点(逗号/句号/分号/冒号/括号/引号), 吸收"撑宽度"空格。
      只动正文, 不碰公式、代码(verbatim)、注释行(% 开头)里的标点。
  (2) 行间公式块 \\begin{equation/align/align*} 与前文的空行删掉(渲染会浪费)。
  (3) align* → align(自动编号)。
  (4) 行内公式 $...$ 相邻是字时, 在 $ 外侧补一个空格。
  (5) \\section/\\subsection/\\subsubsection 标题合并成一行; 后面正文空一行,
      紧跟的 subsection/subsubsection 另起一行(不空行)。

用法: python3 template/reformat.py <stem> [<stem> ...]
"""
import re
import sys

LQUOTE = '\u201c'  # 左双引号 "
RQUOTE = '\u201d'  # 右双引号 "
LBRACKET = '\uff08'  # （
RBRACKET = '\uff09'  # ）
NUL = '\x00'

# 行间公式/代码环境: 整个 body 是保护区, 标点不动
PROTECTED_ENVS = (
    r'verbatim|lstlisting|equation|align|align\*|aligned|cases|gather|gather\*'
    r'|multline|split|eqnarray|eqnarray\*|array|matrix|pmatrix|bmatrix|vmatrix'
    r'|Vmatrix|Bmatrix|smallmatrix'
)
ENV_RE = re.compile(
    r'\\begin\{(' + PROTECTED_ENVS + r')\}.*?\\end\{\1\}',
    re.DOTALL,
)

SECTION_RE = re.compile(r'\\(sub){0,2}section\{')


def is_word(ch):
    """规则(4): 中英文字母/数字算字(中文 isalnum 为 True, 已覆盖)。"""
    return bool(ch) and not ch.isspace() and ch.isalnum()


# ---------------------------------------------------------------- 规则(3)
def fix_alignstar(text):
    text = text.replace('\\begin{align*}', '\\begin{align}')
    text = text.replace('\\end{align*}', '\\end{align}')
    return text


# ---------------------------------------------------------------- 规则(5)
def _match_brace(text, brace):
    """从 brace(指向 '{') 出发, 返回配对 '}' 的下标。"""
    depth, k, n = 0, brace, len(text)
    while k < n:
        if text[k] == '{':
            depth += 1
        elif text[k] == '}':
            depth -= 1
            if depth == 0:
                return k
        k += 1
    return n - 1


def fix_sections(text):
    out = []
    i, n = 0, len(text)
    while i < n:
        m = SECTION_RE.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        start = m.start()
        brace = text.index('{', start)
        k = _match_brace(text, brace)
        title = re.sub(r'[ \t]*\n[ \t]*', ' ', text[brace + 1:k]).strip()
        out.append(text[start:brace + 1] + title + '}')
        j = k + 1  # } 之后
        # 紧跟的 \label{...} 与 section 同行(不空行)
        if text[j:j + 6] == '\\label':
            lb = text.index('{', j)
            lk = _match_brace(text, lb)
            out.append(text[j:lk + 1])
            j = lk + 1
        if j < n:
            if text[j] == '\n':
                out.append('\n')
                i = j + 1
            else:
                if SECTION_RE.match(text, j):
                    out.append('\n')   # 紧跟子标题: 另起一行不空行
                else:
                    out.append('\n\n')  # 紧跟正文: 空一行
                i = j
        else:
            i = j
    return ''.join(out)


# ---------------------------------------------------------------- 规则(2)
def fix_display_blank(text):
    lines = text.split('\n')
    out = []
    begin_re = re.compile(r'[ \t]*\\begin\{(equation|align)\}')
    for line in lines:
        if begin_re.match(line) and out and out[-1].strip() == '':
            out.pop()
        out.append(line)
    return '\n'.join(out)


# ---------------------------------------------------------------- 规则(1)
def fix_quotes(s):
    """`` `` `` 和 '' 都可能是左/右引号(pandoc 混用), 按出现顺序交替配对。"""
    out = []
    i, n = 0, len(s)
    expect_open = True
    while i < n:
        if s.startswith('``', i) or s.startswith("''", i):
            out.append(LQUOTE if expect_open else RQUOTE)
            expect_open = not expect_open
            i += 2
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def fix_brackets(s):
    """( 后紧跟反斜杠命令的是代码/算术括号(如 p{...} 列宽、labelenumi 标签), 整段保持英文。"""
    out = []
    i, n = 0, len(s)
    while i < n:
        if s[i] == '(' and i + 1 < n and s[i + 1] == '\\':
            depth, j = 0, i
            while j < n:
                if s[j] == '(':
                    depth += 1
                elif s[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            out.append(s[i:j + 1])
            i = j + 1
        elif s[i] == '(':
            out.append(LBRACKET)
            i += 1
        elif s[i] == ')':
            out.append(RBRACKET)
            i += 1
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def punct_replace(s):
    s = fix_quotes(s)
    # 保护缩写点(Fig. Eq. Sec. 等, 点不转句号)
    abbrev = {}

    def protect(m):
        key = NUL + 'A' + str(len(abbrev)) + NUL
        abbrev[key] = m.group(0)
        return key

    s = re.sub(
        r'(?<![A-Za-z])(?:Fig|Eq|Sec|Ref|Thm|Lem|Def|Prop|Cor|cf|vs|etc|approx)\.',
        protect, s,
    )
    # 引号前后"撑宽度"空格吸收
    s = re.sub(r'[ \t]*' + LQUOTE, LQUOTE, s)
    s = re.sub(RQUOTE + r'[ \t]*', RQUOTE, s)
    # 括号(代码/算术括号保持英文)
    s = fix_brackets(s)
    s = re.sub(r'[ \t]*' + LBRACKET, LBRACKET, s)  # 左括号前空格吸收
    s = re.sub(RBRACKET + r'[ \t]*', RBRACKET, s)  # 右括号后空格吸收
    # 逗号 / 分号(吸后空格; 跳过 \, \; 等 LaTeX 命令)
    s = re.sub(r'(?<!\\),[ \t]*', '，', s)
    s = re.sub(r'(?<!\\);[ \t]*', '；', s)
    # 句号 / 冒号: 后跟空格→吸收; 后跟占位符(公式)或行尾→不吸收(跳过 \. \: 命令)
    s = re.sub(r'(?<!\\)\.[ \t]+', '。', s)
    s = re.sub(r'(?<!\\)\.(?=' + NUL + r'|$)', '。', s, flags=re.M)
    s = re.sub(r'(?<!\\):[ \t]+', '：', s)
    s = re.sub(r'(?<!\\):(?=' + NUL + r'|$)', '：', s, flags=re.M)
    # 还原缩写
    for key, val in abbrev.items():
        s = s.replace(key, val)
    return s


def fix_punct(text):
    stash = []

    def hide(m):
        stash.append(m.group(0))
        return NUL + str(len(stash) - 1) + NUL

    # 隐藏行间环境 → display math \[...\] → 行内公式 → 注释行
    text = ENV_RE.sub(hide, text)
    text = re.sub(r'\\\[.*?\\\]', hide, text, flags=re.DOTALL)
    text = re.sub(r'(?<!\\)\$(?!\$).*?(?<!\\)\$', hide, text, flags=re.DOTALL)
    text = re.sub(r'^[ \t]*%.*$', hide, text, flags=re.M)
    # 正文标点替换
    text = punct_replace(text)
    # 还原
    def unhide(m):
        return stash[int(m.group(1))]
    return re.sub(NUL + r'(\d+)' + NUL, unhide, text)


# ---------------------------------------------------------------- 规则(4)
def fix_inline_spacing(text):
    def repl(m):
        formula = m.group(0)
        start, end = m.start(), m.end()
        left = text[start - 1] if start > 0 else ''
        right = text[end] if end < len(text) else ''
        pre = ' ' if is_word(left) else ''
        post = ' ' if is_word(right) else ''
        return pre + formula + post
    return re.sub(
        r'(?<!\\)\$(?!\$).*?(?<!\\)\$', repl, text, flags=re.DOTALL
    )


# ---------------------------------------------------------------- 总入口
def reformat(text):
    text = fix_alignstar(text)       # (3)
    text = fix_sections(text)        # (5)
    text = fix_display_blank(text)   # (2)
    text = fix_punct(text)           # (1)
    text = fix_inline_spacing(text)  # (4)
    return text


def main():
    stems = sys.argv[1:]
    for stem in stems:
        path = f'{stem}.tex'
        with open(path, encoding='utf-8') as f:
            original = f.read()
        new = reformat(original)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        print(f'ok  {stem}')


if __name__ == '__main__':
    main()
