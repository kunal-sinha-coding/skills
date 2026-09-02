---
name: hill-climbing
description: Run controlled tiny-batch evaluations, classify every failure, apply one evidence-based fix at a time, and repeat with a durable hill-climbing report. Use when iteratively debugging a training or evaluation pipeline from logs.
---

# Hill Climbing

Use this skill for an iterative model-improvement session in a repository. The primary objective is to maximize pass rate on a fixed small evaluation batch, with reward treated as a secondary diagnostic that may improve as a byproduct. Record every observation, hypothesis, code change, and result in `hillclimbing.txt` beside the configured evaluation log.

## Start safely

1. Read the repository `README.md`, `logs/README.md`, the configured YAML file, and the training and evaluation entry points before running anything. Use the documented command and log schema rather than guessing.
2. Determine the training command from the user. If none is supplied, use the README’s standard command with `configs/default.yaml`.
3. Create or switch to a dedicated Git branch before changing code or configuration. Use the user’s branch name when supplied. Otherwise use `hill-climbing-YYYYMMDD-HHMMSS`, including the creation timestamp. If that name exists, append a more specific timestamp or an incrementing suffix. Do not make the experiment on `main`.
4. Preserve unrelated existing work. Record the starting commit, branch, dirty paths, command, model, dataset split, seed, and log path in the report.
5. Follow the repository’s `AGENTS.md` Git workflow in addition to this skill. Before every commit, update the required notes file, commit all related non-ignored changes, and push the current branch. Push the dedicated branch immediately after its first commit so the experiment is backed up remotely, then push after every later change as well. If repository instructions require a different branch policy, follow the more specific user or repository instruction and document the resulting branch in the report.

## Configure the controlled batch

Use 10 examples by default. Keep the same task IDs and ordering for every iteration so comparisons are valid. Prefer the project’s existing `max_eval_samples` or equivalent setting. Create a temporary experiment config derived from the selected YAML when needed, set the evaluation limit to 10, and do not overwrite the canonical config. If the project cannot select a stable batch, state the limitation and use the least surprising deterministic selection available.

Run the user’s command or the documented default command with only the overrides needed to enforce the batch. Do not silently replace a user-specified training run. Record the exact effective command and configuration. Capture the log byte offset and timestamp immediately before each run so only that iteration’s records are analyzed.

## Analyze every iteration

After each run, read all new evaluation records from the log, following `logs/README.md`. For each example, record its task ID, pass or failure status, raw completion when available, extracted code, execution status, exception or assertion text, and award. Count successes and failures and verify that the number of records matches the intended denominator.

Assign every failed example one mutually exclusive primary error bucket. Use secondary tags only when they add useful information, and state the overlap rule. Ground buckets in observed evidence. Suitable buckets include output-format failure, truncation, syntax failure, interface or missing-name failure, incorrect algorithm or logic, wrong edge-case behavior, wrong return type or shape, timeout, sandbox or dependency failure, data or test inconsistency, and infrastructure failure. Do not call a failure “model error” without describing what actually failed.

Calculate a distribution for the chosen denominator. Include each bucket’s count and percentage, sorted by descending count, with totals that reconcile. Analyze successful examples briefly because they constrain possible causes.

For every nonzero bucket, perform root-cause analysis across data, data formatting, prompt or context construction, model behavior, parser or extraction, reward, training configuration, evaluation code, and environment as applicable. Separate observed facts from hypotheses, list competing explanations, identify upstream causes shared across buckets, and explain residual failures that the shared explanation does not cover.

Choose one highest-priority fix per iteration using pass rate as the primary selection and stopping metric. Prefer the smallest change that tests a specific causal hypothesis. Implement that one fix on the hill-climbing branch, record the affected files and exact behavioral intent, run focused validation, and rerun the identical 10-example evaluation. Use reward and error buckets as secondary diagnostics rather than optimization targets. If the fix fails, regresses, or creates new buckets, document that result and either refine the same hypothesis or abandon it for a different single fix. Never claim success without a before-and-after pass-rate comparison using the same tasks and denominator.

Continue until the user stops, the fixed batch is fully passing, the user’s stopping condition is met, or further changes are not supported by evidence. If a run command fails before producing an evaluation, diagnose the command or environment separately and do not classify it as a model error.

## Maintain `hillclimbing.txt`

Append to `Path(log_path).parent / "hillclimbing.txt"`. Create parent directories as needed. Each new session begins with a timestamped header in the same visual style as `logs/logs.txt`, using `HILL CLIMBING SESSION STARTING` and the date and time. Keep all iterations under that session header. Do not replace earlier sessions.

Use one subsection per iteration, in order. Every subsection must include:

- The exact command, effective config, branch, commit, batch size, task IDs, log range, and model context.
- The pass count, pass rate, failure count, denominator, and complete error-bucket distribution with counts and percentages.
- The observed evidence for every failed example or a clear reference to its task-level records in the source log.
- The root-cause analysis, including evidence, hypotheses, alternatives, shared causes, and limitations.
- The proposed fix, why it tests the selected hypothesis, and the exact files or code paths changed.
- Focused validation and the post-fix evaluation results compared with the previous iteration, with pass rate first and reward second.
- A verdict of improved, regressed, unchanged, inconclusive, or fully passing, based primarily on pass rate and supported by secondary diagnostics.
- Thoughts for the next iteration, including whether to refine, revert, or abandon the current approach.

Use plain text or Markdown headings inside the `.txt` file. Keep raw exceptions, assertion details, and representative completion excerpts sufficiently intact for another agent to audit the classification. Never fabricate unavailable logs or remote metrics. If a W&B or other external source is unavailable, say so explicitly.

## Handoff

At the end of each iteration, print a concise summary containing the branch, command, batch and task IDs, pass rate, bucket distribution, fix, before-and-after pass-rate result, and next proposal. Leave the working tree and branch clearly reported. Do not merge, delete branches, or alter unrelated files unless the user explicitly requests that additional Git operation.
