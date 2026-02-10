import { describe, it, expect, beforeAll } from "vitest";
import WebSocket from "ws";

import {
  GATEWAY_URL,
  GATEWAY_TOKEN,
  gatewayFetch,
  waitForGateway,
} from "../workers/gateway-client";

describe("proxy → Docker OpenClaw gateway", () => {
  beforeAll(async () => {
    await waitForGateway();
  }, 90_000);

  it("HTTP server is reachable", async () => {
    const res = await gatewayFetch("/");
    // Gateway returns 404 for unknown paths — that's fine, means it's alive
    expect(res.status).toBeGreaterThan(0);
  });

  it("authenticated HTTP request succeeds", async () => {
    // gatewayFetch includes the Authorization header with GATEWAY_TOKEN
    const res = await gatewayFetch("/api/health");
    // Even if /api/health doesn't exist, auth should not be rejected
    // (vs an unauthenticated request which may get 401/403)
    expect([200, 404]).toContain(res.status);
  });

  it("WebSocket upgrade is supported", async () => {
    const wsUrl = GATEWAY_URL.replace(/^http/, "ws");
    const ws = new WebSocket(wsUrl);
    try {
      const opened = await new Promise<boolean>((resolve) => {
        ws.addEventListener("open", () => resolve(true));
        ws.addEventListener("error", () => resolve(false));
        setTimeout(() => resolve(false), 5000);
      });
      expect(opened).toBe(true);
    } finally {
      ws.close();
    }
  });

  it("authenticated WebSocket connection receives messages", async () => {
    // Pass token during WebSocket upgrade via query param
    const wsUrl = `${GATEWAY_URL.replace(/^http/, "ws")}?token=${GATEWAY_TOKEN}`;
    const ws = new WebSocket(wsUrl);
    try {
      await new Promise<void>((resolve, reject) => {
        ws.addEventListener("open", () => resolve());
        ws.addEventListener("error", () =>
          reject(new Error("WebSocket connection failed")),
        );
        setTimeout(() => reject(new Error("WebSocket open timed out")), 5000);
      });

      // Send a health check request
      ws.send(
        JSON.stringify({ type: "req", id: "auth-test", method: "health" }),
      );

      const response = await new Promise<string>((resolve) => {
        ws.addEventListener("message", (ev: WebSocket.MessageEvent) =>
          resolve(String(ev.data)),
        );
        setTimeout(() => resolve("timeout"), 5000);
      });

      // Authenticated connection should get a response (not timeout)
      expect(response).not.toBe("timeout");
    } finally {
      ws.close();
    }
  });
});
