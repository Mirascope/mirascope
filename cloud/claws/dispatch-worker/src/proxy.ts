/**
 * Gateway process management and request proxying.
 *
 * Handles:
 * - Finding existing gateway processes
 * - Starting the gateway via start-openclaw.ts
 * - Proxying HTTP and WebSocket requests to the gateway
 */

import type { Sandbox, Process } from "@cloudflare/sandbox";

import type { Logger } from "./logger";
import type { DispatchEnv, OpenClawDeployConfig } from "./types";

import { GATEWAY_PORT, STARTUP_TIMEOUT_MS } from "./config";
import { createLogger, redactUrl, summarizeEnvKeys } from "./logger";

/**
 * Find an existing OpenClaw gateway process in the sandbox.
 */
export async function findGatewayProcess(
  sandbox: Sandbox,
  log?: Logger,
): Promise<Process | null> {
  const l = log ?? createLogger();
  try {
    const processes = await sandbox.listProcesses();
    l.debug(
      "gateway",
      `listProcesses: ${processes.length} processes`,
      processes.map((p) => ({
        id: p.id,
        status: p.status,
        command: p.command,
      })),
    );
    for (const proc of processes) {
      const isGateway =
        proc.command.includes("start-openclaw.ts") ||
        proc.command.includes("openclaw gateway");
      const isCli =
        proc.command.includes("openclaw devices") ||
        proc.command.includes("openclaw --version");

      if (isGateway && !isCli) {
        if (proc.status === "starting" || proc.status === "running") {
          return proc;
        }
      }
    }
  } catch (e) {
    l.error("gateway", "could not list processes:", e);
  }
  return null;
}

/**
 * Build environment variables for the container process from the bootstrap config.
 */
export function buildEnvVars(
  config: OpenClawDeployConfig,
  env: DispatchEnv,
): Record<string, string> {
  const envVars: Record<string, string> = {};

  // Pass all container env vars from the bootstrap config
  for (const [key, value] of Object.entries(config.containerEnv)) {
    if (value !== undefined) {
      envVars[key] = value;
    }
  }

  // Infrastructure env vars from the dispatch worker itself
  if (env.CLOUDFLARE_ACCOUNT_ID)
    envVars.CLOUDFLARE_ACCOUNT_ID = env.CLOUDFLARE_ACCOUNT_ID;
  if (env.SITE_URL) {
    envVars.OPENCLAW_SITE_URL = env.SITE_URL;
    envVars.OPENCLAW_ALLOWED_ORIGINS = env.SITE_URL;
  }

  // R2 persistence credentials (used by rclone in start-openclaw.ts)
  if (config.r2.accessKeyId) envVars.R2_ACCESS_KEY_ID = config.r2.accessKeyId;
  if (config.r2.secretAccessKey)
    envVars.R2_SECRET_ACCESS_KEY = config.r2.secretAccessKey;
  if (config.r2.bucketName) envVars.R2_BUCKET_NAME = config.r2.bucketName;

  return envVars;
}

/**
 * Ensure the OpenClaw gateway is running for the given claw.
 *
 * 1. Checks for an existing gateway process
 * 2. Starts a new one if needed (rclone config handled by start-openclaw.ts)
 * 3. Waits for the gateway port to be ready
 */
export async function ensureGateway(
  sandbox: Sandbox,
  config: OpenClawDeployConfig,
  env: DispatchEnv,
  log?: Logger,
): Promise<Process> {
  const l = log ?? createLogger();

  // Check for existing process
  const existing = await findGatewayProcess(sandbox, l);
  if (existing) {
    l.info(
      "gateway",
      `found existing process: ${existing.id} (${existing.status})`,
    );
    try {
      await existing.waitForPort(GATEWAY_PORT, {
        mode: "tcp",
        timeout: STARTUP_TIMEOUT_MS,
      });
      return existing;
    } catch {
      l.info(
        "gateway",
        "existing process not reachable, killing and restarting",
      );
      try {
        await existing.kill();
      } catch (killErr) {
        l.error("gateway", "failed to kill process:", killErr);
      }
    }
  }

  // Start new gateway
  l.info("gateway", `starting new gateway for claw: ${config.clawId}`);
  const envVars = buildEnvVars(config, env);
  const command = "bun /opt/openclaw/start-openclaw.ts";

  l.info("gateway", `env: ${summarizeEnvKeys(envVars)}`);

  let process: Process;
  try {
    process = await sandbox.startProcess(command, {
      env: Object.keys(envVars).length > 0 ? envVars : undefined,
    });
    l.info("gateway", `process started: ${process.id} (${process.status})`);
  } catch (err) {
    l.error("gateway", "failed to start process:", err);
    throw err;
  }

  // Wait for port
  try {
    await process.waitForPort(GATEWAY_PORT, {
      mode: "tcp",
      timeout: STARTUP_TIMEOUT_MS,
    });
    l.info("gateway", `ready on port ${GATEWAY_PORT}`);

    const logs = await process.getLogs();
    if (logs.stdout) l.debug("gateway", "stdout:", logs.stdout);
    if (logs.stderr) l.debug("gateway", "stderr:", logs.stderr);
  } catch (e) {
    l.error("gateway", "waitForPort failed:", e);

    // Check if start-openclaw detected an existing gateway
    let isAlreadyRunning = false;
    try {
      const logs = await process.getLogs();
      l.debug("gateway", "startup stderr:", logs.stderr);
      l.debug("gateway", "startup stdout:", logs.stdout);
      isAlreadyRunning =
        logs.stdout?.includes("OPENCLAW_ALREADY_RUNNING") ||
        logs.stderr?.includes("OPENCLAW_ALREADY_RUNNING") ||
        false;
    } catch (logErr) {
      l.error("gateway", "failed to get logs:", logErr);
    }

    if (isAlreadyRunning) {
      l.info(
        "gateway",
        "start-openclaw reported existing gateway; searching...",
      );

      const existingProc = await findGatewayProcess(sandbox, l);
      if (existingProc) {
        l.info(
          "gateway",
          `found existing: ${existingProc.id} (${existingProc.status})`,
        );
        try {
          await existingProc.waitForPort(GATEWAY_PORT, {
            mode: "tcp",
            timeout: STARTUP_TIMEOUT_MS,
          });
          l.info("gateway", `existing gateway ready on port ${GATEWAY_PORT}`);
          return existingProc;
        } catch {
          l.error("gateway", "existing gateway not reachable on port");
        }
      }

      // Last resort: direct HTTP health check
      l.debug("gateway", "trying direct health check fallback...");
      try {
        const healthCheck = await sandbox.containerFetch(
          new Request("http://localhost/healthz"),
          GATEWAY_PORT,
        );
        if (healthCheck.ok || healthCheck.status === 404) {
          l.info(
            "gateway",
            `port ${GATEWAY_PORT} responding (status: ${healthCheck.status})`,
          );
          const runningProc = await findGatewayProcess(sandbox, l);
          if (runningProc) return runningProc;
          return process; // Fallback: process ref won't be used for proxying
        }
      } catch {
        l.error("gateway", "direct port check also failed");
      }
    }

    throw new Error(
      `Gateway failed to start for claw ${config.clawId}. ${isAlreadyRunning ? "Detected existing gateway but could not connect." : "Process exited before port was ready."}`,
    );
  }

  return process;
}

/**
 * Proxy an HTTP request to the container gateway.
 */
export async function proxyHttp(
  sandbox: Sandbox,
  request: Request,
  basePath?: string,
  gatewayToken?: string,
  log?: Logger,
): Promise<Response> {
  const l = log ?? createLogger();
  const url = new URL(request.url);
  l.info("http", url.pathname + url.search);

  const response = await sandbox.containerFetch(request, GATEWAY_PORT);
  l.debug("http", `response: ${response.status} ${response.statusText}`);

  const headers = new Headers(response.headers);
  headers.set("X-Claw-Worker", "dispatch");

  // Rewrite Location headers on redirects to include base path
  if (basePath && response.status >= 300 && response.status < 400) {
    const location = headers.get("Location");
    if (location?.startsWith("/")) {
      headers.set("Location", basePath + location);
    }
  }

  // Inject base path into OpenClaw Control UI HTML
  if (basePath && response.headers.get("content-type")?.includes("text/html")) {
    const html = await response.text();
    // Inject base path and patch the default gateway WS URL.
    // The Control UI reads gatewayUrl from localStorage, defaulting to
    // wss://{location.host} (no path). We inject a boot script that ensures
    // the stored URL includes the base path so WebSocket connects correctly.
    const tokLiteral = gatewayToken
      ? JSON.stringify(gatewayToken)
      : "undefined";
    const wsBootScript = [
      "<script>",
      "(function(){",
      `  var bp="${basePath}";`,
      `  var tok=${tokLiteral};`,
      '  var key="openclaw.control.settings.v1";',
      "  try{",
      "    var proto=location.protocol==='https:'?'wss':'ws';",
      "    var want=proto+'://'+location.host+bp;",
      "    var raw=localStorage.getItem(key);",
      "    if(!raw){",
      "      var obj={gatewayUrl:want};",
      "      if(tok)obj.token=tok;",
      "      localStorage.setItem(key,JSON.stringify(obj));",
      "    }else{",
      "      var s=JSON.parse(raw);",
      "      var changed=false;",
      "      if(!s.gatewayUrl||s.gatewayUrl===proto+'://'+location.host){",
      "        s.gatewayUrl=want;",
      "        changed=true;",
      "      }",
      "      if(tok&&s.token!==tok){",
      "        s.token=tok;",
      "        changed=true;",
      "      }",
      "      if(changed){",
      "        localStorage.setItem(key,JSON.stringify(s));",
      "      }",
      "    }",
      "  }catch(e){}",
      "})();",
      "</script>",
    ].join("");
    const rewritten = html
      .replace(
        'window.__OPENCLAW_CONTROL_UI_BASE_PATH__=""',
        `window.__OPENCLAW_CONTROL_UI_BASE_PATH__="${basePath}"`,
      )
      .replace("</head>", wsBootScript + "</head>");
    return new Response(rewritten, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

/**
 * Proxy a WebSocket connection to the container gateway.
 */
export async function proxyWebSocket(
  sandbox: Sandbox,
  request: Request,
  basePath?: string,
  log?: Logger,
): Promise<Response> {
  const l = log ?? createLogger();
  const url = new URL(request.url);
  const hasToken = url.searchParams.has("token");
  l.info("ws", `connect path=${url.pathname} hasToken=${hasToken}`);
  l.debug("ws", `full URL: ${redactUrl(url)}`);

  const containerResponse = await sandbox.wsConnect(request, GATEWAY_PORT);
  const containerWs = containerResponse.webSocket;

  if (!containerWs) {
    l.error(
      "ws",
      `no WebSocket in container response, status: ${containerResponse.status}`,
    );
    const body = await containerResponse
      .clone()
      .text()
      .catch(() => "");
    l.debug("ws", "container response body:", body);
    return containerResponse;
  }

  l.debug("ws", "container WebSocket accepted");

  // Create a WebSocket pair for the client
  const [clientWs, serverWs] = Object.values(new WebSocketPair());

  serverWs.accept();
  containerWs.accept();

  // Relay: client -> container
  serverWs.addEventListener("message", (event) => {
    l.debug("ws", `client→container: ${wsPreview(event.data)}`);
    if (containerWs.readyState === WebSocket.OPEN) {
      containerWs.send(event.data);
    }
  });

  // Relay: container -> client (with URL rewriting for base path)
  containerWs.addEventListener("message", (event) => {
    if (serverWs.readyState === WebSocket.OPEN) {
      let data = event.data;
      l.debug("ws", `container→client: ${wsPreview(data)}`);
      // Rewrite URLs in JSON error messages to include base path.
      if (basePath && typeof data === "string") {
        try {
          const parsed = JSON.parse(data);
          if (
            parsed.error?.message &&
            typeof parsed.error.message === "string"
          ) {
            l.debug("ws", "rewriting error message URLs for base path");
            parsed.error.message = parsed.error.message.replace(
              /wss?:\/\/([^/\s"]+)\//g,
              (match: string, host: string) =>
                `${match.startsWith("wss") ? "wss" : "ws"}://${host}${basePath}/`,
            );
            data = JSON.stringify(parsed);
          }
        } catch {
          // Not JSON, pass through
        }
      }
      serverWs.send(data);
    }
  });

  // Close events — always logged (critical diagnostic signals)
  serverWs.addEventListener("close", (event) => {
    l.info("ws", `client closed: code=${event.code} reason="${event.reason}"`);
    containerWs.close(event.code, event.reason);
  });
  containerWs.addEventListener("close", (event) => {
    l.info(
      "ws",
      `container closed: code=${event.code} reason="${event.reason}"`,
    );
    let reason = event.reason;
    if (reason.length > 123) {
      reason = reason.slice(0, 120) + "...";
    }
    serverWs.close(event.code, reason);
  });

  // Error events — always logged
  serverWs.addEventListener("error", (event) => {
    l.error("ws", "client error:", event);
    containerWs.close(1011, "Client error");
  });
  containerWs.addEventListener("error", (event) => {
    l.error("ws", "container error:", event);
    serverWs.close(1011, "Container error");
  });

  return new Response(null, { status: 101, webSocket: clientWs });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Preview a WebSocket message for debug logging. */
function wsPreview(data: unknown): string {
  if (typeof data === "string") return data.slice(0, 200);
  if (data instanceof ArrayBuffer) return `[binary ${data.byteLength}b]`;
  return `[unknown ${typeof data}]`;
}
