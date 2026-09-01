# Validation-Protocol Audit

This table records the protocol fields needed to interpret a persistent harness update. It is deliberately smaller than the paper catalogue: uncertain details are marked `unverified` rather than inferred from a paper's level, benchmark, or use of the word “validation.”

## Protocol vocabulary

| Label | Meaning |
|---|---|
| `open` | no evaluation can block the proposed state from becoming persistent |
| `search-set` | proposal and selection use the same observed tasks |
| `held-out` | a separate set can reject candidates, but may be reused during search |
| `fresh test` | untouched data evaluate a candidate fixed by the completed selection process |
| `human review` | a person can block persistence; this is governance evidence, not statistical independence |
| `retrospective` | later evidence can trigger rollback; it does not confirm the candidate before persistence |

“Disjoint” describes a split at creation time. “Fresh” additionally requires that the set has not influenced the candidate through earlier scores or accept/reject decisions.

## Representative systems

| System | Persistence gate | Data relationship | Reuse / final test | Evaluator protection | Rollback | Evidence status |
|---|---|---|---|---|---|---|
| [Reflexion](https://arxiv.org/abs/2303.11366) | reflection is written to episodic memory | `open` | not applicable | unverified | unverified | mechanism reported in paper; governance fields not audited here |
| [Voyager](https://arxiv.org/abs/2305.16291) | executable skills are added after synthesis/debugging | `open` for persistence confirmation | no fresh confirmation identified in this audit | unverified | unverified | compile/debug checks are feasibility checks, not evidence of fresh-task benefit |
| [OPRO](https://arxiv.org/abs/2309.03409) | score-based selection | `search-set` | separate evaluation may report final performance; exact reuse should be read from each experiment | unverified | not central | search mechanism reported; per-experiment split details require source inspection |
| [MIPROv2](https://arxiv.org/abs/2406.11695) | Bayesian optimization selects candidates | `search-set` / validation selection | reused during optimization | unverified | not central | protocol terminology varies by DSPy experiment; do not relabel as fresh confirmation |
| [GEPA](https://arxiv.org/abs/2507.19457) | Pareto selection can reject candidates | `held-out`, reuse details experiment-dependent | final-test isolation should be checked per reported experiment | unverified | archive-based | `held-out` does not imply independence after reuse |
| [SkillOpt](https://arxiv.org/abs/2605.23904) | validation can reject a proposed skill edit | `held-out` selection | three-way split; test locked for final reporting; selection set reused across rounds | unverified | rejected-edit buffer / state retention reported | split and edit-loop facts reported in paper |
| [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) | compile, smoke, then fuller evaluation | `held-out` selection | reuse count and final-test handling should be reported explicitly when results are cited | compile isolation described; permission boundary unverified | candidate rejection reported | staged gate reported; full statistical independence not inferred |
| [Trace2Skill](https://arxiv.org/abs/2603.25158) | patch evaluation/merging on training-derived evidence | `search-set` | no independent confirmation inferred from the gate | unverified | unverified | training-derived relation reported; do not label as independent |
| [STOP](https://arxiv.org/abs/2310.02304) | empirical meta-utility selects improvers | `search-set` | theoretical bounded-program analysis is separate from experimental freshness | sandbox/governance not treated as a statistical guarantee | not central | Appendix A.2 motivates a finite-class bound, not a claim about all harness edits |
| [AHE](https://arxiv.org/abs/2604.25850) | prediction manifest plus later regression checks | `retrospective` | later observations depend on deployed history | unverified | reported | rollback is recovery evidence, not pre-persistence confirmation |
| [Meta-Harness](https://arxiv.org/abs/2603.28052) | scored candidates form a Pareto frontier | `search-set`; split details depend on benchmark | expensive terminal setting does not by itself establish a fresh split | filesystem boundary described; evaluator protection requires source-level audit | candidate isolation reported | do not use the older `independent` label |
| [Ouroboros](https://arxiv.org/abs/2608.08311) | reviewed commits enter the evolving core | `human review` | no statistical independence follows from review alone | review boundary reported | version-control rollback plausible; behavioral completeness unverified | governance claim only |

The table does not certify these systems. It records what kind of evidence a cited mechanism can support and identifies fields that need source-level verification before making a stronger claim.

## Cross-cutting observations

1. **Editable-surface size does not determine gate strength.** A code-editing system may be open loop; a narrow skill editor may use a three-way split.
2. **Proposal aggregation and candidate confirmation are different.** Batch evidence may reduce sensitivity to one trace without making the selection set fresh.
3. **Human review, sandboxing, and rollback are governance controls.** They are valuable, but none creates an i.i.d. sample or removes adaptive reuse.
4. **A final locked test has a distinct role.** It evaluates the completed procedure; it should not be used to steer further edits if it is to remain fresh.
5. **File restoration is not necessarily state restoration.** Processes, caches, registries, external services, and persistent memory must also be covered.

## Minimum reporting schema

For each experiment, report:

1. proposal/search, selection, regression, and final-test data, with counts;
2. which result can block persistence;
3. reuse count and information revealed per query;
4. round and candidate counts;
5. runtime protection for evaluator, weights, and task data;
6. the rollback unit and a behavioral restoration check;
7. safety and permission checks relevant to newly introduced tools or interactions; and
8. a direct citation to the section, table, appendix, or code path supporting each field.

If a field is absent from the primary source, use `unverified`. Do not fill it from a related system or a secondary summary.
