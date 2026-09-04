<!-- Mainline literature map for extending the catalogue without weakening its evidence boundary. -->

# Literature Map: Mainline Gaps

This map expands the public reading list along the harness self-evolution update loop. It is a coverage and audit plan, not a claim that every listed paper implements a candidate-level gate. The protocol table remains the source for system-level classifications; use `unverified` when the primary source does not establish a field.

## How to use the map

For each paper, extract the same four facts:

1. **Persistent write target** — what object is written and reloaded (`L0`–`L5`), including primary and secondary targets;
2. **Proposal evidence and geometry** — what the proposer observes, which edit unit is fixed, and how candidates are retained;
3. **Confirmation and data relationship** — what can block persistence, which set drives that decision, and how often it is reused; and
4. **Trajectory evidence** — long-horizon retention, cost, evaluator protection, rollback, and update-versus-benefit measurements.

The labels in this repository are interpretations. A paper's use of “validation,” “test,” “reflection,” or “optimizer” is not sufficient to assign a protocol or level.

## Direct harness evolution

| Work | Mainline role | Audit status |
|---|---|---|
| [Code as Agent Harness](https://arxiv.org/abs/2605.18747) | Scope and architecture anchor for executable, verifiable, stateful harnesses | Source-linked; architecture reading, not candidate-gate evidence |
| [AutoHarness](https://arxiv.org/abs/2603.03329) | Synthesizes and iteratively refines a code harness from environment feedback | Abstract checked; persistence and blocking rule require paper-level audit |
| [SkillCAT](https://arxiv.org/abs/2606.13317) | Contrastive skill proposals, source-task clone replay, and topology-aware skill routing | Protocol row audited conservatively as search-time selection; full split and rollback details remain open |
| [SkillAdaptor](https://arxiv.org/abs/2606.01311) | Step-level failure attribution with qualification checks for targeted skill updates | Full text checked; qualification uses the adaptation set and is not separated confirmation |
| [SkillForge](https://arxiv.org/abs/2604.08618) | Domain-grounded skill creation followed by development-batch refinement | Full text checked; round commits are write-through and the held-out split is a final evaluation set |
| [MCE](https://arxiv.org/abs/2601.21557) | Co-evolves context-engineering skills (L4) and context artifacts (L1) in a bi-level loop | Full text checked; validation-based best-so-far selection is search-time selection |
| [Continual Harness](https://arxiv.org/abs/2605.09998) | Online adaptation of prompts, sub-agents, skills, and memory during a continuing run | Boundary reading; cross-run persistence must be established before counting as a persistent update |
| [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) | Separates the ability to produce useful updates from the ability to use them during task solving | Evaluation anchor; not a new transition protocol |
| [AutoAgent](https://arxiv.org/abs/2603.09716) | Self-evolving cognition with contextual decision-making and elastic memory orchestration | Direct-evolution anchor; persistence scope and candidate-level blocking rule require source audit |
| [Evo-Memory](https://arxiv.org/abs/2511.20857) | Streaming benchmark and framework for test-time self-evolving memory | Memory-evolution anchor; distinguish memory updates from a separated promotion gate |

## Harness architecture and evaluation substrates

These papers make the execution interface, tool boundary, or evaluation environment explicit. They broaden harness self-evolution coverage but do not enter the 33-row protocol counts unless a separate persistence audit is completed.

| Work | Mainline role | Audit status |
|---|---|---|
| [SWE-agent](https://arxiv.org/abs/2405.15793) | Agent-computer interface design for repository navigation, editing, and tests | Architecture anchor; the paper evaluates a fixed interface rather than cross-round harness evolution |
| [OpenHands](https://arxiv.org/abs/2407.16741) | Extensible coding-agent platform with tools, sandboxed execution, delegation, and benchmark integration | Architecture anchor; no candidate-level persistence protocol is inferred |
| [OpenHands Software Agent SDK](https://arxiv.org/abs/2511.03690) | Composable agent, tool, memory, lifecycle, and local-to-remote execution interfaces | Production-harness anchor; persistence and promotion semantics require source audit |
| [BrowserGym ecosystem](https://arxiv.org/abs/2412.05467) | Unified web-agent environment plus AgentLab for creation, testing, and analysis | Evaluation substrate; it standardizes environments, not harness updates |
| [ToolSandbox](https://arxiv.org/abs/2408.04682) | Stateful tool execution, user simulation, and milestone-based evaluation | Stateful-evaluation anchor; no durable candidate write is implied |
| [$\tau$-bench](https://arxiv.org/abs/2406.12045) | Multi-turn tool-agent-user interaction with database-state evaluation and pass$^k$ reliability | Reliability benchmark; no harness update protocol is implied |
| [AgentDojo](https://arxiv.org/abs/2406.13352) | Dynamic tasks and attacks for prompt-injection defenses in tool-using agents | Security/evaluator-integrity anchor; not an evolution method |
| [WorkArena](https://arxiv.org/abs/2403.07718) | Enterprise web-agent tasks implemented on a remote ServiceNow environment | Task substrate; use with a separate persistent-state protocol |

## Candidate proposal and search

| Work | Mainline role | Audit status |
|---|---|---|
| [AdaEvolve](https://arxiv.org/abs/2602.20133) | Adaptive evolutionary search with an explicit bandit-style scheduling component | Abstract checked; verify the exact acquisition rule and data reuse before a strict label |
| [ShinkaEvolve](https://arxiv.org/abs/2509.19349) | Open-ended and sample-efficient program evolution | Coverage anchor; candidate selection and confirmation fields require source inspection |
| [ThetaEvolve](https://arxiv.org/abs/2511.23473) | Test-time evolution on open problems | Coverage anchor; distinguish search-time evaluation from persistence blocking |
| [Promptbreeder](https://arxiv.org/abs/2309.16797) | Self-referential prompt evolution and population-style retention | Proposal anchor; do not infer independent confirmation from evolutionary selection |
| [GEPA](https://arxiv.org/abs/2507.19457) | Trace-informed genetic and Pareto search over prompt programs | Protocol row audited as search-time selection; verify experiment-specific final-test handling |
| [MIPROv2](https://arxiv.org/abs/2406.11695) | Surrogate/Bayesian allocation over instructions and demonstrations | Proposal anchor; validation reuse and stopping rule are experiment-specific |
| [TextGrad](https://arxiv.org/abs/2406.07496) | Textual critiques propagated through a compound system | Proposal anchor; “gradient” is not a numerical estimator in this catalogue |
| [Darwin Gödel Machine](https://arxiv.org/abs/2505.22954) | Open-ended code-agent evolution with archive-based selection | Protocol row audited as search-time selection; inspect evaluator and rollback boundaries |

## Confirmation and trajectory evaluation

| Work | Mainline role | Audit status |
|---|---|---|
| [SkillOpt](https://arxiv.org/abs/2605.23904) | Narrow skill edits with a separate validation stage | Protocol row audited as separated confirmation; cross-round reuse remains material |
| [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) | Staged compile, smoke, and fuller checks with explicit task allocation | Protocol row audited as separated confirmation; report split sizes and reuse |
| [Self-Harness](https://arxiv.org/abs/2606.09498) | Weakness mining, harness proposal, and regression-based proposal validation | Protocol row audited as separated confirmation at the single-round level |
| [AI Agents That Matter](https://arxiv.org/abs/2407.01502) | Cost, standardization, reproducibility, and evaluation-integrity anchor | Evaluation anchor; not a harness update method |
| [HAL](https://arxiv.org/abs/2510.11977) | Holistic agent evaluation and leaderboard infrastructure | Evaluation anchor; extract trajectory and evaluator-integrity fields |
| [RE-Bench](https://arxiv.org/abs/2411.15114) | Long-horizon frontier R&D task evaluation | Benchmark anchor; persistence and state-transition fields are external to the benchmark |
| [MLE-bench](https://arxiv.org/abs/2410.07095) | Machine-learning engineering task evaluation | Benchmark anchor; use for task coverage and cost, not as a promotion gate |
| [PaperBench](https://arxiv.org/abs/2504.01848) | Research-replication evaluation for autonomous agents | Benchmark anchor; pair with a persistent-state protocol when measuring evolution |

## Risk and governance

| Work | Mainline role | Audit status |
|---|---|---|
| [Misevolution](https://arxiv.org/abs/2509.26354) | Emergent risk modes in self-evolving agents | Risk anchor; map failure modes to evaluator, permission, and rollback controls |
| [Defining and Characterizing Reward Hacking](https://arxiv.org/abs/2209.13085) | Formal vocabulary for objective/evaluator mismatch | Risk anchor; use to specify what the loss omits |
| [Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760) | Overoptimization under learned evaluators | Risk anchor; motivates independent checks and evaluator protection |
| [Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) | Reward tampering and deceptive optimization pressure | Risk anchor; audit whether candidates can alter evaluators or reporting paths |

## Audit priority

The next evidence pass should prioritize papers that can change the main conclusions of the survey:

1. direct harness systems with explicit persistence and regression paths;
2. proposal methods whose claims depend on a strict acquisition or bandit interpretation;
3. evaluation studies that report long-horizon update quality separately from downstream harness benefit; and
4. risk papers that supply executable evaluator-integrity, permission, or rollback checks.

Do not inflate the README with every adjacent “self-evolving agent” paper. Add a work to the public catalogue when it clarifies one of these four questions, then record the source location and any remaining `unverified` fields in [audit-table.md](audit-table.md).
