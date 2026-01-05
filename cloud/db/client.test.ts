import { describe, it, expect } from "vitest";
import { Layer } from "effect";
import { DrizzleORM } from "@/db/client";

describe("DrizzleORM", () => {
  describe("layer", () => {
    it("creates a layer with connectionString", () => {
      const layer = DrizzleORM.layer({
        connectionString: "postgresql://user:pass@localhost:5432/db",
      });

      // Verify it returns a Layer
      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });

    it("creates a layer with individual connection parameters", () => {
      const layer = DrizzleORM.layer({
        host: "localhost",
        port: 5432,
        database: "testdb",
        username: "testuser",
        password: "testpass",
      });

      // Verify it returns a Layer
      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });

  describe("Default", () => {
    it("is a Layer", () => {
      expect(Layer.isLayer(DrizzleORM.Default)).toBe(true);
    });
  });
});
