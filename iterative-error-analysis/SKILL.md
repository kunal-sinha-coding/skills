---
name: iterative-error-analysis
description: Run training on an approved batch, analyze every logged error and its patterns, perform evidence-based deep triage, propose fixes, and repeat with before-and-after comparisons. Use for training commands, logs/logs.txt or another specified log, model evaluation failures, and iterative training debugging.
---

# Iterative Error Analysis

Analyze training and evaluation errors in repeatable, user-approved batches. Produce a complete, reviewable report that explains what failed, how often each failure occurred, why it likely occurred, and what should be changed.

## Non-negotiable reporting rules

- Do not impose a sentence cap on the report, on any section, or on any error pattern.
- Do not replace error analysis with an iteration summary. Comparisons are required, but they are only one part of the report.
- Every failed example must be assigned to one or more explicit error patterns. If patterns overlap, state the overlap rule and provide both exclusive counts and total occurrence counts.
- The report must include a distribution of error patterns by count and percentage. Counts must reconcile with the number of evaluated examples or with the number of failure occurrences, as appropriate.
- The report must describe the actual failure for every pattern. A status name such as `execution_error` or `failed` is not a description.
- The report must include representative examples with task IDs, relevant prompt or expected behavior, generated output or a faithful excerpt, observed result, and the reason the result failed.
- Triage must cover every observed pattern individually. For each pattern, distinguish observed evidence from hypotheses, identify likely causes across code, data, prompt or parser, configuration, training regimen, model behavior, evaluation, and environment when relevant, and propose a targeted solution.
- After the individual triage, synthesize the underlying root causes across patterns. Identify the smallest credible set of upstream mechanisms that explains all or most failures, quantify which patterns and occurrences each cause explains, connect the causes to the observed failure chain, distinguish evidence from inference, and explain the important residual failures that the synthesis does not explain. Do not force unrelated failures into one cause.
- Do not claim that a fix helped unless the same or a clearly comparable measurement provides evidence.
- Preserve enough raw detail to make the classification auditable. Do not discard malformed completions, parser input, exception text, assertion text, or expected-versus-actual values when those artifacts are available.

## Establish inputs

1. Ask for the training command and log file if either is not supplied. By default, look for `logs/README.md` and `logs/logs.txt`. Read the logs README for its format and required context. Read the main repository `README.md` to identify the documented default training command and configuration.
2. Ask the user to choose exactly one batch mode: one full epoch through all examples, one training step, or a custom number of examples. If the command does not expose a safe way to select that batch, explain the limitation and ask how to constrain it. Do not silently rewrite the training command.
3. Discover credentials, dataset, output directory, and W&B context from repository files, environment variables, configuration, and training code before asking the user. Ask only for information that is genuinely unavailable or requires an explicit user choice. The user may type `STOP` at any point to end the loop.
4. Ask the user to choose exactly one evaluation mode: the full evaluation set or a subset with a custom number of examples. Before running training, rewrite `max_steps` in the active configuration to match the approved training batch and rewrite `max_eval_samples` to match the approved evaluation mode. Use `-1` or `null` for the full evaluation set, or the requested count for a subset. Record both limits with the command and configuration used for the batch.

## Run and collect a batch

1. Record the command, batch mode, relevant configuration, starting log position, timestamp, model or checkpoint, dataset split, evaluation size, random seed, and W&B run identifier when available.
2. Run the approved command for the selected batch. Stop on a command error and diagnose it through the `run-iteratively` workflow rather than treating it as a training error.
3. Collect every new training sample, evaluation example, parser result, execution result, reward, metric, exception, assertion failure, and generated completion available in the log or auxiliary artifacts.
4. If a completion is malformed, retain the raw completion before classification. If the log does not preserve it, state that limitation and inspect another local artifact or add preservation before drawing conclusions.

## Classify and analyze errors

1. Read every new error or failed example. Do not sample only a few failures.
2. Create a classification taxonomy grounded in the observed behavior. Typical categories include output-format or extraction failure, truncated output, syntax error, missing or wrong function signature, undefined name, wrong algorithm, wrong edge-case handling, wrong return type or shape, wrong ordering or duplicates, incorrect expected value, timeout, sandbox or dependency failure, and infrastructure failure. Combine categories only when the same mechanism explains them.
3. Group related failures into distinct patterns and count every occurrence. Make the grouping rule explicit when an example could fit more than one pattern. Prefer one primary mutually exclusive pattern per example plus secondary tags when both views are useful.
4. Build a distribution table sorted by descending count. Include pattern name, primary count, percentage of evaluated examples, secondary occurrence count when applicable, and a short definition. Percentages must use a stated denominator and sum correctly.
5. For each pattern, write a full analysis without a sentence limit. Include all of the following:
   - What the model or system actually did.
   - What it should have done.
   - The mechanism of failure, including exception, assertion, parser rule, or expected-versus-actual discrepancy.
   - Representative examples from different tasks when possible.
   - Evidence that supports each likely cause.
   - Alternative hypotheses that remain plausible.
   - A targeted fix and the measurement that would confirm or reject it. The fix must address the suspected failure mechanism, not only add logging, tracing, screenshots, or other observability. State the concrete code, data, prompt, parser, configuration, training, evaluation, or environment change that should prevent or reduce the failure.
6. Analyze successes briefly when they constrain the diagnosis. Explain which stage they passed and what that suggests about the failing patterns.
7. Identify shared causes only after the individual pattern analyses are complete. Explain which patterns they connect and which evidence distinguishes a shared cause from coincidence.
8. Synthesize underlying root causes across the patterns. Look for upstream training, data, reward, optimization, model-behavior, pipeline, or evaluation mechanisms that account for most of the observed failures, rather than merely restating pattern-specific symptoms. For each proposed root cause, map the affected patterns and occurrence counts, describe the causal chain from the root cause to the failures, cite supporting evidence, state competing explanations, identify unexplained residuals, and specify the experiment or intervention that would distinguish the explanations. Use this synthesis to prioritize fixes, while keeping pattern-specific fixes for failures it does not explain.

## Required report structure

Append each report to `logs/error_analysis.txt`. Start every report with a header that mirrors the log header separator and timestamp style, but uses `ERROR ANALYSIS` instead of `RUN STARTING`. Include the command and batch mode directly below the header.

Every report must contain these sections in this order:

0. `Run summary`. Give a compact overview of the command, denominator, baseline result, final result, main regression or improvement, dominant failure pattern, and most important next action.
1. `Iteration comparison`. For the first report, state that no prior comparison exists. For later reports, compare the same denominators and list changes in metrics, pattern counts, pattern composition, and representative failures. Separate improvement, regression, and no meaningful change.
2. `Run context and data coverage`. State what was analyzed, what was unavailable, the denominator, and whether all expected examples and log records were present.
3. `Error-pattern distribution`. Provide the complete count and percentage table and the grouping rule.
4. `Observed error patterns`. Provide a subsection for every nonzero pattern. Describe the concrete failures, not only their status labels. Include representative task IDs and raw evidence or faithful excerpts.
5. `Success patterns and controls`. State what passed and what those successes rule out.
6. `Deep triage`. Provide a separate subsection for every observed error pattern. Each subsection must explain evidence, likely causes, alternatives, and the mechanism connecting cause to failure.
7. `Shared causes and interactions`. Explain upstream failures, downstream failures, and any masking or reward effects.
8. `Underlying root-cause synthesis`. Explain which small set of upstream mechanisms accounts for all or most observed failures. Map each cause to the affected patterns and occurrence counts, describe the causal chain, separate evidence from hypotheses, identify residual failures and alternative explanations, and define tests that could distinguish them.
9. `Proposed solutions and confirmation tests`. Prioritize fixes. For each fix, provide enough implementation detail for someone else to act on it. Identify the affected files, components, examples, or data slices when known, describe the underlying change, explain why it should address the observed mechanism, name the patterns it should improve, state risks, tradeoffs, and possible regressions, and define the smallest confirmation test plus the expected result. Separate root-cause fixes from mitigations and observability-only follow-ups. Do not treat “add a log,” “log more fields,” “improve monitoring,” or similar instrumentation as a complete solution unless the problem itself is missing observability.
10. `Limitations`. State missing logs, stochasticity, small samples, parser blind spots, unavailable W&B data, and any other uncertainty.

Use W&B when the connected W&B MCP server is available. Report the exact metrics and run context consulted. Otherwise state that W&B could not be consulted and rely on local artifacts.

## Write and present the report

If a tmux session is available, kill an existing window named `error-analysis` and create a new window with that name whose shell starts in the directory containing `error_analysis.txt`. Do not launch an editor. If the current session cannot support that operation, report the exact command the user can run and continue with the file output.

Present the complete distribution and complete pattern analyses to the user. A concise summary may precede the report, but it must not replace any required section or failure description.

After appending the report, print a concise terminal summary. Include the run command, batch and evaluation sizes, baseline and final metrics, the change from baseline and the previous iteration, the dominant error patterns with counts, the most important training or evaluation diagnostic, and the next recommended action. Keep it short enough to scan without opening the report, but do not omit a negative result or unresolved limitation.

## Approve fixes and repeat

After presenting the report, ask which proposed solutions the user wants implemented. Before asking on every subsequent iteration, first ask which changes from the previous iteration, if any, the user wants to revert.

For selected fixes:

1. Explain the intended implementation and show the exact diff or file-level changes.
2. Ask for explicit approval before applying anything. Allow back-and-forth edits and re-present the revised changes until approved.
3. Apply only approved changes, run focused validation, and rerun the same training batch.
4. At the top of the next report, add an `Iteration comparison` section evaluating whether the fixes changed earlier counts, patterns, metrics, or representative failures. Distinguish improvement, regression, and no meaningful change.

Continue until the user stops, the selected stopping condition is met, or the user declines further fixes. Never hide a failed run or claim a fix worked without evidence.

Artifact location requirement: every report must be appended to `logs/error_analysis.txt`. Any shell window opened for this workflow must start in the logs directory, and no editor should be launched automatically.
