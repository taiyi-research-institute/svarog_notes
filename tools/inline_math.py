"""
inline_math.py — 将 Markdown 文件中的行内双美元号 $$…$$ 替换为单美元号 $…$。

规则：
- 独占一行（去除首尾空格后仅剩 $$）的双美元号是单行公式的边界，不做替换。
- 其余行中出现的 $$ 视为行内公式定界符，将其替换为 $。

用法：
    python tools/inline_math.py <file> [<file> ...]
    python tools/inline_math.py --inplace <file> [<file> ...]

选项：
    --inplace   直接修改原文件（否则输出到标准输出）
"""

import re
import sys


def is_block_fence(line: str) -> bool:
    """判断一行是否是单行公式的边界（去除首尾空格后恰好是 $$）。"""
    return line.strip() == "$$"


def process_line(line: str) -> str:
    """将行内的 $$ 替换为 $（保留行尾换行符）。"""
    # 保留换行符
    ending = ""
    if line.endswith("\n"):
        ending = "\n"
        body = line[:-1]
    else:
        body = line

    # 将所有 $$ 替换为 $
    body = body.replace("$$", "$")
    return body + ending


def process_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    result = []
    for line in lines:
        if is_block_fence(line):
            result.append(line)
        else:
            result.append(process_line(line))
    return "".join(result)


def main():
    args = sys.argv[1:]
    inplace = False

    if "--inplace" in args:
        inplace = True
        args = [a for a in args if a != "--inplace"]

    if not args:
        print(__doc__)
        sys.exit(0)

    for path in args:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()

        processed = process_text(original)

        if inplace:
            if processed != original:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(processed)
                print(f"Updated: {path}")
            else:
                print(f"No change: {path}")
        else:
            sys.stdout.write(processed)


if __name__ == "__main__":
    main()
