---
name: runpod-auto-stop
description: Schedule the current RunPod pod to stop after a user-specified completion condition, such as training and post-processing finishing, with an optional grace period. Use when the user explicitly asks to stop, shut down, or release the current RunPod after a process, artifact, log marker, or custom condition is satisfied.
---

# RunPod Auto-Stop

Schedule a safe, delayed stop for the current RunPod pod after a condition chosen by the user is verifiably satisfied. This skill stops the pod and releases its GPU. It does not terminate or delete the pod unless the user explicitly requests permanent deletion.

## Safety rules

- Use this skill only after the user explicitly authorizes stopping the current pod.
- Translate the user’s stopping condition into concrete checks before scheduling anything. Do not infer that “training finished” means all required post-processing finished.
- Resolve the exact current pod from `RUNPOD_POD_ID`. Never accept a pod ID from an unrelated workspace when the user means the current pod.
- Require `RUNPOD_API_KEY` without printing or logging its value.
- Track exact process IDs captured before starting the watcher when process completion is part of the condition. Avoid broad process-name checks that can match the watcher itself or an unrelated later run.
- Require every requested artifact or marker, such as final results and error analysis, before starting the grace-period timer.
- Verify that the watcher survives the launching shell and remains active without interrupting the workload.
- Prefer stopping with the RunPod REST endpoint. Stopping preserves volume data, while container-disk data may be cleared. Never use the terminate endpoint unless the user explicitly authorizes deletion.

## Workflow

1. Identify the current pod ID, API-key availability, active process IDs, relevant output files, and the user’s exact stopping condition.
2. Convert the condition into a checklist of machine-readable predicates. Examples include tracked PIDs exiting, a required results marker appearing after the run starts, a new report count exceeding its starting count, and a sentinel file containing a required value.
3. Choose a grace period. If the user does not specify one, use 600 seconds and state that choice.
4. Schedule a detached watcher using `scripts/schedule_stop.sh`. Pass exact PIDs and artifact markers rather than embedding an unbounded `pkill` or a vague process search.
5. Record watcher state in `/tmp/runpod-auto-stop.log` and verify the watcher is reparented away from the launching shell. Confirm that the active workload is still present.
6. After the condition is met, the watcher waits the grace period, rechecks that the workload has not unexpectedly restarted, and calls:

   `POST https://rest.runpod.io/v1/pods/$RUNPOD_POD_ID/stop`

7. Report the watcher PID, tracked PIDs, predicates, grace period, and whether the stop request succeeded. Do not claim the pod stopped until the API response or RunPod state confirms it.

## Condition examples

For a training run followed by full results and an error analysis report, capture the starting counts first:

```bash
starting_final_results=$(grep -c '^Evaluation: final$' logs/results.txt || true)
starting_error_reports=$(grep -c '^ERROR ANALYSIS$' logs/error_analysis.txt || true)
```

Then schedule a watcher that requires:

- every captured training PID to exit,
- `Evaluation: final` count to exceed `starting_final_results`,
- `ERROR ANALYSIS` count to exceed `starting_error_reports`,
- and the configured grace period to elapse.

For a custom condition, use a sentinel such as `/workspace/complete.stop` and require its creation time or contents to be newer than the watcher start time. If a condition cannot be checked reliably, stop and ask the user to define a machine-readable completion signal.

## Failure handling

- If the API key, pod ID, or stop endpoint is unavailable, leave the workload untouched and report the blocker.
- If any required artifact never appears, do not stop the pod merely because the main process exited.
- If a tracked process restarts before the grace period ends, cancel the stop and report the restart.
- If the stop API returns an error, preserve the watcher log and report the response without exposing credentials.

## Script

Use [scripts/schedule_stop.sh](scripts/schedule_stop.sh) for the deterministic PID-and-marker workflow. Read it before modifying its predicates or adding a new condition type.
