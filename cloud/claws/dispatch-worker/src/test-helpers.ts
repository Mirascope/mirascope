/**
 * Shared test helpers: mock factories for Sandbox, Process, and OpenClawDeployConfig.
 */

import { vi } from "vitest";

import type { OpenClawDeployConfig, DispatchEnv } from "./types";

/**
 * Minimal mock of the Process interface from @cloudflare/sandbox.
 */
export interface MockProcess {
  id: string;
  command: string;
  status: string;
  exitCode: number | null;
  kill: ReturnType<typeof vi.fn>;
  getStatus: ReturnType<typeof vi.fn>;
  getLogs: ReturnType<typeof vi.fn>;
  waitForPort: ReturnType<typeof vi.fn>;
  waitForLog: ReturnType<typeof vi.fn>;
}

export function createMockProcess(
  overrides: Partial<MockProcess> = {},
): MockProcess {
  return {
    id: "proc-1",
    command: "openclaw gateway --port 18789",
    status: "running",
    exitCode: null,
    kill: vi.fn().mockResolvedValue(undefined),
    getStatus: vi.fn().mockResolvedValue("running"),
    getLogs: vi.fn().mockResolvedValue({ stdout: "", stderr: "" }),
    waitForPort: vi.fn().mockResolvedValue(undefined),
    waitForLog: vi.fn().mockResolvedValue({ matched: true }),
    ...overrides,
  };
}

/**
 * Minimal mock of the Sandbox class from @cloudflare/sandbox.
 */
export interface MockSandbox {
  listProcesses: ReturnType<typeof vi.fn>;
  startProcess: ReturnType<typeof vi.fn>;
  mountBucket: ReturnType<typeof vi.fn>;
  destroy: ReturnType<typeof vi.fn>;
  containerFetch: ReturnType<typeof vi.fn>;
  wsConnect: ReturnType<typeof vi.fn>;
}

export function createMockSandbox(
  overrides: Partial<MockSandbox> = {},
): MockSandbox {
  return {
    listProcesses: vi.fn().mockResolvedValue([]),
    startProcess: vi.fn().mockResolvedValue(createMockProcess()),
    mountBucket: vi.fn().mockResolvedValue(undefined),
    destroy: vi.fn().mockResolvedValue(undefined),
    containerFetch: vi
      .fn()
      .mockResolvedValue(new Response("ok", { status: 200 })),
    wsConnect: vi.fn().mockResolvedValue({ status: 101, webSocket: null }),
    ...overrides,
  };
}

/**
 * Create a minimal valid OpenClawDeployConfig for testing.
 */
export function createMockConfig(
  overrides: Partial<OpenClawDeployConfig> = {},
): OpenClawDeployConfig {
  return {
    clawId: "claw-123",
    clawSlug: "test-claw",
    organizationId: "org-456",
    organizationSlug: "test-org",
    instanceType: "basic",
    r2: {
      bucketName: "claw-claw-123",
      accessKeyId: "test-access-key",
      secretAccessKey: "test-secret-key",
    },
    containerEnv: {
      MIRASCOPE_API_KEY: "mk-test-key",
      ANTHROPIC_API_KEY: "mk-test-key",
      ANTHROPIC_BASE_URL: "https://router.mirascope.com/v1",
      OPENCLAW_GATEWAY_TOKEN: "gw-token-123",
    },
    ...overrides,
  };
}

/**
 * Create a minimal valid DispatchEnv for testing.
 */
export function createMockEnv(
  overrides: Partial<DispatchEnv> = {},
): DispatchEnv {
  return {
    Sandbox: {} as unknown as DurableObjectNamespace,
    MIRASCOPE_CLOUD: {} as unknown as Fetcher,
    CLOUDFLARE_ACCOUNT_ID: "test-account-id",
    SITE_URL: "https://mirascope.com",
    ...overrides,
  };
}
