import { useState, useMemo } from "react";
import { CloudLayout } from "@/app/components/cloud-layout";
import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import { useEnvironmentAnalytics } from "@/app/api/environments";
import { StatCard } from "@/app/components/dashboard/stat-card";
import { TopItemsList } from "@/app/components/dashboard/top-items-list";
import {
  TimePeriodSelector,
  getTimeRange,
  type TimePeriod,
} from "@/app/components/dashboard/time-period-selector";

function CloudDashboardPage() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();
  const [timePeriod, setTimePeriod] = useState<TimePeriod>("7d");

  const { startTime, endTime } = useMemo(
    () => getTimeRange(timePeriod),
    [timePeriod],
  );

  const { data: analytics, isLoading } = useEnvironmentAnalytics(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    startTime,
    endTime,
  );

  const formatCost = (cost: number) => `$${cost.toFixed(2)}`;
  const formatErrorRate = (rate: number) => `${(rate * 100).toFixed(1)}%`;
  const formatDuration = (ms: number | null) =>
    ms !== null ? `${ms.toFixed(0)}ms` : "N/A";

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">Dashboard</h1>
              <p className="text-muted-foreground">
                Analytics for {selectedEnvironment?.name ?? "your environment"}
              </p>
            </div>
            <TimePeriodSelector value={timePeriod} onChange={setTimePeriod} />
          </div>

          {/* Environment not selected state */}
          {!selectedEnvironment ? (
            <div className="flex items-center justify-center h-64">
              <p className="text-muted-foreground">
                Please select an organization, project, and environment to view
                analytics.
              </p>
            </div>
          ) : (
            <>
              {/* Stat Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Total Spans"
                  value={analytics?.totalSpans.toLocaleString() ?? "0"}
                  isLoading={isLoading}
                />
                <StatCard
                  title="Total Cost"
                  value={formatCost(analytics?.totalCostUsd ?? 0)}
                  isLoading={isLoading}
                />
                <StatCard
                  title="Error Rate"
                  value={formatErrorRate(analytics?.errorRate ?? 0)}
                  isLoading={isLoading}
                />
                <StatCard
                  title="Avg Duration"
                  value={formatDuration(analytics?.avgDurationMs ?? null)}
                  subtitle={
                    analytics?.p95DurationMs != null
                      ? `p95: ${formatDuration(analytics.p95DurationMs)}`
                      : undefined
                  }
                  isLoading={isLoading}
                />
              </div>

              {/* Top Items */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <TopItemsList
                  title="Top 5 Models"
                  items={(analytics?.topModels ?? []).map((m) => ({
                    name: m.model,
                    count: m.count,
                  }))}
                  isLoading={isLoading}
                />
                <TopItemsList
                  title="Top 5 Functions"
                  items={(analytics?.topFunctions ?? []).map((f) => ({
                    name: f.functionName,
                    count: f.count,
                  }))}
                  isLoading={isLoading}
                />
              </div>
            </>
          )}
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/dashboard")({
  component: CloudDashboardPage,
});
