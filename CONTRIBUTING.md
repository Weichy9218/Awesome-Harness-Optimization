# Contributing

PRs are very welcome. This list has requirements beyond the usual awesome-list conventions, because its value is in the two analytical axes, not in coverage alone.

## 1. Separate what a paper claims from what this list infers

Entries mix two kinds of statement, and they must stay distinguishable in the prose:

- **What the paper reports** — its stated mechanism, setting, or measured result. Give the section or experimental setting where it matters.
- **What this list infers** — the ZO operator assignment, the PAC class, and any comparison under the unified frame. These are readings, not the authors' conclusions, and must not be phrased as though they were.

Recommendations ("should report", "may serve as a protocol option") must read as recommendations, never as descriptions of current practice.

A PR presenting an inferred reading as the paper's own claim will be asked to revise.

## 2. Place the work on all three axes

- **Level** (L0–L5) — what object is edited
- **`[ZO: operator]`** — which operator role the proposal mechanism plays (see [`docs/zo-operator-map.md`](docs/zo-operator-map.md))
- **`[PAC: class]`** — `open` / `same-set` / `independent` (see [`docs/audit-table.md`](docs/audit-table.md))

## 3. Rules specific to each axis

**For a ZO operator assignment**, say whether the mechanism *implements* the operator or *plays its role*. On plain-text surfaces most operators exist only as analogies; label them as such. Never write that a text method **is** a continuous ZO estimator.

**For a `[PAC: independent]` claim**, state:
- what the split actually is;
- whether the set is reused across rounds;
- whether a test result could have *stopped* the candidate.

"Ran a test" is not independent confirmation. If the gate runs on clones or subsamples of the training failures, the correct class is `same-set`.

## 4. Mark what you could not verify

If gate strength, split structure, or a triggering parameter is not confirmable from the primary source, write **`unverified`**. Do not infer it from the level number, from a related system, or from a secondary summary. An honest `unverified` is more useful than a confident guess.

## 5. Entry format

```
- **Name** — "Title". Authors. *Venue* Year. [[paper]](link) — one-line description tying it to HarnessOpt. `[ZO: operator]` `[PAC: class]`
```

- Use `†` for preprints or very recent postings whose metadata may still change.
- Prefer the canonical venue; otherwise the arXiv abstract page.
- Keep the one-line description about **how the harness is optimized**, not about the paper's headline result.

## 6. Scope

The object being optimized must be **model-external state**, modified using **run-time feedback**, with the **base model frozen**. Harness *design* work and purely weight-side methods belong in §12 at most. L5 (joint harness + weights) is a boundary case, included but not core.

## 7. Corrections to the analysis are welcome

If you think a ZO operator assignment is wrong, a PAC class is misjudged, or a proposition in [`docs/pac-stability.md`](docs/pac-stability.md) has an error or an unstated assumption — open an issue. Corrections to the analysis are more valuable than additional entries.
