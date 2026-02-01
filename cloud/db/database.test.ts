import { Layer } from "effect";
import { describe, it, expect } from "vitest";

import { Database } from "@/db/database";

describe("Database", () => {
  describe("Live", () => {
    it("creates a Database layer from config", () => {
      const layer = Database.Live({
        database: { connectionString: "postgresql://test" },
        payments: {
          secretKey: "sk_test_key",
          webhookSecret: "whsec_test",
          routerPriceId: "price_test",
          routerMeterId: "meter_test",
          cloudFreePriceId: "price_cloud_free_test",
          cloudProPriceId: "price_cloud_pro_test",
          cloudTeamPriceId: "price_cloud_team_test",
          cloudSpansPriceId: "price_cloud_spans_test",
          cloudSpansMeterId: "meter_cloud_spans_test",
        },
      });

      // Verify it returns a Layer
      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });
});
