---
name: take-meeting-notes
description: Create or update chronological experiment notes from the current conversation, working session, transcript, or supporting local artifacts. Use when Codex needs to record repeated cycles of hypotheses, experiments, metrics, outcomes, learnings, and next hypotheses across ML, code, infrastructure, research, or agentic coding work in a durable file such as logs/notes.txt.
---

# Take Meeting Notes

Convert a working session into a chronological series of hypothesis and experiment cycles that preserve how the work evolved.

## Workflow

1. Read the available conversation context and identify the requested time or topic scope.
2. Inspect relevant local artifacts when they verify material claims, metrics, commands, commits, or current status.
3. Divide the session into chronological cycles. Start a new cycle when the hypothesis, implementation, experiment, or interpretation changes materially.
4. For each cycle, record the hypothesis, experiment, metrics, what went well, what went badly, what was learned, and the next hypothesis.
5. Include coding and infrastructure experiments alongside ML experiments when they affected progress or conclusions.
6. Separate observations from interpretations. Label hypotheses when evidence does not establish causality.
7. Write or update the requested notes file. Default to `logs/notes.txt` in the current repository when no path is specified.
8. Preserve existing notes unless the user explicitly requests replacement. Add a dated session section when appending.
9. Add a dedicated Agentic Coding section when the session created or modified skills, tools, automation, orchestration, repository workflows, or agent behavior.
10. Review the notes for factual accuracy, duplicated points, stale status, and missing transitions between cycles.
11. Validate the file and follow the repository's commit and push workflow.

## Note Structure

Begin with minimal session context. Repeat the experiment-cycle section for the duration of the session.

```markdown
# Meeting Notes

## Session

- Date: YYYY-MM-DD
- Topic: A concise description.

## Starting Point

A short explanation of the goal and relevant background.

## Cycle 1: A concise experiment name

### Hypothesis

State what was expected and why.

### Experiment

State what changed, what stayed fixed, and how success was evaluated.

### Metrics

State exact measured results with units, run IDs, or checkpoint names when useful.

### What Went Well

State successful behavior, implementation, tooling, or evidence.

### What Went Badly

State failures, regressions, confounders, or operational problems.

### Learning

State the best current interpretation and distinguish it from measured evidence.

### Next Hypothesis

State the next idea that followed from this cycle.

## Cycle 2: The next experiment

Repeat the same subsections.

## Agentic Coding

### Skills Created or Updated

Record each skill, its purpose, the material change, and its commit when known.

### Workflows and Automation

Record skills invoked, agent delegation, tools, connectors, and automated control loops that changed how the work was performed.

### Code and Infrastructure Changes

Record implementation, evaluation, logging, configuration, repository, and infrastructure changes that supported the experiments.

### What Worked

State which agentic workflows improved speed, reliability, observability, or reuse.

### What Failed

State tooling, permissions, orchestration, synchronization, or automation failures.

### Learning

State the reusable lesson for future agent-driven work.
```

## Writing Rules

- Use concise, complete sentences.
- Preserve chronological causality. Make clear how one result led to the next hypothesis.
- Capture conclusions and rationale instead of reproducing dialogue.
- Include only metrics that help evaluate the hypothesis or explain the next decision.
- Record code, evaluation, logging, orchestration, and infrastructure work as experiment cycles when they materially affected the session.
- Keep the Agentic Coding section separate from domain experiment cycles. Summarize skills and workflows there without repeating all domain metrics.
- Include created, modified, and materially invoked skills. Distinguish skill changes from skill usage.
- Include agent delegation, connector usage, automated stopping, repository synchronization, and permission failures when they affected the work.
- Preserve exact metric names, run identifiers, links, file paths, and commit hashes when useful.
- Distinguish absolute percentage-point changes from relative percentage changes.
- Do not present a best checkpoint as a final result when a run is still active.
- Do not invent attendees, owners, deadlines, decisions, or consensus.
- Note important failures and abandoned approaches when they explain later decisions.
- End with the latest hypothesis rather than a generic summary or action-item list unless the user requests one.
