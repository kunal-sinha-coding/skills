#!/usr/bin/env bash
set -euo pipefail

# Schedule a RunPod stop after tracked processes and required artifact markers complete.
usage() {
    echo "Usage: $0 --pod-id ID --tracked-pids 'PID PID' --results-file FILE --results-marker MARKER --analysis-file FILE --initial-analysis-count N [--initial-results-count N] [--delay-seconds N]" >&2
}

# Parse the explicit stop condition and refuse incomplete targets.
pod_id="${RUNPOD_POD_ID:-}"
tracked_pids=""
results_file=""
results_marker=""
analysis_file=""
initial_analysis_count=""
initial_results_count="0"
delay_seconds="600"
log_file="${RUNPOD_AUTO_STOP_LOG:-/tmp/runpod-auto-stop.log}"
while (($#)); do
    case "$1" in
        --pod-id) pod_id="$2"; shift 2 ;;
        --tracked-pids) tracked_pids="$2"; shift 2 ;;
        --results-file) results_file="$2"; shift 2 ;;
        --results-marker) results_marker="$2"; shift 2 ;;
        --analysis-file) analysis_file="$2"; shift 2 ;;
        --initial-analysis-count) initial_analysis_count="$2"; shift 2 ;;
        --initial-results-count) initial_results_count="$2"; shift 2 ;;
        --delay-seconds) delay_seconds="$2"; shift 2 ;;
        *) usage; exit 2 ;;
    esac
done

# Record watcher progress without ever writing the API key.
log() { echo "$(date -Is) $*" >> "$log_file"; }

# Validate credentials, identifiers, and required files before detaching.
: "${RUNPOD_API_KEY:?RUNPOD_API_KEY is required}"
: "${pod_id:?--pod-id or RUNPOD_POD_ID is required}"
: "${tracked_pids:?--tracked-pids is required}"
: "${results_file:?--results-file is required}"
: "${results_marker:?--results-marker is required}"
: "${analysis_file:?--analysis-file is required}"
: "${initial_analysis_count:?--initial-analysis-count is required}"

log "watcher_started pod=$pod_id tracked_pids=$tracked_pids delay_seconds=$delay_seconds"

# Wait until every explicitly tracked workload process exits.
for pid in $tracked_pids; do
    while kill -0 "$pid" 2>/dev/null; do sleep 30; done
done
log "tracked_processes_stopped"

# Wait until the requested result and analysis artifacts are newer than their starting counts.
while true; do
    results_count=$(grep -F -c "$results_marker" "$results_file" 2>/dev/null || true)
    analysis_count=$(grep -F -c 'ERROR ANALYSIS' "$analysis_file" 2>/dev/null || true)
    if (( results_count > initial_results_count && analysis_count > initial_analysis_count )); then break; fi
    sleep 30
done
log "artifacts_ready results=$results_count analysis=$analysis_count"

# Give the user-requested post-processing grace period before releasing the GPU.
sleep "$delay_seconds"
log "grace_period_complete"

# Cancel instead of stopping if the same workload unexpectedly restarted.
for pid in $tracked_pids; do
    if kill -0 "$pid" 2>/dev/null; then exit 1; fi
done

# Stop the current pod while preserving volume-backed workspace data.
curl --fail --silent --show-error --request POST     "https://rest.runpod.io/v1/pods/${pod_id}/stop"     --header "Authorization: Bearer ${RUNPOD_API_KEY}"
status=$?
log "stop_request_exit=$status"
exit "$status"
