#!/usr/bin/env python3
r"""Render the reading-list sections of README.md and README_zh.md.

Input is data/papers.json only. That file is exported from the survey's two
corpus SSOTs (the audited ledger and the Tier B coverage table), so this script
never decides what an entry's editable surface or confirmation protocol is -- it
only decides how to display them.

Everything between a `<!-- BEGIN:name -->` / `<!-- END:name -->` pair is
replaced. Text outside those markers is hand-written and is left untouched.

Rendered blocks: STATS, CATALOGUE, BY-SURFACE.
"""

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "papers.json"
AUDIT_PAGE = ROOT / "docs" / "audit-table.md"
AUDIT_ANCHOR = "docs/audit-table.md#representative-systems"
TODO = "TODO"

LEVEL_ORDER = ["L0", "L1", "L2", "L3", "L4", "L5", "—"]

LEVEL_TITLES = {
    "en": {
        "L0": "L0 · Instruction and prompt",
        "L1": "L1 · Context, memory and skill",
        "L2": "L2 · Workflow, graph and architecture",
        "L3": "L3 · Harness and agent code",
        "L4": "L4 · Improver, optimizer and context mechanism",
        "L5": "L5 · Harness and model adaptation",
        "—": "Unplaced · analysis and scope anchors",
    },
    "zh": {
        "L0": "L0 · 指令与 prompt",
        "L1": "L1 · 上下文、记忆与 skill",
        "L2": "L2 · workflow、图与架构",
        "L3": "L3 · harness 与 agent 代码",
        "L4": "L4 · improver、optimizer 与上下文机制",
        "L5": "L5 · harness 与模型联合适配",
        "—": "未定级 · 分析与范围锚点",
    },
}

# Short display labels for the ledger's controlled write-authority vocabulary.
PROPOSAL_LABELS = {
    "automated proposer": "proposer",
    "automated search controller": "search",
    "automated co-learning loop": "co-learning",
    "learned runtime policy": "runtime policy",
    "recursive self-modifier": "self-modifier",
}

PROTOCOL_LABELS = {
    "write-through": "✍️ write-through",
    "search-time selection": "🔍 selection",
    "separated confirmation": "✅ separated",
}

PROTOCOL_LABELS_ZH = {
    "write-through": "✍️ 直写",
    "search-time selection": "🔍 搜索期选择",
    "separated confirmation": "✅ 分离确认",
}

STATS_TEXT = {
    "en": (
        "Counted snapshot at ledger revision `{rev}`: **{a}** entries carry all six audited "
        "fields and are counted below. A further **{b}** are coverage entries that sit "
        "outside the frozen snapshot, so no protocol is counted for them — some do have "
        "per-field notes, linked as `audit` in the catalogue.\n\n"
        "| Confirmation protocol | Meaning | Entries |\n|---|---|---:|\n"
        "| ✍️ write-through | the candidate enters persistent state with no candidate-level blocking evaluation | {wt} |\n"
        "| 🔍 selection | candidates are ranked or retained using the same data that proposed them | {st} |\n"
        "| ✅ separated | the candidate is fixed before a separate evaluation that can block promotion | {sc} |\n"
        "| — not counted | coverage entry outside the frozen snapshot; no protocol is counted | {nb} |\n\n"
        "> The scarcity of ✅ is the point of this list. Proposal mechanisms are common; "
        "candidate-level independent confirmation is not. A protocol field is only filled "
        "when a primary source establishes it — never inferred from a system's level, "
        "benchmark, or use of the word \"validation\"."
    ),
    "zh": (
        "Ledger revision `{rev}` 的计数快照：**{a}** 条填满六个审计字段并计入下表；另有 **{b}** 条覆盖条目"
        "位于冻结快照之外，不计入任何协议——其中部分已有逐字段记录，在大表中以 `audit` 链接标出。\n\n"
        "| 状态转移协议 | 含义 | 条目数 |\n|---|---|---:|\n"
        "| ✍️ 直写 | 候选进入持久状态，没有候选级的阻断性评估 | {wt} |\n"
        "| 🔍 搜索期选择 | 用提出候选的同一批数据对候选排序或保留 | {st} |\n"
        "| ✅ 分离确认 | 候选先固定，再由一次可阻断晋级的独立评估裁决 | {sc} |\n"
        "| — 不计入 | 冻结快照之外的覆盖条目；不计入任何协议 | {nb} |\n\n"
        "> ✅ 的稀缺正是本清单要说明的事。提出机制很常见，候选级的独立确认并不常见。"
        "协议字段只在 primary source 能确立时才填写——绝不从层级、benchmark 或论文里出现"
        "\"validation\" 一词反推。"
    ),
}


def audited_ids():
    """arXiv identifiers that have a row on the field-level audit page.

    This is a documentation cross-reference, not classification: several entries
    outside the counted snapshot still have per-field audit notes there, and a
    reader should be able to find them.
    """
    if not AUDIT_PAGE.exists():
        return set()
    body = AUDIT_PAGE.read_text().split("## Representative systems", 1)
    if len(body) < 2:
        return set()
    return set(re.findall(r"abs/(\d{4}\.\d{4,5})", body[1].split("\n##", 1)[0]))


AUDITED = audited_ids()


def level_key(paper):
    """Sort by editable surface, then audited entries before coverage entries."""
    base = paper["level"].rstrip("†‡")
    order = LEVEL_ORDER.index(base) if base in LEVEL_ORDER else len(LEVEL_ORDER)
    return (order, 0 if paper["tier"] == "A" else 1, paper.get("cid") or paper["arxiv"])


def headline(paper):
    """`**Name** - [Full title](url)`, collapsing to just the linked name while the
    title is still TODO so that the short name is not printed twice."""
    name = f"**{paper['name']}**{tier_mark(paper)}"
    if paper["title"] == TODO:
        return f"[{name}]({paper['url']})"
    return f"{name} · [{paper['title']}]({paper['url']})"


def links_cell(paper):
    cells = [f"[abs]({paper['url']})"]
    if paper["code"] != TODO:
        cells.append(f"[code]({paper['code']})")
    if paper["arxiv"] in AUDITED:
        cells.append(f"[audit]({AUDIT_ANCHOR})")
    return " ".join(cells)


def tier_mark(paper):
    return "" if paper["tier"] == "A" else " ᴮ"


def protocol_cell(paper, lang):
    if paper["tier"] == "B":
        return "—"
    table = PROTOCOL_LABELS if lang == "en" else PROTOCOL_LABELS_ZH
    return table.get(paper["protocol"], paper["protocol"])


def proposal_cell(paper):
    if paper["tier"] == "B":
        return "—"
    return PROPOSAL_LABELS.get(paper["proposal"], paper["proposal"])


def render_stats(payload, lang):
    counts = {p: 0 for p in PROTOCOL_LABELS}
    not_audited = 0
    for paper in payload["papers"]:
        if paper["tier"] == "B":
            not_audited += 1
        else:
            counts[paper["protocol"]] = counts.get(paper["protocol"], 0) + 1
    return STATS_TEXT[lang].format(
        rev=payload["ledger_revision"],
        a=payload["tier_a_count"],
        b=payload["tier_b_count"],
        wt=counts["write-through"],
        st=counts["search-time selection"],
        sc=counts["separated confirmation"],
        nb=not_audited,
    )


def render_catalogue(payload, lang):
    head = (
        "| Paper | Venue | Surface | Proposal | Protocol | Links |\n|---|---|---|---|---|---|"
        if lang == "en"
        else "| 论文 | 出处 | 编辑面 | 提出机制 | 协议 | 链接 |\n|---|---|---|---|---|---|"
    )
    rows = [head]
    for paper in sorted(payload["papers"], key=level_key):
        rows.append(
            f"| {headline(paper)} | {paper['venue']} | {paper['level']} "
            f"| {proposal_cell(paper)} | {protocol_cell(paper, lang)} | {links_cell(paper)} |"
        )
    return "\n".join(rows)


# Tier B notes are written for the survey and cite its section numbers. Those
# references are meaningless in the public list, so they are dropped on render
# rather than duplicated out of the upstream table.
SURVEY_SECTION_REF = re.compile(r"\s*§[0-9.]+\s*")


CJK_PUNCT = "；，。：、！？"


def public_note(note):
    """Drop the survey cross-reference and repair the whitespace it leaves behind."""
    text = re.sub(r"\s+", " ", SURVEY_SECTION_REF.sub(" ", note)).strip()
    text = re.sub(f"(?<=[{CJK_PUNCT}]) ", "", text)
    if text and text[-1] not in CJK_PUNCT + ".":
        text += "。"
    return text


def summary_line(paper, lang):
    """Hand-written TL;DR when present, otherwise a sentence built from audited fields.

    The TL;DR in paper-meta.md is English, so it overrides only the English list; the
    Chinese list falls back to the Tier B note, which is written in Chinese.
    """
    if lang == "en" and paper.get("tldr", TODO) != TODO:
        return paper["tldr"]
    if paper["tier"] == "B":
        if lang == "zh":
            return public_note(paper.get("note", ""))
        return "Coverage entry; outside the counted snapshot."
    if lang == "zh":
        return (
            f"持久化 {paper['persistence']}；{paper['proposal']} 以 "
            f"{paper['granularity']} 粒度写入；协议为 {paper['protocol']}。"
        )
    return (
        f"Persists {paper['persistence']}; {paper['proposal']} writes at "
        f"{paper['granularity']} granularity; {paper['protocol']}."
    )


def render_by_surface(payload, lang):
    groups = {}
    for paper in sorted(payload["papers"], key=level_key):
        groups.setdefault(paper["level"].rstrip("†‡"), []).append(paper)

    blocks = []
    for level in LEVEL_ORDER:
        if level not in groups:
            continue
        blocks.append(f"### {LEVEL_TITLES[lang][level]}\n")
        for paper in groups[level]:
            marks = paper["level"][len(level):]
            badge = f" `{paper['venue']}`"
            proto = "" if paper["tier"] == "B" else f" `{protocol_cell(paper, lang)}`"
            code = f" · [code]({paper['code']})" if paper["code"] != TODO else ""
            blocks.append(
                f"- {headline(paper)}{marks}{badge}{proto}{code}<br>"
                f"  {summary_line(paper, lang)}"
            )
        blocks.append("")
    return "\n".join(blocks).rstrip()


def splice(text, name, body, path):
    begin, end = f"<!-- BEGIN:{name} -->", f"<!-- END:{name} -->"
    if begin not in text or end not in text:
        raise SystemExit(f"ERROR: {path.name} is missing the {name} markers")
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{begin}\n{body}\n{end}{tail}"


def main() -> int:
    if not DATA.exists():
        print(f"ERROR: missing {DATA}; run export_awesome_data.py first", file=sys.stderr)
        return 1
    payload = json.loads(DATA.read_text())

    for lang, filename in (("en", "README.md"), ("zh", "README_zh.md")):
        path = ROOT / filename
        text = path.read_text()
        text = splice(text, "STATS", render_stats(payload, lang), path)
        text = splice(text, "CATALOGUE", render_catalogue(payload, lang), path)
        text = splice(text, "BY-SURFACE", render_by_surface(payload, lang), path)
        path.write_text(text)
        print(f"rendered 3 blocks into {filename}")

    print(f"  {len(payload['papers'])} entries at ledger revision {payload['ledger_revision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
