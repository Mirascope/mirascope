/**
 * Vite dev server plugin for proxying WebSocket connections to the OpenClaw gateway.
 *
 * In production, `server-entry.ts` intercepts WebSocket upgrades and
 * `claws-ws-proxy.ts` handles auth + relay using Cloudflare's WebSocketPair.
 * That doesn't work in Vite dev mode because the Vite HTTP server doesn't
 * forward WebSocket upgrades to Miniflare.
 *
 * This plugin hooks into the Vite dev server's HTTP server, intercepts
 * `upgrade` events for `/api/ws/claws/` paths, and proxies them directly
 * to the gateway using the `ws` library.
 *
 * Required env vars (dev only):
 * - OPENCLAW_GATEWAY_WS_URL  — e.g. ws://100.78.10.21:18789
 * - OPENCLAW_GATEWAY_TOKEN   — the token for the connect handshake
 */
import crypto from "crypto";
import { type IncomingMessage } from "http";
import { type Duplex } from "stream";
import { type Plugin } from "vite";
import { WebSocketServer, WebSocket } from "ws";

// --- Device identity for gateway auth (Ed25519) ---

const ED25519_SPKI_PREFIX = Buffer.from("302a300506032b6570032100", "hex");

function base64UrlEncode(buf: Buffer): string {
  return buf
    .toString("base64")
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replace(/=+$/g, "");
}

interface DeviceIdentity {
  deviceId: string;
  publicKeyPem: string;
  privateKeyPem: string;
  publicKeyBase64Url: string;
}

/** Generate an ephemeral Ed25519 device identity (new each Vite start). */
function generateDeviceIdentity(): DeviceIdentity {
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  const publicKeyPem = publicKey
    .export({ type: "spki", format: "pem" })
    .toString();
  const privateKeyPem = privateKey
    .export({ type: "pkcs8", format: "pem" })
    .toString();
  const spki = publicKey.export({ type: "spki", format: "der" });
  const rawKey = spki.subarray(ED25519_SPKI_PREFIX.length);
  const deviceId = crypto.createHash("sha256").update(rawKey).digest("hex");
  const publicKeyBase64Url = base64UrlEncode(rawKey);
  return { deviceId, publicKeyPem, privateKeyPem, publicKeyBase64Url };
}

function signPayload(privateKeyPem: string, payload: string): string {
  const key = crypto.createPrivateKey(privateKeyPem);
  return base64UrlEncode(
    crypto.sign(null, Buffer.from(payload, "utf8"), key) as unknown as Buffer,
  );
}

function buildDeviceAuthPayload(params: {
  deviceId: string;
  clientId: string;
  clientMode: string;
  role: string;
  scopes: string[];
  signedAtMs: number;
  token: string;
  nonce: string;
}): string {
  return [
    "v2",
    params.deviceId,
    params.clientId,
    params.clientMode,
    params.role,
    params.scopes.join(","),
    String(params.signedAtMs),
    params.token,
    params.nonce,
  ].join("|");
}

// Ephemeral identity — regenerated each Vite start (not persisted)
let cachedIdentity: DeviceIdentity | null = null;
function getDeviceIdentity(): DeviceIdentity {
  if (!cachedIdentity) cachedIdentity = generateDeviceIdentity();
  return cachedIdentity;
}

export function viteWsProxy(): Plugin {
  return {
    name: "vite-plugin-ws-proxy",
    configureServer(server) {
      const gatewayUrl = process.env.OPENCLAW_GATEWAY_WS_URL;
      const gatewayToken = process.env.OPENCLAW_GATEWAY_TOKEN;

      if (!gatewayUrl) {
        return;
      }

      if (!gatewayToken) {
        console.warn(
          "[ws-proxy] OPENCLAW_GATEWAY_WS_URL is set but OPENCLAW_GATEWAY_TOKEN is missing — WebSocket proxy disabled",
        );
        return;
      }

      console.log(`[ws-proxy] Dev WebSocket proxy enabled → ${gatewayUrl}`);

      const wss = new WebSocketServer({ noServer: true });

      // We need to intercept upgrade events BEFORE other plugins (cloudflare)
      // destroy the socket. Use httpServer.on("upgrade") but also wrap other
      // listeners so they skip requests we've handled.
      const httpServer = server.httpServer;
      if (!httpServer) return;

      // Wait for the server to start listening, then wrap all upgrade listeners.
      // By this point all plugins have registered their handlers.
      httpServer.once("listening", () => {
        const allListeners = httpServer.listeners("upgrade") as Array<
          (req: IncomingMessage, socket: Duplex, head: Buffer) => void
        >;

        // Remove all existing listeners
        httpServer.removeAllListeners("upgrade");

        // Track which requests we handle
        const handled = new WeakSet<IncomingMessage>();

        // Add our handler first
        httpServer.on(
          "upgrade",
          (req: IncomingMessage, socket: Duplex, head: Buffer) => {
            const url = req.url ?? "";
            if (!url.startsWith("/api/ws/claws/")) return;

            handled.add(req);
            wss.handleUpgrade(req, socket, head, (browserWs) => {
              handleConnection(browserWs, gatewayUrl, gatewayToken);
            });
          },
        );

        // Re-add all original listeners, but skip requests we've handled
        for (const listener of allListeners) {
          httpServer.on(
            "upgrade",
            (req: IncomingMessage, socket: Duplex, head: Buffer) => {
              if (handled.has(req)) return;
              listener(req, socket, head);
            },
          );
        }
      });
    },
  };
}

function handleConnection(
  browserWs: InstanceType<typeof WebSocket>,
  gatewayUrl: string,
  gatewayToken: string,
) {
  const upstreamUrl = gatewayUrl.replace(/\/$/, "");
  console.log(
    `[ws-proxy] Browser connected, opening upstream → ${upstreamUrl}`,
  );

  let browserClosed = false;
  let handshakeComplete = false;

  // Track browser close early so we know not to bother with the upstream
  browserWs.on("close", (code: number, reason: Buffer) => {
    console.log(`[ws-proxy] Browser disconnected: ${code} ${reason}`);
    browserClosed = true;
    // Only close upstream if it's already open
    if (upstreamWs.readyState === WebSocket.OPEN) {
      // Code 1006 is reserved and can't be sent in a close frame; normalize it
      const safeCode =
        code < 1000 || [1004, 1005, 1006, 1015].includes(code) ? 1001 : code;
      upstreamWs.close(safeCode, reason.toString());
    } else if (upstreamWs.readyState === WebSocket.CONNECTING) {
      // Terminate the pending connection (don't wait for it)
      upstreamWs.terminate();
    }
  });

  browserWs.on("error", (err: Error) => {
    console.error("[ws-proxy] Browser WS error:", err.message);
    browserClosed = true;
    upstreamWs.terminate();
  });

  // Set Origin to match the upstream URL (required by gateway's origin check).
  // rejectUnauthorized: false is needed because Tailscale serve uses its own CA.
  const origin = upstreamUrl
    .replace(/^wss:/, "https:")
    .replace(/^ws:/, "http:")
    .replace(/\/$/, "");
  const upstreamWs = new WebSocket(upstreamUrl, {
    headers: { Origin: origin },
    rejectUnauthorized: false,
  });

  upstreamWs.on("error", (err: Error) => {
    console.error("[ws-proxy] Upstream error:", err.message);
    if (!browserClosed && browserWs.readyState === WebSocket.OPEN) {
      browserWs.close(1011, "Gateway connection failed");
    }
  });

  upstreamWs.on("open", () => {
    if (browserClosed) {
      // Browser already left (React strict mode cleanup). Close upstream.
      console.log(
        "[ws-proxy] Upstream connected but browser already gone, closing",
      );
      upstreamWs.close();
      return;
    }
    console.log("[ws-proxy] Upstream connected, waiting for challenge");
  });

  upstreamWs.on("message", (data: Buffer) => {
    if (browserClosed) return;

    const raw = data.toString();

    if (!handshakeComplete) {
      try {
        const msg = JSON.parse(raw);

        if (msg.type === "event" && msg.event === "connect.challenge") {
          const nonce: string = msg.payload?.nonce ?? "";
          console.log("[ws-proxy] Received connect.challenge, sending auth");

          const device = getDeviceIdentity();
          const role = "operator";
          const scopes = [
            "operator.admin",
            "operator.approvals",
            "operator.pairing",
          ];
          const signedAtMs = Date.now();
          const payload = buildDeviceAuthPayload({
            deviceId: device.deviceId,
            clientId: "webchat",
            clientMode: "webchat",
            role,
            scopes,
            signedAtMs,
            token: gatewayToken,
            nonce,
          });
          const signature = signPayload(device.privateKeyPem, payload);

          upstreamWs.send(
            JSON.stringify({
              type: "req",
              id: "__connect",
              method: "connect",
              params: {
                minProtocol: 3,
                maxProtocol: 3,
                auth: { token: gatewayToken },
                client: {
                  id: "webchat",
                  version: "dev",
                  platform: "server",
                  mode: "webchat",
                },
                device: {
                  id: device.deviceId,
                  publicKey: device.publicKeyBase64Url,
                  signature,
                  signedAt: signedAtMs,
                  nonce,
                },
                role,
                scopes,
                caps: [],
              },
            }),
          );
          return;
        }

        if (msg.type === "res" && msg.id === "__connect") {
          if (msg.ok) {
            console.log("[ws-proxy] Handshake complete — relay active");
            handshakeComplete = true;
            // Signal browser that the proxy is ready for messages
            browserWs.send(JSON.stringify({ type: "proxy.ready" }));
          } else {
            console.error(
              "[ws-proxy] Handshake failed:",
              msg.error ?? msg.payload,
            );
            browserWs.close(1008, "Gateway handshake failed");
            upstreamWs.close();
          }
          return;
        }
      } catch {
        // Not JSON, pass through
      }
    }

    // After handshake: relay gateway → browser
    if (handshakeComplete && browserWs.readyState === WebSocket.OPEN) {
      console.log(`[ws-proxy] Gateway → Browser: ${raw.slice(0, 500)}`);
      browserWs.send(raw);
    }
  });

  // Relay: browser → gateway
  browserWs.on("message", (data: Buffer) => {
    const msg = data.toString();
    console.log(`[ws-proxy] Browser → Gateway: ${msg.slice(0, 500)}`);
    if (handshakeComplete && upstreamWs.readyState === WebSocket.OPEN) {
      upstreamWs.send(msg);
    } else {
      console.warn(
        `[ws-proxy] Dropped browser msg: handshake=${handshakeComplete} upstream=${upstreamWs.readyState}`,
      );
    }
  });

  // Upstream close → close browser
  upstreamWs.on("close", (code: number, reason: Buffer) => {
    console.log(`[ws-proxy] Upstream disconnected: ${code} ${reason}`);
    if (!browserClosed && browserWs.readyState === WebSocket.OPEN) {
      const r = reason.toString();
      const safeUpCode =
        code < 1000 || [1004, 1005, 1006, 1015].includes(code) ? 1001 : code;
      const truncatedR =
        new TextEncoder().encode(r).length > 123
          ? new TextDecoder().decode(
              new TextEncoder().encode(r).slice(0, 120),
            ) + "..."
          : r;
      browserWs.close(safeUpCode, truncatedR);
    }
  });
}
