# Confirmation-Protocol Audit

This table records the protocol fields needed to interpret a persistent harness update. It is a representative audit, deliberately smaller than the paper catalogue: uncertain details are marked `unverified` rather than inferred from a paper's level, benchmark, or use of the word “validation.” The 11/19/3 protocol counts cited in the README and manuscript refer to the broader audited set, not to the rows displayed on this page.

## State-transition protocols

| Protocol | Meaning |
|---|---|
| `write-through` | the candidate enters the next persistent state without a candidate-level blocking evaluation |
| `search-time selection` | candidates are ranked or retained using proposal/search data, and the selected object enters the next state |
| `separated confirmation` | a candidate is fixed before a separate confirmation evaluation can block promotion |

## Data relationships and controls

| Label | Meaning |
|---|---|
| `open` | no blocking confirmation rule is identified; use as a data-relationship label for write-through updates |
| `search-set` | proposal and selection use the same observed tasks |
| `held-out` | a separate set can reject candidates; repeated reuse still creates adaptive dependence |
| `fresh test` | untouched data evaluate a candidate fixed by the completed selection process; this is not a gate unless it can block persistence |
| `human review` | a person can block persistence; this is governance evidence, not statistical independence |
| `retrospective` | later evidence can trigger rollback; it does not confirm the candidate before persistence |
| `unverified` | the primary source does not establish the protocol field; do not infer it from the system's level or benchmark |

“Disjoint” describes a split at creation time. “Fresh” additionally requires that the set has not influenced the candidate through earlier scores or accept/reject decisions.

The state-transition protocol is operational; PAC-style confirmation is a conditional statistical interpretation that requires the `separated confirmation` structure plus independence, bounded-loss, and protected-boundary assumptions. Plugin registration, isolation, activation, and cleanup are lifecycle fields in this audit; they affect whether rejection restores behavior, not whether confirmation data are independent.

## Representative systems

| System | State-transition protocol | Blocking rule / persistence path | Data relationship | Reuse / final test | Evaluator protection | Rollback | Evidence status |
|---|---|---|---|---|---|---|---|
| [Reflexion](https://arxiv.org/abs/2303.11366) | `write-through` | reflection is written to episodic memory | `open` | not applicable | unverified | unverified | mechanism reported in paper; governance fields not audited here |
| [Voyager](https://arxiv.org/abs/2305.16291) | `write-through` | executable skills are added after synthesis/debugging | `open` | no fresh confirmation identified in this audit | unverified | unverified | compile/debug checks are feasibility checks, not evidence of fresh-task benefit |
| [OPRO](https://arxiv.org/abs/2309.03409) | `search-time selection` | score-based selection | `search-set` | separate evaluation may report final performance; exact reuse should be read from each experiment | unverified | not central | search mechanism reported; per-experiment split details require source inspection |
| [MIPROv2](https://arxiv.org/abs/2406.11695) | `search-time selection` | Bayesian optimization selects candidates | `search-set` / validation selection | reused during optimization | unverified | not central | protocol terminology varies by DSPy experiment; do not relabel as fresh confirmation |
| [GEPA](https://arxiv.org/abs/2507.19457) | `search-time selection` | Pareto selection can reject candidates | `search-set` | final-test isolation should be checked per reported experiment | unverified | archive-based | parent/child scores and Pareto selection are search-time evidence, not independent confirmation |
| [SkillCAT](https://arxiv.org/abs/2606.13317) | `search-time selection` | assessment-augmented replay can reject a patch before merge | `search-set` | source-task clones are part of the proposal/selection process; cross-task confirmation requires source inspection | unverified | patch merge; behavioral rollback unverified | full text §3, Algorithm 1, and Eq. (2–4) report contrastive extraction, clone replay, thresholded selection, and hierarchical merge; no independent confirmation inferred |
| [SkillAdaptor](https://arxiv.org/abs/2606.01311) | `search-time selection` | qualification re-executes the current and candidate skill collections on $Q$ and accepts only when $\Delta\ge0$ | `search-set` | $Q$ supplies failure trajectories and qualification across adaptation rounds; no independent confirmation identified | sandbox, tools, grading pipeline, and aggregation held fixed in the reported setup | rejected collection discarded; parent retained | full text §3 and Eq. (8) report the qualification rule; this is selection on the adaptation set, not separated confirmation |
| [SkillForge](https://arxiv.org/abs/2604.08618) | `write-through` | each optimized `Skill_v_{n+1}` is committed after the development batch; the held-out split is not a blocking gate | `search-set` / `fresh test` | three sequential development splits drive evolution; fourth split is held out for final generalization reporting | benchmark runtime and judge setup described; enforcement details require source inspection | version history is reported; behavioral rollback unverified | full text §2.7 and §3.1.1 report round commits and the held-out split; do not relabel the final test as promotion confirmation |
| [SkillOpt](https://arxiv.org/abs/2605.23904) | `separated confirmation` | validation can reject a proposed skill edit | `held-out` | three-way split; test locked for final reporting; selection set reused across rounds | unverified | rejected-edit buffer / state retention reported | split and edit-loop facts reported in paper |
| [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) | `separated confirmation` | compile, smoke, then fuller evaluation | `held-out` | reuse count and final-test handling should be reported explicitly when results are cited | compile isolation described; permission boundary unverified | candidate rejection reported | staged gate reported; full statistical independence not inferred |
| [Trace2Skill](https://arxiv.org/abs/2603.25158) | `write-through` (default) / `search-time selection` (selective path) | default path aggregates learned patches; selective path evaluates a validation subset | `open` (default) / `search-set` (selective path) | no independent confirmation inferred from either path | unverified | unverified | the top-level split and the candidate-level gate are separate properties |
| [STOP](https://arxiv.org/abs/2310.02304) | `search-time selection` | empirical meta-utility selects improvers | `search-set` | theoretical bounded-program analysis is separate from experimental freshness | sandbox/governance not treated as a statistical guarantee | not central | Appendix A.2 motivates a finite-class bound, not a claim about all harness edits |
| [MCE](https://arxiv.org/abs/2601.21557) | `search-time selection` | best-so-far context/skill pair is selected by validation performance in the bi-level loop | `search-set` | validation is reused across outer iterations; no independent promotion set identified | unverified | best-so-far retention; behavioral rollback unverified | full text §3.2–3.3 and Algorithm 1 report outer skill evolution, inner context optimization, and validation-based selection |
| [AHE](https://arxiv.org/abs/2604.25850) | `write-through` | prediction manifest plus later regression checks | `retrospective` | later observations depend on deployed history | unverified | reported | rollback is recovery evidence, not pre-persistence confirmation |
| [AutoHarness](https://arxiv.org/abs/2603.03329) | `unverified` | iterative code-harness refinement from environment feedback; candidate-level blocking rule not established | `unverified` | task/game feedback is reported; split and reuse require source inspection | unverified | unverified | abstract establishes synthesized code harness and iterative refinement, not a persistence protocol |
| [Meta-Harness](https://arxiv.org/abs/2603.28052) | `search-time selection` | scored candidates form a Pareto frontier | `search-set`; split details depend on benchmark | expensive terminal setting does not by itself establish a fresh split | filesystem boundary described; evaluator protection requires source-level audit | candidate isolation reported | do not use the older `independent` label |
| [Self-Harness](https://arxiv.org/abs/2606.09498) | `separated confirmation` | held-in and held-out outcomes can block promotion | `held-out` | fixed split across rounds; cross-round reuse must be reported | evaluator boundary and permission details require source-level audit | accept/reject recorded | separated confirmation at the single-round level; not automatically fresh across rounds |
| [Ouroboros](https://arxiv.org/abs/2608.08311) | `write-through` | human review can block a reviewed commit | `human review` | no statistical independence follows from review alone | review boundary reported | version-control rollback plausible; behavioral completeness unverified | governance claim only |

The table does not certify these systems. It records what kind of evidence a cited mechanism can support and identifies fields that need source-level verification before making a stronger claim.

## Boundary readings

Some papers are important to the mainline but do not satisfy every inclusion condition. [Continual Harness](https://arxiv.org/abs/2605.09998) performs online refinement of prompts, sub-agents, skills, and memory within a continuing run, so it is a boundary reading for the distinction between online adaptation and cross-run persistent state. [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) is an evaluation study rather than a new transition protocol; it separates the ability to produce useful updates from the ability to use them during task solving. [Code as Agent Harness](https://arxiv.org/abs/2605.18747) is a scope and architecture survey, not evidence of a candidate-level gate.

## Literature extension queue

The [literature map](literature-map.md) keeps the expansion mainline-oriented. It lists direct harness evolution, proposal/search, confirmation/trajectory evaluation, and risk/governance anchors; the entries are coverage targets and do not change the protocol counts above until their state-transition fields are audited.

## Cross-cutting observations

1. **Editable-surface size does not determine protocol strength.** A code-editing system may be write-through; a narrow skill editor may use a three-way split.
2. **Proposal aggregation and candidate confirmation are different.** Batch evidence may reduce sensitivity to one trace without making the selection set fresh.
3. **Human review, sandboxing, and rollback are governance controls.** They are valuable, but none creates an i.i.d. sample or removes adaptive reuse.
4. **A final locked test has a distinct role.** It evaluates the completed procedure; it should not be used to steer further edits if it is to remain fresh.
5. **File restoration is not necessarily state restoration.** Processes, caches, registries, external services, and persistent memory must also be covered.

## Minimum reporting schema

For each experiment, report:

1. proposal/search, selection, regression, and final-test data, with counts and split ratios;
2. which result can block persistence;
3. reuse count and information revealed per query;
4. round and candidate counts, including rejected candidates scored by the evaluator;
5. runtime protection for evaluator, weights, and task data;
6. the rollback unit and a behavioral restoration check;
7. for pluginized runtimes, component version, dependency, activation, and cleanup records;
8. safety and permission checks relevant to newly introduced tools or interactions; and
9. a direct citation to the section, table, appendix, or code path supporting each field.

If a field is absent from the primary source, use `unverified`. Do not fill it from a related system or a secondary summary.
