---
name: iterative-error-analysis
description: Run training on an approved batch, analyze logged errors and their patterns, triage likely causes, propose fixes, and repeat with before-and-after comparisons. Use for training commands, logs/logs.txt or another specified log, model evaluation failures, and iterative training debugging.
---

# Iterative Error Analysis

Analyze training errors in repeatable, user-approved batches and keep the analysis in a reviewable file.

## Establish inputs

1. Ask for the training command and the log file if either is not supplied. By default, look for `logs/README.md` and `logs/logs.txt`; read the logs README for its format and required context. Read the main repository `README.md` to identify the documented default training command and configuration.
2. Ask the user to choose exactly one batch mode: one full epoch through all examples, one training step, or a custom number of examples. If the command does not expose a safe way to select that batch, explain the limitation and ask how to constrain it; do not silently rewrite the training command.
3. Discover credentials, dataset, output directory, and W&B context from repository files, environment variables, configuration, and the training code before asking the user. Ask only for information that is genuinely unavailable or requires an explicit user choice. The user may type `STOP` at any point to end the loop.
4. Ask the user to choose exactly one evaluation mode: the full evaluation set or a subset with a custom number of examples. Before running training, rewrite `max_steps` in the active configuration to match the approved training batch and rewrite `max_eval_samples` to match the approved evaluation mode: use `-1` or `null` for the full evaluation set, or the requested count for a subset. Record both limits with the command and configuration used for the batch.

## Run and analyze a batch

1. Record the command, batch mode, relevant configuration, starting log position, and timestamp.
2. Run the approved command for the selected batch. Stop on a command error and diagnose it through the `run-iteratively` workflow rather than treating it as a training error.
3. Read each new error or failed example in the log. Group related failures into distinct patterns and count every occurrence, making the grouping rules explicit when an example could fit more than one pattern.
4. For each pattern, report its count and percentage, a 1-2 sentence description, and one or two representative examples. Keep each pattern's final analysis to at most 10 sentences and use readable bullet points.
5. Add a `Triage` section that considers code, data, configuration, training regimen, execution environment, and W&B results. Use the connected W&B MCP server when available; otherwise state that W&B could not be consulted and rely on local artifacts.
6. Note when multiple error patterns appear downstream of one shared cause. Separate observed evidence from hypotheses.
7. Add a `Proposed solutions` section with prioritized fixes and the expected evidence that would confirm or reject each fix.

## Write and present the report

Append the report to `error_analysis.txt`. Start every batch with a header that mirrors the log header's separator and timestamp style, but uses `ERROR ANALYSIS` instead of `RUN STARTING`. Include the command and batch mode directly below the header.

If a tmux session is available, kill an existing window named `error-analysis` and create a new window with that name whose shell starts in the directory containing `error_analysis.txt`. Do not launch an editor; the user handles that. If the current session cannot support that operation, report the exact command the user can run and continue with the file output.

## Approve fixes and repeat

After presenting the report, ask which proposed solutions the user wants implemented. Before asking on every subsequent iteration, first ask which changes from the previous iteration, if any, the user wants to revert.

For selected fixes:

1. Explain the intended implementation and show the exact diff or file-level changes.
2. Ask for explicit approval before applying anything. Allow back-and-forth edits and re-present the revised changes until approved.
3. Apply only approved changes, run focused validation, and rerun the same training batch.
4. At the top of the next report, add an `Iteration comparison` section evaluating whether the fixes changed the earlier error counts, patterns, metrics, or representative failures. Distinguish improvement, regression, and no meaningful change.

Continue until the user stops, the selected stopping condition is met, or the user declines further fixes. Never hide a failed run or claim a fix worked without evidence.
Artifact location requirement: every report must be appended to logs/error_analysis.txt in the repository. Any shell window opened for this workflow must start in the logs directory, and no editor should be launched automatically.
