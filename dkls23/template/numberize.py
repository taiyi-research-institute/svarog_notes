#!/usr/bin/env python3
"""Convert \\begin{equation*} -> \\begin{equation} and inject \\label.

Label scheme (stable across pipeline re-runs):
  tagged:   eq:<stem>:<tag>   (tag name sanitized; -2/-3 suffix on in-file dupes)
  untagged: eq:<stem>:<n>     (n = 1-based position among ALL equation envs)

Keeps \\tag{...} (semantic names, e.g. \\tag{umat}, displayed as the equation
number). Skips verbatim blocks. Idempotent: a body that already carries a
\\label is left alone. Does not touch align/align* environment rows.
"""
import re
import sys

EQBLOCK = re.compile(
    r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}", re.S
)
TAG = re.compile(r"\\tag\{([^{}]*)\}")
LABEL = re.compile(r"\\label\{[^{}]*\}")
SAFE = re.compile(r"[^A-Za-z0-9_-]+")
VERBATIM = re.compile(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", re.S)


def convert(path: str) -> int:
    stem = path.rsplit("/", 1)[-1][:-4]
    text = open(path, encoding="utf-8").read()
    verb = [m.span() for m in VERBATIM.finditer(text)]

    def in_verb(p: int) -> bool:
        return any(a <= p < b for a, b in verb)

    used = set()
    n = 0
    changed = 0

    def repl(m):
        nonlocal n, changed
        n += 1
        body = m.group(1).strip()
        # body keeps inner structure; stripping outer whitespace so the
        # equation env has no blank lines inside (blank line = \par in
        # math mode -> "Missing $ inserted" cascade).
        if LABEL.search(body):
            return m.group(0)
        tm = TAG.search(body)
        if tm:
            name = SAFE.sub("-", tm.group(1)).strip("-")
            if not name:
                name = str(n)
            base = f"eq:{stem}:{name}"
        else:
            base = f"eq:{stem}:{n}"
        cand, k = base, 2
        while cand in used:
            cand, k = f"{base}-{k}", k + 1
        used.add(cand)
        changed += 1
        return (f"\\begin{{equation}}\n\\label{{{cand}}}\n"
                + body + "\n\\end{equation}")

    # rebuild, skipping verbatim regions
    out = []
    pos = 0
    for m in EQBLOCK.finditer(text):
        if in_verb(m.start()):
            continue
        out.append(text[pos : m.start()])
        out.append(repl(m))
        pos = m.end()
    out.append(text[pos:])
    new = "".join(out)
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
    return changed


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(f"{path}: {convert(path)} labels injected")
