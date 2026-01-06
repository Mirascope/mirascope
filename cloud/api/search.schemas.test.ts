import { describe, it, expect } from "vitest";
import {
  SearchApi,
  type SearchRequest,
  type SearchResponse,
  type TraceDetailResponse,
  type AnalyticsSummaryResponse,
} from "@/api/search.schemas";

describe("SearchApi schema definitions", () => {
  describe("SearchRequest", () => {
    it("accepts valid search request with required fields", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
      };

      expect(input.startTime).toBe("2024-01-01T00:00:00Z");
      expect(input.endTime).toBe("2024-01-31T23:59:59Z");
    });

    it("accepts search request with optional filters", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
        query: "llm call",
        model: ["gpt-4", "gpt-3.5-turbo"],
        provider: ["openai"],
        hasError: false,
        limit: 100,
        offset: 0,
        sortBy: "start_time",
        sortOrder: "desc",
      };

      expect(input.query).toBe("llm call");
      expect(input.model).toHaveLength(2);
      expect(input.provider).toHaveLength(1);
      expect(input.limit).toBe(100);
    });

    it("accepts search request with attribute filters", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
        attributeFilters: [
          { key: "gen_ai.request.model", operator: "eq", value: "gpt-4" },
          { key: "custom.tag", operator: "exists" },
        ],
      };

      expect(input.attributeFilters).toHaveLength(2);
      expect(input.attributeFilters?.[0]?.operator).toBe("eq");
      expect(input.attributeFilters?.[1]?.operator).toBe("exists");
    });

    it("accepts all valid sortBy values", () => {
      const validSortByValues: SearchRequest["sortBy"][] = [
        "start_time",
        "duration_ms",
        "total_tokens",
      ];

      for (const sortBy of validSortByValues) {
        const input: SearchRequest = {
          startTime: "2024-01-01T00:00:00Z",
          endTime: "2024-01-31T23:59:59Z",
          sortBy,
        };
        expect(input.sortBy).toBe(sortBy);
      }
    });

    it("accepts all valid sortOrder values", () => {
      const validSortOrderValues: SearchRequest["sortOrder"][] = [
        "asc",
        "desc",
      ];

      for (const sortOrder of validSortOrderValues) {
        const input: SearchRequest = {
          startTime: "2024-01-01T00:00:00Z",
          endTime: "2024-01-31T23:59:59Z",
          sortOrder,
        };
        expect(input.sortOrder).toBe(sortOrder);
      }
    });
  });

  describe("SearchResponse", () => {
    it("validates response structure", () => {
      const response: SearchResponse = {
        spans: [
          {
            id: "span-id-1",
            traceId: "trace-id-1",
            spanId: "otel-span-id-1",
            name: "llm.call",
            startTime: "2024-01-15T10:00:00Z",
            durationMs: 1500,
            model: "gpt-4",
            provider: "openai",
            totalTokens: 150,
            functionId: "func-id-1",
            functionName: "my_function",
          },
        ],
        total: 1,
        hasMore: false,
      };

      expect(response.spans).toHaveLength(1);
      expect(response.spans[0]?.name).toBe("llm.call");
      expect(response.total).toBe(1);
      expect(response.hasMore).toBe(false);
    });

    it("allows null values for optional span fields", () => {
      const response: SearchResponse = {
        spans: [
          {
            id: "span-id-1",
            traceId: "trace-id-1",
            spanId: "otel-span-id-1",
            name: "http.request",
            startTime: "2024-01-15T10:00:00Z",
            durationMs: null,
            model: null,
            provider: null,
            totalTokens: null,
            functionId: null,
            functionName: null,
          },
        ],
        total: 1,
        hasMore: false,
      };

      expect(response.spans[0]?.durationMs).toBeNull();
      expect(response.spans[0]?.model).toBeNull();
    });
  });

  describe("TraceDetailResponse", () => {
    it("validates trace detail response structure", () => {
      const response: TraceDetailResponse = {
        traceId: "trace-id-1",
        spans: [
          {
            id: "span-id-1",
            traceDbId: "trace-db-id-1",
            traceId: "trace-id-1",
            spanId: "otel-span-id-1",
            parentSpanId: null,
            environmentId: "env-id-1",
            projectId: "project-id-1",
            organizationId: "org-id-1",
            startTime: "2024-01-15T10:00:00Z",
            endTime: "2024-01-15T10:00:01Z",
            durationMs: 1000,
            name: "root.span",
            kind: 1,
            statusCode: 0,
            statusMessage: null,
            model: "gpt-4",
            provider: "openai",
            inputTokens: 100,
            outputTokens: 50,
            totalTokens: 150,
            costUsd: 0.01,
            functionId: null,
            functionName: null,
            functionVersion: null,
            errorType: null,
            errorMessage: null,
            attributes: "{}",
            events: null,
            links: null,
            serviceName: "my-service",
            serviceVersion: "1.0.0",
            resourceAttributes: null,
          },
        ],
        rootSpanId: "otel-span-id-1",
        totalDurationMs: 1000,
      };

      expect(response.traceId).toBe("trace-id-1");
      expect(response.spans).toHaveLength(1);
      expect(response.rootSpanId).toBe("otel-span-id-1");
      expect(response.totalDurationMs).toBe(1000);
    });

    it("allows null rootSpanId and totalDurationMs for empty traces", () => {
      const response: TraceDetailResponse = {
        traceId: "non-existent-trace",
        spans: [],
        rootSpanId: null,
        totalDurationMs: null,
      };

      expect(response.spans).toHaveLength(0);
      expect(response.rootSpanId).toBeNull();
      expect(response.totalDurationMs).toBeNull();
    });
  });

  describe("AnalyticsSummaryResponse", () => {
    it("validates analytics summary response structure", () => {
      const response: AnalyticsSummaryResponse = {
        totalSpans: 1000,
        avgDurationMs: 500.5,
        p50DurationMs: 400,
        p95DurationMs: 1200,
        p99DurationMs: 2000,
        errorRate: 0.05,
        totalTokens: 150000,
        totalCostUsd: 15.5,
        topModels: [
          { model: "gpt-4", count: 500 },
          { model: "gpt-3.5-turbo", count: 400 },
        ],
        topFunctions: [
          { functionName: "my_function", count: 300 },
          { functionName: "other_function", count: 200 },
        ],
      };

      expect(response.totalSpans).toBe(1000);
      expect(response.errorRate).toBe(0.05);
      expect(response.topModels).toHaveLength(2);
      expect(response.topFunctions).toHaveLength(2);
    });

    it("allows null duration percentiles", () => {
      const response: AnalyticsSummaryResponse = {
        totalSpans: 0,
        avgDurationMs: null,
        p50DurationMs: null,
        p95DurationMs: null,
        p99DurationMs: null,
        errorRate: 0,
        totalTokens: 0,
        totalCostUsd: 0,
        topModels: [],
        topFunctions: [],
      };

      expect(response.avgDurationMs).toBeNull();
      expect(response.p50DurationMs).toBeNull();
    });
  });

  describe("SearchApi group", () => {
    it("is defined as an HttpApiGroup", () => {
      expect(SearchApi).toBeDefined();
    });
  });
});
