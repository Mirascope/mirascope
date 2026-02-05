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
          claws: 1,
          clawInstanceType: "basic",
          includedCreditsCenticents: 10_000,
          burstCreditsCenticents: 2_000,
          estimatedRequestsPerDay: 70,
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
          claws: 1,
          clawInstanceType: "standard-2",
          includedCreditsCenticents: 500_000,
          burstCreditsCenticents: 100_000,
          estimatedRequestsPerDay: 50,
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
          claws: 3,
          clawInstanceType: "standard-3",
          includedCreditsCenticents: 2_500_000,
          burstCreditsCenticents: 500_000,
          estimatedRequestsPerDay: 300,
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

    describe("claw limits", () => {
      it("should have valid claw counts for all tiers", () => {
        expect(PLAN_LIMITS.free.claws).toBe(1);
        expect(PLAN_LIMITS.pro.claws).toBe(1);
        expect(PLAN_LIMITS.team.claws).toBe(3);
      });

      it("should have increasing instance types across tiers", () => {
        expect(PLAN_LIMITS.free.clawInstanceType).toBe("basic");
        expect(PLAN_LIMITS.pro.clawInstanceType).toBe("standard-2");
        expect(PLAN_LIMITS.team.clawInstanceType).toBe("standard-3");
      });

      it("should have increasing included credits across tiers", () => {
        expect(PLAN_LIMITS.free.includedCreditsCenticents).toBeLessThan(
          PLAN_LIMITS.pro.includedCreditsCenticents,
        );
        expect(PLAN_LIMITS.pro.includedCreditsCenticents).toBeLessThan(
          PLAN_LIMITS.team.includedCreditsCenticents,
        );
      });

      it("should have burst credits at 20% of weekly credits", () => {
        for (const tier of PLAN_TIERS) {
          const limits = PLAN_LIMITS[tier];
          expect(limits.burstCreditsCenticents).toBe(
            limits.includedCreditsCenticents * 0.2,
          );
        }
      });
    });

    describe("type safety", () => {
      it("should satisfy PlanLimits interface", () => {
        const limits: PlanLimits = PLAN_LIMITS.free;
        expect(limits).toHaveProperty("seats");
        expect(limits).toHaveProperty("projects");
        expect(limits).toHaveProperty("spansPerMonth");
        expect(limits).toHaveProperty("apiRequestsPerMinute");
        expect(limits).toHaveProperty("claws");
        expect(limits).toHaveProperty("clawInstanceType");
        expect(limits).toHaveProperty("includedCreditsCenticents");
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
        claws: 1,
        clawInstanceType: "basic",
        includedCreditsCenticents: 10_000,
        burstCreditsCenticents: 2_000,
        estimatedRequestsPerDay: 70,
      };
      expect(limits).toBeDefined();
    });
  });
});
