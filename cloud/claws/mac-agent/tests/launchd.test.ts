import { describe, it, expect } from "vitest";

import { generatePlist } from "../src/services/launchd.js";

describe("launchd", () => {
  describe("generatePlist", () => {
    it("generates valid plist XML", () => {
      const plist = generatePlist({
        macUsername: "claw-abc12345",
        localPort: 3001,
        gatewayToken: "test-token",
      });

      expect(plist).toContain("com.mirascope.claw.claw-abc12345");
      expect(plist).toContain("/usr/local/bin/openclaw");
      expect(plist).toContain("gateway");
      expect(plist).toContain("start");
      expect(plist).toContain("<string>3001</string>");
      expect(plist).toContain("/Users/claw-abc12345");
      expect(plist).toContain("KeepAlive");
      expect(plist).toContain("RunAtLoad");
    });

    it("includes custom env vars", () => {
      const plist = generatePlist({
        macUsername: "claw-test1234",
        localPort: 3002,
        gatewayToken: "tok",
        envVars: { MY_VAR: "my-value", OTHER: "other-val" },
      });

      expect(plist).toContain("<key>MY_VAR</key>");
      expect(plist).toContain("<string>my-value</string>");
      expect(plist).toContain("<key>OTHER</key>");
    });

    it("escapes XML special characters", () => {
      const plist = generatePlist({
        macUsername: "claw-test1234",
        localPort: 3003,
        gatewayToken: "tok",
        envVars: { KEY: 'val<with>&special"chars' },
      });

      expect(plist).toContain("&lt;");
      expect(plist).toContain("&amp;");
      expect(plist).toContain("&quot;");
      expect(plist).not.toContain("val<with>");
    });
  });
});
