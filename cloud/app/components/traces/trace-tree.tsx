import { ChevronRight, ChevronDown, AlertCircle } from "lucide-react";
import { useState, useMemo } from "react";

import type { SpanDetail } from "@/api/traces-search.schemas";

import { formatDuration } from "@/app/lib/traces/formatting";
import { buildSpanTree, type SpanNode } from "@/app/lib/traces/types";
import { cn } from "@/app/lib/utils";

interface TraceTreeProps {
  spans: readonly SpanDetail[];
  selectedSpanId: string;
  onSpanSelect: (spanId: string) => void;
}

interface TraceTreeNodeProps {
  node: SpanNode;
  depth: number;
  expandedSpans: Set<string>;
  onToggle: (spanId: string) => void;
  selectedSpanId: string;
  onSpanSelect: (spanId: string) => void;
}

function TraceTreeNode({
  node,
  depth,
  expandedSpans,
  onToggle,
  selectedSpanId,
  onSpanSelect,
}: TraceTreeNodeProps) {
  const { span, children } = node;
  const hasChildren = children.length > 0;
  const isExpanded = expandedSpans.has(span.spanId);
  const isSelected = selectedSpanId === span.spanId;
  const hasError = !!span.errorType;

  return (
    <>
      <div
        className={cn(
          "flex items-center gap-2 rounded-md px-2 py-1.5",
          isSelected ? "bg-accent" : "cursor-pointer hover:bg-muted/50",
        )}
        style={{ paddingLeft: `${depth * 1.5 + 0.5}rem` }}
        onClick={() => onSpanSelect(span.spanId)}
      >
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggle(span.spanId);
            }}
            className="flex h-5 w-5 shrink-0 cursor-pointer items-center justify-center rounded hover:bg-muted"
            aria-label={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? (
              <ChevronDown size={16} className="text-muted-foreground" />
            ) : (
              <ChevronRight size={16} className="text-muted-foreground" />
            )}
          </button>
        ) : (
          <span className="w-5 shrink-0" />
        )}
        <span className="min-w-0 flex-1 truncate text-sm font-medium">
          {span.name}
        </span>
        <div className="flex shrink-0 items-center gap-2">
          {hasError && <AlertCircle size={14} className="text-destructive" />}
          <span className="text-xs text-muted-foreground">
            {formatDuration(span.durationMs)}
          </span>
        </div>
      </div>
      {isExpanded &&
        children.map((child) => (
          <TraceTreeNode
            key={child.span.spanId}
            node={child}
            depth={depth + 1}
            expandedSpans={expandedSpans}
            onToggle={onToggle}
            selectedSpanId={selectedSpanId}
            onSpanSelect={onSpanSelect}
          />
        ))}
    </>
  );
}

export function TraceTree({
  spans,
  selectedSpanId,
  onSpanSelect,
}: TraceTreeProps) {
  // Build tree from flat spans
  const tree = useMemo(() => buildSpanTree(spans), [spans]);

  // Track expanded spans - default all expanded
  const [expandedSpans, setExpandedSpans] = useState<Set<string>>(() => {
    // Start with all spans expanded
    return new Set(spans.map((s) => s.spanId));
  });

  const toggleSpan = (spanId: string) => {
    setExpandedSpans((prev) => {
      const next = new Set(prev);
      if (next.has(spanId)) {
        next.delete(spanId);
      } else {
        next.add(spanId);
      }
      return next;
    });
  };

  if (tree.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
        No spans found
      </div>
    );
  }

  return (
    <div className="space-y-0.5">
      {tree.map((node) => (
        <TraceTreeNode
          key={node.span.spanId}
          node={node}
          depth={0}
          expandedSpans={expandedSpans}
          onToggle={toggleSpan}
          selectedSpanId={selectedSpanId}
          onSpanSelect={onSpanSelect}
        />
      ))}
    </div>
  );
}
