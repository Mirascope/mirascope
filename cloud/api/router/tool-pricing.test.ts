import { describe, it, expect } from "@effect/vitest";

import {
  TOOL_PRICING,
  getToolPricing,
  calculateToolCost,
  type ToolType,
} from "@/api/router/tool-pricing";

describe("tool-pricing", () => {
  describe("TOOL_PRICING", () => {
    it("should have pricing for anthropic_web_search", () => {
      const pricing = TOOL_PRICING.anthropic_web_search;
      expect(pricing).toBeDefined();
      expect(pricing.costPerCall).toBeDefined();
      expect(pricing.costPerCall).toBeGreaterThan(0n);
    });

    it("should have pricing for anthropic_code_execution", () => {
      const pricing = TOOL_PRICING.anthropic_code_execution;
      expect(pricing).toBeDefined();
      expect(pricing.costPerHour).toBeDefined();
      expect(pricing.costPerHour).toBeGreaterThan(0n);
      expect(pricing.minBillingSeconds).toBe(300); // 5 minutes
    });

    it("should have pricing for google_grounding_search", () => {
      const pricing = TOOL_PRICING.google_grounding_search;
      expect(pricing).toBeDefined();
      expect(pricing.costPerCall).toBeDefined();
      expect(pricing.costPerCall).toBeGreaterThan(0n);
    });

    it("should have pricing for openai_web_search", () => {
      const pricing = TOOL_PRICING.openai_web_search;
      expect(pricing).toBeDefined();
      expect(pricing.costPerCall).toBeDefined();
      expect(pricing.costPerCall).toBeGreaterThan(0n);
    });

    it("should have pricing for openai_code_interpreter", () => {
      const pricing = TOOL_PRICING.openai_code_interpreter;
      expect(pricing).toBeDefined();
      expect(pricing.costPerHour).toBeDefined();
      expect(pricing.costPerHour).toBeGreaterThan(0n);
      expect(pricing.minBillingSeconds).toBe(3600); // 1 hour
    });

    it("should have pricing for openai_file_search", () => {
      const pricing = TOOL_PRICING.openai_file_search;
      expect(pricing).toBeDefined();
      expect(pricing.costPerCall).toBeDefined();
      expect(pricing.costPerCall).toBeGreaterThan(0n);
    });
  });

  describe("getToolPricing", () => {
    it("should return pricing for known tool types", () => {
      const pricing = getToolPricing("anthropic_web_search");
      expect(pricing).toBeDefined();
      expect(pricing?.costPerCall).toBeDefined();
    });

    it("should return pricing for openai_code_interpreter", () => {
      const pricing = getToolPricing("openai_code_interpreter");
      expect(pricing).toBeDefined();
      expect(pricing?.costPerHour).toBeDefined();
      expect(pricing?.minBillingSeconds).toBe(3600);
    });

    it("should return null for unknown tool type", () => {
      // Use type assertion to test with invalid tool type
      const pricing = getToolPricing("unknown_tool" as ToolType);
      expect(pricing).toBeNull();
    });
  });

  describe("calculateToolCost", () => {
    describe("per-call pricing", () => {
      it("should calculate cost for single call", () => {
        const cost = calculateToolCost("anthropic_web_search", 1);
        expect(cost).toBeDefined();
        expect(cost).toBeGreaterThan(0n);
        // $0.01 per call = 100 centi-cents (1 centi-cent = $0.0001)
        expect(cost).toBe(100n);
      });

      it("should calculate cost for multiple calls", () => {
        const cost = calculateToolCost("openai_web_search", 5);
        expect(cost).toBeDefined();
        // $0.01 per call * 5 = 500 centi-cents
        expect(cost).toBe(500n);
      });

      it("should return 0n for zero calls", () => {
        const cost = calculateToolCost("anthropic_web_search", 0);
        expect(cost).toBe(0n);
      });

      it("should calculate cost for google grounding search", () => {
        const cost = calculateToolCost("google_grounding_search", 2);
        expect(cost).toBeDefined();
        // $0.014 per query * 2 = 280 centi-cents
        expect(cost).toBe(280n);
      });

      it("should calculate cost for openai file search", () => {
        const cost = calculateToolCost("openai_file_search", 10);
        expect(cost).toBeDefined();
        // $0.0025 per call * 10 = 250 centi-cents
        expect(cost).toBe(250n);
      });
    });

    describe("time-based pricing", () => {
      it("should apply minimum billing for anthropic code execution", () => {
        // Even with 0 duration, should bill for 5 minutes minimum
        const cost = calculateToolCost("anthropic_code_execution", 1);
        expect(cost).toBeDefined();
        // $0.05/hour = 500 centi-cents/hour
        // 500 * 300 / 3600 = 41 centi-cents (BigInt truncation)
        expect(cost).toBe(41n);
      });

      it("should bill for actual duration when greater than minimum", () => {
        // 10 minutes (600 seconds) > 5 minute minimum
        const cost = calculateToolCost("anthropic_code_execution", 1, 600);
        expect(cost).toBeDefined();
        // $0.05/hour = 500 centi-cents/hour
        // 500 * 600 / 3600 = 83 centi-cents (BigInt truncation)
        expect(cost).toBe(83n);
      });

      it("should use minimum when duration is less than minimum", () => {
        // 2 minutes (120 seconds) < 5 minute minimum
        const cost = calculateToolCost("anthropic_code_execution", 1, 120);
        expect(cost).toBeDefined();
        // Should bill for 5 minutes minimum
        expect(cost).toBe(41n);
      });

      it("should apply minimum billing for openai code interpreter", () => {
        // OpenAI code interpreter has 1 hour minimum
        const cost = calculateToolCost("openai_code_interpreter", 1);
        expect(cost).toBeDefined();
        // $0.03/hour = 300 centi-cents/hour * 1 hour = 300 centi-cents
        expect(cost).toBe(300n);
      });

      it("should bill for actual duration when greater than 1 hour", () => {
        // 2 hours (7200 seconds)
        const cost = calculateToolCost("openai_code_interpreter", 1, 7200);
        expect(cost).toBeDefined();
        // $0.03/hour = 300 centi-cents/hour * 2 hours = 600 centi-cents
        expect(cost).toBe(600n);
      });
    });

    describe("unknown tool types", () => {
      it("should return null for unknown tool type", () => {
        const cost = calculateToolCost("unknown_tool" as ToolType, 1);
        expect(cost).toBeNull();
      });
    });
  });
});
