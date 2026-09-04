# Contributing

Pull requests are welcome. This list has requirements beyond the usual awesome-list conventions, because its value is in the three analytical axes — editable surface, proposal mechanism, confirmation protocol — and not in coverage alone.

The most important thing to know before you start: **the catalogue in the README is generated.** Editing the table by hand will be overwritten on the next build.

## 1. How the data flows

```text
CORPUS-LEDGER.md  (Tier A: audited classification, upstream)
LITERATURE-DISCOVERY.md §1  (Tier B: coverage, upstream)
data/paper-meta.md  (bibliographic fields, editable here)
        │
        ▼
data/papers.json  ──  scripts/build_readme.py  ──▶  README.md / README_zh.md
```

`data/papers.json` is committed so the list builds from a single file. Everything between a `<!-- BEGIN:X -->` / `<!-- END:X -->` pair in the READMEs is machine-written; everything outside those markers is hand-written prose you may edit freely.

`data/papers.json` carries the full classification snapshot, so this repository is self-contained: you can read every audited field and rebuild the list without access to anything upstream. What is upstream is the *authority to change* those fields. Classification travels one way only — `data/paper-meta.md` carries **no** editable surface, proposal mechanism, or confirmation protocol, and a pull request may not add one.

Field-level detail for the systems that have it lives in [`docs/audit-table.md`](docs/audit-table.md); catalogue rows link to it as `audit`.

## 2. What you can change, and how

| Change | Where | Review |
|---|---|---|
| Add or fix a title, venue, code link, or `TL;DR` | [`data/paper-meta.md`](data/paper-meta.md) | merged on verification |
| Fix hand-written prose, a broken link, a typo | README sections outside the markers, or `docs/` | merged on verification |
| Add a paper | open an issue | low bar; it enters as a coverage entry (`ᴮ`), outside the counted snapshot |
| Assign or change an editable surface, proposal mechanism, or confirmation protocol | not accepted as a pull request | requires a primary-source audit upstream |
| Correct an existing classification | open an issue with the passage from the primary source | most valuable kind of report |

After editing `data/paper-meta.md`, regenerate and commit both the data and the rendered READMEs:

```bash
python3 scripts/build_readme.py       # re-render the generated blocks
python3 scripts/check_consistency.py  # catalogue vs. audit page, and that the render is current
python3 scripts/check_github_math.py  # inline math still renders on GitHub
```

`build_readme.py` reads `data/papers.json` only. If your change also needs a new row in `papers.json` — that is, a new arXiv identifier — say so in the issue or PR description; the export is run upstream.

## 3. Bibliographic fields: verify against the primary source

- **Title** — the full title from the paper itself, not from a citation service. `TODO` is the correct value while it is unverified; a plausible guess is not. The `Src` column records provenance: `bib` (authoritative), `pdf` (heuristic first-page extraction, spot-check before relying on it), `TODO` (unresolved). Set `Src` to `manual` when you correct a title by hand.
- **Venue** — `arXiv'YY` is derived from the identifier and asserts nothing about peer review. Replace it with the formal venue when the paper has one, in the repository's existing short form (`NeurIPS'24`, `ICLR'25`, `COLM'24`).
- **Code** — the canonical repository or project page. Not a mirror, not a fork, not a paper-page aggregator.
- **`TL;DR`** — optional, and **English**. It overrides the generated sentence in `README.md` only; `README_zh.md` falls back to the Chinese Tier B note. Leave `TODO` to fall back to a sentence generated from the audited fields. An override must stay consistent with those fields: it may not describe a confirmation step the protocol column does not record.

Verify that every link resolves. If a claim depends on a later arXiv version, say which version.

## 4. Separate what a paper claims from what this list infers

Entries mix two kinds of statement, and they must stay distinguishable:

- **What the paper reports** — its stated mechanism, setting, or measured result. Give the section or experimental setting where it matters.
- **What this list infers** — the proposal labels, the confirmation-protocol classification, and any comparison under the unified frame. These are readings, not the authors' conclusions, and must not be phrased as though they were.

Recommendations ("should report", "may serve as a protocol option") must read as recommendations, never as descriptions of current practice. A contribution presenting an inferred reading as the paper's own claim will be asked to revise.

## 5. Rules the classification axes follow

These govern the upstream audit. Read them before filing a classification correction, because a report that follows them can be acted on directly.

**Editable surface (L0–L5)** — what object is edited. See the level table in the README. `†` marks a boundary case (joint model–harness adaptation, runtime-only state, or self-modification of the improver); `‡` marks adjacent program-evolution work; `—` means deliberately unassigned. `ᴮ` says the entry is outside the frozen counted snapshot — a statement about the protocol counts, not about how carefully the paper was read.

**Proposal mechanism** — what the proposer observes and how the candidate is formed; see [`docs/zo-operator-map.md`](docs/zo-operator-map.md). Say whether the mechanism *implements* a classical operator or only *plays its role*. On plain-text surfaces most operators exist only as analogies, so prefer the conservative label. Never write that a text method **is** a continuous ZO estimator.

**Confirmation protocol** — how the state transition occurs and how confirmation data relate to proposal data; see [`docs/audit-table.md`](docs/audit-table.md). The three values are operational:

- `write-through` — the candidate enters persistent state with no candidate-level blocking evaluation;
- `search-time selection` — candidates are ranked or retained using the same data that proposed them;
- `separated confirmation` — the candidate is fixed before a separate evaluation that can block promotion.

For any label involving `held-out` or `fresh test` data, state what the split actually is, whether the set is reused across rounds, and whether a test result could have *stopped* the candidate. "Ran a test" is not independent confirmation. If the confirmation rule runs on clones or subsamples of the proposal failures, the data relationship is `search-set`. A final test used only for reporting is not a persistence gate.

PAC-style confirmation is a conditional statistical reading that applies only when a separated-confirmation protocol meets its independence, bounded-loss, and protected-boundary assumptions. It is not a synonym for a gate.

## 6. Mark what you could not verify

If protocol strength, split structure, reuse, or a triggering parameter is not confirmable from the primary source, the field stays empty (`—`) or `unverified`. Do not infer it from the level number, from a related system, from a benchmark score, or from the paper's use of the word "validation". An honest gap is more useful than a confident guess, and the scarcity of `separated confirmation` in the snapshot is only meaningful because the gaps are honest.

## 7. Scope

The edited object must be **model-external state**, modified using **run-time feedback**, with the **base model frozen**. Harness *design* work and purely weight-side methods are out of scope except as boundary notes. L5 (joint harness and weight adaptation) is included as a boundary case, marked `†`, not as core harness self-evolution.

## 8. Corrections to the analysis are welcome

If a ZO analogy is wrong, a protocol is misclassified, or a bound in [`docs/pac-stability.md`](docs/pac-stability.md) has an error or an unstated assumption, open an issue. Corrections to the analysis are worth more than additional entries.

## 9. Keep Markdown math readable

Use plain `$...$` delimiters for inline math and fenced `math` blocks for displayed equations. GitHub also accepts a backtick-wrapped inline delimiter, but it adds visual noise and is not the repository default. Run `python3 scripts/check_github_math.py` before opening a pull request.
