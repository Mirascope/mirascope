/**
 * @fileoverview Tests for plan types, constants, and limits.
 */

import { describe, it, expect } from "vitest";
import {
  PLAN_TIERS,
  PLAN_TIER_ORDER,
  PLAN_LIMITS,
  type PlanTier,
  type PlanLimits,
} from "./plans";

describe("Plans Module", () => {
  describe("PLAN_TIERS", () => {
    it("should contain all expected plan tiers", () => {
      expect(PLAN_TIERS).toEqual(["free", "pro", "team"]);
    });
  });

  describe("PLAN_TIER_ORDER", () => {
    it("should have correct ordering (free < pro < team)", () => {
      expect(PLAN_TIER_ORDER.free).toBe(0);
      expect(PLAN_TIER_ORDER.pro).toBe(1);
      expect(PLAN_TIER_ORDER.team).toBe(2);
    });

    it("should enable upgrade/downgrade comparison", () => {
      // Upgrades
      expect(PLAN_TIER_ORDER.pro > PLAN_TIER_ORDER.free).toBe(true);
      expect(PLAN_TIER_ORDER.team > PLAN_TIER_ORDER.pro).toBe(true);
      expect(PLAN_TIER_ORDER.team > PLAN_TIER_ORDER.free).toBe(true);

      // Downgrades
      expect(PLAN_TIER_ORDER.free < PLAN_TIER_ORDER.pro).toBe(true);
      expect(PLAN_TIER_ORDER.pro < PLAN_TIER_ORDER.team).toBe(true);
      expect(PLAN_TIER_ORDER.free < PLAN_TIER_ORDER.team).toBe(true);
    });
  });

  describe("PLAN_LIMITS", () => {
    describe("free plan", () => {
      it("should have correct limits", () => {
        expect(PLAN_LIMITS.free).toEqual({
          seats: 1,
          projects: 1,
          spansPerMonth: 1_000_000,
          apiRequestsPerMinute: 100,
          dataRetentionDays: 30,
        });
      });
    });

    describe("pro plan", () => {
      it("should have correct limits", () => {
        expect(PLAN_LIMITS.pro).toEqual({
          seats: 5,
          projects: 5,
          spansPerMonth: Infinity,
          apiRequestsPerMinute: 1000,
          dataRetentionDays: 90,
        });
      });

      it("should have unlimited spans", () => {
        expect(PLAN_LIMITS.pro.spansPerMonth).toBe(Infinity);
      });
    });

    describe("team plan", () => {
      it("should have correct limits", () => {
        expect(PLAN_LIMITS.team).toEqual({
          seats: Infinity,
          projects: Infinity,
          spansPerMonth: Infinity,
          apiRequestsPerMinute: 10000,
          dataRetentionDays: 180,
        });
      });

      it("should have unlimited seats, projects, and spans", () => {
        expect(PLAN_LIMITS.team.seats).toBe(Infinity);
        expect(PLAN_LIMITS.team.projects).toBe(Infinity);
        expect(PLAN_LIMITS.team.spansPerMonth).toBe(Infinity);
      });
    });

    describe("limit enforcement", () => {
      it("should have increasing API rate limits across tiers", () => {
        expect(PLAN_LIMITS.free.apiRequestsPerMinute).toBeLessThan(
          PLAN_LIMITS.pro.apiRequestsPerMinute,
        );
        expect(PLAN_LIMITS.pro.apiRequestsPerMinute).toBeLessThan(
          PLAN_LIMITS.team.apiRequestsPerMinute,
        );
      });

      it("should have hard limit for free, unlimited for pro/team", () => {
        expect(PLAN_LIMITS.free.spansPerMonth).toBe(1_000_000);
        expect(PLAN_LIMITS.pro.spansPerMonth).toBe(Infinity);
        expect(PLAN_LIMITS.team.spansPerMonth).toBe(Infinity);
      });
    });

    describe("type safety", () => {
      it("should satisfy PlanLimits interface", () => {
        const limits: PlanLimits = PLAN_LIMITS.free;
        expect(limits).toHaveProperty("seats");
        expect(limits).toHaveProperty("projects");
        expect(limits).toHaveProperty("spansPerMonth");
        expect(limits).toHaveProperty("apiRequestsPerMinute");
      });

      it("should have all plan tiers as keys", () => {
        const planKeys = Object.keys(PLAN_LIMITS);
        expect(planKeys).toEqual(
          expect.arrayContaining(["free", "pro", "team"]),
        );
        expect(planKeys.length).toBe(3);
      });
    });
  });

  describe("Type exports", () => {
    it("should export PlanTier type", () => {
      // Type-only test - if this compiles, the type exists
      const tier: PlanTier = "free";
      expect(tier).toBe("free");
    });

    it("should export PlanLimits interface", () => {
      // Type-only test - if this compiles, the interface exists
      const limits: PlanLimits = {
        seats: 1,
        projects: 1,
        spansPerMonth: 1_000_000,
        apiRequestsPerMinute: 100,
        dataRetentionDays: 30,
      };
      expect(limits).toBeDefined();
    });
  });
});
