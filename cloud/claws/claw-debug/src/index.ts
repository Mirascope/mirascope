#!/usr/bin/env bun
/**
 * mirascope-claw-debug — One-command tool to open the OpenClaw Control UI
 * connected to any gateway for debugging.
 *
 * Usage:
 *   bunx mirascope-claw-debug --gateway ws://localhost:18789
 *   bunx mirascope-claw-debug --gateway wss://claw-abc.claws.mirascope.dev
 *   bunx mirascope-claw-debug   # defaults to ws://localhost:18789
 */

import { parseArgs, type ParsedArgs } from "./args";
import { buildBootstrapHtml } from "./html";
import { checkGatewayReachable, gatewayToHttpUrl } from "./gateway";

async function main() {
  let args: ParsedArgs;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (e: any) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }

  if (args.help) {
    printUsage();
    process.exit(0);
  }

  const gatewayUrl = args.gateway;
  const httpUrl = gatewayToHttpUrl(gatewayUrl);

  console.log(`🔌 Gateway: ${gatewayUrl}`);
  console.log(`🌐 HTTP:    ${httpUrl}`);

  // Check if gateway is reachable
  console.log("⏳ Checking gateway...");
  const reachable = await checkGatewayReachable(httpUrl);
  if (!reachable) {
    console.error(
      `\n❌ Gateway not reachable at ${httpUrl}\n` +
        `   Make sure the OpenClaw gateway is running.\n` +
        `   For local: openclaw gateway start\n` +
        `   For remote: check your tunnel is active\n`,
    );
    process.exit(1);
  }
  console.log("✅ Gateway is reachable");

  // Start local server serving the bootstrap page
  const html = buildBootstrapHtml(gatewayUrl, args.token);
  const port = args.port ?? 0;

  const server = Bun.serve({
    port,
    fetch(_req) {
      return new Response(html, {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    },
  });

  const localUrl = `http://localhost:${server.port}`;
  console.log(`\n🚀 Debug UI running at ${localUrl}`);

  // Open browser
  if (args.open) {
    const { exec } = await import("child_process");
    const cmd =
      process.platform === "darwin"
        ? "open"
        : process.platform === "win32"
          ? "start"
          : "xdg-open";
    exec(`${cmd} ${localUrl}`, (err) => {
      if (err) console.warn("Could not open browser automatically");
    });
  }

  console.log("Press Ctrl+C to stop\n");
}

function printUsage() {
  console.log(`
mirascope-claw-debug — Debug a claw by chatting with it directly

Usage:
  mirascope-claw-debug [options]

Options:
  --gateway <url>   Gateway WebSocket URL (default: ws://localhost:18789)
  --token <token>   Gateway auth token (optional, for remote claws)
  --port <port>     Local server port (default: auto)
  --no-open         Don't auto-open browser
  --help            Show this help message

Examples:
  mirascope-claw-debug
  mirascope-claw-debug --gateway wss://claw-abc.claws.mirascope.dev
  mirascope-claw-debug --gateway ws://localhost:18789 --token mytoken
`);
}

main();
