import { describe, it, expect } from "vitest";
import { PLAN_LIMITS, type PlanLimits } from "./plan-limits";
import type { PlanTier } from "./types";

describe("plan-limits", () => {
  describe("PLAN_LIMITS structure", () => {
    it("contains all three plan tiers", () => {
      expect(PLAN_LIMITS).toHaveProperty("free");
      expect(PLAN_LIMITS).toHaveProperty("pro");
      expect(PLAN_LIMITS).toHaveProperty("team");
    });

    it("has correct free plan limits", () => {
      const freeLimits = PLAN_LIMITS.free;

      expect(freeLimits.seats).toBe(1);
      expect(freeLimits.projects).toBe(1);
      expect(freeLimits.spansPerMonth).toBe(1_000_000);
      expect(freeLimits.apiRequestsPerMinute).toBe(100);
    });

    it("has correct pro plan limits", () => {
      const proLimits = PLAN_LIMITS.pro;

      expect(proLimits.seats).toBe(5);
      expect(proLimits.projects).toBe(5);
      expect(proLimits.spansPerMonth).toBe(1_000_000);
      expect(proLimits.apiRequestsPerMinute).toBe(1000);
    });

    it("has correct team plan limits (unlimited seats and projects)", () => {
      const teamLimits = PLAN_LIMITS.team;

      expect(teamLimits.seats).toBe(Infinity); // Unlimited
      expect(teamLimits.projects).toBe(Infinity); // Unlimited
      expect(teamLimits.spansPerMonth).toBe(1_000_000);
      expect(teamLimits.apiRequestsPerMinute).toBe(10000);
    });
  });

  describe("PlanLimits interface", () => {
    it("all plan limits conform to the interface", () => {
      const validatePlanLimits = (limits: PlanLimits) => {
        expect(limits).toHaveProperty("seats");
        expect(limits).toHaveProperty("projects");
        expect(limits).toHaveProperty("spansPerMonth");
        expect(limits).toHaveProperty("apiRequestsPerMinute");
        expect(typeof limits.spansPerMonth).toBe("number");
        expect(typeof limits.apiRequestsPerMinute).toBe("number");
        // seats and projects are numbers (including Infinity for unlimited)
        expect(typeof limits.seats).toBe("number");
        expect(typeof limits.projects).toBe("number");
      };

      validatePlanLimits(PLAN_LIMITS.free);
      validatePlanLimits(PLAN_LIMITS.pro);
      validatePlanLimits(PLAN_LIMITS.team);
    });
  });

  describe("PlanTier type", () => {
    it("accepts valid plan tier values", () => {
      const tierValues: PlanTier[] = ["free", "pro", "team"];

      tierValues.forEach((tier) => {
        expect(PLAN_LIMITS[tier]).toBeDefined();
      });
    });
  });

  describe("Plan comparison", () => {
    it("free plan has the most restrictive limits (excluding unlimited nulls)", () => {
      const { free, pro, team } = PLAN_LIMITS;

      // Free has fewer seats than Pro
      expect(free.seats).toBeLessThan(pro.seats);

      // Free has fewer projects than Pro
      expect(free.projects).toBeLessThan(pro.projects);

      // Free has lower API rate limit than Pro
      expect(free.apiRequestsPerMinute).toBeLessThan(pro.apiRequestsPerMinute);

      // Free has lower API rate limit than Team
      expect(free.apiRequestsPerMinute).toBeLessThan(team.apiRequestsPerMinute);
    });

    it("pro plan has more limits than free but less than team", () => {
      const { free, pro, team } = PLAN_LIMITS;

      // Pro has more seats than Free
      expect(pro.seats).toBeGreaterThan(free.seats);

      // Pro has more projects than Free
      expect(pro.projects).toBeGreaterThan(free.projects);

      // Pro has higher API rate limit than Free
      expect(pro.apiRequestsPerMinute).toBeGreaterThan(
        free.apiRequestsPerMinute,
      );

      // Pro has lower API rate limit than Team
      expect(pro.apiRequestsPerMinute).toBeLessThan(team.apiRequestsPerMinute);
    });

    it("team plan has unlimited seats and projects", () => {
      const teamLimits = PLAN_LIMITS.team;

      expect(teamLimits.seats).toBe(Infinity);
      expect(teamLimits.projects).toBe(Infinity);
    });

    it("all plans have the same base span quota", () => {
      const { free, pro, team } = PLAN_LIMITS;

      expect(free.spansPerMonth).toBe(1_000_000);
      expect(pro.spansPerMonth).toBe(1_000_000);
      expect(team.spansPerMonth).toBe(1_000_000);
    });
  });
});
