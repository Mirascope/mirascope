import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { ClawStatus } from "@/lib/types";
import { agent } from "@/lib/agent";
import { StatusBadge } from "./status-badge";

function fmtUptime(s: number | null): string {
  if (s == null) return "—";
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function fmtMem(mb: number | null): string {
  if (mb == null) return "—";
  return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb.toFixed(0)} MB`;
}

export function ClawTable({ claws }: { claws: ClawStatus[] }) {
  const qc = useQueryClient();
  const [busy, setBusy] = useState<Record<string, string>>({});

  async function act(user: string, action: "restart" | "backup" | "deprovision") {
    if (action === "deprovision" && !confirm(`Deprovision ${user}? This deletes the macOS user and all data.`))
      return;

    setBusy((p) => ({ ...p, [user]: action }));
    try {
      if (action === "restart") await agent.restartClaw(user);
      else if (action === "backup") await agent.backupClaw(user);
      else await agent.deprovisionClaw(user);
      await qc.invalidateQueries({ queryKey: ["claws"] });
      await qc.invalidateQueries({ queryKey: ["health"] });
    } catch (e) {
      alert(`Failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setBusy((p) => {
        const n = { ...p };
        delete n[user];
        return n;
      });
    }
  }

  if (claws.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-500">
        No claws provisioned on this machine.
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400 text-left">
            <th className="px-4 py-3 font-medium">User</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Gateway PID</th>
            <th className="px-4 py-3 font-medium">Uptime</th>
            <th className="px-4 py-3 font-medium">Memory</th>
            <th className="px-4 py-3 font-medium">Disk</th>
            <th className="px-4 py-3 font-medium">Chromium</th>
            <th className="px-4 py-3 font-medium">Procs</th>
            <th className="px-4 py-3 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {claws.map((c) => (
            <tr key={c.macUsername} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
              <td className="px-4 py-3 font-mono text-gray-200">{c.macUsername}</td>
              <td className="px-4 py-3"><StatusBadge status={c.launchdStatus} /></td>
              <td className="px-4 py-3 font-mono text-gray-400">{c.gatewayPid ?? "—"}</td>
              <td className="px-4 py-3 text-gray-400">{fmtUptime(c.gatewayUptime)}</td>
              <td className="px-4 py-3 text-gray-400">{fmtMem(c.memoryUsageMb)}</td>
              <td className="px-4 py-3 text-gray-400">{c.diskMb != null ? fmtMem(c.diskMb) : "—"}</td>
              <td className="px-4 py-3 font-mono text-gray-400">{c.chromiumPid ?? "—"}</td>
              <td className="px-4 py-3 text-gray-400">{c.processCount}</td>
              <td className="px-4 py-3 text-right space-x-1">
                <Btn onClick={() => act(c.macUsername, "restart")} loading={busy[c.macUsername] === "restart"} title="Restart">🔄</Btn>
                <Btn onClick={() => act(c.macUsername, "backup")} loading={busy[c.macUsername] === "backup"} title="Backup">💾</Btn>
                <Btn onClick={() => act(c.macUsername, "deprovision")} loading={busy[c.macUsername] === "deprovision"} title="Deprovision" danger>🗑️</Btn>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Btn({ onClick, loading, title, danger, children }: {
  onClick: () => void;
  loading: boolean;
  title: string;
  danger?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      title={title}
      className={`inline-flex items-center justify-center w-8 h-8 rounded-lg transition-colors disabled:opacity-50 ${danger ? "hover:bg-red-500/20" : "hover:bg-gray-700"}`}
    >
      {loading ? <span className="animate-spin text-xs">⏳</span> : children}
    </button>
  );
}
