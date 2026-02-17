import { describe, it, expect, vi, beforeEach } from "vitest";

import { createMockExec, successResult, failResult } from "./helpers.js";

// Mock the tunnel module to avoid filesystem operations
vi.mock("../src/services/tunnel.js", () => ({
  addRoute: vi.fn().mockResolvedValue(undefined),
  removeRoute: vi.fn().mockResolvedValue(undefined),
  restartCloudflared: vi.fn().mockResolvedValue(undefined),
  hasRoute: vi.fn().mockResolvedValue(true),
  readTunnelConfig: vi.fn().mockResolvedValue({ tunnel: "test", ingress: [] }),
}));

// Mock fetch for gateway health check
beforeEach(() => {
  globalThis.fetch = vi
    .fn()
    .mockResolvedValue({ ok: true }) as unknown as typeof fetch;
});

import type { AgentConfig } from "../src/lib/config.js";

import { provision, listClawUsers } from "../src/services/provisioning.js";

const testConfig: AgentConfig = {
  authToken: "test",
  port: 7600,
  tunnelConfigPath: "/tmp/test-config.yml",
  tunnelHostnameSuffix: "claws.mirascope.dev",
  maxClaws: 12,
  portRangeStart: 3001,
  portRangeEnd: 3100,
};

describe("provisioning", () => {
  describe("provision", () => {
    it("creates user, loads launchd, adds tunnel route", async () => {
      const { exec, calls } = createMockExec();

      const result = await provision(
        {
          clawId: "test-claw-id",
          macUsername: "claw-testclaw",
          localPort: 3001,
          gatewayToken: "gw-token",
          tunnelHostname: "claw-test.claws.mirascope.dev",
          envVars: {},
        },
        testConfig,
        exec,
      );

      expect(result.success).toBe(true);
      expect(result.macUsername).toBe("claw-testclaw");
      expect(result.localPort).toBe(3001);

      // Verify user creation was called
      const sysadminCall = calls.find(
        (c) => c.command === "sysadminctl" || c.args.includes("sysadminctl"),
      );
      expect(sysadminCall).toBeDefined();

      // Verify launchd load was called
      const launchctlCall = calls.find(
        (c) => c.command === "launchctl" || c.args.includes("launchctl"),
      );
      expect(launchctlCall).toBeDefined();
    });

    it("cleans up on user creation failure", async () => {
      const { exec } = createMockExec(
        new Map([["sysadminctl", failResult("user creation failed")]]),
      );

      const result = await provision(
        {
          clawId: "test-fail",
          macUsername: "claw-failtest",
          localPort: 3002,
          gatewayToken: "gw-token",
          tunnelHostname: "claw-fail.claws.mirascope.dev",
          envVars: {},
        },
        testConfig,
        exec,
      );

      expect(result.success).toBe(false);
      expect(result.error).toContain("user creation failed");
    });
  });

  describe("listClawUsers", () => {
    it("lists claw users from dscl output", async () => {
      const { exec } = createMockExec(
        new Map([
          [
            "dscl",
            successResult(
              "root\ndaemon\nclaw-abc12345\nclaw-def67890\nnobody\n",
            ),
          ],
        ]),
      );

      const users = await listClawUsers(exec);
      expect(users).toEqual(["claw-abc12345", "claw-def67890"]);
    });

    it("returns empty array on dscl failure", async () => {
      const { exec } = createMockExec(new Map([["dscl", failResult()]]));
      const users = await listClawUsers(exec);
      expect(users).toEqual([]);
    });
  });
});
