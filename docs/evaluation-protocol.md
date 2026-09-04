<!-- Moved out of README.md: the trajectory-report schema and the eight evaluation
     dimensions. The reading list links here rather than restating them. -->

# Evaluating a Self-Evolving Harness: Report the Trajectory

The correct unit of evaluation is an **evolution trajectory**, not only the final version score. [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) separates the ability to produce useful persistent updates from the ability of a task-solving agent to use those updates, so a trajectory report should measure both update quality and downstream harness interaction.

A trajectory report should make five groups of fields visible:

| Field group | Minimum content |
|---|---|
| **Fixed boundary** | model, evaluator, tools, environment, permissions, editable surface |
| **Data roles** | proposal, selection, confirmation, regression, and final-test sets; sample counts; reuse; proposer visibility |
| **State history** | $s_0$, every accepted $s_t$, rejected candidates, final $s_T$, and old-task/OOD/fresh-task curves |
| **Runtime cost** | model tokens, tool calls, wall-clock, task rollouts, memory growth, human interventions, rollback cost |
| **Audit artifacts** | diffs, traces, seeds, evaluator configuration, replay command, safety checks, and rejected branches |

Evaluate the trajectory along eight dimensions:

- **Adaptivity:** does the state improve on the failure distribution that motivated the update?
- **Retention and non-regression:** are earlier tasks and important clusters preserved?
- **Generalization and transfer:** does the gain hold on OOD or fresh tasks?
- **Harness interaction:** was the new state loaded, followed, and behaviorally effective?
- **Reliability and auditability:** can runs be replayed, attributed, and recovered?
- **Efficiency and maintainability:** what are the runtime, token, dependency, and state-growth costs?
- **Safety and policy compliance:** do safety and permission outcomes remain acceptable?
- **Evaluation integrity:** can the candidate alter the evaluator, task data, logging, or model route?

Benchmarks such as [SWE-bench](https://arxiv.org/abs/2310.06770), [Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak), [PaperBench](https://arxiv.org/abs/2504.01848), and long-horizon memory benchmarks can supply tasks. [AI Agents That Matter](https://arxiv.org/abs/2407.01502) and [HAL](https://arxiv.org/abs/2510.11977) motivate standardized cost and integrity reporting, while [RE-Bench](https://arxiv.org/abs/2411.15114) and [MLE-bench](https://arxiv.org/abs/2410.07095) provide long-horizon task substrates. None supplies the full protocol automatically. Episodic benchmarks do not measure persistent state; a visible smoke test may be only a proxy; and scores across different base models, harnesses, optimizers, and evaluators are not directly additive.
