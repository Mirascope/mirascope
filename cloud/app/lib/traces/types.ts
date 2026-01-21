import type { SpanDetail } from "@/api/traces-search.schemas";

export interface SpanNode {
  span: SpanDetail;
  children: SpanNode[];
}

/**
 * Builds a tree structure from a flat array of spans.
 * Root spans (those with no parent) become top-level nodes.
 */
export function buildSpanTree(spans: readonly SpanDetail[]): SpanNode[] {
  const childrenMap = new Map<string | null, SpanDetail[]>();

  for (const span of spans) {
    const parentId = span.parentSpanId;
    if (!childrenMap.has(parentId)) {
      childrenMap.set(parentId, []);
    }
    childrenMap.get(parentId)!.push(span);
  }

  function buildNode(span: SpanDetail): SpanNode {
    const children = childrenMap.get(span.spanId) ?? [];
    return { span, children: children.map(buildNode) };
  }

  return (childrenMap.get(null) ?? []).map(buildNode);
}
