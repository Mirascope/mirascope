import { writeFile, unlink, mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect, beforeEach, afterEach } from "vitest";

import {
  addRouteToConfig,
  removeRouteFromConfig,
  hasRouteInConfig,
  getRouteCountFromConfig,
  readTunnelConfigFromFile,
} from "../src/services/tunnel.js";

describe("tunnel", () => {
  let configPath: string;
  let tmpDir: string;

  const baseConfig = `tunnel: test-tunnel-id
credentials_file: /etc/cloudflared/credentials.json
ingress:
  - hostname: agent.mini.claws.mirascope.dev
    service: http://localhost:7600
  - service: http_status:404
`;

  beforeEach(async () => {
    tmpDir = await mkdtemp(path.join(tmpdir(), "mac-agent-test-"));
    configPath = path.join(tmpDir, "config.yml");
    await writeFile(configPath, baseConfig, "utf-8");
  });

  afterEach(async () => {
    try {
      await unlink(configPath);
    } catch {
      /* cleanup */
    }
  });

  it("reads tunnel config", async () => {
    const config = await readTunnelConfigFromFile(configPath);
    expect(config.tunnel).toBe("test-tunnel-id");
    expect(config.ingress).toHaveLength(2);
  });

  it("adds a route before catch-all", async () => {
    await addRouteToConfig(configPath, "claw-abc.claws.mirascope.dev", 3001);

    const config = await readTunnelConfigFromFile(configPath);
    expect(config.ingress).toHaveLength(3);
    expect(config.ingress[1]!.hostname).toBe("claw-abc.claws.mirascope.dev");
    expect(config.ingress[1]!.service).toBe("http://localhost:3001");
    expect(config.ingress[2]!.hostname).toBeUndefined();
  });

  it("updates existing route", async () => {
    await addRouteToConfig(configPath, "claw-abc.claws.mirascope.dev", 3001);
    await addRouteToConfig(configPath, "claw-abc.claws.mirascope.dev", 3002);

    const config = await readTunnelConfigFromFile(configPath);
    const matching = config.ingress.filter(
      (r) => r.hostname === "claw-abc.claws.mirascope.dev",
    );
    expect(matching).toHaveLength(1);
    expect(matching[0]!.service).toBe("http://localhost:3002");
  });

  it("removes a route", async () => {
    await addRouteToConfig(configPath, "claw-abc.claws.mirascope.dev", 3001);
    await removeRouteFromConfig(configPath, "claw-abc.claws.mirascope.dev");

    const config = await readTunnelConfigFromFile(configPath);
    expect(
      config.ingress.some((r) => r.hostname === "claw-abc.claws.mirascope.dev"),
    ).toBe(false);
    expect(config.ingress[config.ingress.length - 1]!.service).toBe(
      "http_status:404",
    );
  });

  it("checks route existence", async () => {
    expect(
      await hasRouteInConfig(configPath, "claw-abc.claws.mirascope.dev"),
    ).toBe(false);
    await addRouteToConfig(configPath, "claw-abc.claws.mirascope.dev", 3001);
    expect(
      await hasRouteInConfig(configPath, "claw-abc.claws.mirascope.dev"),
    ).toBe(true);
  });

  it("counts routes", async () => {
    expect(await getRouteCountFromConfig(configPath)).toBe(1);
    await addRouteToConfig(configPath, "claw-a.test", 3001);
    await addRouteToConfig(configPath, "claw-b.test", 3002);
    expect(await getRouteCountFromConfig(configPath)).toBe(3);
  });
});
