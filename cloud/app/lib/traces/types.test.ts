import { describe, it, expect } from "@effect/vitest";
import type { SpanDetail } from "@/api/traces-search.schemas";
import { buildSpanTree } from "./types";

// Helper to create a minimal SpanDetail for testing
function createSpan(
  spanId: string,
  parentSpanId: string | null,
  name = "test-span",
): SpanDetail {
  return {
    traceId: "trace-1",
    spanId,
    parentSpanId,
    environmentId: "env-1",
    projectId: "proj-1",
    organizationId: "org-1",
    startTime: "2024-01-01T00:00:00Z",
    endTime: "2024-01-01T00:00:01Z",
    durationMs: 1000,
    name,
    kind: 1,
    statusCode: 0,
    statusMessage: null,
    model: null,
    provider: null,
    inputTokens: null,
    outputTokens: null,
    totalTokens: null,
    costUsd: null,
    functionId: null,
    functionName: null,
    functionVersion: null,
    errorType: null,
    errorMessage: null,
    attributes: "{}",
    events: null,
    links: null,
    serviceName: null,
    serviceVersion: null,
    resourceAttributes: null,
  };
}

describe("buildSpanTree", () => {
  it("should return empty array for empty input", () => {
    const result = buildSpanTree([]);
    expect(result).toEqual([]);
  });

  it("should handle a single root span", () => {
    const spans = [createSpan("span-1", null, "root")];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(1);
    expect(result[0].span.spanId).toBe("span-1");
    expect(result[0].span.name).toBe("root");
    expect(result[0].children).toEqual([]);
  });

  it("should handle multiple root spans", () => {
    const spans = [
      createSpan("span-1", null, "root-1"),
      createSpan("span-2", null, "root-2"),
    ];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(2);
    expect(result[0].span.spanId).toBe("span-1");
    expect(result[1].span.spanId).toBe("span-2");
  });

  it("should build a simple parent-child relationship", () => {
    const spans = [
      createSpan("root", null, "root-span"),
      createSpan("child", "root", "child-span"),
    ];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(1);
    expect(result[0].span.spanId).toBe("root");
    expect(result[0].children).toHaveLength(1);
    expect(result[0].children[0].span.spanId).toBe("child");
    expect(result[0].children[0].children).toEqual([]);
  });

  it("should build multiple children under a parent", () => {
    const spans = [
      createSpan("root", null, "root-span"),
      createSpan("child-1", "root", "child-span-1"),
      createSpan("child-2", "root", "child-span-2"),
      createSpan("child-3", "root", "child-span-3"),
    ];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(1);
    expect(result[0].children).toHaveLength(3);
    expect(result[0].children[0].span.spanId).toBe("child-1");
    expect(result[0].children[1].span.spanId).toBe("child-2");
    expect(result[0].children[2].span.spanId).toBe("child-3");
  });

  it("should build a deep nested tree", () => {
    const spans = [
      createSpan("root", null, "root"),
      createSpan("child", "root", "child"),
      createSpan("grandchild", "child", "grandchild"),
      createSpan("great-grandchild", "grandchild", "great-grandchild"),
    ];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(1);
    expect(result[0].span.name).toBe("root");
    expect(result[0].children).toHaveLength(1);
    expect(result[0].children[0].span.name).toBe("child");
    expect(result[0].children[0].children).toHaveLength(1);
    expect(result[0].children[0].children[0].span.name).toBe("grandchild");
    expect(result[0].children[0].children[0].children).toHaveLength(1);
    expect(result[0].children[0].children[0].children[0].span.name).toBe(
      "great-grandchild",
    );
    expect(result[0].children[0].children[0].children[0].children).toHaveLength(
      0,
    );
  });

  it("should handle a complex tree with multiple branches", () => {
    const spans = [
      createSpan("root", null, "root"),
      createSpan("child-a", "root", "child-a"),
      createSpan("child-b", "root", "child-b"),
      createSpan("grandchild-a1", "child-a", "grandchild-a1"),
      createSpan("grandchild-a2", "child-a", "grandchild-a2"),
      createSpan("grandchild-b1", "child-b", "grandchild-b1"),
    ];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(1);
    expect(result[0].children).toHaveLength(2);

    const childA = result[0].children.find((c) => c.span.spanId === "child-a");
    const childB = result[0].children.find((c) => c.span.spanId === "child-b");

    expect(childA).toBeDefined();
    expect(childA!.children).toHaveLength(2);
    expect(childA!.children[0].span.spanId).toBe("grandchild-a1");
    expect(childA!.children[1].span.spanId).toBe("grandchild-a2");

    expect(childB).toBeDefined();
    expect(childB!.children).toHaveLength(1);
    expect(childB!.children[0].span.spanId).toBe("grandchild-b1");
  });

  it("should handle spans given in any order", () => {
    // Provide spans in reverse order (children before parents)
    const spans = [
      createSpan("grandchild", "child", "grandchild"),
      createSpan("child", "root", "child"),
      createSpan("root", null, "root"),
    ];

    const result = buildSpanTree(spans);

    expect(result).toHaveLength(1);
    expect(result[0].span.spanId).toBe("root");
    expect(result[0].children).toHaveLength(1);
    expect(result[0].children[0].span.spanId).toBe("child");
    expect(result[0].children[0].children).toHaveLength(1);
    expect(result[0].children[0].children[0].span.spanId).toBe("grandchild");
  });

  it("should handle orphan spans (parent not in list)", () => {
    // This case represents a partial trace where parent span wasn't included
    const spans = [
      createSpan("orphan", "missing-parent", "orphan-span"),
      createSpan("root", null, "root-span"),
    ];

    const result = buildSpanTree(spans);

    // Should only return spans that are truly roots (parentSpanId === null)
    expect(result).toHaveLength(1);
    expect(result[0].span.spanId).toBe("root");
    // The orphan is grouped under "missing-parent" key, but since that parent
    // doesn't exist, it won't appear anywhere in the tree
  });
});
