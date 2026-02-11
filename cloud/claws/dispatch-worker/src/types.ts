import type { Sandbox } from "@cloudflare/sandbox";

/**
 * Environment bindings for the Claw Dispatch Worker.
 *
 * Unlike moltworker which has all secrets directly, the dispatch worker
 * gets per-claw secrets dynamically via the bootstrap config (fetched
 * through service binding to the Mirascope API).
 */
export interface DispatchEnv {
  /** Durable Object namespace for Sandbox containers */
  Sandbox: DurableObjectNamespace<Sandbox>;

  /**
   * Service binding to the Mirascope Cloud worker.
   * Internal API calls (bootstrap, resolve, status) are routed in-process
   * via the binding — no network hop, no bearer token.
   */
  MIRASCOPE_CLOUD: Fetcher;

  /** Cloudflare account ID for R2 endpoint URL */
  CLOUDFLARE_ACCOUNT_ID?: string;

  /** Site URL for CORS origin checking (e.g. "https://mirascope.com") */
  SITE_URL: string;
}

/**
 * Hono app environment type.
 */
export type AppEnv = {
  Bindings: DispatchEnv;
  Variables: {
    sandbox: Sandbox;
    clawId: string;
  };
};

/**
 * Bootstrap config returned by the Mirascope internal API.
 *
 * Mirrors the OpenClawConfig interface from cloud/claws/deployment/types.ts.
 * Duplicated here because the dispatch worker is a separate package.
 */
export interface OpenClawConfig {
  clawId: string;
  clawSlug: string;
  organizationId: string;
  organizationSlug: string;
  instanceType: string;
  r2: {
    bucketName: string;
    accessKeyId: string;
    secretAccessKey: string;
  };
  containerEnv: Record<string, string | undefined>;
}

/**
 * Process statuses returned by the @cloudflare/sandbox Process API.
 *
 * These are the possible values of `process.status` on a sandbox Process:
 *   - starting:  process is being created
 *   - running:   process is actively running
 *   - completed: process exited normally (exit code 0)
 *   - failed:    process exited with non-zero exit code
 *   - killed:    process was killed (e.g. via proc.kill())
 *   - error:     internal sandbox error
 */
export type SandboxProcessStatus =
  | "starting"
  | "running"
  | "completed"
  | "failed"
  | "killed"
  | "error";

/**
 * Container status as reported by the dispatch worker to the cloud backend.
 *
 * Mirrors ContainerStatus from cloud/cloudflare/containers/types.ts.
 */
export type ContainerStatus =
  | "running"
  | "stopping"
  | "stopped"
  | "healthy"
  | "unknown";

/**
 * Container state as reported by the dispatch worker.
 *
 * Mirrors ContainerState from cloud/cloudflare/containers/types.ts.
 */
export interface ContainerState {
  status: ContainerStatus;
  lastChange?: number;
  exitCode?: number;
}

/**
 * Health status returned by the public /_health endpoint.
 */
export type HealthStatus =
  | "running"
  | "starting"
  | "stopped"
  | "error"
  | "unknown"
  | "not_found";

/**
 * Map from @cloudflare/sandbox ProcessStatus → ContainerStatus.
 *
 * Used by /_internal/state to translate sandbox process status into
 * the container status vocabulary understood by the cloud backend.
 */
export const PROCESS_TO_CONTAINER_STATUS: Record<
  SandboxProcessStatus,
  ContainerStatus
> = {
  starting: "running",
  running: "running",
  completed: "stopped",
  failed: "stopped",
  killed: "stopped",
  error: "stopped",
};

/**
 * Map from @cloudflare/sandbox ProcessStatus → HealthStatus.
 *
 * Used by the public /_health endpoint to report process state.
 */
export const PROCESS_TO_HEALTH_STATUS: Record<
  SandboxProcessStatus,
  HealthStatus
> = {
  starting: "starting",
  running: "running",
  completed: "stopped",
  failed: "error",
  killed: "error",
  error: "error",
};
