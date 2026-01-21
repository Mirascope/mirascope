import { useState, useMemo, useEffect } from "react";
import { DragHandleDots2Icon } from "@radix-ui/react-icons";
import { Loader2, ArrowLeft, RefreshCw } from "lucide-react";
import { Link, createFileRoute } from "@tanstack/react-router";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import { useFunctionsList } from "@/app/api/functions";
import { useTracesSearch, useTraceDetail } from "@/app/api/traces";
import { TracesTable } from "@/app/components/traces/traces-table";
import { SpanDetailPanel } from "@/app/components/traces/span-detail-panel";
import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/app/components/ui/tabs";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/app/components/ui/resizable";
import type { FunctionResponse } from "@/api/functions.schemas";
import type { SpanDetail, SpanSearchResult } from "@/api/traces-search.schemas";

/**
 * Compare semantic versions (e.g., "1.0", "1.1", "2.0").
 */
function compareVersions(a: string, b: string): number {
  const [aMajor, aMinor] = a.split(".").map(Number);
  const [bMajor, bMinor] = b.split(".").map(Number);
  if (aMajor !== bMajor) return aMajor - bMajor;
  return (aMinor ?? 0) - (bMinor ?? 0);
}

/**
 * Find the latest version of a function by name.
 */
function findLatestByName(
  functions: readonly FunctionResponse[],
  name: string,
): FunctionResponse | null {
  let latest: FunctionResponse | null = null;
  for (const fn of functions) {
    if (fn.name === name) {
      if (!latest || compareVersions(fn.version, latest.version) > 0) {
        latest = fn;
      }
    }
  }
  return latest;
}

/** Type guard to check if span has detailed data */
function isSpanDetail(span: SpanDetail | SpanSearchResult): span is SpanDetail {
  return "attributes" in span;
}

function FunctionDetailPage() {
  const { functionName } = Route.useParams();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

  const [activeTab, setActiveTab] = useState("code");
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<
    SpanDetail | SpanSearchResult | null
  >(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch all functions and find the latest version by name
  const { data: functionsData, isLoading: isLoadingFunctions } =
    useFunctionsList(
      selectedOrganization?.id ?? null,
      selectedProject?.id ?? null,
      selectedEnvironment?.id ?? null,
    );

  const fn = useMemo(() => {
    if (!functionsData?.functions) return null;
    return findLatestByName(functionsData.functions, functionName);
  }, [functionsData?.functions, functionName]);

  // Time range for traces (last 24 hours)
  // Re-compute when refreshKey changes (user clicks refresh)
  const { startTime, endTime } = useMemo(() => {
    const end = new Date().toISOString();
    const start = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    return { startTime: start, endTime: end };
  }, [refreshKey]);

  // Fetch traces filtered by function name using spanNamePrefix
  // This matches spans where name equals functionName or starts with functionName.
  // (e.g., "myFunc" matches "myFunc", "myFunc.call", "myFunc.stream")
  const searchParams = {
    startTime,
    endTime,
    rootSpansOnly: true,
    limit: 50,
    spanNamePrefix: functionName,
  };

  const {
    data: tracesData,
    isLoading: isLoadingTraces,
    isFetching: isFetchingTraces,
  } = useTracesSearch(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    searchParams,
    !!selectedEnvironment && activeTab === "traces",
  );

  // Fetch trace detail when a trace is selected
  const { data: traceDetail, isLoading: isLoadingDetail } = useTraceDetail(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
    selectedTraceId,
  );

  // Update selectedSpan with full SpanDetail when traceDetail arrives
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
            <div className="flex h-64 items-center justify-center">
              <p className="text-muted-foreground text-lg">
                Select an environment to view function details.
              </p>
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  if (isLoadingFunctions) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <div className="flex h-64 items-center justify-center">
              <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  if (!fn) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <div className="flex h-64 items-center justify-center">
              <div className="text-center">
                <p className="text-muted-foreground mb-2 text-lg">
                  Function not found.
                </p>
                <Link to="/cloud/functions">
                  <Button variant="outline" size="sm">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to Functions
                  </Button>
                </Link>
              </div>
            </div>
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
          <div className="shrink-0 p-6 pb-4">
            <div className="mb-2 flex items-center gap-2">
              <Link to="/cloud/functions">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="mr-1 h-4 w-4" />
                  Functions
                </Button>
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <h1 className="font-mono text-2xl font-semibold">{fn.name}</h1>
              <Badge variant="default">v{fn.version}</Badge>
            </div>
            {fn.description && (
              <p className="text-muted-foreground mt-1">{fn.description}</p>
            )}
          </div>

          {/* Tabs */}
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="flex min-h-0 flex-1 flex-col"
          >
            {/* Code Tab - tabs row outside resizable area */}
            {activeTab === "code" && (
              <>
                <div className="shrink-0 px-6">
                  <TabsList>
                    <TabsTrigger value="code">Code</TabsTrigger>
                    <TabsTrigger value="traces">Traces</TabsTrigger>
                  </TabsList>
                </div>
                <TabsContent
                  value="code"
                  className="m-0 flex-1 overflow-hidden"
                >
                  <div className="flex h-full gap-4 px-6 pt-2 pb-6">
                    {/* Code Block */}
                    <div className="min-w-0 flex-1 overflow-auto">
                      <CodeBlock
                        code={fn.code}
                        language="python"
                        showLineNumbers={true}
                      />
                    </div>

                    {/* Metadata Placeholder */}
                    <Card className="w-80 shrink-0">
                      <CardHeader>
                        <CardTitle className="text-base">Metadata</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-muted-foreground text-sm">
                          Usage metrics and cost information coming soon.
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </>
            )}

            {/* Traces Tab - tabs row inside resizable area for alignment */}
            {activeTab === "traces" && (
              <TabsContent
                value="traces"
                className="m-0 flex-1 overflow-hidden"
                forceMount
              >
                <ResizablePanelGroup direction="horizontal" className="h-full">
                  <ResizablePanel
                    defaultSize={selectedSpan ? 70 : 100}
                    minSize={30}
                  >
                    <div className="overflow-auto p-6">
                      <div className="mb-4 flex items-center justify-between">
                        <TabsList>
                          <TabsTrigger value="code">Code</TabsTrigger>
                          <TabsTrigger value="traces">Traces</TabsTrigger>
                        </TabsList>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setRefreshKey((k) => k + 1)}
                          disabled={isFetchingTraces}
                        >
                          <RefreshCw
                            className={`mr-2 h-4 w-4 ${isFetchingTraces ? "animate-spin" : ""}`}
                          />
                          Refresh
                        </Button>
                      </div>
                      <TracesTable
                        spans={tracesData?.spans ?? []}
                        isLoading={isLoadingTraces}
                        onTraceSelect={setSelectedTraceId}
                        traceDetail={traceDetail ?? null}
                        isLoadingDetail={isLoadingDetail}
                        onSpanClick={setSelectedSpan}
                        selectedSpanId={selectedSpan?.spanId}
                      />
                    </div>
                  </ResizablePanel>

                  {selectedSpan && (
                    <>
                      <ResizableHandle className="cursor-col-resize">
                        <div className="z-10 flex h-8 w-4 translate-x-0.5 items-center justify-center rounded-sm border bg-background">
                          <DragHandleDots2Icon className="h-4 w-4" />
                        </div>
                      </ResizableHandle>
                      <ResizablePanel
                        defaultSize={30}
                        minSize={20}
                        maxSize={50}
                      >
                        <div className="h-full py-6 pr-6">
                          <SpanDetailPanel
                            span={selectedSpan}
                            functionData={fn}
                            onClose={() => setSelectedSpan(null)}
                          />
                        </div>
                      </ResizablePanel>
                    </>
                  )}
                </ResizablePanelGroup>
              </TabsContent>
            )}
          </Tabs>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/functions/$functionName")({
  component: FunctionDetailPage,
});
