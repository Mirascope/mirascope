const styles: Record<string, { color: string; label: string }> = {
  connected: { color: "bg-emerald-500/20 text-emerald-400", label: "Connected" },
  active: { color: "bg-emerald-500/20 text-emerald-400", label: "Active" },
  loaded: { color: "bg-emerald-500/20 text-emerald-400", label: "Running" },
  unloaded: { color: "bg-gray-500/20 text-gray-400", label: "Stopped" },
  error: { color: "bg-red-500/20 text-red-400", label: "Error" },
  draining: { color: "bg-amber-500/20 text-amber-400", label: "Draining" },
  maintenance: { color: "bg-blue-500/20 text-blue-400", label: "Maintenance" },
  offline: { color: "bg-red-500/20 text-red-400", label: "Offline" },
};

export function StatusBadge({ status }: { status: string }) {
  const s = styles[status] ?? { color: "bg-gray-500/20 text-gray-400", label: status };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${s.color}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {s.label}
    </span>
  );
}
