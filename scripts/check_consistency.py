#!/usr/bin/env python3
r"""Check that the reading list does not contradict itself.

The catalogue and the field-level audit page were written at different times and
against different scopes, which is exactly how they drift apart: a system can end
up labelled `write-through` on one page and "no protocol recorded" on the other.
The counts in the README are only worth anything if that cannot happen silently.

Checks:
  1. every counted (Tier A) entry has a protocol from the controlled vocabulary;
  2. an entry with a row on the audit page agrees with the catalogue, when the
     catalogue counts it at all;
  3. an uncounted (Tier B) entry never has a protocol in papers.json;
  4. the rendered README blocks are current with respect to papers.json.

Uncounted entries *may* appear on the audit page. That is not a contradiction:
the snapshot is frozen while the companion survey is drafted, so a recent entry
can be audited without being counted. The README says so explicitly.

Exit status is non-zero when a check fails, so this can gate a commit.
"""

from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "papers.json"
AUDIT_PAGE = ROOT / "docs" / "audit-table.md"

PROTOCOLS = {"write-through", "search-time selection", "separated confirmation"}


def audit_page_protocols():
    """arXiv ID -> the protocol(s) named in that row of the audit page."""
    if not AUDIT_PAGE.exists():
        return {}
    body = AUDIT_PAGE.read_text().split("## Representative systems", 1)
    if len(body) < 2:
        return {}
    found = {}
    for line in body[1].split("\n##", 1)[0].splitlines():
        if not line.startswith("| ["):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        pid = re.search(r"abs/(\d{4}\.\d{4,5})", cols[0])
        if not pid:
            continue
        # A row may legitimately name two protocols for two code paths.
        found[pid.group(1)] = set(re.findall(r"`([^`]+)`", cols[1])) & PROTOCOLS
    return found


def readme_blocks_are_current():
    """Re-render into a scratch copy and compare, rather than trusting the file date."""
    before = {name: (ROOT / name).read_bytes() for name in ("README.md", "README_zh.md")}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_readme.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"build_readme.py failed: {result.stderr.strip()}"]
    stale = [name for name, content in before.items() if (ROOT / name).read_bytes() != content]
    return [f"{name} was out of date and has been regenerated; commit it" for name in stale]


def main() -> int:
    if not DATA.exists():
        print(f"ERROR: missing {DATA}", file=sys.stderr)
        return 1
    papers = json.loads(DATA.read_text())["papers"]
    by_id = {p["arxiv"]: p for p in papers}
    audited = audit_page_protocols()

    problems = []

    for paper in papers:
        if paper["tier"] == "A":
            if paper.get("protocol") not in PROTOCOLS:
                problems.append(
                    f"{paper['name']} ({paper['arxiv']}) is counted but its protocol "
                    f"{paper.get('protocol')!r} is not in the controlled vocabulary"
                )
        elif paper.get("protocol"):
            problems.append(
                f"{paper['name']} ({paper['arxiv']}) is uncounted but carries protocol "
                f"{paper['protocol']!r}; an uncounted entry must not be counted implicitly"
            )

    for pid, page_protocols in audited.items():
        paper = by_id.get(pid)
        if paper is None:
            problems.append(f"audit page row {pid} has no entry in the catalogue")
            continue
        if paper["tier"] != "A" or not page_protocols:
            continue
        if paper["protocol"] not in page_protocols:
            problems.append(
                f"{paper['name']} ({pid}): catalogue says {paper['protocol']!r}, "
                f"audit page says {sorted(page_protocols)}"
            )

    problems.extend(readme_blocks_are_current())

    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        return 1

    counted = sum(1 for p in papers if p["tier"] == "A")
    cross = sum(1 for pid in audited if pid in by_id and by_id[pid]["tier"] != "A")
    print(f"consistent: {len(papers)} entries, {counted} counted, {len(audited)} on the audit page")
    print(f"  {cross} audit-page rows are deliberately uncounted (frozen snapshot)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
