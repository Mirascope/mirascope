import { DragHandleDots2Icon } from "@radix-ui/react-icons";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Loader2, AlertCircle } from "lucide-react";
import { useMemo } from "react";

import type { SpanDetail } from "@/api/traces-search.schemas";

import { useFunctionDetail } from "@/app/api/functions";
import { useTraceDetail } from "@/app/api/traces";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { SpanDetailPanel } from "@/app/components/traces/span-detail-panel";
import { TraceTree } from "@/app/components/traces/trace-tree";
import { Alert, AlertDescription, AlertTitle } from "@/app/components/ui/alert";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/app/components/ui/resizable";
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

function FullTraceViewPage() {
  const { traceId, spanId } = Route.useParams();
  const navigate = useNavigate();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

  // Fetch the complete trace
  const { data: traceDetail, isLoading } = useTraceDetail(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    traceId,
  );

  // Find the selected span from trace data
  const selectedSpan = useMemo((): SpanDetail | null => {
    if (!traceDetail) return null;
    return traceDetail.spans.find((s) => s.spanId === spanId) ?? null;
  }, [traceDetail, spanId]);

  // Find the root span for the page title
  const rootSpan = useMemo((): SpanDetail | null => {
    if (!traceDetail) return null;
    return traceDetail.spans.find((s) => !s.parentSpanId) ?? null;
  }, [traceDetail]);

  // Get functionId from selected span
  const selectedFunctionId = useMemo((): string | null => {
    if (!selectedSpan) return null;

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

  // Handle span selection - update URL
  const handleSpanSelect = (newSpanId: string) => {
    void navigate({
      to: "/cloud/projects/trace-view/$traceId/$spanId",
      params: { traceId, spanId: newSpanId },
      replace: true,
    });
  };

  // No environment selected
  if (!selectedEnvironment) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <div className="flex h-64 items-center justify-center">
              <p className="text-lg text-muted-foreground">
                Select an environment to view trace details.
              </p>
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <div className="flex h-64 items-center justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  // Trace not found
  if (!traceDetail || traceDetail.spans.length === 0) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Trace not found</AlertTitle>
              <AlertDescription>
                The trace with ID &quot;{traceId}&quot; could not be found.
              </AlertDescription>
            </Alert>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  // Span not found in trace
  if (!selectedSpan) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Span not found</AlertTitle>
              <AlertDescription>
                The span with ID &quot;{spanId}&quot; could not be found in this
                trace.
              </AlertDescription>
            </Alert>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  return (
    <Protected>
      <CloudLayout>
        <div className="flex h-full flex-col overflow-hidden">
          {/* Header */}
          <div className="shrink-0 px-6 py-4">
            <h1 className="truncate text-xl font-semibold">
              {rootSpan?.name ?? "Trace"}
            </h1>
          </div>

          {/* Main content */}
          <ResizablePanelGroup
            direction="horizontal"
            className="min-h-0 flex-1"
          >
            {/* Left panel - Trace tree */}
            <ResizablePanel defaultSize={40} minSize={20} maxSize={60}>
              <div className="h-full overflow-auto p-4">
                <TraceTree
                  spans={traceDetail.spans}
                  selectedSpanId={spanId}
                  onSpanSelect={handleSpanSelect}
                />
              </div>
            </ResizablePanel>

            <ResizableHandle className="cursor-col-resize">
              <div className="z-10 flex h-8 w-4 items-center justify-center rounded-sm border bg-background">
                <DragHandleDots2Icon className="h-4 w-4" />
              </div>
            </ResizableHandle>

            {/* Right panel - Span detail */}
            <ResizablePanel defaultSize={60} minSize={30}>
              <div className="h-full py-4 pr-4">
                <SpanDetailPanel
                  span={selectedSpan}
                  functionData={functionDetail ?? null}
                  mode="full-view"
                />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute(
  "/cloud/projects/trace-view/$traceId/$spanId",
)({
  component: FullTraceViewPage,
});
