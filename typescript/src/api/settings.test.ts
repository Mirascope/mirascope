import { afterEach, describe, expect, it, vi } from "vitest";

import { getSettings, updateSettings, resetSettings } from "@/api/settings";

describe("settings", () => {
  afterEach(() => {
    resetSettings();
    vi.unstubAllEnvs();
  });

  describe("getSettings", () => {
    it("returns default values when env vars are not set", () => {
      vi.stubEnv("MIRASCOPE_API_KEY", "");
      vi.stubEnv("MIRASCOPE_BASE_URL", "");
      resetSettings();

      const settings = getSettings();

      expect(settings.baseURL).toBe("https://mirascope.com/api/v2");
      expect(settings.apiKey).toBe("");
    });

    it("returns a copy of settings", () => {
      const settings1 = getSettings();
      const settings2 = getSettings();

      expect(settings1).not.toBe(settings2);
      expect(settings1).toEqual(settings2);
    });
  });

  describe("updateSettings", () => {
    it("updates apiKey", () => {
      updateSettings({ apiKey: "test-api-key" });

      const settings = getSettings();

      expect(settings.apiKey).toBe("test-api-key");
    });

    it("updates baseURL", () => {
      updateSettings({ baseURL: "https://custom.example.com" });

      const settings = getSettings();

      expect(settings.baseURL).toBe("https://custom.example.com");
    });

    it("updates multiple settings at once", () => {
      updateSettings({
        apiKey: "new-key",
        baseURL: "https://new.example.com",
      });

      const settings = getSettings();

      expect(settings.apiKey).toBe("new-key");
      expect(settings.baseURL).toBe("https://new.example.com");
    });

    it("preserves existing settings when updating partially", () => {
      updateSettings({ apiKey: "first-key" });
      updateSettings({ baseURL: "https://new.example.com" });

      const settings = getSettings();

      expect(settings.apiKey).toBe("first-key");
      expect(settings.baseURL).toBe("https://new.example.com");
    });
  });

  describe("resetSettings", () => {
    it("resets settings to default values", () => {
      vi.stubEnv("MIRASCOPE_API_KEY", "");
      vi.stubEnv("MIRASCOPE_BASE_URL", "");

      updateSettings({
        apiKey: "custom-key",
        baseURL: "https://custom.example.com",
      });

      resetSettings();

      const settings = getSettings();

      expect(settings.baseURL).toBe("https://mirascope.com/api/v2");
      expect(settings.apiKey).toBe("");
    });
  });
});
