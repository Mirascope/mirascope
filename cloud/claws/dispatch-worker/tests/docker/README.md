# Dispatch Worker Docker Integration Tests

Integration tests that run against a real OpenClaw gateway in a Docker container.

## Prerequisites

- Docker and Docker Compose
- Access to the `openclaw` repo (for building the container image)
- `bun` installed

## Quick Start

```bash
# Set the path to your openclaw repo checkout
export OPENCLAW_SRC=/path/to/openclaw

# Start the gateway (from cloud/claws/dispatch-worker/tests/docker/)
docker compose up -d --build --wait

# Run tests (from cloud/claws/dispatch-worker/)
bun run test:docker

# Stop the gateway (from cloud/claws/dispatch-worker/tests/docker/)
docker compose down -v
```

## Configuration

| Variable                 | Default                  | Description                                |
| ------------------------ | ------------------------ | ------------------------------------------ |
| `GATEWAY_URL`            | `http://localhost:18789` | Gateway URL for tests                      |
| `OPENCLAW_GATEWAY_TOKEN` | `test-gateway-token`     | Auth token                                 |
| `OPENCLAW_SRC`           | _(required)_             | Path to openclaw source (for Docker build) |

## Notes

- The OpenClaw gateway is **WebSocket-based** and has no REST health endpoint
- Health checks verify the HTTP server responds (any status = alive)
- The container binds to `0.0.0.0:18789` via `--bind lan`
- In CI, `OPENCLAW_SRC` points to a separate checkout of the openclaw repo
