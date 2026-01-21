import { describe, it, expect } from "vitest";
import {
  dollarsToCenticents,
  centicentsToDollars,
  formatCostForDisplay,
  type CostInCenticents,
} from "@/api/router/cost-utils";

describe("cost-utils", () => {
  describe("dollarsToCenticents", () => {
    it("should convert $1.00 to 10000 centi-cents", () => {
      expect(dollarsToCenticents(1.0)).toBe(10000n);
    });

    it("should convert $0.0001 to 1 centi-cent", () => {
      expect(dollarsToCenticents(0.0001)).toBe(1n);
    });

    it("should convert $1.2345 to 12345 centi-cents", () => {
      expect(dollarsToCenticents(1.2345)).toBe(12345n);
    });

    it("should convert $0.15 to 1500 centi-cents", () => {
      expect(dollarsToCenticents(0.15)).toBe(1500n);
    });

    it("should convert $10.50 to 105000 centi-cents", () => {
      expect(dollarsToCenticents(10.5)).toBe(105000n);
    });

    it("should handle zero correctly", () => {
      expect(dollarsToCenticents(0)).toBe(0n);
    });

    it("should handle very small amounts with rounding", () => {
      // $0.00009 = 0.9 centi-cents -> rounds to 1
      expect(dollarsToCenticents(0.00009)).toBe(1n);
    });

    it("should handle large amounts", () => {
      expect(dollarsToCenticents(1000000)).toBe(10000000000n);
    });
  });

  describe("centicentsToDollars", () => {
    it("should convert 10000 centi-cents to $1.00", () => {
      expect(centicentsToDollars(10000n)).toBe(1.0);
    });

    it("should convert 1 centi-cent to $0.0001", () => {
      expect(centicentsToDollars(1n)).toBe(0.0001);
    });

    it("should convert 12345 centi-cents to $1.2345", () => {
      expect(centicentsToDollars(12345n)).toBe(1.2345);
    });

    it("should convert 1500 centi-cents to $0.15", () => {
      expect(centicentsToDollars(1500n)).toBe(0.15);
    });

    it("should convert 105000 centi-cents to $10.50", () => {
      expect(centicentsToDollars(105000n)).toBe(10.5);
    });

    it("should handle zero correctly", () => {
      expect(centicentsToDollars(0n)).toBe(0);
    });

    it("should handle large amounts", () => {
      expect(centicentsToDollars(10000000000n)).toBe(1000000);
    });
  });

  describe("formatCostForDisplay", () => {
    it("should format 10000 centi-cents as $1.0000", () => {
      expect(formatCostForDisplay(10000n)).toBe("$1.0000");
    });

    it("should format 1 centi-cent as $0.0001", () => {
      expect(formatCostForDisplay(1n)).toBe("$0.0001");
    });

    it("should format 12345 centi-cents as $1.2345", () => {
      expect(formatCostForDisplay(12345n)).toBe("$1.2345");
    });

    it("should format 1500 centi-cents as $0.1500", () => {
      expect(formatCostForDisplay(1500n)).toBe("$0.1500");
    });

    it("should format zero correctly", () => {
      expect(formatCostForDisplay(0n)).toBe("$0.0000");
    });

    it("should format large amounts with 4 decimal places", () => {
      expect(formatCostForDisplay(10000000000n)).toBe("$1000000.0000");
    });

    it("should format fractional centi-cents correctly", () => {
      // 12346 centi-cents = $1.2346
      expect(formatCostForDisplay(12346n)).toBe("$1.2346");
    });
  });

  describe("round-trip conversion", () => {
    it("should maintain precision for round-trip conversions", () => {
      const values: number[] = [0, 0.0001, 0.15, 1.0, 1.2345, 10.5, 100.99];

      for (const dollars of values) {
        const centicents = dollarsToCenticents(dollars);
        const backToDollars = centicentsToDollars(centicents);
        expect(backToDollars).toBeCloseTo(dollars, 4);
      }
    });

    it("should handle centi-cents to dollars and back", () => {
      const centicents: CostInCenticents[] = [
        0n,
        1n,
        1500n,
        10000n,
        12345n,
        105000n,
      ];

      for (const cc of centicents) {
        const dollars = centicentsToDollars(cc);
        const backToCenticents = dollarsToCenticents(dollars);
        expect(backToCenticents).toBe(cc);
      }
    });
  });

  describe("type safety", () => {
    it("should ensure CostInCenticents is a bigint", () => {
      const cost: CostInCenticents = 12345n;
      expect(typeof cost).toBe("bigint");
    });
  });
});
