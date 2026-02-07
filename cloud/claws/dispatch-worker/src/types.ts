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
  CF_ACCOUNT_ID?: string;
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
 * Container state as reported by the dispatch worker.
 *
 * Mirrors ContainerState from cloud/claws/cloudflare/containers/types.ts.
 */
export interface ContainerState {
  status: "running" | "stopping" | "stopped" | "healthy" | "unknown";
  lastChange?: number;
  exitCode?: number;
}
