import { DragHandleDots2Icon } from "@radix-ui/react-icons";
import { createFileRoute } from "@tanstack/react-router";
import { RefreshCw } from "lucide-react";
import { useState, useMemo, useEffect } from "react";

import type { SpanDetail, SpanSearchResult } from "@/api/traces-search.schemas";

import { useFunctionDetail } from "@/app/api/functions";
import { useTracesSearch, useTraceDetail } from "@/app/api/traces";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { SpanDetailPanel } from "@/app/components/traces/span-detail-panel";
import { TracesTable } from "@/app/components/traces/traces-table";
import { Button } from "@/app/components/ui/button";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/app/components/ui/resizable";
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

/** Type guard to check if span has detailed data (attributes field) */
function isSpanDetail(span: SpanDetail | SpanSearchResult): span is SpanDetail {
  return "attributes" in span;
}

function TracesPage() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [selectedSpan, setSelectedSpan] = useState<
    SpanDetail | SpanSearchResult | null
  >(null);

  // Memoize time range to prevent infinite re-renders
  // Re-compute when refreshKey changes (user clicks refresh)
  const { startTime, endTime } = useMemo(() => {
    const end = new Date().toISOString();
    const start = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    return { startTime: start, endTime: end };
  }, [refreshKey]);

  const { data, isLoading, isFetching } = useTracesSearch(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    { startTime, endTime, rootSpansOnly: true, limit: 50 },
    !!selectedEnvironment,
  );

  const { data: traceDetail, isLoading: isLoadingDetail } = useTraceDetail(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    selectedTraceId,
  );

  // Get functionId from selected span - check both functionId field and attributes
  const selectedFunctionId = useMemo((): string | null => {
    if (!selectedSpan || !isSpanDetail(selectedSpan)) return null;

    // First try the direct functionId field
    if (selectedSpan.functionId) return selectedSpan.functionId;

    // Otherwise, try to extract from attributes (mirascope.version.uuid)
    try {
      const attrs = JSON.parse(selectedSpan.attributes) as Record<
        string,
        unknown
      >;
      const versionUuid = attrs["mirascope.version.uuid"];
      return typeof versionUuid === "string" ? versionUuid : null;
    } catch {
      return null;
    }
  }, [selectedSpan]);

  const { data: functionDetail } = useFunctionDetail(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    selectedFunctionId,
  );

  // Update selectedSpan with full SpanDetail when traceDetail arrives
  // This ensures the detail panel shows complete data on first click
  useEffect(() => {
    if (traceDetail && selectedSpan && !isSpanDetail(selectedSpan)) {
      const fullSpan = traceDetail.spans.find(
        (s) => s.spanId === selectedSpan.spanId,
      );
      if (fullSpan) {
        setSelectedSpan(fullSpan);
      }
    }
  }, [traceDetail, selectedSpan]);

  if (!selectedEnvironment) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <div className="flex items-center justify-center h-64">
              <p className="text-muted-foreground text-lg">
                Select an environment to view traces.
              </p>
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  return (
    <Protected>
      <CloudLayout>
        <ResizablePanelGroup direction="horizontal" className="h-full">
          {/* Main content area */}
          <ResizablePanel defaultSize={selectedSpan ? 70 : 100} minSize={30}>
            <div className="overflow-auto p-6">
              <div className="mb-4 flex items-center justify-between">
                <h1 className="text-2xl font-semibold">Traces</h1>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRefreshKey((k) => k + 1)}
                  disabled={isFetching}
                >
                  <RefreshCw
                    className={`mr-2 h-4 w-4 ${isFetching ? "animate-spin" : ""}`}
                  />
                  Refresh
                </Button>
              </div>
              <TracesTable
                spans={data?.spans ?? []}
                isLoading={isLoading}
                onTraceSelect={setSelectedTraceId}
                traceDetail={traceDetail ?? null}
                isLoadingDetail={isLoadingDetail}
                onSpanClick={setSelectedSpan}
                selectedSpanId={selectedSpan?.spanId}
              />
            </div>
          </ResizablePanel>

          {/* Detail panel - resizable */}
          {selectedSpan && (
            <>
              <ResizableHandle className="cursor-col-resize">
                <div className="z-10 flex h-8 w-4 translate-x-0.5 items-center justify-center rounded-sm border bg-background">
                  <DragHandleDots2Icon className="h-4 w-4" />
                </div>
              </ResizableHandle>
              <ResizablePanel defaultSize={30} minSize={20} maxSize={50}>
                <div className="h-full py-6 pr-6">
                  <SpanDetailPanel
                    span={selectedSpan}
                    functionData={functionDetail ?? null}
                    onClose={() => setSelectedSpan(null)}
                  />
                </div>
              </ResizablePanel>
            </>
          )}
        </ResizablePanelGroup>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/traces")({
  component: TracesPage,
});
