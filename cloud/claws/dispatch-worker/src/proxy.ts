/**
 * Gateway process management and request proxying.
 *
 * Handles:
 * - Finding existing gateway processes
 * - Configuring rclone for R2 persistence
 * - Starting the gateway via start-openclaw.ts
 * - Proxying HTTP and WebSocket requests to the gateway
 */

import type { Sandbox, Process } from "@cloudflare/sandbox";

import type { DispatchEnv, OpenClawConfig } from "./types";

import { GATEWAY_PORT, STARTUP_TIMEOUT_MS } from "./config";

const RCLONE_CONF_PATH = "/root/.config/rclone/rclone.conf";
const CONFIGURED_FLAG = "/tmp/.rclone-configured";

/**
 * Find an existing OpenClaw gateway process in the sandbox.
 */
export async function findGatewayProcess(
  sandbox: Sandbox,
): Promise<Process | null> {
  try {
    const processes = await sandbox.listProcesses();
    console.log(
      "[proxy] findGatewayProcess: all processes:",
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
    console.log("[proxy] Could not list processes:", e);
  }
  return null;
}

/**
 * Configure rclone for R2 access in the sandbox.
 * Idempotent — skips if already configured.
 */
export async function ensureRcloneConfig(
  sandbox: Sandbox,
  r2Config: OpenClawConfig["r2"],
  accountId: string,
): Promise<boolean> {
  if (!r2Config.accessKeyId || !r2Config.secretAccessKey || !accountId) {
    console.log("[proxy] R2 credentials not configured, skipping rclone setup");
    return false;
  }

  // Check if already configured (idempotent)
  try {
    const exists = await sandbox.readFile(CONFIGURED_FLAG);
    if (exists) {
      console.log("[proxy] Rclone already configured (flag exists)");
      return true;
    }
  } catch {
    // Flag file doesn't exist, proceed with configuration
  }

  const rcloneConfig = [
    "[r2]",
    "type = s3",
    "provider = Cloudflare",
    `access_key_id = ${r2Config.accessKeyId}`,
    `secret_access_key = ${r2Config.secretAccessKey}`,
    `endpoint = https://${accountId}.r2.cloudflarestorage.com`,
    "acl = private",
    "no_check_bucket = true",
  ].join("\n");

  // Create rclone config directory and files
  await sandbox.writeFile(RCLONE_CONF_PATH, rcloneConfig);
  await sandbox.writeFile(CONFIGURED_FLAG, "");

  console.log("[proxy] Rclone configured for R2 bucket:", r2Config.bucketName);
  return true;
}

/**
 * Build environment variables for the container process from the bootstrap config.
 */
export function buildEnvVars(config: OpenClawConfig): Record<string, string> {
  const envVars: Record<string, string> = {};

  // Pass all container env vars from the bootstrap config
  for (const [key, value] of Object.entries(config.containerEnv)) {
    if (value !== undefined) {
      envVars[key] = value;
    }
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
 * 1. Mounts R2 storage using per-claw scoped credentials
 * 2. Checks for an existing gateway process
 * 3. Starts a new one if needed
 * 4. Waits for the gateway port to be ready
 */
export async function ensureGateway(
  sandbox: Sandbox,
  config: OpenClawConfig,
  env: DispatchEnv,
): Promise<Process> {
  // Configure rclone for R2 persistence
  const cfAccountId = env.CLOUDFLARE_ACCOUNT_ID;
  if (cfAccountId) {
    await ensureRcloneConfig(sandbox, config.r2, cfAccountId);
  } else {
    console.log("[proxy] CF_ACCOUNT_ID not set, skipping rclone setup");
  }

  // Check for existing process
  const existing = await findGatewayProcess(sandbox);
  if (existing) {
    console.log(
      "[proxy] Found existing gateway process:",
      existing.id,
      "status:",
      existing.status,
    );
    try {
      await existing.waitForPort(GATEWAY_PORT, {
        mode: "tcp",
        timeout: STARTUP_TIMEOUT_MS,
      });
      return existing;
    } catch {
      console.log(
        "[proxy] Existing process not reachable, killing and restarting",
      );
      try {
        await existing.kill();
      } catch (killErr) {
        console.log("[proxy] Failed to kill process:", killErr);
      }
    }
  }

  // Start new gateway
  console.log("[proxy] Starting new gateway for claw:", config.clawId);
  const envVars = buildEnvVars(config);
  const command = "bun /usr/local/bin/start-openclaw.ts";

  console.log("[proxy] Env var keys:", Object.keys(envVars));

  let process: Process;
  try {
    process = await sandbox.startProcess(command, {
      env: Object.keys(envVars).length > 0 ? envVars : undefined,
    });
    console.log(
      "[proxy] Process started:",
      process.id,
      "status:",
      process.status,
    );
  } catch (err) {
    console.error("[proxy] Failed to start process:", err);
    throw err;
  }

  // Wait for port
  try {
    await process.waitForPort(GATEWAY_PORT, {
      mode: "tcp",
      timeout: STARTUP_TIMEOUT_MS,
    });
    console.log("[proxy] Gateway is ready on port", GATEWAY_PORT);

    const logs = await process.getLogs();
    if (logs.stdout) console.log("[proxy] stdout:", logs.stdout);
    if (logs.stderr) console.log("[proxy] stderr:", logs.stderr);
  } catch (e) {
    console.error("[proxy] waitForPort failed:", e);

    // Check if start-openclaw detected an existing gateway
    let isAlreadyRunning = false;
    try {
      const logs = await process.getLogs();
      console.error("[proxy] Startup stderr:", logs.stderr);
      console.error("[proxy] Startup stdout:", logs.stdout);
      isAlreadyRunning =
        logs.stdout?.includes("OPENCLAW_ALREADY_RUNNING") ||
        logs.stderr?.includes("OPENCLAW_ALREADY_RUNNING") ||
        false;
    } catch (logErr) {
      console.error("[proxy] Failed to get logs:", logErr);
    }

    if (isAlreadyRunning) {
      console.log(
        "[proxy] start-openclaw reported existing gateway; checking running processes",
      );

      // The gateway is already running from a previous start — find it
      console.log("[proxy] Searching for existing gateway process...");
      const existingProc = await findGatewayProcess(sandbox);
      console.log(
        "[proxy] findGatewayProcess result:",
        existingProc?.id ?? "not found",
      );
      if (existingProc) {
        console.log(
          "[proxy] Found existing gateway process:",
          existingProc.id,
          "status:",
          existingProc.status,
        );
        try {
          await existingProc.waitForPort(GATEWAY_PORT, {
            mode: "tcp",
            timeout: STARTUP_TIMEOUT_MS,
          });
          console.log(
            "[proxy] Existing gateway is ready on port",
            GATEWAY_PORT,
          );
          return existingProc;
        } catch {
          console.error("[proxy] Existing gateway not reachable on port");
        }
      }

      // Last resort: try a direct HTTP check — the gateway might be running
      // under a command string that findGatewayProcess doesn't recognize
      console.log("[proxy] Trying direct health check fallback...");
      try {
        const healthCheck = await sandbox.containerFetch(
          new Request("http://localhost/healthz"),
          GATEWAY_PORT,
        );
        if (healthCheck.ok || healthCheck.status === 404) {
          // Any non-connection-error response means something is listening
          console.log(
            "[proxy] Port",
            GATEWAY_PORT,
            "is responding (status:",
            healthCheck.status,
            ") — gateway is running",
          );
          // Re-find the actual gateway process now that we know it's listening
          console.log("[proxy] Health check passed, re-scanning processes...");
          const runningProc = await findGatewayProcess(sandbox);
          console.log(
            "[proxy] Re-scan result:",
            runningProc?.id ?? "not found",
          );
          if (runningProc) return runningProc;
          return process; // Fallback: process ref won't be used for proxying
        }
      } catch {
        console.error("[proxy] Direct port check also failed");
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
): Promise<Response> {
  const url = new URL(request.url);
  console.log("[proxy] HTTP:", url.pathname + url.search);

  const response = await sandbox.containerFetch(request, GATEWAY_PORT);

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
  debug = false,
): Promise<Response> {
  const url = new URL(request.url);
  const hasToken = url.searchParams.has("token");
  console.log(
    `[ws] connect path=${url.pathname} hasToken=${hasToken} basePath=${basePath ?? "none"}`,
  );

  const containerResponse = await sandbox.wsConnect(request, GATEWAY_PORT);
  const containerWs = containerResponse.webSocket;

  if (!containerWs) {
    console.error(
      "[ws] no WebSocket in container response, status:",
      containerResponse.status,
    );
    if (debug) {
      const body = await containerResponse
        .clone()
        .text()
        .catch(() => "");
      console.error("[ws:debug] container response body:", body);
    }
    return containerResponse;
  }

  if (debug) console.log("[ws:debug] container WebSocket accepted");

  // Create a WebSocket pair for the client
  const [clientWs, serverWs] = Object.values(new WebSocketPair());

  serverWs.accept();
  containerWs.accept();

  // Relay: client -> container
  serverWs.addEventListener("message", (event) => {
    if (debug) {
      const preview =
        typeof event.data === "string"
          ? event.data.slice(0, 200)
          : `[binary ${(event.data as ArrayBuffer).byteLength}b]`;
      console.log("[ws:debug] client→container:", preview);
    }
    if (containerWs.readyState === WebSocket.OPEN) {
      containerWs.send(event.data);
    }
  });

  // Relay: container -> client (with URL rewriting for base path)
  containerWs.addEventListener("message", (event) => {
    if (serverWs.readyState === WebSocket.OPEN) {
      let data = event.data;
      if (debug) {
        const preview =
          typeof data === "string"
            ? data.slice(0, 200)
            : `[binary ${(data as ArrayBuffer).byteLength}b]`;
        console.log("[ws:debug] container→client:", preview);
      }
      // Rewrite URLs in JSON error messages to include base path.
      // Currently targets OpenClaw gateway's { error: { message: "..." } }
      // shape only. Other URL-bearing fields (e.g. redirect, url) are not
      // rewritten — extend the parsing below if those become relevant.
      if (basePath && typeof data === "string") {
        try {
          const parsed = JSON.parse(data);
          if (
            parsed.error?.message &&
            typeof parsed.error.message === "string"
          ) {
            if (debug)
              console.log(
                "[ws:debug] rewriting error message URLs for base path",
              );
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

  // Close events
  serverWs.addEventListener("close", (event) => {
    console.log(
      `[ws] client closed: code=${event.code} reason="${event.reason}"`,
    );
    containerWs.close(event.code, event.reason);
  });
  containerWs.addEventListener("close", (event) => {
    console.log(
      `[ws] container closed: code=${event.code} reason="${event.reason}"`,
    );
    let reason = event.reason;
    if (reason.length > 123) {
      reason = reason.slice(0, 120) + "...";
    }
    serverWs.close(event.code, reason);
  });

  // Error events
  serverWs.addEventListener("error", (event) => {
    console.error("[ws] client error:", event);
    containerWs.close(1011, "Client error");
  });
  containerWs.addEventListener("error", (event) => {
    console.error("[ws] container error:", event);
    serverWs.close(1011, "Container error");
  });

  return new Response(null, { status: 101, webSocket: clientWs });
}
