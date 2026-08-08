---
name: run-iteratively
description: Run a user-provided command repeatedly until an agreed stopping condition is met. Use when command failures require diagnosis, solution comparison, user-selected fixes, and approval of code changes before each retry.
---

# Run Iteratively

Run one command through a user-controlled diagnose, propose, approve, fix, and retry loop.

## Start the loop

1. Ask for the exact command, working directory, relevant environment assumptions, and a concrete stopping condition. Do not start until the stopping condition is explicit; examples include a successful run, a target metric, a number of successful iterations, or a user-entered `STOP`.
2. Confirm the command and stopping condition back to the user.
3. Run the command and capture its output, exit status, and any files it produces.
4. If the stopping condition is met, report the result and stop.

## Handle an error

When the command fails or returns an error, stop immediately. Do not retry, make a speculative fix, or continue past the failure.

1. Diagnose the failure using the command output, relevant logs, the repository, configuration, and tests.
2. Identify one or more plausible solutions. For every solution, explain the change, benefits, risks, and tradeoffs in concise prose.
3. Ask the user to choose a solution or request a different one. If the user asks for edits to a proposal, revise it and ask again.
4. After the user chooses, prepare the smallest appropriate code or configuration change and show the exact diff or file-level changes.
5. Ask for explicit approval to apply the displayed changes. Treat revisions, rejection, or further discussion as an opportunity to edit the proposal; do not apply unapproved changes.
6. Apply only the approved changes, run focused validation when practical, and then restart the same command.

Repeat this loop until the stopping condition is met. Preserve the user's command unless they approve a command change. Accept `STOP` at any point and report the last known state without making further changes.
