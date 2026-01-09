import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  getSettings,
  getSettingsFromEnvironment,
  type CloudflareEnvironment,
} from "@/settings";

describe("settings", () => {
  describe("getSettings", () => {
    const originalEnv = process.env;

    beforeEach(() => {
      vi.resetModules();
      process.env = { ...originalEnv };
    });

    afterEach(() => {
      process.env = originalEnv;
    });

    it("returns default values when environment variables are not set", () => {
      delete process.env.ENVIRONMENT;
      delete process.env.CLICKHOUSE_URL;
      delete process.env.CLICKHOUSE_USER;
      delete process.env.CLICKHOUSE_DATABASE;

      const settings = getSettings();

      expect(settings.env).toBe("local");
      expect(settings.CLICKHOUSE_URL).toBe("http://localhost:8123");
      expect(settings.CLICKHOUSE_USER).toBe("default");
      expect(settings.CLICKHOUSE_DATABASE).toBe("mirascope_analytics");
    });

    it("reads ClickHouse settings from environment variables", () => {
      process.env.CLICKHOUSE_URL = "https://ch.example.com";
      process.env.CLICKHOUSE_USER = "testuser";
      process.env.CLICKHOUSE_PASSWORD = "testpass";
      process.env.CLICKHOUSE_DATABASE = "testdb";

      const settings = getSettings();

      expect(settings.CLICKHOUSE_URL).toBe("https://ch.example.com");
      expect(settings.CLICKHOUSE_USER).toBe("testuser");
      expect(settings.CLICKHOUSE_PASSWORD).toBe("testpass");
      expect(settings.CLICKHOUSE_DATABASE).toBe("testdb");
    });

    it("reads TLS settings from environment variables", () => {
      process.env.CLICKHOUSE_TLS_ENABLED = "true";
      process.env.CLICKHOUSE_TLS_CA = "/path/to/ca.pem";
      process.env.CLICKHOUSE_TLS_SKIP_VERIFY = "false";
      process.env.CLICKHOUSE_TLS_HOSTNAME_VERIFY = "true";
      process.env.CLICKHOUSE_TLS_MIN_VERSION = "TLSv1.3";

      const settings = getSettings();

      expect(settings.CLICKHOUSE_TLS_ENABLED).toBe(true);
      expect(settings.CLICKHOUSE_TLS_CA).toBe("/path/to/ca.pem");
      expect(settings.CLICKHOUSE_TLS_SKIP_VERIFY).toBe(false);
      expect(settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY).toBe(true);
      expect(settings.CLICKHOUSE_TLS_MIN_VERSION).toBe("TLSv1.3");
    });

    it("defaults TLS_HOSTNAME_VERIFY to true when not set", () => {
      delete process.env.CLICKHOUSE_TLS_HOSTNAME_VERIFY;

      const settings = getSettings();

      expect(settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY).toBe(true);
    });

    it("sets TLS_HOSTNAME_VERIFY to false when explicitly set to 'false'", () => {
      process.env.CLICKHOUSE_TLS_HOSTNAME_VERIFY = "false";

      const settings = getSettings();

      expect(settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY).toBe(false);
    });

    it("throws error in production when TLS is not enabled", () => {
      process.env.ENVIRONMENT = "production";
      process.env.CLICKHOUSE_TLS_ENABLED = "false";

      expect(() => getSettings()).toThrow(
        "CLICKHOUSE_TLS_ENABLED=true is required in production",
      );
    });

    it("throws error in production when TLS_SKIP_VERIFY is true", () => {
      process.env.ENVIRONMENT = "production";
      process.env.CLICKHOUSE_TLS_ENABLED = "true";
      process.env.CLICKHOUSE_TLS_SKIP_VERIFY = "true";

      expect(() => getSettings()).toThrow(
        "CLICKHOUSE_TLS_SKIP_VERIFY=true is not allowed in production",
      );
    });

    it("throws error in production when TLS_HOSTNAME_VERIFY is false", () => {
      process.env.ENVIRONMENT = "production";
      process.env.CLICKHOUSE_TLS_ENABLED = "true";
      process.env.CLICKHOUSE_TLS_SKIP_VERIFY = "false";
      process.env.CLICKHOUSE_TLS_HOSTNAME_VERIFY = "false";

      expect(() => getSettings()).toThrow(
        "CLICKHOUSE_TLS_HOSTNAME_VERIFY=true is required in production",
      );
    });

    it("succeeds in production with valid TLS settings", () => {
      process.env.ENVIRONMENT = "production";
      process.env.CLICKHOUSE_TLS_ENABLED = "true";
      process.env.CLICKHOUSE_TLS_SKIP_VERIFY = "false";
      process.env.CLICKHOUSE_TLS_HOSTNAME_VERIFY = "true";

      const settings = getSettings();

      expect(settings.env).toBe("production");
      expect(settings.CLICKHOUSE_TLS_ENABLED).toBe(true);
    });
  });

  describe("getSettingsFromEnvironment", () => {
    it("defaults env to 'local' when ENVIRONMENT is not set", () => {
      const env: CloudflareEnvironment = {};
      const settings = getSettingsFromEnvironment(env);

      expect(settings.env).toBe("local");
    });

    it("uses ENVIRONMENT from env bindings", () => {
      const env: CloudflareEnvironment = { ENVIRONMENT: "production" };
      const settings = getSettingsFromEnvironment(env);

      expect(settings.env).toBe("production");
    });

    it("maps all ClickHouse settings from env", () => {
      const env: CloudflareEnvironment = {
        CLICKHOUSE_URL: "https://ch.example.com",
        CLICKHOUSE_USER: "user",
        CLICKHOUSE_PASSWORD: "pass",
        CLICKHOUSE_DATABASE: "analytics",
      };
      const settings = getSettingsFromEnvironment(env);

      expect(settings.CLICKHOUSE_URL).toBe("https://ch.example.com");
      expect(settings.CLICKHOUSE_USER).toBe("user");
      expect(settings.CLICKHOUSE_PASSWORD).toBe("pass");
      expect(settings.CLICKHOUSE_DATABASE).toBe("analytics");
    });

    it("returns default ClickHouse values when not set", () => {
      const env: CloudflareEnvironment = {};
      const settings = getSettingsFromEnvironment(env);

      expect(settings.CLICKHOUSE_URL).toBe("http://localhost:8123");
      expect(settings.CLICKHOUSE_USER).toBe("default");
      expect(settings.CLICKHOUSE_DATABASE).toBe("mirascope_analytics");
    });

    it("maps TLS settings from env", () => {
      const env: CloudflareEnvironment = {
        CLICKHOUSE_TLS_ENABLED: "true",
        CLICKHOUSE_TLS_CA: "/path/to/ca.pem",
        CLICKHOUSE_TLS_SKIP_VERIFY: "true",
        CLICKHOUSE_TLS_HOSTNAME_VERIFY: "false",
      };
      const settings = getSettingsFromEnvironment(env);

      expect(settings.CLICKHOUSE_TLS_ENABLED).toBe(true);
      expect(settings.CLICKHOUSE_TLS_CA).toBe("/path/to/ca.pem");
      expect(settings.CLICKHOUSE_TLS_SKIP_VERIFY).toBe(true);
      expect(settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY).toBe(false);
    });

    it("defaults TLS_HOSTNAME_VERIFY to true when not set", () => {
      const env: CloudflareEnvironment = {};
      const settings = getSettingsFromEnvironment(env);

      expect(settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY).toBe(true);
    });
  });
});
