import { describe, it, expect } from "vitest";

import { getClawResources } from "../src/services/monitoring.js";
import { createMockExec, successResult } from "./helpers.js";

describe("monitoring", () => {
  describe("getClawResources", () => {
    it("parses ps output correctly", async () => {
      const psOutput = `  PID   RSS     ELAPSED COMM
  123 51200    01:23:45 openclaw gateway
  456 102400   00:45:30 Chromium Helper
  789 25600    00:10:00 node`;

      const { exec } = createMockExec(
        new Map([["ps", successResult(psOutput)]]),
      );

      const resources = await getClawResources("claw-test", exec);

      expect(resources.gatewayPid).toBe(123);
      expect(resources.chromiumPid).toBe(456);
      expect(resources.processCount).toBe(3);
      expect(resources.memoryUsageMb).toBe(
        Math.round((51200 + 102400 + 25600) / 1024),
      );
      expect(resources.gatewayUptime).toBe(1 * 3600 + 23 * 60 + 45);
    });

    it("returns nulls when user has no processes", async () => {
      const { exec } = createMockExec(
        new Map([["ps", { exitCode: 1, stdout: "", stderr: "no processes" }]]),
      );

      const resources = await getClawResources("claw-nonexist", exec);

      expect(resources.gatewayPid).toBeNull();
      expect(resources.chromiumPid).toBeNull();
      expect(resources.processCount).toBe(0);
    });
  });
});
