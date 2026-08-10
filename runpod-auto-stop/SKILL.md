---
name: runpod-auto-stop
description: Schedule the current RunPod GPU pod to stop after explicit, user-approved criteria are met, such as successful training completion, a required report sentinel, or a maximum runtime. Use when Codex must monitor a local process and durable artifacts before safely stopping a RunPod pod through the RunPod REST API.
---

# RunPod Auto Stop

Safely schedule the current RunPod pod to stop after a user-defined condition.

## Safety contract

- Require the user to state the stop criteria before starting a supervisor.
- Treat all listed criteria as an AND condition.
- Require a pod ID from `RUNPOD_POD_ID` or an explicit argument.
- Require `RUNPOD_API_KEY` for REST control.
- Refuse to stop when the pod ID, API key, criteria, or required process identity is missing.
- Default to dry-run mode. Require the explicit `--execute` flag after the criteria have been confirmed.
- Write durable state before requesting the stop. A pod stop can terminate the supervisor immediately.
- Stop the pod, rather than terminate it, unless the user explicitly requests permanent deletion.
- Never infer that a training process succeeded merely because it exited. Require exit code zero and any requested sentinel files.
- Do not stop on a stale sentinel without checking its modification time when the user requires a fresh artifact.
- Do not stop the current pod merely because the GPU is idle. Idle checks are diagnostics and are not safe completion criteria by themselves.

## Workflow

1. Discover the current pod ID from `RUNPOD_POD_ID`. Do not guess it from unrelated pod listings.
2. Ask for explicit criteria if the user has not provided them. Useful criteria include:
   - The named process exits with code zero.
   - One or more report or completion files exist.
   - A completion file is newer than the supervisor start time.
   - A maximum wall-clock duration is reached.
3. Show the resolved criteria, pod ID, state file, and exact stop action. Ask for confirmation before using `--execute`.
4. Start `scripts/runpod_stop_supervisor.py` with all criteria. Keep the supervisor attached when possible, or use a durable process manager. Do not use an untracked detached shell.
5. Monitor the state file and supervisor output. The expected phases are `monitoring`, `criteria_met`, `stop_requested`, and `stopped_or_exited`.
6. After a stop request, report that the pod may terminate the supervisor before final API confirmation. The pre-stop state file is the durable record.
7. After criteria are met, pass `--grace-seconds 300`. The supervisor remains in `grace_period` for five minutes, rechecks that the tracked process has not restarted, and only then requests the stop.

## Command patterns

Dry-run a completion-gated schedule:

```bash
python3 scripts/runpod_stop_supervisor.py \
  --process-pid "$TRAINING_PID" \
  --require-process-success \
  --require-file logs/error_analysis.txt \
  --require-fresh-file \
  --poll-seconds 30 \
  --grace-seconds 300 \
  --state-file /workspace/runpod-auto-stop.json
```

Start the same schedule only after the user confirms:

```bash
python3 scripts/runpod_stop_supervisor.py \
  --process-pid "$TRAINING_PID" \
  --require-process-success \
  --require-file logs/error_analysis.txt \
  --require-fresh-file \
  --poll-seconds 30 \
  --grace-seconds 300 \
  --state-file /workspace/runpod-auto-stop.json \
  --execute
```

Use `--max-runtime-seconds` as an additional safety cutoff. It is combined with other criteria, not used to override missing completion evidence. For a time-only schedule, omit process and file criteria and provide explicit user confirmation that a time-only stop is intended.

## Current training workflow integration

For iterative training, require all of the following before stopping:

- The training command exits with code zero.
- The final evaluation artifact exists.
- The required error analysis report exists.
- The report sentinel is newer than the current run start.
- The terminal summary has been written, if the workflow provides one.
- If the selected stopping criteria require work outside the supervisor, create a fresh readiness sentinel after that work succeeds.
- Require that sentinel as an additional fresh file only when the selected criteria include it.

The supervisor can verify files and process state, but it cannot perform arbitrary user-specific post-processing. Use an optional readiness sentinel to bridge those external checks into the supervisor.

## RunPod API behavior

The bundled script uses the documented REST endpoints:

- `GET https://rest.runpod.io/v1/pods/{podId}` to verify the target.
- `POST https://rest.runpod.io/v1/pods/{podId}/stop` to stop the target.

It sends the API key only in the Authorization header. It never prints the key. It records response status and non-secret response text in the state file.

## Failure handling

- If the API check fails, keep monitoring and do not stop.
- If the pod is already stopped or exited, record that state and exit successfully.
- If a required condition becomes false, reset the stability counter.
- Require two consecutive qualifying polls by default.
- If the supervisor itself exits before `stop_requested`, treat the schedule as incomplete and inspect the state file.
