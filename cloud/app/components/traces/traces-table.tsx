import { useState, useEffect, useRef } from "react";
import { ChevronRight, ChevronDown, Loader2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/app/components/ui/table";
import { TruncatedText } from "@/app/components/ui/truncated-text";
import { cn } from "@/app/lib/utils";
import {
  formatDuration,
  formatTimestamp,
  formatTokens,
} from "@/app/lib/traces/formatting";
import type { SpanSearchResult, SpanDetail } from "@/api/traces-search.schemas";
import { buildSpanTree, type SpanNode } from "@/app/lib/traces/types";

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
          {span.model ? <TruncatedText>{span.model}</TruncatedText> : "-"}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(span.inputTokens)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(span.outputTokens)}
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
}: RootSpanRowProps) {
  // Hide chevron if either API or cache confirms no children
  // Cache takes precedence when available (source of truth from actual data)
  const showChevron = span.hasChildren !== false && hasChildren !== false;
  const isSelected = selectedSpanId === span.spanId;

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
          {span.model ? <TruncatedText>{span.model}</TruncatedText> : "-"}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(span.inputTokens)}
        </TableCell>
        <TableCell className="text-muted-foreground">
          {formatTokens(span.outputTokens)}
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
    <div className="rounded-lg border">
      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[40%] min-w-[200px]">Name</TableHead>
            <TableHead className="w-[100px]">Duration</TableHead>
            <TableHead className="w-[220px]">Model</TableHead>
            <TableHead className="w-[110px] whitespace-nowrap">
              Input Tokens
            </TableHead>
            <TableHead className="w-[110px] whitespace-nowrap">
              Output Tokens
            </TableHead>
            <TableHead className="w-[180px]">Timestamp</TableHead>
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
              />
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
