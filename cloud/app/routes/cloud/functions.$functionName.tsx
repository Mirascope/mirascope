import type { SupportedLanguages } from "@pierre/diffs";

import { DragHandleDots2Icon } from "@radix-ui/react-icons";
import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import {
  Loader2,
  ArrowLeft,
  RefreshCw,
  ArrowRight,
  GitCompare,
  X,
} from "lucide-react";
import { useState, useMemo, useEffect } from "react";

import type { SpanDetail, SpanSearchResult } from "@/api/traces-search.schemas";

import { useFunctionsList } from "@/app/api/functions";
import { useTracesSearch, useTraceDetail } from "@/app/api/traces";
import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
import { DiffTool } from "@/app/components/blocks/diff-tool";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { SpanDetailPanel } from "@/app/components/traces/span-detail-panel";
import { TracesTable } from "@/app/components/traces/traces-table";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/app/components/ui/resizable";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/app/components/ui/tabs";
import { useAnalytics } from "@/app/contexts/analytics";
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

/**
 * Compare semantic versions (e.g., "1.0", "1.1", "2.0").
 */
function compareVersions(a: string, b: string): number {
  const [aMajor, aMinor] = a.split(".").map(Number);
  const [bMajor, bMinor] = b.split(".").map(Number);
  if (aMajor !== bMajor) return aMajor - bMajor;
  return (aMinor ?? 0) - (bMinor ?? 0);
}

/** Type guard to check if span has detailed data */
function isSpanDetail(span: SpanDetail | SpanSearchResult): span is SpanDetail {
  return "attributes" in span;
}

function FunctionDetailPage() {
  const { functionName } = Route.useParams();
  const { version: versionFromUrl } = Route.useSearch();
  const navigate = useNavigate();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();
  const analytics = useAnalytics();

  const [activeTab, setActiveTab] = useState("code");
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<
    SpanDetail | SpanSearchResult | null
  >(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isCompareMode, setIsCompareMode] = useState(false);
  const [compareVersionId, setCompareVersionId] = useState<string | null>(null);

  // Fetch all functions in the environment
  const { data: functionsData, isLoading: isLoadingFunctions } =
    useFunctionsList(
      selectedOrganization?.id ?? null,
      selectedProject?.id ?? null,
      selectedEnvironment?.id ?? null,
    );

  // Get all versions of this function, sorted newest to oldest
  const allVersions = useMemo(() => {
    if (!functionsData?.functions) return [];
    return functionsData.functions
      .filter((f) => f.name === functionName)
      .sort((a, b) => compareVersions(b.version, a.version));
  }, [functionsData?.functions, functionName]);

  // Find selected function based on URL param or default to latest
  const fn = useMemo(() => {
    if (allVersions.length === 0) return null;
    if (versionFromUrl) {
      const found = allVersions.find((f) => f.id === versionFromUrl);
      if (found) return found;
    }
    return allVersions[0]; // Default to latest
  }, [allVersions, versionFromUrl]);

  // Find the compare version (left side of diff)
  const compareVersion = useMemo(() => {
    if (!compareVersionId || !allVersions.length) return null;
    return allVersions.find((f) => f.id === compareVersionId) ?? null;
  }, [compareVersionId, allVersions]);

  // Enter compare mode with default previous version
  const enterCompareMode = () => {
    if (!fn || allVersions.length < 2) return;
    analytics.trackEvent("function_compare_entered", {
      function_name: functionName,
    });
    // Find the index of current version
    const currentIndex = allVersions.findIndex((v) => v.id === fn.id);
    // Default to the next older version, or first version if current is oldest
    const defaultCompareIndex =
      currentIndex < allVersions.length - 1 ? currentIndex + 1 : 0;
    setCompareVersionId(allVersions[defaultCompareIndex].id);
    setIsCompareMode(true);
  };

  // Exit compare mode
  const exitCompareMode = () => {
    analytics.trackEvent("function_compare_exited", {
      function_name: functionName,
    });
    setIsCompareMode(false);
    setCompareVersionId(null);
  };

  // Handle compare version change (left pill)
  const handleCompareVersionChange = (newVersionId: string) => {
    setCompareVersionId(newVersionId);
  };

  // Redirect if version param is invalid
  useEffect(() => {
    if (versionFromUrl && allVersions.length > 0) {
      const found = allVersions.find((f) => f.id === versionFromUrl);
      if (!found) {
        void navigate({
          to: "/cloud/functions/$functionName",
          params: { functionName },
          search: {},
          replace: true,
        });
      }
    }
  }, [versionFromUrl, allVersions, navigate, functionName]);

  const handleVersionChange = (newVersionId: string) => {
    analytics.trackEvent("function_version_changed", {
      function_name: functionName,
      version_id: newVersionId,
    });
    void navigate({
      to: "/cloud/functions/$functionName",
      params: { functionName },
      search: { version: newVersionId },
      replace: true,
    });
  };

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
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h1 className="font-mono text-2xl font-semibold">{fn.name}</h1>
                {isCompareMode && compareVersion ? (
                  <>
                    {/* Compare mode: [v1.1 ▼] → [v1.2 ▼] */}
                    <Select
                      value={compareVersion.id}
                      onValueChange={handleCompareVersionChange}
                    >
                      <SelectTrigger className="h-auto w-auto gap-1 rounded-md border-transparent bg-muted px-2.5 py-0.5 text-xs font-semibold shadow hover:bg-muted/80">
                        <SelectValue>v{compareVersion.version}</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {allVersions
                          .filter((v) => v.id !== fn.id)
                          .map((version) => (
                            <SelectItem key={version.id} value={version.id}>
                              <span className="flex items-center gap-2">
                                v{version.version}
                                {version.id === allVersions[0].id && (
                                  <span className="text-xs text-muted-foreground">
                                    (latest)
                                  </span>
                                )}
                              </span>
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                    <ArrowRight className="text-muted-foreground h-4 w-4" />
                    <Select value={fn.id} onValueChange={handleVersionChange}>
                      <SelectTrigger className="h-auto w-auto gap-1 rounded-md border-transparent bg-primary px-2.5 py-0.5 text-xs font-semibold text-primary-foreground shadow hover:bg-primary/80">
                        <SelectValue>v{fn.version}</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {allVersions
                          .filter((v) => v.id !== compareVersionId)
                          .map((version) => (
                            <SelectItem key={version.id} value={version.id}>
                              <span className="flex items-center gap-2">
                                v{version.version}
                                {version.id === allVersions[0].id && (
                                  <span className="text-xs text-muted-foreground">
                                    (latest)
                                  </span>
                                )}
                              </span>
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                  </>
                ) : (
                  <>
                    {/* Normal mode: [v1.2 ▼] */}
                    {allVersions.length > 1 ? (
                      <Select value={fn.id} onValueChange={handleVersionChange}>
                        <SelectTrigger className="h-auto w-auto gap-1 rounded-md border-transparent bg-primary px-2.5 py-0.5 text-xs font-semibold text-primary-foreground shadow hover:bg-primary/80">
                          <SelectValue>v{fn.version}</SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                          {allVersions.map((version) => (
                            <SelectItem key={version.id} value={version.id}>
                              <span className="flex items-center gap-2">
                                v{version.version}
                                {version.id === allVersions[0].id && (
                                  <span className="text-xs text-muted-foreground">
                                    (latest)
                                  </span>
                                )}
                              </span>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <Badge variant="default">v{fn.version}</Badge>
                    )}
                  </>
                )}
              </div>
              {/* Right side: Compare or Exit Compare button */}
              {isCompareMode ? (
                <Button variant="outline" size="sm" onClick={exitCompareMode}>
                  <X className="mr-1 h-4 w-4" />
                  Exit Compare
                </Button>
              ) : (
                allVersions.length > 1 &&
                activeTab === "code" && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={enterCompareMode}
                  >
                    <GitCompare className="mr-1 h-4 w-4" />
                    Compare
                  </Button>
                )
              )}
            </div>
            {fn.description && (
              <p className="text-muted-foreground mt-1">{fn.description}</p>
            )}
          </div>

          {/* Content area with tabs overlay */}
          <div className="relative min-h-0 flex-1">
            {/* Tab buttons - absolutely positioned */}
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="absolute left-6 top-0 z-10"
            >
              <TabsList>
                <TabsTrigger value="code">Code</TabsTrigger>
                <TabsTrigger value="traces" disabled={isCompareMode}>
                  Traces
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Code content */}
            {activeTab === "code" && (
              <div className="h-full overflow-hidden">
                <div className="flex h-full gap-4 px-6 pt-12 pb-6">
                  <div className="min-w-0 flex-1 overflow-auto">
                    {isCompareMode && compareVersion ? (
                      <DiffTool
                        baseCode={compareVersion.code}
                        newCode={fn.code}
                        language={
                          (fn.language ?? "python") as SupportedLanguages
                        }
                        baseName={`v${compareVersion.version}`}
                        newName={`v${fn.version}`}
                      />
                    ) : (
                      <CodeBlock
                        code={fn.code}
                        language={fn.language ?? "python"}
                        showLineNumbers={true}
                      />
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Traces content */}
            {activeTab === "traces" && (
              <ResizablePanelGroup direction="horizontal" className="h-full">
                <ResizablePanel
                  defaultSize={selectedSpan ? 70 : 100}
                  minSize={30}
                >
                  <div className="h-full overflow-auto px-6 pb-6">
                    <div className="mb-4 flex justify-end">
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
                      onSpanClick={(span) => {
                        analytics.trackEvent("span_selected", {
                          span_id: span?.spanId,
                          trace_id: selectedTraceId,
                          environment_id: selectedEnvironment?.id,
                        });
                        setSelectedSpan(span);
                      }}
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
                    <ResizablePanel defaultSize={30} minSize={20} maxSize={50}>
                      <div className="h-full overflow-hidden pb-6 pr-6">
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
            )}
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

type FunctionSearchParams = {
  version?: string;
};

export const Route = createFileRoute("/cloud/functions/$functionName")({
  component: FunctionDetailPage,
  validateSearch: (search: Record<string, unknown>): FunctionSearchParams => ({
    version: typeof search.version === "string" ? search.version : undefined,
  }),
});
