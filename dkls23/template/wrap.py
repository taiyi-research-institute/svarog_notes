"""Generate a note wrapper from the shared main.tex template."""

import re
import sys
from pathlib import Path


root = Path(__file__).resolve().parent.parent
stem = sys.argv[1]
source = (root / f"{stem}.tex").read_text(encoding="utf-8")
title = re.search(r"^%\s*title:\s*(.+)$", source, re.MULTILINE)
if title is None:
    raise SystemExit(f"Missing title comment in {stem}.tex")

template = (root / "main.tex").read_text(encoding="utf-8")
template, titles = re.subn(
    r"^\\providecommand\{\\doctitle\}.*$",
    lambda _: rf"\def\doctitle{{{title.group(1)}}}",
    template,
    flags=re.MULTILINE,
)
template, inputs = re.subn(
    r"^\\input\{[^}]+\}.*$",
    lambda _: rf"\input{{../{stem}}}",
    template,
    flags=re.MULTILINE,
)
if titles != 1 or inputs != 1:
    raise SystemExit("Expected exactly one title and one input in main.tex")
sys.stdout.write(template)
