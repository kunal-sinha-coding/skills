---
name: take-meeting-notes
description: Create or update concise meeting notes from the current conversation, working session, transcript, or supporting local artifacts. Use when Codex needs to capture discussion context, verified findings, decisions, rationale, metrics, unresolved questions, and action items in a durable notes file such as logs/notes.txt.
---

# Take Meeting Notes

Convert a working session into useful notes that let a reader understand what happened without reading the full transcript.

## Workflow

1. Read the available conversation context and identify the requested time or topic scope.
2. Inspect relevant local artifacts when they verify material claims, metrics, commands, commits, or current status.
3. Separate observations from interpretations. Label hypotheses when evidence does not establish causality.
4. Write or update the requested notes file. Default to `logs/notes.txt` in the current repository when no path is specified.
5. Preserve existing notes unless the user explicitly requests replacement. Add a dated session section when appending.
6. Review the notes for factual accuracy, duplicated points, stale status, and missing action owners.
7. Validate the file and follow the repository's commit and push workflow.

## Note Structure

Use only sections supported by the session. Prefer this order.

```markdown
# Meeting Notes

## Session

- Date: YYYY-MM-DD
- Topic: A concise description.

## Context

A short explanation of the goal and relevant background.

## Key Findings

- State measured results with exact values and units.
- Mark interpretations as hypotheses.

## Decisions

- Record what was decided and why.

## Experiments and Results

| Experiment | Result | Interpretation |
| --- | --- | --- |

## Open Questions

- Record unresolved questions that affect subsequent work.

## Action Items

- [ ] State the action, owner when known, and success condition.
```

## Writing Rules

- Use concise, complete sentences.
- Capture conclusions and rationale instead of reproducing dialogue.
- Preserve exact metric names, run identifiers, links, file paths, and commit hashes when useful.
- Distinguish absolute percentage-point changes from relative percentage changes.
- Do not present a best checkpoint as a final result when a run is still active.
- Do not invent attendees, owners, deadlines, decisions, or consensus.
- Note important failures and abandoned approaches when they explain later decisions.
- Keep action items specific and testable.
