# Contributing

PRs are very welcome. This list has requirements beyond the usual awesome-list conventions, because its value is in the three analytical axes, not in coverage alone.

## 1. Separate what a paper claims from what this list infers

Entries mix three kinds of statement, and they must stay distinguishable in the prose:

- **What the paper reports** — its stated mechanism, setting, or measured result. Give the section or experimental setting where it matters.
- **What this list infers** — the proposal labels, confirmation-protocol classification, and any comparison under the unified frame. These are readings, not the authors' conclusions, and must not be phrased as though they were.

Recommendations ("should report", "may serve as a protocol option") must read as recommendations, never as descriptions of current practice.

A PR presenting an inferred reading as the paper's own claim will be asked to revise.

## 2. Record all three fields

- **Level** (L0–L5) — what object is edited
- **`[Proposal: evidence + structure]`** — what the proposer observes and how the candidate is formed (see [`docs/zo-operator-map.md`](docs/zo-operator-map.md))
- **`[Confirmation: protocol; data: relationship; reuse: scope]`** — how the state transition occurs and how confirmation data relate to proposal data (see [`docs/audit-table.md`](docs/audit-table.md))

The state-transition rule is operational. PAC-style confirmation is a conditional statistical reading that applies only when a separated-confirmation protocol meets its independence, bounded-loss, and protected-boundary assumptions. Do not use PAC-style as a synonym for a gate.

## 3. Rules specific to each axis

**For a proposal assignment**, say whether the mechanism *implements* a classical operator or only *plays its role*. On plain-text surfaces most operators exist only as analogies; use a conservative proposal label. Never write that a text method **is** a continuous ZO estimator.

**For any confirmation label with `held-out` or `fresh test` data**, state:

- what the split actually is;
- whether the set is reused across rounds;
- whether a test result could have *stopped* the candidate.

"Ran a test" is not independent confirmation. If the confirmation rule runs on clones or subsamples of the proposal failures, use `search-set` for the data relationship. A final test used only for reporting is not a persistence gate.

## 4. Mark what you could not verify

If protocol strength, split structure, reuse, or a triggering parameter is not confirmable from the primary source, write **`unverified`**. Do not infer it from the level number, from a related system, or from a secondary summary. An honest `unverified` is more useful than a confident guess.

## 5. Entry format

```text
- **Name** — "Title". Authors. *Venue* Year. [[paper]](link) — one-line description tying it to HarnessOpt. `[Proposal: evidence + structure]` `[Confirmation: protocol; data: relationship; reuse: scope]`
```

- Use `†` for preprints or very recent postings whose metadata may still change.
- Prefer the canonical venue; otherwise the arXiv abstract page.
- Keep the one-line description about **how the harness is optimized**, not about the paper's headline result.
- Before opening a PR, verify that the link resolves and that the title, authors, year, and arXiv identifier match the primary source. If a claim depends on a later version, cite that version explicitly.

## 6. Scope

The object being optimized must be **model-external state**, modified using **run-time feedback**, with the **base model frozen**. Harness *design* work and purely weight-side methods belong only in the boundary notes of the README. L5 (joint harness + weights) is included as a boundary case, not as core HarnessOpt.

## 7. Corrections to the analysis are welcome

If you think a ZO analogy is wrong, a gate protocol is misclassified, or a bound in [`docs/pac-stability.md`](docs/pac-stability.md) has an error or an unstated assumption, open an issue. Corrections to the analysis are more valuable than additional entries.

## 8. Keep Markdown math readable

Use plain `$...$` delimiters for inline math and fenced `math` blocks for displayed equations. GitHub also accepts a backtick-wrapped inline delimiter, but it adds visual noise and is not the repository default. Run `python3 scripts/check_github_math.py` before opening a PR.
