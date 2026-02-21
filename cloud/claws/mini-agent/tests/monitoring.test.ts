import { describe, it, expect } from "vitest";

import { parseClawResources, parseEtime } from "../src/services/monitoring.js";

describe("monitoring", () => {
  describe("parseClawResources", () => {
    it("parses ps output correctly", () => {
      const psOutput = `  PID   RSS     ELAPSED COMM
  123 51200    01:23:45 openclaw gateway
  456 102400   00:45:30 Chromium Helper
  789 25600    00:10:00 node`;

      const resources = parseClawResources(0, psOutput);

      expect(resources.gatewayPid).toBe(123);
      expect(resources.chromiumPid).toBe(456);
      expect(resources.processCount).toBe(3);
      expect(resources.memoryUsageMb).toBe(
        Math.round((51200 + 102400 + 25600) / 1024),
      );
      expect(resources.gatewayUptime).toBe(1 * 3600 + 23 * 60 + 45);
    });

    it("returns nulls when exit code is non-zero", () => {
      const resources = parseClawResources(1, "no processes");

      expect(resources.gatewayPid).toBeNull();
      expect(resources.chromiumPid).toBeNull();
      expect(resources.processCount).toBe(0);
    });
  });

  describe("parseEtime", () => {
    it("parses mm:ss format", () => {
      expect(parseEtime("10:30")).toBe(10 * 60 + 30);
    });

    it("parses hh:mm:ss format", () => {
      expect(parseEtime("01:23:45")).toBe(1 * 3600 + 23 * 60 + 45);
    });

    it("parses dd-hh:mm:ss format", () => {
      expect(parseEtime("2-01:23:45")).toBe(
        2 * 86400 + 1 * 3600 + 23 * 60 + 45,
      );
    });
  });
});
