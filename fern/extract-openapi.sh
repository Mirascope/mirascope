#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the root directory (parent of fern)
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Starting development server..."
cd "$ROOT_DIR"
bun run cloud:dev > /dev/null 2>&1 &
SERVER_PID=$!

# Function to cleanup on exit
cleanup() {
  echo "Stopping server..."
  kill $SERVER_PID 2>/dev/null || true
  wait $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for server to be ready..."
for i in {1..60}; do
  if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "Server is ready!"
    break
  fi
  if [ $i -eq 60 ]; then
    echo "Server failed to start after 60 seconds"
    exit 1
  fi
  sleep 1
done

echo "Extracting OpenAPI specification..."
curl -s http://localhost:3000/openapi.json | npx prettier --parser json > "$SCRIPT_DIR/openapi.json"

echo "OpenAPI extraction complete!"
