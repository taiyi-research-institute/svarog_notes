#!/usr/bin/env python3
"""Postprocess pandoc-generated LaTeX fragments.

1. Unwrap \[...\] around \begin{align...} blocks (amsmath nesting error).
2. Drop pandoc's hex-encoded \label{ux...} for CJK headings.
3. Drop \tightlist lines (undefined outside pandoc's template).
4. Rewrite \(...\) / \[...\] to $...$ / $$...$$.
"""
import re
import sys

WRAPPED_ALIGN = re.compile(
    r"\\\[\s*(\\begin\{(?:align\*?|equation\*?|gather\*?|multline\*?)\}.*?"
    r"\\end\{(?:align\*?|equation\*?|gather\*?|multline\*?)\})\s*\\\]",
    re.DOTALL,
)
LABEL = re.compile(r"\\label\{[0-9a-z._-]*ux[0-9a-f]{4}[0-9a-z._-]*\}\s*")
TIGHTLIST = re.compile(r"^\s*\\tightlist\s*$", re.MULTILINE)


def dollar_math(text: str) -> str:
    """Rewrite pandoc's \\(...\\) / \\[...\\] to $...$ / equation*.

    Every display block becomes \\begin{equation*}...\\end{equation*}
    (bare \\begin{align} blocks from the earlier unwrap stay untouched).
    """
    out = []
    in_verb = False
    in_disp = False
    disp = []
    for ln in text.split("\n"):
        s = ln.strip()
        if s == r"\begin{verbatim}":
            in_verb = True
        elif s == r"\end{verbatim}":
            in_verb = False
        if in_verb:
            out.append(ln)
            continue
        if in_disp:
            if s == r"\]":
                body = "\n".join(disp)
                out.extend([r"\begin{equation*}", body, r"\end{equation*}"])
                disp = []
                in_disp = False
            else:
                disp.append(ln)
        elif s == r"\[":
            in_disp = True
        else:
            out.append(ln.replace(r"\(", "$").replace(r"\)", "$"))
    return "\n".join(out)


HDR = re.compile(r"\\(?:sub)*section\{|\\paragraph\{")
VERBATIM = re.compile(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", re.DOTALL)
NUM = re.compile(
    r"^(?:附录\s*[A-Z]\.\s*|Round\s+\d+\.\s*|"
    r"[0-9A-Z]+(?:\.[0-9A-Z]+)+\.\([^)]*\)\.?\s*|"  # 2.2.(1) / 2.2.(1).
    r"[0-9A-Z]+(?:\.[0-9A-Z]+)+(?=[\$\\a-z\s])|"     # 2.3.1$w_i$ / 2.3.1w\_i
    r"[0-9A-Z]+(?:\.[0-9A-Z]+)*\.(?![0-9A-Z])\s*)"   # 0. / 2.2. / 2.3.1.
)


def _arg(t: str, start: int):
    """Return (content, index-after-closing-brace) of a braced group
    starting at t[start] == '{', skipping escaped chars."""
    depth = 1
    i = start + 1
    while i < len(t) and depth > 0:
        c = t[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return t[start + 1 : i - 1], i


def strip_heading_numbers(text: str) -> str:
    """Drop hand-written numbering from heading titles (LaTeX numbers
    sections automatically). Handles plain and \\texorpdfstring args,
    headings that span multiple lines, and several headings on one
    line. Matches inside verbatim blocks are skipped."""
    verb = [m.span() for m in VERBATIM.finditer(text)]

    def in_verb(p):
        return any(a <= p < b for a, b in verb)

    pos = 0
    out = []
    for m in HDR.finditer(text):
        if in_verb(m.start()):
            continue
        out.append(text[pos : m.end()])
        title, end = _arg(text, m.end() - 1)  # m.end() is just past '{'
        if title.startswith(r"\texorpdfstring{"):
            a, k = _arg(title, len(r"\texorpdfstring{") - 1)
            b, _ = _arg(title, k)
            title = r"\texorpdfstring{" + NUM.sub("", a) + "}{" + NUM.sub("", b) + "}"
        else:
            title = NUM.sub("", title)
        out.append(title + "}")  # the '{' is already in text[pos:m.end()]
        pos = end
    out.append(text[pos:])
    return "".join(out)


def post(text: str) -> str:
    text = WRAPPED_ALIGN.sub(r"\1", text)
    text = LABEL.sub("", text)
    text = TIGHTLIST.sub("", text)
    text = dollar_math(text)
    text = strip_heading_numbers(text)
    return text


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        new = post(src)
        if new != src:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
        print(f"postprocessed {path}")
