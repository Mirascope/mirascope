import type { HealthResponse, ClawListResponse } from "./types";

/**
 * Agent API client.
 *
 * In dev, Vite proxies /api/agent → localhost:8787 to avoid CORS.
 * The base URL and token can be overridden via localStorage for
 * connecting to remote agents.
 */

function getConfig(): { url: string; token?: string } {
  if (typeof window === "undefined") return { url: "/api/agent" };
  return {
    url: localStorage.getItem("admin:agentUrl") ?? "/api/agent",
    token: localStorage.getItem("admin:agentToken") ?? undefined,
  };
}

export function setConfig(url: string, token?: string) {
  localStorage.setItem("admin:agentUrl", url);
  if (token) localStorage.setItem("admin:agentToken", token);
  else localStorage.removeItem("admin:agentToken");
}

async function agentFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const config = getConfig();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (config.token) headers["Authorization"] = `Bearer ${config.token}`;

  const res = await fetch(`${config.url}${path}`, {
    ...options,
    headers: { ...headers, ...options?.headers },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Agent ${res.status}: ${body}`);
  }

  return res.json() as Promise<T>;
}

export const agent = {
  health: () => agentFetch<HealthResponse>("/health"),
  listClaws: () => agentFetch<ClawListResponse>("/claws"),
  restartClaw: (user: string) =>
    agentFetch<{ success: boolean }>(`/claws/${user}/restart`, { method: "POST" }),
  backupClaw: (user: string) =>
    agentFetch<{ success: boolean; backupId: string }>(`/claws/${user}/backup`, { method: "POST" }),
  deprovisionClaw: (user: string) =>
    agentFetch<{ success: boolean }>(`/claws/${user}`, { method: "DELETE" }),
};
