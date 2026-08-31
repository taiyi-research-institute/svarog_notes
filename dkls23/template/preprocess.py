#!/usr/bin/env python3
"""Preprocess Jupyter-Book-style md notes before pandoc conversion to LaTeX.

1. Drop blank lines inside $$...$$ display-math blocks (they break
   pandoc's tex_math_dollars parsing).
2. Move any \tag{...} trailing after \end{align...} onto the last row
   (invalid in LaTeX where it is).
3. Strip emoji and variation selectors.
4. Collapse [text](./other-note.md) links to plain `text`.
"""
import re
import sys

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F️]"
)
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
TRAILING_TAG = re.compile(r"\s*\\tag\{([^}]*)\}\s*$")
END_ENV = re.compile(r"\\end\{align\*?\}\s*$")

# Unicode math symbols -> LaTeX, per context.
MATH_CMD = {
    "⇒": r"\Rightarrow",
    "⇔": r"\Leftrightarrow",
    "→": r"\rightarrow",
    "←": r"\leftarrow",
    "↔": r"\leftrightarrow",
    "≠": r"\neq",
    "≤": r"\leq",
    "≥": r"\geq",
    "∈": r"\in",
    "∉": r"\notin",
    "≈": r"\approx",
    "⊕": r"\oplus",
    "⊗": r"\otimes",
    "−": "-",
    "μ": r"\mu",
    "⊋": r"\supsetneq",
}
# text mode: the same commands, but wrapped in inline math
TEXT_CMD = {k: f"${v}$" for k, v in MATH_CMD.items()}


def translate_symbols(text: str) -> str:
    """Translate Unicode math symbols, context-aware (in/out of $...$)."""
    out = []
    in_code = False
    in_disp = False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            in_code = not in_code
        if in_code:
            out.append(ln)
            continue
        if ln.strip() == "$$":
            in_disp = not in_disp
            out.append(ln)
            continue
        if in_disp:
            out.append("".join(MATH_CMD.get(c, c) for c in ln))
            continue
        parts = re.split(r"(\$[^$]*\$)", ln)
        line = ""
        for seg in parts:
            if seg.startswith("$") and seg.endswith("$") and len(seg) > 2:
                inner = "".join(MATH_CMD.get(c, c) for c in seg[1:-1])
                line += "$" + inner + "$"
            else:
                line += "".join(TEXT_CMD.get(c, c) for c in seg)
        out.append(line)
    return "\n".join(out)


def fix_trailing_tag(body: str) -> str:
    """Move \tag{X} trailing after \end{align} onto the last row."""
    m = TRAILING_TAG.search(body)
    if not m:
        return body
    tag = m.group(1)
    body = body[: m.start()]
    endm = END_ENV.search(body)
    if not endm:
        return body + f" \\tag{{{tag}}}"  # no env end found: put it back
    before_end = body[: endm.start()]
    if before_end.rstrip().endswith("\\\\"):
        k = before_end.rstrip()
        before_end = k[:-2].rstrip() + f" \\tag{{{tag}}} \\\\"
    else:
        before_end = before_end.rstrip() + f" \\tag{{{tag}}}\n"
    return before_end + body[endm.start():]


def clean(text: str) -> str:
    lines = text.split("\n")
    out = []
    buf = []
    in_math = False
    in_code = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
        if s == "$$":
            if in_math:
                out.extend(fix_trailing_tag("\n".join(buf)).split("\n"))
                buf = []
            out.append("$$")
            in_math = not in_math
        elif in_math:
            if s:
                buf.append(ln)
        else:
            out.append(ln)
    text = "\n".join(out)
    # pandoc's $ math requires the delimiters to hug the content:
    # normalize "$ x ... y $" -> "$x ... y$" (skip code fences)
    fixed = []
    in_code = False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            in_code = not in_code
        if not in_code:
            ln = re.sub(r"(?<!\$)\$ +", "$", ln)
            ln = re.sub(r" +\$(?!\$)", "$", ln)
        fixed.append(ln)
    text = "\n".join(fixed)
    text = EMOJI.sub("", text)

    def repl(m):
        label, target = m.group(1), m.group(2)
        if ".md" in target:  # internal note link, possibly with #fragment
            return label
        return m.group(0)  # keep external links for pandoc's \href

    text = MD_LINK.sub(repl, text)
    return translate_symbols(text)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(clean(src))
        print(f"cleaned {path}")
