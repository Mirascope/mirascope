#!/usr/bin/env bash
set -euo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://localhost:18789}"
MAX_WAIT="${MAX_WAIT:-60}"

echo "Waiting for OpenClaw gateway at $GATEWAY_URL..."
elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
  # Gateway has no REST health endpoint; any HTTP response means it's alive
  status=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/" 2>/dev/null || true)
  if [ -n "$status" ] && [ "$status" != "000" ]; then
    echo "Gateway ready after ${elapsed}s (HTTP $status)"
    exit 0
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

echo "Gateway failed to start within ${MAX_WAIT}s"
exit 1
