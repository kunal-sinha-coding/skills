#!/usr/bin/env python3
"""Monitor explicit completion criteria and stop one RunPod pod safely."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    """Parse the explicit safety and monitoring settings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pod-id", default=os.getenv("RUNPOD_POD_ID"))
    parser.add_argument("--api-key-env", default="RUNPOD_API_KEY")
    parser.add_argument("--process-pid", type=int)
    parser.add_argument("--process-exit-file")
    parser.add_argument("--require-process-success", action="store_true")
    parser.add_argument("--require-file", action="append", default=[])
    parser.add_argument("--require-fresh-file", action="store_true")
    parser.add_argument("--max-runtime-seconds", type=float)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--stable-polls", type=int, default=2)
    parser.add_argument("--state-file", default="/tmp/runpod-auto-stop.json")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if not args.pod_id:
        parser.error("--pod-id or RUNPOD_POD_ID is required")
    if not args.require_process_success and not args.require_file and args.max_runtime_seconds is None:
        parser.error("at least one explicit stop criterion is required")
    if args.require_process_success and not args.process_exit_file:
        parser.error("--process-exit-file is required with --require-process-success")
    if args.stable_polls < 1:
        parser.error("--stable-polls must be positive")
    return args


def write_state(path: Path, state: dict[str, Any]) -> None:
    """Persist supervisor state atomically before and after lifecycle changes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def request_json(url: str, api_key: str, method: str = "GET") -> tuple[int, dict[str, Any] | str]:
    """Call a RunPod REST endpoint without exposing the API key."""
    request = urllib.request.Request(
        url,
        method=method,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(body) if body else {}
            except json.JSONDecodeError:
                return response.status, body
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return error.code, body
    except urllib.error.URLError as error:
        return 0, str(error.reason)


def read_exit_code(path_value: str | None) -> int | None:
    """Read a wrapper-written process exit code without guessing from a missing process."""
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_file():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def process_exists(pid: int | None) -> bool:
    """Check whether the target process still exists."""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def file_conditions(paths: list[str], started_at: float, require_fresh: bool) -> dict[str, Any]:
    """Check required files and optionally require them to be fresh."""
    results = {}
    for value in paths:
        path = Path(value)
        exists = path.is_file()
        fresh = exists and (not require_fresh or path.stat().st_mtime >= started_at)
        results[value] = {"exists": exists, "fresh": fresh}
    return results


def all_criteria_met(args: argparse.Namespace, started_at: float) -> tuple[bool, dict[str, Any]]:
    """Evaluate every requested criterion as one fail-closed conjunction."""
    exit_code = read_exit_code(args.process_exit_file)
    files = file_conditions(args.require_file, started_at, args.require_fresh_file)
    process_ok = not args.require_process_success or (exit_code == 0 and not process_exists(args.process_pid))
    elapsed = time.time() - started_at
    time_ok = args.max_runtime_seconds is None or elapsed >= args.max_runtime_seconds
    details = {
        "process_exists": process_exists(args.process_pid) if args.process_pid is not None else None,
        "process_exit_code": exit_code,
        "files": files,
        "elapsed_seconds": elapsed,
        "time_limit_met": time_ok,
    }
    return process_ok and all(item["exists"] and item["fresh"] for item in files.values()) and time_ok, details


def main() -> int:
    """Monitor criteria and request a pod stop only after stable confirmation."""
    args = parse_args()
    api_key = os.getenv(args.api_key_env)
    if not api_key:
        print(f"Missing API key environment variable: {args.api_key_env}", file=sys.stderr)
        return 2
    state_path = Path(args.state_file)
    started_at = time.time()
    state: dict[str, Any] = {
        "phase": "monitoring",
        "started_at": utc_now(),
        "pod_id": args.pod_id,
        "criteria": vars(args).copy(),
    }
    state["criteria"].pop("execute", None)
    write_state(state_path, state)
    stop_url = f"https://rest.runpod.io/v1/pods/{args.pod_id}/stop"
    pod_url = f"https://rest.runpod.io/v1/pods/{args.pod_id}"
    stable_count = 0
    while True:
        status_code, pod = request_json(pod_url, api_key)
        state["pod_check"] = {"status_code": status_code, "response": pod if isinstance(pod, dict) else str(pod)[:500]}
        if status_code == 200 and isinstance(pod, dict):
            desired = str(pod.get("desiredStatus", pod.get("desired_status", ""))).upper()
            if desired in {"EXITED", "STOPPED"}:
                state["phase"] = "stopped_or_exited"
                write_state(state_path, state)
                print("Pod is already stopped or exited.")
                return 0
        met, details = all_criteria_met(args, started_at)
        state["criteria_check"] = details
        stable_count = stable_count + 1 if met else 0
        state["stable_count"] = stable_count
        if met and stable_count >= args.stable_polls:
            state["phase"] = "criteria_met"
            state["criteria_met_at"] = utc_now()
            write_state(state_path, state)
            print("All explicit stop criteria are met.")
            if not args.execute:
                print("Dry run: add --execute after confirming this state.")
                return 0
            state["phase"] = "stop_requested"
            state["stop_requested_at"] = utc_now()
            write_state(state_path, state)
            stop_status, stop_response = request_json(stop_url, api_key, method="POST")
            state["stop_response"] = {"status_code": stop_status, "response": stop_response if isinstance(stop_response, dict) else str(stop_response)[:500]}
            state["phase"] = "stopped_or_exited" if 200 <= stop_status < 300 else "stop_request_failed"
            write_state(state_path, state)
            print(f"Stop request returned HTTP {stop_status}.")
            return 0 if 200 <= stop_status < 300 else 1
        if args.once:
            write_state(state_path, state)
            print("Criteria are not yet met.")
            return 0
        write_state(state_path, state)
        time.sleep(max(1.0, args.poll_seconds))


if __name__ == "__main__":
    raise SystemExit(main())

