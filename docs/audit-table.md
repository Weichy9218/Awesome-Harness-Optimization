# Stability & Confirmation Audit

**What this table is.** For each system, which of the two bounds of [Axis II](pac-stability.md) its protocol can actually support — and, when it cannot, *which premise* it violates.

**What this table is not.** A quality ranking. A system may be excellent and still sit in the open-loop column; the columns record what a protocol licenses one to *conclude*, not how useful the system is.

> **[Ana] Every classification in this file is this list's reading of the published protocol, not the paper's self-description.** Where a system's gate strength could not be confirmed from the primary source, the cell reads `unverified` rather than being inferred from the level number or from secondary summaries.

**Legend** — ✅ satisfied · ⚠️ partial / conditional · ❌ not satisfied · ❔ unverified · — not applicable

---

## The two questions each column asks

| Column | Question | Bound |
|---|---|---|
| **$\beta_{\exp}$ control** | Can a single rollout anomaly hijack the update? | (B1) — stability |
| **Independent confirmation** | Was the candidate selected *before* seeing the confirming set, and is that set fresh? | (B2) — validation |
| **Multi-round status** | Which bound is the applicable reading after $T$ rounds? | Proposition A / A′ |

**[Ana]** These are orthogonal. A system with strong consensus mining and a reused selection set has good (B1) and degrading (B2); a system with a clean disjoint split and single-trace updates has the reverse. **Neither substitutes for the other.**

---

## Class 1 — Open loop (no independent confirmation)

*Experience is written straight into later state. No candidate test can stop it; there is no failure recovery path.*

| System | Level | $\beta_{\exp}$ control | Indep. confirmation | Notes |
|---|---|---|---|---|
| **Reflexion** | L1 | ❌ single-trace reflection | ❌ | **[Lit]** Bypasses dynamic validation entirely in an open loop. **[Ana]** The archetypal one-point estimator, and the highest-$\beta_{\exp}$ design in this list |
| **Voyager** | L1 | ❌ single-error trigger | ❌ | **[Ana]** Single error signals trigger local program overwrites. The skill library *is* executable, so a feasibility oracle exists — but it gates compilation, not generalization |
| **ExpeL** | L1 | ⚠️ cross-experience extraction | ❌ | **[Ana]** Extracting insights across an experience pool is a genuine $\beta_{\exp}$-reducing mechanism even absent a formal gate |
| **Dynamic Cheatsheet** | L1 | ❌ | ❌ | Test-time memory curation with no candidate rejection path |
| **ACE** | L1 | ⚠️ delta updates | ❌ | **[Ana]** Incremental delta updates act as a trust region on a text surface. The "context collapse" it prevents is a concrete instance of high $\beta_{\exp}$ |
| **ReasoningBank** | L1 | ⚠️ success+failure distillation | ❌ | **[Ana]** Success/failure pairing plays the central-difference role at the memory layer |
| **AWM** | L1 | ⚠️ workflow induction over multiple traces | ❌ | |
| **Memp** | L1 | ⚠️ | ❌ | **[Ana]** One of the few works specifying *deletion*, not only writing — relevant to the lifecycle open problem |
| **MemAct** | L1 | — (trained policy) | ❌ | Memory management as a learned policy; the bounds here are about the harness update loop, not the policy's own training |
| **Continual Harness** | L1–L3 | ❔ | ❌ | **[Ana]** Online adaptation places it directly in the small-$m$, large-$T$ regime that corollary A-2 flags |
| **Gödel Agent** | L3 | ❌ | ❌ | **[Ana]** Runtime monkey-patching makes *behaviorally exact* rollback hard, which directly threatens the monotonicity premise B-2 |
| **Alita** | L2 | ❔ | ❌ | **[Ana]** On-the-fly MCP tool generation expands the interaction surface — the case where safety probes must cover newly introduced surfaces, not only final output |

**[Ana] What can and cannot be said about this class.** These systems demonstrate *experience accumulation*: performance improves as the store grows. That is a real and reportable phenomenon. What the protocol cannot support is a confirmation claim — there is no set whose result could have stopped a bad entry, so premise (i) of (B2) is absent by construction rather than by degradation.

---

## Class 2 — Same-set scoring and selection

*Score / elitism / archive on the search tasks; a test set is reported separately at the end.*

| System | Level | $\beta_{\exp}$ control | Indep. confirmation | Notes |
|---|---|---|---|---|
| **APE** | L0 | ⚠️ population averaging | ❌ | |
| **OPRO** | L0 | ❌ scalar-return-only proposal | ❌ | **[Ana]** The meta-prompt sees (solution, score) pairs only — no trace evidence, so the semantic advantage of Axis I is unused |
| **EvoPrompt** | L0 | ⚠️ population | ❌ | |
| **Promptbreeder** | L0/L4 | ⚠️ population | ❌ | Evolves the mutation-prompts too — an L0 content / L4 mechanism hybrid |
| **ProTeGi** | L0 | ⚠️ beam over batches | ❌ | **[Ana]** "Textual gradients" are the central-difference *role* without a constructible $s-\mu u$ |
| **DSPy** | L0 | ⚠️ | ❌ | |
| **MIPROv2** | L0 | ⚠️ BO surrogate | ❌ | **[Ana]** Modeling $f$ rather than querying it blindly is a materially different ZO strategy from LLM-proposal |
| **TextGrad** | L0–L2 | ⚠️ | ❌ | |
| **ADAS** | L2 | ⚠️ archive | ❌ | |
| **AFlow** | L2 | ⚠️ MCTS | ❌ | **[Ana]** MCTS makes the exploration/exploitation schedule explicit — the adaptive-step row |
| **GPTSwarm** | L2 | ⚠️ | ❌ | **[Ana]** Edge-level REINFORCE is genuinely *not* zeroth-order over the topology; a useful boundary case |
| **AgentSquare** | L2 | ⚠️ evolution + recombination | ❌ | **[Ana]** Module slots give the cleanest objective coordinate basis in this list |
| **MaAS** | L2 | ⚠️ supernet | ❌ | |
| **MASS** | L2 | ⚠️ | ❌ | |
| **ScoreFlow** | L2 | — | ❌ | First-order boundary case (Score-DPO) |
| **FlowReasoner** | L2 | — (RL) | ❌ | |
| **EvoAgent** | L2 | ⚠️ population | ❌ | |
| **Agent Symbolic Learning** | L0–L3 | ⚠️ | ❌ | |
| **STOP** | L3–L4 | ⚠️ | ❌ | **[Lit]** Provides Lemma 1: uniform convergence over all programs of length $\le l$. **[Ana]** Proposition A is its dynamic counterpart under an anchored start and bounded per-round edits |
| **DGM** | L3 | ⚠️ open-ended archive | ❌ | **[Ana]** Large per-round $L$ with archive search — the regime where $\eta_T$ grows fastest (corollary A-3) |
| **SICA** | L3 | ⚠️ | ❌ | |
| **AutoHarness** | L3 | ❔ | ❔ | |
| **Hyperagents** | L4 | ❔ | ❔ | |
| **AlphaEvolve** | L3 | ⚠️ ensemble + population | ❌ | **[Ana]** `EVOLVE-BLOCK` is an explicit human-declared coordinate basis — a surface *engineered* so coordinate descent is implementable rather than analogical |
| **ShinkaEvolve** | L3 | ⚠️ novelty rejection | ❌ | **[Ana]** Novelty rejection sampling plays the control-variate role: steering proposals away from covered directions |
| **ThetaEvolve** | L3 | ⚠️ | ❌ | |
| **AdaEvolve** | L3 | ⚠️ adaptive schedule | ❌ | **[Ana]** The nearest published neighbor to Axis I; explicitly casts LLM-driven search as ZO |
| **ELM** | L3 | ⚠️ MAP-Elites | ❌ | **[Ana]** A diff model is a literal bounded-edit-script proposer — the concrete realization of assumption A2 |
| **AIDE** | L3 | ⚠️ tree search | ❌ | |
| **SkillWeaver** | L1 | ⚠️ | ❌ | Skill synthesis + debugging; the debug loop is a feasibility oracle, not a confirmation gate |
| **SkillCAT** | L1 | ✅ contrastive over trace pairs | ❌ | **[Lit]** Runs its gate on direct clones of the source training-failure instances |
| **SkillAdaptor** | L1 | ⚠️ step-localized | ❌ | **[Lit]** Gates on training-derived instances |
| **Trace2Skill** | L1 | ✅ map-reduce patch merging | ❌ | **[Lit]** Gates on sub-sampled training subsets. **[Ana]** Strong (B1), compromised (B2) — the cleanest illustration that the two are independent |
| **SoftSkill** | L1 | ⚠️ hard prefix bound | ❔ | **[Ana]** A rare case where the trust region is a hard dimensional constraint ($m{=}32$ tokens), not an edit-count heuristic |
| **MCE** | L1/L4 | ⚠️ | ❔ | Bi-level: context-management skills (meta) + context artifacts (base) |
| **SIA** | L5 | ❔ | ❔ | **[Ana]** Once weights move, the "base model fixed" condition is suspended and $\beta_{\exp}$ must be redefined over the joint state |
| **SEAL** | L5 | — (RL) | ❔ | |

**[Ana] What can and cannot be said about this class.** Candidates depend on repeatedly-observed tasks, so the independence premise fails and (B2) is not the applicable reading. **The correct reading is Proposition A**, with slack $\eta_T$ growing in $T$ and in the edit budget $L$. A bare final test score, reported without $T$, $L$, $m$, and reuse count, overstates how much confirmation the protocol delivered.

---

## Class 3 — Independent validation and rollback

*Candidates confirmed on a disjoint set, or via retrospective prediction plus version test; failures rejected or rolled back.*

| System | Level | $\beta_{\exp}$ control | Indep. confirmation | Multi-round status |
|---|---|---|---|---|
| **SkillOpt** | L1 | ✅ mini-batch $B_m{=}8$, hierarchical tree reduction, rejected buffer | ✅ **[Lit]** three-way disjoint split; test set locked before final reporting | ⚠️ selection set reused across rounds → Proposition A applies; rotation would give A′ |
| **SkillOpt-Lite** | L1 | ✅ consensus mining | ✅ held-out selection + staged compile–smoke–full | ⚠️ same caveat; **[Lit]** reports high variance on small validation splits — the small-$m$ regime of corollary A-2 |
| **SkillForge** | L1 | ✅ batch ticket pool | ✅ | ⚠️ |
| **GEPA** | L0 | ⚠️ Pareto population | ✅ | ⚠️ |
| **DemoEvolve** | L3 | ✅ demonstration contrast | ✅ | ⚠️ |
| **Self-Harness** | L3 | ✅ weakness mining over batches | ✅ **[Lit]** bidirectional held-in/held-out non-regression | ⚠️ **[Ana]** the closest published approximation to the four acceptance checks |
| **Meta-Harness** | L3–L4 | ⚠️ Pareto frontier | ⚠️ **[Lit]** declines to carve an independent split on expensive terminal tasks | ❌ **[Ana]** exactly the small-$m$, non-small-$T$ case corollary A-2 warns about |
| **AHE** | L3 | ⚠️ | ⚠️ retrospective: prediction manifest + next-round rollback, no disjoint held-out | **[Ana]** its safety ceiling is bounded by attribution accuracy, which is reported low |
| **CORAL** | L3 | ⚠️ archive of scored attempts | ✅ external grader | **[Ana]** worktree isolation is a concrete implementation of the exact-rollback premise B-2 |
| **Ouroboros** | L3 | ❔ | ✅ human-reviewed commits | **[Ana]** human review in the write path is a distinct point on the write-authority sub-axis, and it changes what $\mathcal{H}_T$ contains |

**[Ana] What can and cannot be said about this class.** Premise (i) holds at round 1. It **degrades across rounds unless the validation set is rotated** — which is why the multi-round column matters more here than anywhere else. Report $T$, $L$, $m$, and reuse count, and the applicable bound follows: Proposition A′ if rotated, Proposition A otherwise.

---

## Cross-cutting observations

**[Ana] 1 — Editable-surface size and gate strength are not conserved quantities.** Systems whose surface covers control flow and executable code are not thereby more rigorously gated. Some of the largest surfaces in Class 1 ship with no confirmation gate at all, while some of the narrowest surfaces in Class 3 have three-way disjoint splits. Do not infer gate strength from level number.

**[Ana] 2 — (B1) and (B2) are met by different systems.** Trace2Skill and SkillCAT have strong consensus mechanisms and weak confirmation. Several Class-2 evolutionary systems have the reverse profile in a weaker form. If the two were substitutable, this pattern would not persist.

**[Ana] 3 — The strongest ZO operator inventories are not the strongest gates.** SkillOpt and ShinkaEvolve implement the widest range of operators; neither rotates its validation set. Operator sophistication is Axis I; confirmation is Axis II. They do not correlate.

**[Ana] 4 — Every acceptance gate in this table measures task pass rate.** Not one of the surveyed protocols places a safety metric *inside* $G$. Given documented cases of performance rising while refusal rate collapses and attack success rate rises, this is a structural blind spot of the current protocol space, not an oversight in any one system.

---

## Reporting fields required to place a system in this table

**[Rec]** A paper that omits these cannot be audited, and its improvement claim cannot be interpreted:

1. The split: train / selection / test, with counts;
2. $T$ (rounds), candidates per round, and validation-set **reuse count**;
3. $L$ — the per-round edit budget, as diff description length, not edit count;
4. $\Delta$ — the acceptance dead-zone, and whether it was set relative to $\eta_T$;
5. Whether Round-0 consumed tasks later used for confirmation;
6. Whether read-only status of evaluator / weights / optimizer is **runtime-enforced** or **prompt-declared**;
7. Evidence that a rejected candidate leaves the state behaviorally unchanged.

Fields 1–3 determine $\eta_T$. Field 4 determines whether Proposition B applies. Field 5 determines assumption A1. Field 6 determines premise (iii). Field 7 determines corollary B-2.
