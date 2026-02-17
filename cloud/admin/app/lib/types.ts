/** Mirrors the Mac Mini Agent API schemas. */

export interface HealthResponse {
  hostname: string;
  uptime: number;
  cpu: { usage: number; cores: number };
  memory: { usedGb: number; totalGb: number };
  disk: { usedGb: number; totalGb: number };
  loadAverage: [number, number, number];
  claws: { active: number; max: number };
  tunnel: { status: "connected"; routes: number };
}

export interface ClawStatus {
  macUsername: string;
  launchdStatus: "loaded" | "unloaded" | "error";
  memoryUsageMb: number | null;
  gatewayPid: number | null;
  gatewayUptime: number | null;
  chromiumPid: number | null;
  processCount: number;
  diskMb?: number | null;
}

export interface ClawListResponse {
  claws: ClawStatus[];
}
