import type { HealthResponse } from "@/lib/types";
import { Gauge, CountGauge } from "./gauge";
import { StatusBadge } from "./status-badge";

function formatUptime(s: number): string {
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export function MacCard({ health }: { health: HealthResponse }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">{health.hostname}</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            {health.cpu.cores} cores · {health.memory.totalGb.toFixed(0)} GB RAM
          </p>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <StatusBadge status="active" />
          <StatusBadge status={health.tunnel.status} />
        </div>
      </div>

      <div className="flex gap-6 text-sm">
        <div>
          <span className="text-gray-500">Uptime</span>
          <p className="text-gray-200 font-medium">{formatUptime(health.uptime)}</p>
        </div>
        <div>
          <span className="text-gray-500">Load</span>
          <p className="text-gray-200 font-medium">
            {health.loadAverage.map((l) => l.toFixed(2)).join(" / ")}
          </p>
        </div>
        <div>
          <span className="text-gray-500">Tunnel Routes</span>
          <p className="text-gray-200 font-medium">{health.tunnel.routes}</p>
        </div>
      </div>

      <div className="space-y-3">
        <CountGauge label="Claws" value={health.claws.active} max={health.claws.max} />
        <Gauge label="CPU" value={health.cpu.usage} max={100} unit="%" />
        <Gauge label="Memory" value={health.memory.usedGb} max={health.memory.totalGb} unit=" GB" />
        <Gauge
          label="Disk"
          value={health.disk.usedGb}
          max={health.disk.totalGb}
          unit=" GB"
          thresholds={{ warning: 0.7, critical: 0.85 }}
        />
      </div>
    </div>
  );
}
