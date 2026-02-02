import { afterEach, describe, expect, it, vi } from "vitest";

import { MirascopeClient, getClient, resetClient } from "@/api/client";
import { resetSettings, updateSettings } from "@/api/settings";

describe("MirascopeClient", () => {
  afterEach(() => {
    resetClient();
    resetSettings();
    vi.unstubAllEnvs();
  });

  it("creates a client with default settings", () => {
    const client = new MirascopeClient();

    expect(client).toBeInstanceOf(MirascopeClient);
  });

  it("creates a client with custom options", () => {
    const client = new MirascopeClient({
      apiKey: "custom-key",
      baseURL: "https://custom.example.com",
      timeoutInSeconds: 60,
      maxRetries: 5,
    });

    expect(client).toBeInstanceOf(MirascopeClient);
  });

  it("uses settings when no options provided", () => {
    updateSettings({
      apiKey: "settings-key",
      baseURL: "https://settings.example.com",
    });

    const client = new MirascopeClient();

    expect(client).toBeInstanceOf(MirascopeClient);
  });

  it("options override settings", () => {
    updateSettings({
      apiKey: "settings-key",
      baseURL: "https://settings.example.com",
    });

    const client = new MirascopeClient({
      apiKey: "override-key",
    });

    expect(client).toBeInstanceOf(MirascopeClient);
  });

  it("exposes resource clients", () => {
    const client = new MirascopeClient();

    expect(client.health).toBeDefined();
    expect(client.traces).toBeDefined();
    expect(client.functions).toBeDefined();
    expect(client.annotations).toBeDefined();
    expect(client.organizations).toBeDefined();
    expect(client.projects).toBeDefined();
    expect(client.environments).toBeDefined();
    expect(client.apiKeys).toBeDefined();
    expect(client.tags).toBeDefined();
  });
});

describe("getClient", () => {
  afterEach(() => {
    resetClient();
    resetSettings();
    vi.unstubAllEnvs();
  });

  it("returns a cached client when called without options", () => {
    const client1 = getClient();
    const client2 = getClient();

    expect(client1).toBe(client2);
  });

  it("creates a new client when called with options", () => {
    const client1 = getClient();
    const client2 = getClient({ apiKey: "different-key" });

    expect(client1).not.toBe(client2);
  });

  it("does not cache clients created with options", () => {
    const client1 = getClient({ apiKey: "key1" });
    const client2 = getClient({ apiKey: "key2" });

    expect(client1).not.toBe(client2);
  });
});

describe("resetClient", () => {
  afterEach(() => {
    resetClient();
    resetSettings();
  });

  it("clears the cached client", () => {
    const client1 = getClient();

    resetClient();

    const client2 = getClient();

    expect(client1).not.toBe(client2);
  });
});
