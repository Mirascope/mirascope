interface GaugeProps {
  label: string;
  value: number;
  max: number;
  unit?: string;
  thresholds?: { warning: number; critical: number };
}

export function Gauge({
  label,
  value,
  max,
  unit = "",
  thresholds = { warning: 0.7, critical: 0.9 },
}: GaugeProps) {
  const pct = max > 0 ? value / max : 0;
  const width = `${Math.min(pct * 100, 100)}%`;
  const color =
    pct >= thresholds.critical
      ? "bg-red-500"
      : pct >= thresholds.warning
        ? "bg-amber-500"
        : "bg-emerald-500";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span>
          {value.toFixed(1)}{unit} / {max.toFixed(1)}{unit}
        </span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width }}
        />
      </div>
    </div>
  );
}

export function CountGauge({
  label,
  value,
  max,
}: {
  label: string;
  value: number;
  max: number;
}) {
  const pct = max > 0 ? value / max : 0;
  const width = `${Math.min(pct * 100, 100)}%`;
  const color =
    pct >= 0.9 ? "bg-red-500" : pct >= 0.7 ? "bg-amber-500" : "bg-sky-500";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span>{value} / {max}</span>
      </div>
      <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width }}
        />
      </div>
    </div>
  );
}
