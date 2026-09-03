#!/usr/bin/env python3
"""Check Markdown math for syntax accepted by GitHub's renderer."""

from __future__ import annotations

import re
import sys
from pathlib import Path


INLINE_MATH = re.compile(r"(?<!\\)\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)")
INLINE_CODE = re.compile(r"(?<!`)`+(?!`)(.+?)(?<!`)`+(?!`)")
# GitHub also supports $`...`$, but the repository standardizes on plain
# $...$ because its current formulas do not need Markdown disambiguation.
BACKTICK_INLINE_MATH = re.compile(r"\$`[^`\n]*`\$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})([A-Za-z0-9_-]*)\s*$")


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    in_fence = False
    fence_char = ""
    fence_length = 0
    fence_language = ""

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fence_match = FENCE.match(line)
        if fence_match:
            marker, language = fence_match.groups()
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_length = len(marker)
                fence_language = language
            elif marker[0] == fence_char and len(marker) >= fence_length:
                in_fence = False
                fence_language = ""
            continue

        if "\\operatorname" in line:
            errors.append(f"{path}:{line_number}: unsupported \\operatorname macro")
        if "\\(" in line or "\\)" in line:
            errors.append(f"{path}:{line_number}: use GitHub math delimiters, not \\(...\\)")

        # Math fences may contain arbitrary LaTeX. Outside a fence, remove
        # code spans and valid $...$ spans first; any remaining single dollar
        # is an unmatched inline delimiter (or an unescaped dollar sign) that
        # needs review.
        if not in_fence:
            if BACKTICK_INLINE_MATH.search(line):
                errors.append(
                    f"{path}:{line_number}: backtick-wrapped inline math; use $...$"
                )
            remaining = INLINE_CODE.sub("", line)
            remaining = INLINE_MATH.sub("", remaining).replace("$$", "")
            remaining = remaining.replace(r"\$", "")
            if "$" not in remaining:
                continue
            errors.append(
                f"{path}:{line_number}: unprotected inline math; use $...$"
            )

    if in_fence:
        errors.append(f"{path}: unterminated {fence_language or fence_char + ' fence'}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    markdown_files = sorted(root.glob("*.md")) + sorted((root / "docs").glob("*.md"))
    errors = [error for path in markdown_files for error in check_file(path)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"checked GitHub math in {len(markdown_files)} Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
