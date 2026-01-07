import { describe, it, expect } from "vitest";
import { Layer } from "effect";
import { Database } from "@/db/database";

describe("Database", () => {
  describe("Live", () => {
    it("creates a Database layer from config", () => {
      const layer = Database.Live({
        database: { connectionString: "postgresql://test" },
        payments: {
          apiKey: "sk_test_key",
          routerPriceId: "price_test",
          routerMeterId: "meter_test",
        },
      });

      // Verify it returns a Layer
      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });
});
