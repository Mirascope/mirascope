# mirascope-claw-debug

One-command tool to open the OpenClaw Control UI connected to any gateway for debugging. No auth, no proxy, no Mirascope Cloud — just the raw Control UI talking directly to a gateway.

## Usage

```bash
# Connect to a local gateway (default)
bun run cloud/claws/claw-debug/src/index.ts

# Connect to a specific gateway
bun run cloud/claws/claw-debug/src/index.ts --gateway wss://claw-abc.claws.mirascope.dev

# With auth token
bun run cloud/claws/claw-debug/src/index.ts --gateway wss://claw-abc.claws.mirascope.dev --token mytoken
```

## How it works

1. Checks that the gateway is reachable via HTTP
2. Starts a tiny local HTTP server
3. Serves a bootstrap page that configures `localStorage` with the gateway WebSocket URL
4. Redirects the browser to the gateway's built-in Control UI
5. You're chatting with the claw — no sign-in, no proxy, direct WebSocket

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--gateway <url>` | Gateway WebSocket URL | `ws://localhost:18789` |
| `--token <token>` | Gateway auth token | — |
| `--port <port>` | Local server port | auto |
| `--no-open` | Don't auto-open browser | — |
| `--help` | Show help | — |

## Development

```bash
cd cloud/claws/claw-debug
bun test
```
