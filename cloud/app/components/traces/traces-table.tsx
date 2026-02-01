import { ChevronRight, ChevronDown, Loader2 } from "lucide-react";
import { useState, useEffect, useRef } from "react";

import type { SpanSearchResult, SpanDetail } from "@/api/traces-search.schemas";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/app/components/ui/table";
import { TruncatedText } from "@/app/components/ui/truncated-text";
import {
  formatDuration,
  formatTimestamp,
  formatTokens,
  formatCost,
} from "@/app/lib/traces/formatting";
import { buildSpanTree, type SpanNode } from "@/app/lib/traces/types";
import { cn, safeParseJSON } from "@/app/lib/utils";

// =============================================================================
// Attribute extraction helpers for mirascope.response.* fallback
// =============================================================================

/** Extract a numeric field from mirascope.response.usage JSON */
function getMirascopeUsageField(
  attrs: Record<string, unknown> | null,
  field: string,
): number | null {
  if (!attrs) return null;
  const usageRaw = attrs["mirascope.response.usage"];
  if (usageRaw == null) return null;
  try {
    const parsed: unknown =
      typeof usageRaw === "string" ? JSON.parse(usageRaw) : usageRaw;
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      const value = (parsed as Record<string, unknown>)[field];
      return typeof value === "number" ? value : null;
    }
  } catch {
    // Invalid JSON
  }
  return null;
}

/** Extract model from attributes (mirascope first, then gen_ai) */
function extractModel(attrs: Record<string, unknown> | null): string | null {
  if (!attrs) return null;
  const mirascopeModel = attrs["mirascope.response.model_id"];
  if (typeof mirascopeModel === "string") return mirascopeModel;
  const genAiModel = attrs["gen_ai.request.model"];
  if (typeof genAiModel === "string") return genAiModel;
  return null;
}

/** Extract input tokens from attributes */
function extractInputTokens(
  attrs: Record<string, unknown> | null,
): number | null {
  const mirascopeTokens = getMirascopeUsageField(attrs, "input_tokens");
  if (mirascopeTokens !== null) return mirascopeTokens;
  if (!attrs) return null;
  const genAiTokens = attrs["gen_ai.usage.input_tokens"];
  return typeof genAiTokens === "number" ? genAiTokens : null;
}

/** Extract output tokens from attributes */
function extractOutputTokens(
  attrs: Record<string, unknown> | null,
): number | null {
  const mirascopeTokens = getMirascopeUsageField(attrs, "output_tokens");
  if (mirascopeTokens !== null) return mirascopeTokens;
  if (!attrs) return null;
  const genAiTokens = attrs["gen_ai.usage.output_tokens"];
  return typeof genAiTokens === "number" ? genAiTokens : null;
}

/** Extract cost from attributes (mirascope centicents or gen_ai USD) */
function extractCostUsd(attrs: Record<string, unknown> | null): number | null {
  if (!attrs) return null;
  // Try mirascope.response.cost first (JSON with centicents)
  const costRaw = attrs["mirascope.response.cost"];
  if (costRaw != null) {
    try {
      const parsed: unknown =
        typeof costRaw === "string" ? JSON.parse(costRaw) : costRaw;
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        const totalCost = (parsed as Record<string, unknown>).total_cost;
        if (typeof totalCost === "number") {
          return totalCost / 10000; // Convert centicents to USD
        }
      }
    } catch {
      // Invalid JSON
    }
  }
  // Fallback to gen_ai.usage.cost
  const genAiCost = attrs["gen_ai.usage.cost"];
  return typeof genAiCost === "number" ? genAiCost : null;
}

/** Parse attributes JSON string and extract display values with fallbacks */
function getDisplayValues(
  span: SpanDetail | SpanSearchResult,
  attrs: Record<string, unknown> | null,
): {
  model: string | null;
  inputTokens: number | null;
  outputTokens: number | null;
  costUsd: number | null;
} {
  return {
    model: span.model ?? extractModel(attrs),
    inputTokens: span.inputTokens ?? extractInputTokens(attrs),
    outputTokens: span.outputTokens ?? extractOutputTokens(attrs),
    costUsd: span.costUsd ?? extractCostUsd(attrs),
  };
}

/**
 * Recursively finds a node in the span tree by spanId.
 */
function findNodeInTree(nodes: SpanNode[], spanId: string): SpanNode | null {
  for (const node of nodes) {
    if (node.span.spanId === spanId) {
      return node;
    }
    const found = findNodeInTree(node.children, spanId);
    if (found) {
      return found;
    }
  }
  return null;
}

interface TraceDetailCache {
  traceId: string;
  spans: readonly SpanDetail[];
  tree: SpanNode[];
}

interface TracesTableProps {
  spans: readonly SpanSearchResult[];
  isLoading: boolean;
  onTraceSelect?: (traceId: string) => void;
  traceDetail?: {
    traceId: string;
    spans: readonly SpanDetail[];
  } | null;
  isLoadingDetail?: boolean;
  onSpanClick?: (span: SpanDetail | SpanSearchResult) => void;
  selectedSpanId?: string | null;
}

interface SpanRowProps {
  node: SpanNode;
  depth: number;
  expandedSpans: Set<string>;
  onToggle: (spanId: string) => void;
  onSpanClick?: (span: SpanDetail) => void;
  selectedSpanId?: string | null;
}

function SpanRow({
  node,
  depth,
  expandedSpans,
  onToggle,
  onSpanClick,
  selectedSpanId,
}: SpanRowProps) {
  const { span, children } = node;
  const hasChildren = children.length > 0;
  const isExpanded = expandedSpans.has(span.spanId);
  const isSelected = selectedSpanId === span.spanId;

  // Extract display values with fallback from raw attributes
  const rawAttrs = "attributes" in span ? safeParseJSON(span.attributes) : null;
  const attrs = rawAttrs && !Array.isArray(rawAttrs) ? rawAttrs : null;
  const displayValues = getDisplayValues(span, attrs);

  return (
    <>
      <TableRow
        className={cn(
          "cursor-pointer hover:bg-muted/50",
          isSelected && "bg-muted",
        )}
        onClick={() => onSpanClick?.(span)}
      >
        <TableCell>
          <div
            className="flex items-center"
            style={{ paddingLeft: `${depth * 1.5}rem` }}
          >
            {hasChildren ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onToggle(span.spanId);
                }}
                className="mr-2 flex h-5 w-5 cursor-pointer items-center justify-center rounded hover:bg-muted"
                aria-label={isExpanded ? "Collapse" : "Expand"}
              >
                {isExpanded ? (
                  <ChevronDown size={16} className="text-muted-foreground" />
                ) : (
                  <ChevronRight size={16} className="text-muted-foreground" />
                )}
              </button>
            ) : (
              <span className="mr-2 w-5" />
            )}
            <TruncatedText className="font-medium">{span.name}</TruncatedText>
          </div>
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatDuration(span.durationMs)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {displayValues.model ? (
            <TruncatedText>{displayValues.model}</TruncatedText>
          ) : (
            "-"
          )}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(displayValues.inputTokens)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(displayValues.outputTokens)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatCost(displayValues.costUsd)}
        </TableCell>
        <TableCell className="whitespace-nowrap text-muted-foreground">
          {formatTimestamp(span.startTime)}
        </TableCell>
      </TableRow>
      {isExpanded &&
        children.map((child) => (
          <SpanRow
            key={child.span.spanId}
            node={child}
            depth={depth + 1}
            expandedSpans={expandedSpans}
            onToggle={onToggle}
            onSpanClick={onSpanClick}
            selectedSpanId={selectedSpanId}
          />
        ))}
    </>
  );
}

interface RootSpanRowProps {
  span: SpanSearchResult;
  isExpanded: boolean;
  isLoading: boolean;
  onToggle: () => void;
  childNodes: SpanNode[];
  expandedSpans: Set<string>;
  onToggleChild: (spanId: string) => void;
  /** undefined = unknown, true = has children, false = no children */
  hasChildren: boolean | undefined;
  /** Called when clicking the root span row itself */
  onRootSpanClick?: (span: SpanSearchResult) => void;
  /** Called when clicking child spans */
  onChildSpanClick?: (span: SpanDetail) => void;
  selectedSpanId?: string | null;
  /** Cached SpanDetail for fallback attribute extraction */
  cachedDetail?: SpanDetail;
}

function RootSpanRow({
  span,
  isExpanded,
  isLoading,
  onToggle,
  childNodes,
  expandedSpans,
  onToggleChild,
  hasChildren,
  onRootSpanClick,
  onChildSpanClick,
  selectedSpanId,
  cachedDetail,
}: RootSpanRowProps) {
  // Hide chevron if either API or cache confirms no children
  // Cache takes precedence when available (source of truth from actual data)
  const showChevron = span.hasChildren !== false && hasChildren !== false;
  const isSelected = selectedSpanId === span.spanId;

  // Extract display values with fallback from cached SpanDetail attributes
  const rawAttrs = cachedDetail ? safeParseJSON(cachedDetail.attributes) : null;
  const attrs = rawAttrs && !Array.isArray(rawAttrs) ? rawAttrs : null;
  const displayValues = getDisplayValues(span, attrs);

  return (
    <>
      <TableRow
        className={cn(
          "cursor-pointer hover:bg-muted/50",
          isSelected && "bg-muted",
        )}
        onClick={() => onRootSpanClick?.(span)}
      >
        <TableCell>
          <div className="flex items-center">
            {showChevron ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onToggle();
                }}
                className="mr-2 flex h-5 w-5 cursor-pointer items-center justify-center rounded hover:bg-muted"
                aria-label={isExpanded ? "Collapse" : "Expand"}
              >
                {isLoading ? (
                  <Loader2
                    size={16}
                    className="animate-spin text-muted-foreground"
                  />
                ) : isExpanded ? (
                  <ChevronDown size={16} className="text-muted-foreground" />
                ) : (
                  <ChevronRight size={16} className="text-muted-foreground" />
                )}
              </button>
            ) : (
              <span className="mr-2 w-5" />
            )}
            <TruncatedText className="font-medium">{span.name}</TruncatedText>
          </div>
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatDuration(span.durationMs)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {displayValues.model ? (
            <TruncatedText>{displayValues.model}</TruncatedText>
          ) : (
            "-"
          )}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(displayValues.inputTokens)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(displayValues.outputTokens)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatCost(displayValues.costUsd)}
        </TableCell>
        <TableCell className="whitespace-nowrap text-muted-foreground">
          {formatTimestamp(span.startTime)}
        </TableCell>
      </TableRow>
      {isExpanded &&
        childNodes.map((child) => (
          <SpanRow
            key={child.span.spanId}
            node={child}
            depth={1}
            expandedSpans={expandedSpans}
            onToggle={onToggleChild}
            onSpanClick={onChildSpanClick}
            selectedSpanId={selectedSpanId}
          />
        ))}
    </>
  );
}

export function TracesTable({
  spans,
  isLoading,
  onTraceSelect,
  traceDetail,
  isLoadingDetail,
  onSpanClick,
  selectedSpanId,
}: TracesTableProps) {
  // Track which top-level rows are expanded (by spanId)
  const [expandedRowSpans, setExpandedRowSpans] = useState<Set<string>>(
    new Set(),
  );
  // Track which nested spans are expanded (by spanId)
  const [expandedSpans, setExpandedSpans] = useState<Set<string>>(new Set());

  // Cache for trace details - persists across re-renders (keyed by traceId)
  const traceDetailsCacheRef = useRef<Map<string, TraceDetailCache>>(new Map());
  // Track which span we're currently fetching details for (for loading indicator)
  const [fetchingSpanId, setFetchingSpanId] = useState<string | null>(null);

  // Add incoming trace detail to cache
  useEffect(() => {
    if (traceDetail && traceDetail.traceId) {
      const tree = buildSpanTree(traceDetail.spans);

      traceDetailsCacheRef.current.set(traceDetail.traceId, {
        traceId: traceDetail.traceId,
        spans: traceDetail.spans,
        tree,
      });

      // Clear fetching state when this trace's data arrives
      if (fetchingSpanId) {
        setFetchingSpanId(null);
      }
    }
  }, [traceDetail, fetchingSpanId]);

  const toggleRowSpan = (traceId: string, spanId: string) => {
    const newExpanded = new Set(expandedRowSpans);
    if (newExpanded.has(spanId)) {
      newExpanded.delete(spanId);
    } else {
      newExpanded.add(spanId);
      // Only fetch if trace not already in cache
      if (!traceDetailsCacheRef.current.has(traceId)) {
        setFetchingSpanId(spanId);
        onTraceSelect?.(traceId);
      }
    }
    setExpandedRowSpans(newExpanded);
  };

  const toggleSpan = (spanId: string) => {
    const newExpanded = new Set(expandedSpans);
    if (newExpanded.has(spanId)) {
      newExpanded.delete(spanId);
    } else {
      newExpanded.add(spanId);
    }
    setExpandedSpans(newExpanded);
  };

  // Build child nodes from cached trace detail for a specific span
  const getChildNodes = (traceId: string, spanId: string): SpanNode[] => {
    const cached = traceDetailsCacheRef.current.get(traceId);
    if (!cached) {
      return [];
    }
    // Find the specific span in the tree and return its children
    const node = findNodeInTree(cached.tree, spanId);
    return node?.children ?? [];
  };

  // Check if a specific span has children (undefined if not yet fetched)
  const getHasChildren = (
    traceId: string,
    spanId: string,
  ): boolean | undefined => {
    const cached = traceDetailsCacheRef.current.get(traceId);
    if (!cached) {
      return undefined;
    }
    const node = findNodeInTree(cached.tree, spanId);
    return node ? node.children.length > 0 : false;
  };

  // Get full SpanDetail for a root span from cache (if available)
  const getFullSpanDetail = (
    rootSpan: SpanSearchResult,
  ): SpanDetail | undefined => {
    const cached = traceDetailsCacheRef.current.get(rootSpan.traceId);
    if (!cached) return undefined;
    return cached.spans.find((s) => s.spanId === rootSpan.spanId);
  };

  // Handle click on row span - use full SpanDetail if cached, otherwise fetch
  const handleRowSpanClick = (rowSpan: SpanSearchResult) => {
    const fullSpan = getFullSpanDetail(rowSpan);
    if (fullSpan) {
      onSpanClick?.(fullSpan);
      return;
    }
    // Not cached - trigger fetch and pass the summary for now
    if (!traceDetailsCacheRef.current.has(rowSpan.traceId)) {
      setFetchingSpanId(rowSpan.spanId);
      onTraceSelect?.(rowSpan.traceId);
    }
    onSpanClick?.(rowSpan);
  };

  // Loading state - only show full loader on initial load (no existing data)
  if (isLoading && spans.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Empty state
  if (spans.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No traces found for the selected time range.</p>
      </div>
    );
  }

  return (
    <div className="max-h-[calc(100vh-10rem)] overflow-auto rounded-lg border">
      <Table className="min-w-[900px] table-fixed">
        <TableHeader className="sticky top-0 z-10 [&_th]:bg-background">
          <TableRow>
            <TableHead className="min-w-[200px]">Name</TableHead>
            <TableHead className="w-[100px]">Duration</TableHead>
            <TableHead className="w-[200px]">Model</TableHead>
            <TableHead className="w-[100px] whitespace-nowrap">
              Input Tokens
            </TableHead>
            <TableHead className="w-[110px] whitespace-nowrap">
              Output Tokens
            </TableHead>
            <TableHead className="w-[80px]">Cost</TableHead>
            <TableHead className="w-[120px]">Timestamp</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {spans.map((span) => {
            const isExpanded = expandedRowSpans.has(span.spanId);
            const isLoadingThis =
              fetchingSpanId === span.spanId && isLoadingDetail;

            return (
              <RootSpanRow
                key={`${span.traceId}-${span.spanId}`}
                span={span}
                isExpanded={isExpanded}
                isLoading={!!isLoadingThis}
                onToggle={() => toggleRowSpan(span.traceId, span.spanId)}
                childNodes={getChildNodes(span.traceId, span.spanId)}
                expandedSpans={expandedSpans}
                onToggleChild={toggleSpan}
                hasChildren={getHasChildren(span.traceId, span.spanId)}
                onRootSpanClick={handleRowSpanClick}
                onChildSpanClick={onSpanClick}
                selectedSpanId={selectedSpanId}
                cachedDetail={getFullSpanDetail(span)}
              />
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
